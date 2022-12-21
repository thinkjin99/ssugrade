from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from scrapping import *
import utils

app = FastAPI()

class User(BaseModel):
    student_id:str
    password:str

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.post("/")
async def root(user:User):
    try:
        res = await run(user.student_id, user.password)
        return res

    except:
        raise HTTPException(status_code=500, detail="Erorr Occurs in Scrapping Server")


@app.post("/login", status_code=200)
async def login(user:User):
    payload = utils.get_payload(user.student_id, user.password)
    try:
        await get_login_cookie(payload)
        return "Login Success"
    
    except AssertionError:
        raise HTTPException(status_code=401, detail="Login Failed")
