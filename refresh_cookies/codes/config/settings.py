from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(str(Path.cwd().joinpath("config/.env")))
app_env = os.getenv("APP_ENV", "dev")

if app_env == "dev":
    USER_ID = os.getenv("USER_ID")
    PASSWORD = os.getenv("PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    HOST = os.getenv("DB_HOST")

elif app_env == "local":
    USER_ID = os.getenv("LOCAL_USER_ID")
    PASSWORD = os.getenv("LOCAL_PASSWORD")
    DB_NAME = os.getenv("LOCAL_DB_NAME")
    HOST = os.getenv("LOCAL_DB_HOST")
