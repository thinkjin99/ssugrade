import json
import requests
import sqlalchemy

from lambda_utils import *
from constant import *
from database import execute_query


def login(student_number: str, password: str) -> requests.Response:
    """
    유세인트 로그인을 진행합니다

    Args:
        student_number (str): 학번
        password (str): 비밀번호

    Returns:
        requests.Response: 로그인 응답
    """
    payload = PAYLOAD.copy()
    payload["sap-user"] = student_number
    payload["sap-password"] = password
    login_res = None
    for _ in range(3):
        try:
            login_res = requests.post(
                URL,
                data=payload,
                allow_redirects=False,
                timeout=5,
                headers=LOGIN_HEADER,
            )  # 로그인 시도
        except Exception:
            continue

    if login_res == None:
        raise Exception("Connection Fail")

    login_cookies = login_res.cookies
    assert "MYSAPSSO2" in login_cookies.keys(), "login fail"  # 실패 코드 전달시
    return login_res


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
def handler(event, context) -> str:
    body = json.loads(event["body"])

    student_number = body["student_number"]
    password = body["password"]

    login_res = login(student_number, password)
    cookie = get_cookie(login_res)
    update_cookie(student_number, cookie)
    return "success"
