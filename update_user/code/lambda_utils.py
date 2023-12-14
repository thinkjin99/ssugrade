import traceback
import json


def create_response(status_code: str | int, data: dict) -> dict:
    """
    AWS_PROXY 설정의 람다 응답 기본형태

    Args:
        status_code (str | int): 상태 코드
        msg (str): 반환 메시지

    Returns:
        dict: 응답
    """
    response = {
        "isBase64Encoded": False,
        "headers": {"Content-Type": "application/json"},
        "statusCode": status_code,
        "body": json.dumps(data),
    }
    return response


def check_vaild_request(event: dict, properties: list):
    """
    리퀘스트 속성 검사 함수

    Args:
        event (dict): 이벤트 객체
        properties (list): 속성들
    """
    for p in properties:
        assert p in event, "Invalid Request"


def lamdba_decorator(func):
    """
    람다 핸들러 데코레이터

    Args:
        func (function): 핸들러 함수
    """

    def wrapper(context: dict, event: dict):
        response = {}
        try:
            res = func(context, event)
            response = create_response(200, res)

        except AssertionError as e:
            response = create_response(401, {"msg": str(e)})

        except Exception as e:
            response = create_response(500, {"msg": str(traceback.format_exc())})

        finally:
            return response

    return wrapper
