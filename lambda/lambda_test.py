import create_key_lambda as create_key_lambda
import refresh_cookie_lambda as refresh_cookie_lambda
import json


def create_body(body: dict):
    return {"body": json.dumps(body)}


def test_create_key():
    student_number = "20180811"
    password = "qlalf2023*"
    fcm_token = "c2aK9KHmw8E:APA91bF7MY9bNnvGAXgbHN58lyDxc9KnuXNXwsqUs4uV4GyeF06HM1hMm-etu63S_4C-GnEtHAxJPJJC4H__VcIk90A69qQz65toFejxyncceg0_j5xwoFWvPQ5pzKo69rUnuCl1GSSv"
    body = create_body(
        {"student_number": student_number, "password": password, "fcm_token": fcm_token}
    )
    return create_key_lambda.handler(body, {})


def test_refresh():
    student_number = "20180811"
    password = "qlalf2023*"
    body = create_body({"student_number": student_number, "password": password})
    return refresh_cookie_lambda.handler(body, {})


if __name__ == "__main__":
    # print(test_refresh())
    print(test_create_key())
