from constant import *

def get_payload(student_id:str, password:str):
    payload = PAYLOAD.copy()
    payload['sap-user'] = student_id
    payload['sap-password'] = password
    return payload
