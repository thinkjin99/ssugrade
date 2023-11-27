import requests
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
