import asyncio
import boto3
import sqlalchemy
from functools import partial

from scrap import run_single_browser_scrap_now
from database import mapping_result, execute_query
from cookies import *
from grades import *


@mapping_result(is_all=True)
@execute_query
def select_datas():
    stmt = f"""SELECT student_number, fcm_token, grades FROM users"""
    query = sqlalchemy.text(stmt)
    return query


def yield_datas(datas: list, offset: int):
    index = 0
    while len(datas) > index:
        yield datas[index : index + offset]
        index += offset


async def push_sqs(body: list | str, fcm_token: str, attributes: dict):
    loop = asyncio.get_event_loop()
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    send_msg = partial(
        sqs.send_message,
        QueueUrl=queue_url,
        MessageBody=json.dumps({"fcm_token": fcm_token, "body": body}),
        MessageGroupId="ssurade",
        MessageAttributes=attributes,
    )
    resp = await loop.run_in_executor(None, send_msg)
    return resp


async def create_message(student_number: str, fcm_token: str, grades: str):
    try:
        body = await run_single_browser_scrap_now(student_number, fcm_token)
        print(body)
        if grades != hash_data(body):  # 해싱한 성적 데이터와 디비 저장 값을 대조
            attributes = {
                "title": {"StringValue": "New Grade", "DataType": "String"},
            }
            return body, fcm_token, attributes

    except AssertionError as e:  # login error
        body = str(e)
        attributes = {
            "title": {"StringValue": "Login Error", "DataType": "String"},
        }
        return body, fcm_token, attributes

    except Exception as e:
        print(e)  # TODO 에러 처리용 슬렉 봇이 필요하지 않을까...


async def main():
    async def create_task_routine(row: dict):
        message = await create_message(
            row["student_number"], row["fcm_token"], row["grades"]
        )
        if message:  # if  mesaage exist push sqs
            return await push_sqs(*message)

    # datas = [
    #     {"student_number": "20180811", "fcm_token": "test3", "grades": "aa"}
    #     for _ in range(20)
    # ]
    # query_result = yield_datas(datas, 5)

    query_result = yield_datas(select_datas(), 5)

    try:
        while rows := next(query_result):
            datas = [row for row in rows]
            tasks = [asyncio.create_task(create_task_routine(row)) for row in datas]
            res = await asyncio.gather(*tasks, return_exceptions=False)
            print(f"{datas} is completed...")

    except StopIteration:
        pass


if __name__ == "__main__":
    res = asyncio.run(main())
