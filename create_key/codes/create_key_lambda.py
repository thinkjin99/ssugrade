import json
import sqlalchemy
from Crypto.PublicKey import RSA

from database import execute_query
from lambda_utils import lamdba_decorator
from login import login


def create_key():
    key = RSA.generate(1024)
    private_key = key.exportKey()
    public_key = key.publickey().exportKey()
    return private_key, public_key


@execute_query
def save_public_key(student_number: str, public_key: str, fcm_token: str):
    public_key = "\n".join(public_key.split("\n")[1:-1])  # 밑줄 아래줄 삭제
    stmt = f"""
    INSERT INTO users(student_number, public_key, fcm_token) VALUES("{student_number}","{public_key}","{fcm_token}") 
    ON DUPLICATE KEY UPDATE 
    public_key="{public_key}",
    fcm_token="{fcm_token}"
    """  # 정보 upsert
    query = sqlalchemy.text(stmt)
    return query


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    student_number = body["student_number"]
    password = body["password"]
    fcm_token = body["fcm_token"]

    login(student_number, password)
    private_key, public_key = create_key()
    save_public_key(student_number, public_key.decode(), fcm_token)
    return {"key": private_key.decode()}
