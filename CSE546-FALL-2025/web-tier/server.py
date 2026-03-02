import os
import uuid
import time
from io import BytesIO
from flask import Flask, request, Response
import boto3
from botocore.exceptions import ClientError

# configuration
ASU_ID = os.getenv("ASU_ID", "1233282975")
REGION = os.getenv("AWS_REGION", "us-east-1")
IN_BUCKET = os.getenv("IN_BUCKET", f"{ASU_ID}-in-bucket")
REQ_QUEUE_NAME = os.getenv("REQ_QUEUE_NAME", f"{ASU_ID}-req-queue")
RESP_QUEUE_NAME = os.getenv("RESP_QUEUE_NAME", f"{ASU_ID}-resp-queue")

RESPONSE_TIMEOUT = int(os.getenv("RESPONSE_TIMEOUT", "90"))
LONG_POLL_SECONDS = int(os.getenv("LONG_POLL_SECONDS", "20"))

app = Flask(__name__)
s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

def get_queue_url(name):
    return sqs.get_queue_url(QueueName=name)["QueueUrl"]

REQ_QURL = get_queue_url(REQ_QUEUE_NAME)
RESP_QURL = get_queue_url(RESP_QUEUE_NAME)

def put_image_to_s3(fileobj, bucket, key):
    fileobj.seek(0)
    s3.upload_fileobj(fileobj, bucket, key)

def send_request_to_app_tier(filename, bucket, key, request_id):
    sqs.send_message(
        QueueUrl=REQ_QURL,
        MessageBody=filename,
        MessageAttributes={
            "request_id": {"DataType": "String", "StringValue": request_id},
            "bucket": {"DataType": "String", "StringValue": bucket},
            "key": {"DataType": "String", "StringValue": key},
            "origin": {"DataType": "String", "StringValue": "web-tier"},
        },
    )

def wait_for_response(request_id, timeout_seconds):
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        resp = sqs.receive_message(
            QueueUrl=RESP_QURL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=LONG_POLL_SECONDS,
            MessageAttributeNames=["All"],
        )
        messages = resp.get("Messages", [])
        if not messages:
            continue

        for msg in messages:
            attrs = msg.get("MessageAttributes", {}) or {}
            rid = attrs.get("request_id", {}).get("StringValue")
            receipt = msg["ReceiptHandle"]

            if rid == request_id:
                body = msg["Body"]
                sqs.delete_message(QueueUrl=RESP_QURL, ReceiptHandle=receipt)
                return body
            else:
                try:
                    sqs.change_message_visibility(
                        QueueUrl=RESP_QURL,
                        ReceiptHandle=receipt,
                        VisibilityTimeout=0,
                    )
                except ClientError:
                    pass

    raise TimeoutError("Timed out waiting for response from application tier")

@app.route("/", methods=["POST"])
def handle_request():
    file = request.files.get("inputFile") or request.files.get("file") or request.files.get("image")
    if not file or not file.filename:
        return Response("No file provided under field 'file' or 'image'", status=400, mimetype="text/plain")

    filename = os.path.basename(file.filename)
    upload_key = f"uploads/{uuid.uuid4()}_{filename}"
    request_id = str(uuid.uuid4())

    try:
        print(f"Received upload request for {filename}", flush=True)
        put_image_to_s3(file.stream if hasattr(file, "stream") else BytesIO(file.read()), IN_BUCKET, upload_key)
        print(f"Uploaded {filename} to S3 bucket {IN_BUCKET}", flush=True)

        send_request_to_app_tier(filename, IN_BUCKET, upload_key, request_id)
        print(f"Sent processing request {request_id} to queue {REQ_QUEUE_NAME}", flush=True)

        result = wait_for_response(request_id, RESPONSE_TIMEOUT)
        print(f"Received response for {filename}: {result}", flush=True)

        return Response(result, status=200, mimetype="text/plain")

    except TimeoutError:
        print(f"Timeout while waiting for {filename} result", flush=True)
        return Response(f"{filename}:processing_delayed", status=504, mimetype="text/plain")
    except ClientError as e:
        print(f"AWS error while processing {filename}: {e}", flush=True)
        return Response(f"{filename}:internal_error", status=500, mimetype="text/plain")
    except Exception as e:
        print(f"Unexpected error while processing {filename}: {e}", flush=True)
        return Response(f"{filename}:internal_error", status=500, mimetype="text/plain")

if __name__ == "__main__":
    print("Web server started and listening on port 8000", flush=True)
    app.run(host="0.0.0.0", port=8000, debug=False)
