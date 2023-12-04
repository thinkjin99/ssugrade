from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.responses import JSONResponse

from scrap import (
    run_single_browser_scrap_now,
    run_multy_browser_scrapl_all_grades,
)

app = FastAPI()


class User(BaseModel):
    student_id: str


@app.post("/grade/all")
async def _scrap_all(user: User):
    try:
        data = await run_multy_browser_scrapl_all_grades(user.student_id)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/now", status_code=200)
async def _scrap_now(user: User):
    try:
        data = await run_single_browser_scrap_now(user.student_id)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
