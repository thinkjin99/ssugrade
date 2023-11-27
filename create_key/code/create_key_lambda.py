import json
import sqlalchemy
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import boto3

from database import execute_query
from lambda_utils import lamdba_decorator


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


def create_key():
    key = RSA.generate(1024)
    private_key = key.exportKey(randfunc=get_random_bytes)
    public_key = key.publickey().exportKey()
    return private_key, public_key


@execute_query
def save_public_key(
    student_number: str, public_key: str, fcm_token: str, cookies: list
):
    public_key = "\n".join(public_key.split("\n")[1:-1])  # 밑줄 아래줄 삭제
    stmt = f"""
    INSERT INTO users(student_number, public_key, fcm_token, cookies) VALUES("{student_number}","{public_key}","{fcm_token}",'{json.dumps(cookies)}') 
    ON DUPLICATE KEY UPDATE 
    public_key="{public_key}",
    fcm_token="{fcm_token}",
    cookies = '{json.dumps(cookies)}'
    """  # 정보 upsert
    query = sqlalchemy.text(stmt)
    return query


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    student_number = body["student_number"]
    password = body["password"]
    fcm_token = body["fcm_token"]
    cookies = call_login_lambda(student_number, password)
    private_key, public_key = create_key()
    save_public_key(student_number, public_key.decode(), fcm_token, cookies)
    return {"key": private_key.decode()}
