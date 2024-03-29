import hashlib
import json
from database import execute_query
import sqlalchemy


def hash_data(data: list):
    # 데이터를 문자열로 직렬화
    dict_str = json.dumps(data, sort_keys=True)
    # 직렬화된 문자열을 해시
    sha256 = hashlib.sha256()
    sha256.update(dict_str.encode("utf-8"))
    hash_str = sha256.hexdigest()
    return hash_str


@execute_query
def update_grades(fcm_token: str, hash_str: str):
    stmt = f'''UPDATE users SET grades='{hash_str}' WHERE fcm_token="{fcm_token}"'''
    query = sqlalchemy.text(stmt)
    return query

