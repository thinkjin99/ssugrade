from functools import wraps
from typing import Callable

import json
import requests
from requests.adapters import HTTPAdapter, Retry

from constant import *
from lambda_utils import lamdba_decorator


class SessionRequest:
    def __init__(self) -> None:
        self.session = self.create_session()

    def create_session(self):
        retries = Retry(total=3, backoff_factor=1, raise_on_redirect=False)
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))  # Retry 세션 생성
        return session

    def session_request(self, request: requests.Request):
        prepared_request = self.session.prepare_request(request)
        try:
            resp = self.session.send(prepared_request)  # send request
            resp.raise_for_status()  # HTTP 에러 발생시
            return resp

        except Exception as e:
            print(f"Request:{prepared_request} got error {str(e)}")
            return


def login(student_number: str, password: str) -> requests.Request:
    """
    유세인트 로그인을 진행합니다

    Args:
        student_number (str): 학번
        password (str): 비밀번호

    Returns:
        requests.Response: 로그인 응답
    """
    login_url = "https://mobile.ssu.ac.kr/login.do"
    login_request = requests.Request(
        headers=LOGIN_HEADER,
        method="POST",
        url=login_url,
        data={"LOGIN_ID": student_number, "LOGIN_PW": password, "AUTO_LOGIN": "1"},
    )
    return login_request  # 인코딩된 HTTP request


def get_all_grade():
    grade_url = "https://mobile.ssu.ac.kr/student/gradeGrade.do"
    grade_request = requests.Request(method="GET", url=grade_url)
    return grade_request


# @session_request
# def get_grade(year: str, hakgi: str):
#     grade_url = "https://mobile.ssu.ac.kr/student/gradeGrade.do"  # to
#     grade_request = requests.Request(
#         method="GET", url=grade_url, data={"IN_YEAR": year, "IN_HAKGI": hakgi}
#     )
#     return grade_request.prepare()


if __name__ == "__main__":
    session = SessionRequest()
    login_res = session.session_request(login("20180806", "kidok0714!"))
    res = session.session_request(get_all_grade())


# @lamdba_decorator
# def handler(event, context) -> dict:
#     body = json.loads(event["body"])

#     student_number = body["student_number"]
#     password = body["password"]

#     cookies = login(student_number, password)
#     return {"cookies": cookies}
