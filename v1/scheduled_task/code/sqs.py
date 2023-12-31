import asyncio
import json
from functools import partial

import boto3

from data.grades import hash_data
from scrap.main import run_single_browser_scrap_now


async def push_sqs(
    data: list, notification_body: list | str, fcm_token: str, attributes: dict
) -> dict:
    """

    Args:
        data (list): 메시지의 데이터
        notification_body (list | str): 알림 내용
        fcm_token (str): fcm 토큰
        attributes (dict): 메시지 속성

    Returns:
        dict: 메시지 큐 응답
    """
    loop = asyncio.get_event_loop()  # 비동기 전송을 위한 처리
    sqs = boto3.client("sqs", region_name="ap-northeast-2")
    queue_url = "https://sqs.us-east-1.amazonaws.com/393430687602/ssugrade-push.fifo"
    send_msg = partial(
        sqs.send_message,
        QueueUrl=queue_url,
        MessageBody=json.dumps(
            {
                "fcm_token": fcm_token,
                "notification_body": notification_body,
                "data": data,
            }
        ),
        MessageGroupId="ssurade",
        MessageAttributes=attributes,
    )
    resp = await loop.run_in_executor(None, send_msg)
    return resp


async def create_message(
    student_number: str, fcm_token: str, grades: str
) -> tuple | None:
    """
    메시지의 내용을 생성합니다. 메시지를 생성할 수 없거나 필요 없는 경우 None을 반환한다

    Args:
        student_number (str): 학번
        fcm_token (str): 토큰
        grades (str): 성적

    Returns:
        tuple | None: 성적, 알림내용, 토큰,
    """
    try:
        now_grades = await run_single_browser_scrap_now(student_number, fcm_token)
        if grades != hash_data(now_grades):  # 해싱한 성적 데이터와 디비 저장 값을 대조
            notification_body = "새로운 성적이 나왔어요"
            attributes = {
                "title": {"StringValue": "신규 성적 갱신", "DataType": "String"},
            }
            return now_grades, notification_body, fcm_token, attributes

        else:  # 성적 데이터가 동일할 경우 푸시 보내지 않음
            return

    except AssertionError as e:  # login error
        now_grades = []
        notification_body = "로그인 토큰이 만료 됐어요"
        attributes = {
            "title": {"StringValue": "로그인 에러", "DataType": "String"},
        }
        return now_grades, notification_body, fcm_token, attributes

    except Exception as e:
        print(e)  # TODO 에러 처리용 슬렉 봇이 필요하지 않을까...
        return
