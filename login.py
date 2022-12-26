from constant import *
import requests

def get_payload(student_id:str, password:str):
    payload = PAYLOAD.copy()
    payload['sap-user'] = student_id
    payload['sap-password'] = password
    return payload


async def get_login_cookie(student_id:str, password:str):
    payload = get_payload(student_id, password)
    login_res = requests.post(URL, data=payload, allow_redirects=False, timeout=3)
    login_cookies = login_res.cookies
    if 'MYSAPSSO2' not in login_cookies.keys():
        raise AssertionError("Wrong ID or Password") #401에러 등의 응답 메시지 줘야 할듯
    cookie_list = [{'name':cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path':cookie.path} for cookie in login_cookies]
    return cookie_list
