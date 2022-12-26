from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from scrapping import Usaint
import login

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

@app.get("/")
async def root_get():
    return RedirectResponse("/docs")


@app.post("/grade")
async def root(user:User, year:str=2022, semester:str=2):
    try:
        my_saint = Usaint(user.student_id, user.password)
        data = await my_saint.run(year, semester)
        return JSONResponse(content=data, status_code=200)

    except Exception:
        raise HTTPException(status_code=500, detail="Erorr Occurs in Scrapping Server")


@app.post("/login", status_code=200)
async def login(user:User):
    try:
        await login.get_login_cookie(user.student_id, user.password)
        return JSONResponse(content="Login Success")
    
    except AssertionError:
        raise HTTPException(status_code=401, detail="Login Failed")
