import json

from layer.session import RequestSession
from layer.grade import (
    scrap_all_hakgi_grades,
    scrap_hakgi_grade_summary,
)

from layer.lambda_utils import lamdba_decorator


@lamdba_decorator
def lambda_handler(event, context) -> dict:
    body = json.loads(event["body"])
    jsessionid = body["JSESSIONID"]
    token = body["loginCookie"]
    session = RequestSession()
    session.session.cookies.set("loginCookie", token, domain="mobile.ssu.ac.kr")
    session.session.cookies.set("JSESSIONID", jsessionid, domain="mobile.ssu.ac.kr")

    summary: list = scrap_hakgi_grade_summary(session)["요약성적들"]
    res = scrap_all_hakgi_grades(session, summary)
    return {"성적들": res}
