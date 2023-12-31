import asyncio

from data.user_info import select_user_infos
from sqs import *


def yield_datas(datas: list, offset: int):
    """
    데이터를 5개씩 추출한다.

    Args:
        datas (list): 이터러블 데이터
        offset (int): 한번에 추출할 데이터의 크기

    Yields:
        iterable: 5개씩 잘라서 전송
    """
    index = 0
    while len(datas) > index:
        yield datas[index : index + offset]
        index += offset


async def create_task_routine(user_info: dict) -> dict | None:
    """
    SQS 메시지 작성 및 전송

    Args:
        user_info (dict): 유저 행 정보

    Returns:
        dict | None: 성공시 메시지 정보 실패시 None
    """
    message = await create_message(
        user_info["student_number"], user_info["fcm_token"], user_info["grades"]
    )
    if message:  # if  mesaage exist push sqs
        res = await push_sqs(*message)
        print(f"{res} is completed...")
    else:
        return


async def main():
    """
    데이터 베이스에 존재하는 모든 유저 정보 순회하며 현재 학기 성적 갱신
    """

    query_result = yield_datas(select_user_infos(), 5)  # 5개씩 유저 정보 추출

    try:
        while user_infos := next(query_result):
            tasks = [
                asyncio.create_task(create_task_routine(user_info))
                for user_info in user_infos
            ]  # 5개 비동기로 실행
            await asyncio.gather(*tasks, return_exceptions=False)

    except StopIteration:
        pass


if __name__ == "__main__":
    res = asyncio.run(main())
