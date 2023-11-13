import json
import traceback
import boto3
import requests

from lambda_utils import *
from constant import *


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

    login_res = requests.post(
        URL, data=payload, allow_redirects=False, timeout=3, headers=LOGIN_HEADER
    )  # 로그인 시도

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


def put_cookie_to_s3(student_number: str, cookie: dict):
    s3 = boto3.client("s3")
    resp = s3.put_object(
        ACL="private",
        Bucket="user-tokens",
        Body=json.dumps(cookie),
        ContentType="application/json",
        Key=student_number + ".json",
        ServerSideEncryption="AES256",
    )
    return resp


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    check_vaild_request(body, ["student_number", "password"])

    student_number = body["student_number"]
    password = body["password"]

    login_res = login(student_number, password)
    cookie = get_cookie(login_res)

    put_cookie_to_s3(student_number, {"cookie": cookie})
    response = create_response(200, "success")
    return response
