import os
import time
import math
import boto3
from botocore.exceptions import ClientError

# configuration
ASU_ID = os.getenv("ASU_ID", "1233282975")
REGION = os.getenv("AWS_REGION", "us-east-1")
REQ_QUEUE_NAME = os.getenv("REQ_QUEUE_NAME", f"{ASU_ID}-req-queue")

MIN_INSTANCES = int(os.getenv("MIN_INSTANCES", "0"))
MAX_INSTANCES = int(os.getenv("MAX_INSTANCES", "15"))
APP_NAME_PREFIX = os.getenv("APP_NAME_PREFIX", "app-tier-instance-")

INSTANCE_PROFILE_ARN = os.getenv("INSTANCE_PROFILE_ARN", "arn:aws:iam::703800905816:instance-profile/cse546-ec2-role")
SECURITY_GROUP_IDS = os.getenv("SECURITY_GROUP_IDS", "sg-0d53fae5b18bdcf85")
SUBNET_ID = os.getenv("SUBNET_ID", "subnet-01029bec0302bedb0")
AMI_ID = os.getenv("AMI_ID", "ami-0c0f7669249208047")
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE", "t3.micro")
KEY_NAME = os.getenv("KEY_NAME", "cse546-rsa")

MESSAGES_PER_INSTANCE = int(os.getenv("MESSAGES_PER_INSTANCE", "1"))
POLL_SEC = float(os.getenv("POLL_SEC", "5"))

# aws clients
ec2 = boto3.resource("ec2", region_name=REGION)
ec2_client = boto3.client("ec2", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

def get_queue_url(name: str) -> str:
    return sqs.get_queue_url(QueueName=name)["QueueUrl"]

REQ_QURL = get_queue_url(REQ_QUEUE_NAME)

def backlog_counts():
    attrs = sqs.get_queue_attributes(
        QueueUrl=REQ_QURL,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
        ],
    )["Attributes"]
    visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
    inflight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    return {"visible": visible, "inflight": inflight, "total": visible + inflight}

def list_app_instances():
    filters = [
        {"Name": "tag:Name", "Values": [f"{APP_NAME_PREFIX}*"]},
        {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
    ]
    return list(ec2.instances.filter(Filters=filters))

def count_running(instances):
    return sum(1 for i in instances if i.state["Name"] in ("running", "pending"))

def pick_stopped(instances):
    return [i for i in instances if i.state["Name"] == "stopped"]

def name_of(instance):
    for tag in instance.tags or []:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return instance.id

def ensure_pool_upto(target):
    existing = list_app_instances()
    if len(existing) >= target:
        print(f"Pool already has {len(existing)} instances, target is {target}", flush=True)
        return

    missing = target - len(existing)
    if not AMI_ID or not SECURITY_GROUP_IDS:
        print("AMI ID or security group is missing, skipping creation", flush=True)
        return

    sg_ids = [s.strip() for s in SECURITY_GROUP_IDS.split(",") if s.strip()]
    user_data = """#!/bin/bash
        set -eux
        cd /home/ubuntu/cse546-fall-2025/app-tier/model/
        source /home/ubuntu/cse546-fall-2025/venv/bin/activate
        python3 backend.py > /home/ubuntu/cse546-fall-2025/app-tier/model/backend.log 2>&1 &
    """
    for k in range(missing):
        index = len(existing) + k + 1
        name_tag = f"{APP_NAME_PREFIX}{index}"
        params = {
            "ImageId": AMI_ID,
            "InstanceType": INSTANCE_TYPE,
            "MinCount": 1,
            "MaxCount": 1,
            "TagSpecifications": [
                {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": name_tag}]}
            ],
            "UserData": user_data,
            "SecurityGroupIds": sg_ids,
        }
        if KEY_NAME:
            params["KeyName"] = KEY_NAME
        if SUBNET_ID:
            params["SubnetId"] = SUBNET_ID
        if INSTANCE_PROFILE_ARN:
            params["IamInstanceProfile"] = {"Arn": INSTANCE_PROFILE_ARN}

        try:
            ec2_client.run_instances(**params)
            print(f"Created new instance {name_tag}", flush=True)
        except ClientError as e:
            print(f"Failed to create instance {name_tag}: {e}", flush=True)

def start_some(stopped, needed):
    if needed <= 0 or not stopped:
        return
    to_start = stopped[:needed]
    ec2_client.start_instances(InstanceIds=[i.id for i in to_start])
    for i in to_start:
        print(f"Starting stopped instance {name_of(i)}", flush=True)

def stop_all_if_idle(instances):
    running = [i for i in instances if i.state["Name"] == "running"]
    if not running:
        return
    print(f"Queue empty. {len(running)} app-tier instances still running, letting them self-stop", flush=True)

def desired_instances(backlog_total):
    if backlog_total <= 0:
        return 0
    desired = math.ceil(backlog_total / max(1, MESSAGES_PER_INSTANCE))
    return max(MIN_INSTANCES, min(desired, MAX_INSTANCES))

def main():
    print("Autoscaling controller started", flush=True)
    print(f"Watching queue {REQ_QUEUE_NAME} in region {REGION}", flush=True)

    while True:
        try:
            # Check queue size
            q = backlog_counts()
            instances = list_app_instances()
            running_cnt = count_running(instances)
            target = desired_instances(q["total"])

            print(f"Queue: {q} | Running: {running_cnt} | Desired: {target}", flush=True)

            # --- Scale logic ---
            if q["total"] == 0:
                # nothing to process, allow workers to self-stop
                stop_all_if_idle(instances)
            else:
                # only create new instances when there are messages waiting
                ensure_pool_upto(MAX_INSTANCES)

            # scale adjustments
            delta = target - running_cnt
            if delta > 0:
                stopped_pool = pick_stopped(instances)
                print(f"Scaling up by {delta} instances, stopped pool size is {len(stopped_pool)}", flush=True)
                start_some(stopped_pool, delta)
            elif delta < 0:
                print("Scaling down not forced, letting workers self-terminate", flush=True)
            else:
                print("System stable, no scaling change needed", flush=True)

        except ClientError as e:
            print(f"AWS client error: {e}", flush=True)
        except Exception as e:
            print(f"Unexpected error: {e}", flush=True)

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    main()
