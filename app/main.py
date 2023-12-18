from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.responses import JSONResponse

from scrap import (
    run_single_browser_scrap_now,
    run_single_browser_scrap_all,
)


app = FastAPI()


class User(BaseModel):
    fcm_token: str


@app.post("/grade/all")
async def _scrap_all(user: User):
    try:
        data = await run_single_browser_scrap_all(user.fcm_token)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/now", status_code=200)
async def _scrap_now(user: User):
    try:
        data = await run_single_browser_scrap_now(user.fcm_token)
        return JSONResponse(content=data, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
