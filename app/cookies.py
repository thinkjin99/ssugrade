import sqlalchemy
import json
from database import execute_query, mapping_result


@mapping_result(is_all=False)
@execute_query
def select_cookies(fcm_token: str):
    json_path = "'$.cookies'"
    stmt = f"""SELECT JSON_EXTRACT(cookies, {json_path}) as cookies FROM users where fcm_token='{fcm_token}'"""
    query = sqlalchemy.text(stmt)
    return query


def get_cookies(fcm_token: str) -> list[dict]:
    cookies = select_cookies(fcm_token)
    if cookies:
        data = json.loads(cookies["cookies"])
        return data
    else:
        raise AssertionError("No cookies")
