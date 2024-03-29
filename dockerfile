FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy as build-image


ARG FUNCTION_DIR
COPY ./app .

COPY ./app/requirements.txt .

RUN pip install -r requirements.txt
RUN playwright install

ENV YEAR="2023" SEMESTER="2"
CMD ["uvicorn", "main:app","--host", "0.0.0.0", "--port", "8080"]







