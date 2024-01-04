import json

from layer.session import RequestSession
from layer.grade import (
    scrap_all_hakgi_grades,
    scrap_hakgi_grade_summary,
)

from layer.lambda_utils import lamdba_decorator


#     res = scrap_hakgi_grade_summary(session)
# res = scrap_all_hakgi_grades(session, res["grades"])
# res = scrap_one_hakgi_grades(session, "2022", "2")

# grade = session.session_request(get_grade("2022", "2"))  # TODO 세션 재활용 고려해 작성하기
# soup = parse.create_soup_object(grade.text)
# parsed_grades = parse.parse_hakgi_detail_grades(soup)
# print(parsed_grades)

# parsed_table = parse.parse_average_grade(soup)
# parsed_table = parse.parse_grade_per_semester(soup)
# print(parsed_table)


@lamdba_decorator
def handler(event, context) -> dict:
    body = json.loads(event["body"])
    jsessionid = body["JSESSIONID"]
    token = body["loginCookie"]
    session = RequestSession()
    session.session.cookies.set("loginCookie", token, domain="mobile.ssu.ac.kr")
    session.session.cookies.set("JSESSIONID", jsessionid, domain="mobile.ssu.ac.kr")

    summary: list = scrap_hakgi_grade_summary(session)["요약성적들"]
    res = scrap_all_hakgi_grades(session, summary)
    return {"성적들": res}


