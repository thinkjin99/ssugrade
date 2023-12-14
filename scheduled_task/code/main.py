import asyncio
import boto3
import sqlalchemy
from functools import partial

from scrap import run_single_browser_scrap_now
from database import *
from cookies import *


@mapping_result(is_all=True)
@execute_query
def select_datas():
    json_path = "'$.cookies'"
    stmt = (
        f"""SELECT JSON_EXTRACT(cookies,{json_path}) as cookies, fcm_token FROM users"""
    )
    query = sqlalchemy.text(stmt)
    return query


def push_sqs(fcm_token: str, body: list | str):
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    resp = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"fcm_token": fcm_token, "body": body}),
        MessageGroupId="default",
    )
    return resp


async def get_grade_and_push(cookie, fcm_token):
    loop = asyncio.get_event_loop()
    try:
        body = await run_single_browser_scrap_now(cookie)
    except Exception as e:
        body = str(e)
    send_msg = partial(push_sqs, fcm_token=fcm_token, body=body)
    resp = await loop.run_in_executor(None, send_msg)
    return resp


async def main():
    datas = [(json.loads(row["cookies"]), row["fcm_token"]) for row in select_datas()]
    tasks = [
        asyncio.create_task(get_grade_and_push(cookie, fcm_token))
        for cookie, fcm_token in datas
    ]
    res = await asyncio.gather(*tasks, return_exceptions=True)
    print(res)


if __name__ == "__main__":
    res = asyncio.run(main())
