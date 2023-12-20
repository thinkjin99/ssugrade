import firebase_admin as admin
from firebase_admin import credentials
from firebase_admin import messaging

# 어드민 계정 정보를 이용해 firebase-admin을 초기화
cred = credentials.Certificate("config.json")
admin.initialize_app(cred)


# firebase 모듈을 이용한 푸시 알림 message send
def send_notification(payload):
    fcm_token = payload["fcm_token"]
    message = messaging.Message(
        notification=messaging.Notification(
            title=payload["type"],
            body=payload["payload"],
        ),
        token=fcm_token,
    )
    print(message)
    return messaging.send(message)


# sqs 메시지 파싱
def parse_sqs_message(sqs_message):
    for record in sqs_message["Records"]:
        type_ = record["messageAttributes"]["type"]["stringValue"]
        payload = record["body"]
        parsed_payload = {"type": type_, "payload": payload}
        print(parsed_payload)


def lambda_handler(event, context):
    parsed_payload = parse_sqs_message(event)
    return
