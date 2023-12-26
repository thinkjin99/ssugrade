import json

import boto3
import firebase_admin as admin
from firebase_admin import credentials
from firebase_admin import messaging

# 어드민 계정 정보를 이용해 firebase-admin을 초기화
cred = credentials.Certificate("config.json")
admin.initialize_app(cred)


# sqs 메시지 파싱
def parse_sqs_message(record):
    title = record["messageAttributes"]["title"]["stringValue"]
    receipt_handle = record["receiptHandle"]
    body = json.loads(record["body"])
    return {
        "receipt_handle": receipt_handle,
        "title": title,
        "notification_body": body["notification_body"],
        "fcm_token": body["fcm_token"],
        "data": body["data"],
    }


# firebase 모듈을 이용한 푸시 알림 message send
def send_notification(payload):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=payload["title"],
                body=payload["notification_body"],
            ),
            data={"grades": json.dumps(payload["data"])},
            token=payload["fcm_token"],
        )
        res = messaging.send(message)
        print(f"send: {res} complete")

    except Exception as e:
        print(f"error occurs {payload} {str(e)}")


def delete_message_from_sqs(receipt_handle: str):
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def lambda_handler(event, context):
    for record in event["Records"]:
        parsed_payload = parse_sqs_message(record)
        send_notification(parsed_payload)
        delete_message_from_sqs(parsed_payload["receipt_handle"])

    return
