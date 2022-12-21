import requests
from playwright.async_api import async_playwright, Page
from playwright.async_api import expect

from constant import *
import logger
import utils

logger = logger.create_logger()

async def max_retry(function, *args, retry=3):
    for _ in range(retry):
        res = await function(*args) if args else await function()
        if res: break
    assert res
    return res


async def get_login_cookie(payload:dict):
    try:
        login_res = requests.post(URL, data=payload, allow_redirects=False)
        login_cookies = login_res.cookies
        if 'MYSAPSSO2' not in login_cookies.keys():
            raise AssertionError("Wrong ID or Password") #401에러 등의 응답 메시지 줘야 할듯
        cookie_list = [{'name':cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path':cookie.path} for cookie in login_cookies]
        return cookie_list

    except TimeoutError:
        logger.warning("Login has Tiemout.") #연결 오류 에러.


async def load_main_page(cookie_list:list):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,  
        args=[
            '--headless',
            '--disable-gpu',
            '--single-process',
            '--no-sandbox',
            '--disable-extensions',
            '--incognito',
            '--v=99',
            '--no-zygote',
            '--deterministic-fetch',
            '--disable-dev-shm-usage',
            ]
    )

    context = await browser.new_context()
    await context.add_cookies(cookie_list)    
    page = await context.new_page()
    try:
        await max_retry(page.goto, URL)
        if not page:
            raise AssertionError("Page Load Failed")
        return page
    
    except TimeoutError:
        logger.warning("Usaint down") #유세인트 연결 안됨.


def parse_grade(inner_texts:str):
    column_names = ['이수학년도','이수학기','과목코드','과목명','과목학점','성적','등급','교수명','비고']
    column_len = len(column_names)
    table_texts = inner_texts.split('\t')
    text_by_rows = [table_texts[i:i + len(column_names)] for i in range(column_len + 2, len(table_texts), column_len + 1)]
    grade_info = [{col:value for col, value in zip(column_names,row)} for row in text_by_rows]
    return grade_info


async def get_inner_texts(page:Page):
    # "tr > td:not(:first-child):not(:last-child)"
    try:
        selector = 'tbody[id^="WD0"]'
        loc = page.locator(selector)
        await expect(loc).to_be_visible()
        inner_texts = await loc.inner_text()

        if not inner_texts: 
            raise AssertionError("Locator can't locate table")
        return inner_texts

    except TimeoutError:
        logger.warning("Time out in locating")


async def run(student_id:str, password:str):
    grade_info = None
    try:
        payload = utils.get_payload(student_id, password)
        cookie_list = await max_retry(get_login_cookie, payload)
        page = await max_retry(load_main_page, cookie_list)
        inner_texts = await max_retry(get_inner_texts, page)
        grade_info = parse_grade(inner_texts)

    except AssertionError as e:
        logger.error(e)

    except Exception as e:
        logger.error("Something goes Wrong")
    
    finally:
        return grade_info


# if __name__ == '__main__':
    # asyncio.ensure_future(run())