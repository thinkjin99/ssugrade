import firebase_admin as admin
from firebase_admin import credentials
from firebase_admin import messaging
import json

# 어드민 계정 정보를 이용해 firebase-admin을 초기화
cred = credentials.Certificate("config.json")
admin.initialize_app(cred)


# firebase 모듈을 이용한 푸시 알림 message send
def send_notification(payload):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=payload["title"],
                body=payload["body"],
            ),
            token=payload["fcm_token"],
        )
        return messaging.send(message)

    except Exception as e:
        print(f"error occurs {payload} {str(e)}")


# sqs 메시지 파싱
def parse_sqs_message(record):
    title = record["messageAttributes"]["title"]["stringValue"]
    body = json.loads(record["body"])
    return {"title": title, "fcm_token": body["fcm_token"], "body": body["body"]}


def lambda_handler(event, context):
    for record in event["Records"]:
        parsed_payload = parse_sqs_message(record)
        send_notification(parsed_payload)
        print("send: ", parsed_payload)
    return
