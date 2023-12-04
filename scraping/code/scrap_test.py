import scraping_all_lambda
import json
import requests


def create_body(body: dict):
    return {"body": json.dumps(body)}


if __name__ == "__main__":
    body = create_body({"student_number": "20180811"})
    print(json.dumps(body))
    # res = scraping_all_lambda.handler(body, {})
    # res = requests.post(
    # "http://localhost:9000/2015-03-31/functions/function/invocations", json=body
    # )
    # print(res.json())
