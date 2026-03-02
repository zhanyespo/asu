import datetime
import os
import uuid
import pathlib
import subprocess
import time
import urllib.request
import boto3
from botocore.exceptions import ClientError

# configuration
ASU_ID = os.getenv("ASU_ID", "1233282975")
REGION = os.getenv("AWS_REGION", "us-east-1")

IN_BUCKET = os.getenv("IN_BUCKET", f"{ASU_ID}-in-bucket")
OUT_BUCKET = os.getenv("OUT_BUCKET", f"{ASU_ID}-out-bucket")
REQ_QUEUE_NAME = os.getenv("REQ_QUEUE_NAME", f"{ASU_ID}-req-queue")
RESP_QUEUE_NAME = os.getenv("RESP_QUEUE_NAME", f"{ASU_ID}-resp-queue")

WAIT_TIME = int(os.getenv("WAIT_TIME", "20"))
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "120"))
WORKDIR = os.getenv("WORKDIR", "/tmp/app_worker")
os.makedirs(WORKDIR, exist_ok=True)

# aws clients
s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)
ec2 = boto3.client("ec2", region_name=REGION)

def get_queue_url(name: str) -> str:
    return sqs.get_queue_url(QueueName=name)["QueueUrl"]

REQ_QURL = get_queue_url(REQ_QUEUE_NAME)
RESP_QURL = get_queue_url(RESP_QUEUE_NAME)

# run face recognition model
def classify(local_path: str) -> str:
    model_dir = os.path.dirname(__file__)
    script_path = os.path.join(model_dir, "face_recognition.py")
    try:
        result = subprocess.run(
            ["python3", script_path, local_path],
            cwd=model_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "model error")
        label = result.stdout.strip()
        if not label:
            raise RuntimeError("model returned empty label")
        return label
    except Exception as e:
        raise RuntimeError(f"model inference failed: {e}")

# process one message
def process_message(msg: dict):
    start_time = time.time()

    receipt = msg["ReceiptHandle"]
    attrs = msg.get("MessageAttributes", {}) or {}
    request_id = attrs.get("request_id", {}).get("StringValue")
    bucket = attrs.get("bucket", {}).get("StringValue", IN_BUCKET)
    key = attrs.get("key", {}).get("StringValue")

    if not key or not request_id:
        print("Malformed message, deleting it", flush=True)
        sqs.delete_message(QueueUrl=REQ_QURL, ReceiptHandle=receipt)
        return

    filename = os.path.basename(key)
    local_path = os.path.join(WORKDIR, f"{uuid.uuid4()}_{filename}")
    print(f"[{datetime.datetime.now()}] Processing request {request_id} for {key}", flush=True)

    # download image from s3
    t0 = time.time()
    try:
        print(f"[{datetime.datetime.now()}] Downloading {key} from {bucket}", flush=True)
        s3.download_file(bucket, key, local_path)
        print(f"[{datetime.datetime.now()}] Downloaded in {time.time() - t0:.2f} sec", flush=True)
    except Exception as e:
        print(f"Failed to download from S3: {e}", flush=True)
        return

    # run inference
    t1 = time.time()
    print(f"[{datetime.datetime.now()}] Running face recognition inference", flush=True)
    try:
        label = classify(local_path)
        print(f"[{datetime.datetime.now()}] Inference completed in {time.time() - t1:.2f} sec", flush=True)
    except Exception as e:
        label = f"Error: {e}"
        print(f"Classification failed: {e}", flush=True)

    # upload result to s3
    t2 = time.time()
    try:
        out_key = pathlib.Path(filename).stem
        print(f"[{datetime.datetime.now()}] Uploading result to {OUT_BUCKET}/{out_key}", flush=True)
        s3.put_object(Bucket=OUT_BUCKET, Key=out_key, Body=(label or "").encode("utf-8"))
        print(f"[{datetime.datetime.now()}] Uploaded result in {time.time() - t2:.2f} sec", flush=True)
    except Exception as e:
        print(f"Could not upload to S3: {e}", flush=True)

    # send response message
    t3 = time.time()
    try:
        print(f"[{datetime.datetime.now()}] Sending response to response queue", flush=True)
        sqs.send_message(
            QueueUrl=RESP_QURL,
            MessageBody=f"{filename}:{label}",
            MessageAttributes={
                "request_id": {"DataType": "String", "StringValue": request_id},
                "origin": {"DataType": "String", "StringValue": "app-tier"},
            },
        )
        print(f"[{datetime.datetime.now()}] Sent response in {time.time() - t3:.2f} sec", flush=True)
    except Exception as e:
        print(f"Could not send response message: {e}", flush=True)

    # delete message
    try:
        print(f"[{datetime.datetime.now()}] Deleting processed message from request queue", flush=True)
        sqs.delete_message(QueueUrl=REQ_QURL, ReceiptHandle=receipt)
    except Exception as e:
        print(f"Could not delete message: {e}", flush=True)

    try:
        os.remove(local_path)
    except OSError:
        pass

    total_time = time.time() - start_time
    print(f"[{datetime.datetime.now()}] ✅ Completed {filename} with result '{label}' in {total_time:.2f} sec", flush=True)

# stop the current instance
def stop_self_instance():
    try:
        token_req = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        )
        token = urllib.request.urlopen(token_req, timeout=2).read().decode()

        id_req = urllib.request.Request(
            "http://169.254.169.254/latest/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
        )
        instance_id = urllib.request.urlopen(id_req, timeout=2).read().decode()

        print(f"Stopping self instance {instance_id}", flush=True)
        ec2.stop_instances(InstanceIds=[instance_id])
    except Exception as e:
        print(f"Could not stop instance: {e}", flush=True)

# main function
def main_loop():
    overall_start = time.time()
    print(f"[{datetime.datetime.now()}] Backend worker started, polling for messages...", flush=True)
    empty_polls = 0
    MAX_EMPTY_POLLS = 3

    try:
        while True:
            resp = sqs.receive_message(
                QueueUrl=REQ_QURL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=WAIT_TIME,
                VisibilityTimeout=VISIBILITY_TIMEOUT,
                MessageAttributeNames=["All"],
            )

            messages = resp.get("Messages", [])
            if not messages:
                empty_polls += 1
                print(f"[{datetime.datetime.now()}] No messages found (#{empty_polls})", flush=True)

                # Stop only after multiple consecutive empty polls
                print(f"[{datetime.datetime.now()}] Queue empty for {MAX_EMPTY_POLLS} polls. Double-checking before stop...", flush=True)
                time.sleep(5)
                # One last recheck
                attrs = sqs.get_queue_attributes(QueueUrl=REQ_QURL, AttributeNames=["ApproximateNumberOfMessages"])["Attributes"]
                if int(attrs.get("ApproximateNumberOfMessages", "0")) == 0:
                    print(f"[{datetime.datetime.now()}] Confirmed empty. Stopping instance.", flush=True)
                    break
                else:
                    print(f"[{datetime.datetime.now()}] New messages appeared, continuing...", flush=True)
                    empty_polls = 0
                    continue

            empty_polls = 0  # Reset counter after finding a message
            process_message(messages[0])

    except ClientError as e:
        print(f"AWS error: {e}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        print(f"[{datetime.datetime.now()}] Total backend runtime: {time.time() - overall_start:.2f} sec", flush=True)
        stop_self_instance()



if __name__ == "__main__":
    main_loop()
