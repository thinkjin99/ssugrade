import json
import boto3

from lambda_utils import lamdba_decorator

_lambda = boto3.client("lambda", region_name="ap-northeast-2")


def login_usaint(student_number: str, password: str):
    payload = {
        "body": json.dumps({"student_number": student_number, "password": password})
    }
    res = _lambda.invoke(FunctionName="login", Payload=json.dumps(payload))
    json_res = json.loads(res["Payload"].read())
    body = json.loads(json_res.get("body"))
    if json_res.get("statusCode") == 200:
        return body
    else:
        raise AssertionError(body.get("msg"))


def update_user(student_number: str, cookies: list, fcm_token: str):
    payload = {
        "student_number": student_number,
        "cookies": cookies,
        "fcm_token": fcm_token,
    }
    res = _lambda.invoke(FunctionName="update-user", Payload=json.dumps(payload))
    json_res = json.loads(res["Payload"].read())
    body = json.loads(json_res.get("body"))
    return body


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    student_number = body["student_number"]
    password = body["password"]
    fcm_token = body["fcm_token"]

    cookies = login_usaint(student_number, password)
    res = update_user(student_number, cookies, fcm_token)
    return res
