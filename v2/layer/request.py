import requests

from layer.constant import LOGIN_HEADER


def post_login(student_number: str, password: str) -> requests.Request:
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


def get_hakgi_grade_summary() -> requests.Request:
    grade_url = "https://mobile.ssu.ac.kr/student/gradeGrade.do"
    grade_request = requests.Request(method="GET", url=grade_url)
    return grade_request


def post_hakgi_detail_grade(year: str, hakgi: str) -> requests.Request:
    grade_url = "https://mobile.ssu.ac.kr/student/gradeGradeInfo.do"  # to
    grade_request = requests.Request(
        method="POST",
        url=grade_url,
        data={
            "IN_HAKJUM": "",
            "IN_SUKCHA": "",
            "IN_YEAR": year,
            "IN_HAKGI": hakgi,
            "IN_COURSE": "",
            "REQ_USER_ID": "",
        },
    )
    return grade_request
