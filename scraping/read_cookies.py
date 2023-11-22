import sqlalchemy
from database import execute_query, mapping_result
import json


@mapping_result(is_all=False)
@execute_query
def select_cookies(studuent_number: str):
    stmt = f"SELECT cookies FROM users where student_number={studuent_number}"
    query = sqlalchemy.text(stmt)
    return query


def get_cookies(studen_number: str) -> list[dict]:
    cookies = select_cookies(studen_number)
    data = json.loads(cookies["cookies"])
    return data
