import json
import sqlalchemy

from lambda_utils import *
from constant import *
from database import execute_query


@execute_query
def update_cookie(student_number: str, cookies: list, fcm_token: str | None = None):
    if fcm_token:
        stmt = f'''UPDATE users SET cookies='{json.dumps(cookies)}', fcm_token="{fcm_token}" WHERE student_number="{student_number}"'''
    else:
        stmt = f'''UPDATE users SET cookies='{json.dumps(cookies)}' WHERE student_number="{student_number}"'''
    query = sqlalchemy.text(stmt)
    return query


@lamdba_decorator
def handler(event, context) -> dict:
    student_number = event["student_number"]
    fcm_token = event["fcm_token"]
    cookies = event["cookies"]
    update_cookie(student_number, cookies, fcm_token)
    return {"msg:": "success"}
