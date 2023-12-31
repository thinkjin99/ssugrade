import sqlalchemy
from database import mapping_result, execute_query


@mapping_result(is_all=True)
@execute_query
def select_user_infos():
    stmt = f"""SELECT student_number, fcm_token, grades FROM users"""
    query = sqlalchemy.text(stmt)
    return query


def yield_datas(datas: list, offset: int):
    index = 0
    while len(datas) > index:
        yield datas[index : index + offset]
        index += offset
