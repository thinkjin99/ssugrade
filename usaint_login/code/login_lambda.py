import json
import requests
from constant import *
from lambda_utils import lamdba_decorator


def create_cookies(
    response: requests.Response, neccessary_cookies: tuple
) -> list[dict[str, str]]:
    cookie_list = [
        {
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
            "path": cookie.path,
        }
        for cookie in response.cookies
        if cookie.name in neccessary_cookies
    ]
    return cookie_list


def login(student_number: str, password: str) -> list:
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

    neccessary_cookies = ("SAP_SESSIONID_SSP_100",)  # 필요 쿠키 리스트
    cookies = create_cookies(login_res, neccessary_cookies)  # 필요한 쿠키만 추출

    if len(cookies):
        return cookies
    else:
        raise AssertionError("Login Fail")


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])

    student_number = body["student_number"]
    password = body["password"]

    cookies = login(student_number, password)
    return {"cookies": cookies}
