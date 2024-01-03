from layer.session import RequestSession
from layer.request import post_login
from layer.grade import (
    scrap_all_hakgi_grades,
    scrap_hakgi_grade_summary,
    scrap_one_hakgi_grades,
)

from layer.lambda_utils import lamdba_decorator


if __name__ == "__main__":
    session = RequestSession()

    login_res = session.send_request(post_login("20180806", "kidok0714!"))
    res = scrap_hakgi_grade_summary(session)
    # res = scrap_all_hakgi_grades(session, res["grades"])
    # res = scrap_one_hakgi_grades(session, "2022", "2")

    print(res)

    # grade = session.session_request(get_grade("2022", "2"))  # TODO 세션 재활용 고려해 작성하기
    # soup = parse.create_soup_object(grade.text)
    # parsed_grades = parse.parse_hakgi_detail_grades(soup)
    # print(parsed_grades)

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
