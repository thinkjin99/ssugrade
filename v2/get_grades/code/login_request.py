import json

import requests

from constant import *
from session import SessionRequest


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


def get_all_grade() -> requests.Request:
    grade_url = "https://mobile.ssu.ac.kr/student/gradeGrade.do"
    grade_request = requests.Request(method="GET", url=grade_url)
    return grade_request


def get_grade(year: str, hakgi: str) -> requests.Request:
    grade_url = "https://mobile.ssu.ac.kr/student/gradeGradeInfo.do"  # to
    grade_request = requests.Request(
        method="POST",
        url=grade_url,
        data={
            "IN_HAKJUM": "",
            "IN_SUKCHA": "",
            "IN_YEAR": year,
            "IN_HAKGI": f"{hakgi} 학기",
            "IN_COURSE": "",
            "REQ_USER_ID": "",
        },
    )
    return grade_request


if __name__ == "__main__":
    import parse

    session = SessionRequest()
    # all_grades = session.session_request(get_all_grade())
    grade = session.session_request(get_grade("2022", "2"))  # TODO 세션 재활용 고려해 작성하기
    soup = parse.create_soup_object(grade.text)
    parsed_grades = parse.parse_hakgi_detail_grades(soup)
    print(parsed_grades)

    # parsed_table = parse.parse_average_grade(soup)
    # parsed_table = parse.parse_grade_per_semester(soup)
    # print(parsed_table)


# @lamdba_decorator
# def handler(event, context) -> dict:
#     body = json.loads(event["body"])

#     student_number = body["student_number"]
#     password = body["password"]

#     cookies = login(student_number, password)
#     return {"cookies": cookies}
