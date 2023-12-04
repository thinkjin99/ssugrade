# import asyncio
# import json

# from scrap import run_multy, run_single
# from lambda_utils import lamdba_decorator


# @lamdba_decorator
# def handler(event, context) -> dict:
#     body = json.loads(event["body"])
#     student_number = body["student_number"]
#     grades = asyncio.run(run_multy(student_number))
#     return {"grades": grades}
