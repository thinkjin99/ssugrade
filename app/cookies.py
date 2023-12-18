import sqlalchemy
import boto3
import json

from database import execute_query, mapping_result


def call_refresh_lambda(student_number: str, password: str):
    login_lambda = boto3.client("lambda", region_name="ap-northeast-2")
    payload = {
        "body": json.dumps({"student_number": student_number, "password": password})
    }
    res = login_lambda.invoke(
        FunctionName="refresh-cookies", Payload=json.dumps(payload)
    )
    json_res = json.loads(res["Payload"].read())
    body = json.loads(json_res.get("body"))  # cookies
    assert json_res.get("statusCode") == 200, body.get("msg")
    return body  # cookies


@mapping_result(is_all=False)
@execute_query
def select_cookies(fcm_token: str):
    json_path = "'$.cookies'"
    stmt = f"""SELECT JSON_EXTRACT(cookies, {json_path}) as cookies FROM users where fcm_token='{fcm_token}'"""
    query = sqlalchemy.text(stmt)
    return query


def get_cookies(fcm_token: str) -> list[dict]:
    cookies = select_cookies(fcm_token)
    if cookies:
        data = json.loads(cookies["cookies"])
        return data
    else:
        raise AssertionError("No cookies")
