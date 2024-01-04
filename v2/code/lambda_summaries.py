import json

from layer.session import RequestSession
from layer.grade import scrap_hakgi_grade_summary

from layer.lambda_utils import lamdba_decorator


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    jsessionid = body["JSESSIONID"]
    token = body["loginCookie"]
    session = RequestSession()
    session.session.cookies.set("loginCookie", token, domain="mobile.ssu.ac.kr")
    session.session.cookies.set("JSESSIONID", jsessionid, domain="mobile.ssu.ac.kr")
    return scrap_hakgi_grade_summary(session)
