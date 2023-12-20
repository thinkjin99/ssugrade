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
    stmt = f"""SELECT fcm_token, grades FROM users"""
    query = sqlalchemy.text(stmt)
    return query


def push_sqs(body: list | str, fcm_token: str, attributes: dict):
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    resp = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"fcm_token": fcm_token, "body": body}),
        MessageGroupId="default",
        MessageAttributes=attributes,
    )
    return resp


async def get_grade_and_push(fcm_token: str, grades: str):
    loop = asyncio.get_event_loop()
    try:
        body = await run_single_browser_scrap_now(fcm_token)

        if grades != hash_data(body):  # 해싱한 성적 데이터와 디비 저장 값을 대조
            attributes = {
                "type": {"StringValue": "data", "DataType": "String"},
            }
            send_msg = partial(
                push_sqs, fcm_token=fcm_token, body=body, attributes=attributes
            )
            resp = await loop.run_in_executor(None, send_msg)
            return resp

    except AssertionError as e:
        attributes = {
            "type": {"StringValue": "error", "DataType": "String"},
        }
        send_msg = partial(
            push_sqs, fcm_token=fcm_token, body=str(e), attributes=attributes
        )
        resp = await loop.run_in_executor(None, send_msg)
        return resp

    except Exception as e:
        print(e)  # TODO 에러 처리용 슬렉 봇이 필요하지 않을까...


async def main():
    datas = [(row["fcm_token"], row["grades"]) for row in select_datas()]
    tasks = [
        asyncio.create_task(get_grade_and_push(cookie, fcm_token))
        for cookie, fcm_token in datas
    ]
    res = await asyncio.gather(*tasks, return_exceptions=False)
    print(res)


if __name__ == "__main__":
    res = asyncio.run(main())
