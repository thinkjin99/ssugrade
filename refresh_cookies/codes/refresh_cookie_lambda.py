import json
import requests
import sqlalchemy

from lambda_utils import *
from constant import *
from database import execute_query
from login import login


def get_cookie(response: requests.Response) -> list[dict[str, str]]:
    cookie_list = [
        {
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
            "path": cookie.path,
        }
        for cookie in response.cookies
    ]
    return cookie_list


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

    login_res = login(student_number, password)
    cookie = get_cookie(login_res)
    update_cookie(student_number, cookie)
    return {"msg:": "success"}
