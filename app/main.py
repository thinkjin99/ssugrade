from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from constant import USAINT_SEMESTER, USAINT_SEMESTER

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
async def _scrap_all(user: User):
    try:
        all_grades = await run_single_browser_scrap_all(
            user.student_number, user.fcm_token
        )
        now_grade = [
            grade
            for grade in all_grades
            if grade["학년도"] == USAINT_SEMESTER and grade["학기"] == USAINT_SEMESTER
        ]

        update_grades(user.fcm_token, hash_data(now_grade))
        return JSONResponse(content=all_grades, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/now", status_code=200)
async def _scrap_now(user: User):
    try:
        grades = await run_single_browser_scrap_now(user.student_number, user.fcm_token)
        update_grades(user.fcm_token, hash_data(grades))
        return JSONResponse(content=grades, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
