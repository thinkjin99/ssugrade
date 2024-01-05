import json

from layer.session import RequestSession
from layer.grade import scrap_hakgi_detail_grades

from layer.lambda_utils import lamdba_decorator


@lamdba_decorator
def lambda_handler(event, context) -> dict:
    body = json.loads(event["body"])
    jsessionid = body["JSESSIONID"]
    token = body["loginCookie"]
    year = body["year"]
    hakgi = body["hakgi"]

    if hakgi == "1" or hakgi == "2":
        hakgi = f"{hakgi} 학기"

    elif hakgi == "여름" or hakgi == "겨울":
        hakgi = f"{hakgi}학기"

    else:
        raise ValueError("Hakgi must be 1,2 or 여름, 겨울")

    session = RequestSession()
    session.session.cookies.set("loginCookie", token, domain="mobile.ssu.ac.kr")
    session.session.cookies.set("JSESSIONID", jsessionid, domain="mobile.ssu.ac.kr")
    return scrap_hakgi_detail_grades(session, year, hakgi)
