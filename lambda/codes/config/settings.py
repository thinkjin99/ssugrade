import os

app_env = os.getenv("APP_ENV", "dev")

USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")
HOST = os.getenv("DB_HOST")
