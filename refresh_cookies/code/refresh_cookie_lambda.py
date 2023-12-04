import json
import boto3
import sqlalchemy

from lambda_utils import *
from constant import *
from database import execute_query


def call_login_lambda(student_number: str, password: str):
    login_lambda = boto3.client("lambda", region_name="ap-northeast-2")
    payload = {
        "body": json.dumps({"student_number": student_number, "password": password})
    }
    res = login_lambda.invoke(FunctionName="login", Payload=json.dumps(payload))
    json_res = json.loads(res["Payload"].read())
    body = json.loads(json_res.get("body"))
    assert json_res.get("statusCode") == 200, body.get("msg")
    return body


@execute_query
def update_cookie(student_number: str, cookies: list):
    stmt = f'''UPDATE users SET cookies='{json.dumps(cookies)}' WHERE student_number="{student_number}"'''
    query = sqlalchemy.text(stmt)
    return query


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])

    student_number = body["student_number"]
    password = body["password"]

    cookies = call_login_lambda(student_number, password)
    update_cookie(student_number, cookies)
    return {"msg:": "success"}