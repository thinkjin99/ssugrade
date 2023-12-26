import datetime
import json
import boto3
import requests


def push_sqs(
    data: list, notification_body: list | str, fcm_token: str, attributes: dict
):
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    now = datetime.datetime.now().strftime("%Y-%M-%d %H:%m:%S")
    resp = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(
            {
                "fcm_token": fcm_token,
                "notification_body": notification_body,
                "data": data,
                "time": now,
            }
        ),
        MessageGroupId="ssurade",
        MessageAttributes=attributes,
    )
    return resp


def create_message(student_number: str, fcm_token: str):
    payload = {"student_number": student_number, "fcm_token": fcm_token}
    try:
        resp = requests.post(
            "http://ssugrade-scraping-elb-809623769.ap-northeast-2.elb.amazonaws.com/grade/now",
            json=payload,
            timeout=20,
        )
        data = resp.json()

    except Exception as e:
        print(e)
        raise e

    if resp.status_code == 200:
        notification_body = "새로운 성적이 나왔어요"
        attributes = {
            "title": {"StringValue": "신규 성적 갱신", "DataType": "String"},
        }

    else:
        if resp.json()["detail"] == "Login Error!":
            notification_body = "로그인 토큰이 만료 됐어요"
            attributes = {
                "title": {"StringValue": "로그인 에러", "DataType": "String"},
            }
        else:
            notification_body = "에러 발생"
            attributes = {
                "title": {"StringValue": "서버 에러", "DataType": "String"},
            }

    return data, notification_body, fcm_token, attributes


def lambda_handler(event, context):
    body = json.loads(event["body"])
    student_number = body["student_number"]
    fcm_token = body["fcm_token"]
    msg = create_message(student_number, fcm_token)
    if msg:
        try:
            res = push_sqs(*msg)
            return {"body": res, "statusCode": 200}
        except Exception as e:
            return {"body": str(e), "statusCode": 500}
