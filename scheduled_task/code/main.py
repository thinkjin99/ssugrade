import asyncio
import boto3
import sqlalchemy
from functools import partial

from scrap import run_single_browser_scrap_now
from database import *
from cookies import *
from grades import *


@mapping_result(is_all=True)
@execute_query
def select_datas():
    stmt = f"""SELECT student_number, fcm_token, grades FROM users"""
    query = sqlalchemy.text(stmt)
    return query


async def push_sqs(body: list | str, fcm_token: str, attributes: dict):
    loop = asyncio.get_event_loop()
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    # resp = sqs.send_message(
    #     QueueUrl=queue_url,
    #     MessageBody=json.dumps({"fcm_token": fcm_token, "body": body}),
    #     MessageGroupId="ssurade",
    #     MessageAttributes=attributes,
    # )
    send_msg = partial(
        sqs.send_message,
        QueueUrl=queue_url,
        MessageBody=json.dumps({"fcm_token": fcm_token, "body": body}),
        MessageGroupId="ssurade",
        MessageAttributes=attributes,
    )
    resp = await loop.run_in_executor(None, send_msg)

    return resp


async def get_grade_and_push(student_number: str, fcm_token: str, grades: str):
    try:
        body = await run_single_browser_scrap_now(student_number, fcm_token)
        if grades != hash_data(body):  # 해싱한 성적 데이터와 디비 저장 값을 대조
            attributes = {
                "title": {"StringValue": "New Grade", "DataType": "String"},
            }
            send_msg = partial(
                push_sqs, fcm_token=fcm_token, body=body, attributes=attributes
            )
            # return resp

    except AssertionError as e:
        attributes = {
            "title": {"StringValue": "Login Error", "DataType": "String"},
        }
        send_msg = partial(
            push_sqs, fcm_token=fcm_token, body=str(e), attributes=attributes
        )
        # resp = await loop.run_in_executor(None, send_msg)
        # return resp

    except Exception as e:
        print(e)  # TODO 에러 처리용 슬렉 봇이 필요하지 않을까...


async def main():
    # datas = [
    #     (row["student_number"], row["fcm_token"], row["grades"])
    #     for row in select_datas()
    # ]
    datas = [("20180811", "test3", "aa") for _ in range(10)]
    tasks = [
        asyncio.create_task(get_grade_and_push(student_number, fcm_token, cookie))
        for student_number, fcm_token, cookie, in datas
    ]
    res = await asyncio.gather(*tasks, return_exceptions=False)


if __name__ == "__main__":
    res = asyncio.run(main())
