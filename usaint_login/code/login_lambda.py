import json
import requests
from constant import *
from lambda_utils import lamdba_decorator


# def get_cookie(response: requests.Response) -> list[dict[str, str]]:
#     cookie_list = [
#         {
#             "name": cookie.name,
#             "value": cookie.value,
#             "domain": cookie.domain,
#             "path": cookie.path,
#         }
#         for cookie in response.cookies
#     ]
#     return cookie_list


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

    assert "SAP_SESSIONID_SSP_100" in login_res.cookies, "Login Fail"  # 실패 코드 전달시
    login_cookies = login_res.cookies.get("SAP_SESSIONID_SSP_100")
    return login_cookies


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])

    student_number = body["student_number"]
    password = body["password"]

    login_cookies = login(student_number, password)
    return {"cookies": login_cookies}
