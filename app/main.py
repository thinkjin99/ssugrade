from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from constant import USAINT_SEMESTER, SSURADE_SEMESTER

from grades import update_grades, hash_data
from scrap import (
    run_single_browser_scrap_now,
    run_single_browser_scrap_all,
)


app = FastAPI()


class User(BaseModel):
    student_number: str
    fcm_token: str


@app.post("/grade/all")
async def scrap_all(user: User):
    try:
        grades = await run_single_browser_scrap_all(user.student_number, user.fcm_token)
        for grade in grades:
            if (
                grade["year"] == USAINT_SEMESTER
                and grade["semester"] == SSURADE_SEMESTER
            ):
                update_grades(
                    user.fcm_token, hash_data(grade["grades"])
                )  # 현재 학기 성적 업데이트

        return JSONResponse(content={"data": grades}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/now", status_code=200)
async def scrap_now(user: User):
    try:
        grades = await run_single_browser_scrap_now(user.student_number, user.fcm_token)
        update_grades(user.fcm_token, hash_data(grades)) #성적 업데이트
        return JSONResponse(content={"data": grades}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
