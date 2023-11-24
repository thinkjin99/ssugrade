import refresh_cookie_lambda
import json


def create_body(body: dict):
    return {"body": json.dumps(body)}


def test_refresh():
    student_number = ""
    password = "*"
    body = create_body({"student_number": student_number, "password": password})
    return refresh_cookie_lambda.handler(body, {})


if __name__ == "__main__":
    print(test_refresh())
    # print(test_create_key())
