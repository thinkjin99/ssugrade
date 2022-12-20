import requests
from playwright.sync_api import sync_playwright
from constant import *
from playwright.sync_api import expect

def max_retry(function, *args, retry=3):
    try:
        for _ in range(retry):
            res = function(*args) if args else function()
            if res: break
        return res
        
    except Exception as e:
        print(f"{function},{args} has faild\n", e)


def get_login_cookie(payload=PAYLOAD):
    try:
        login_res = requests.post(URL, data=payload, allow_redirects=False)
        login_cookies = login_res.cookies
        assert 'MYSAPSSO2' in login_cookies.keys(), "Wrong ID or Password" #401에러 등의 응답 메시지 줘야 할듯
        cookie_list = [{'name':cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path':cookie.path} for cookie in login_cookies]
        return cookie_list
    
    except TimeoutError:
        print("Login has failed.") #연결 오류 에러.


def load_main_page(cookie_list):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookie_list)    
    page = context.new_page()
    try:
        max_retry(page.goto, URL)
    
    except TimeoutError:
        print("Usaint down") #유세인트 연결 안됨.
    
    return page


def parse_grade(inner_texts):
    column_names = ['이수학년도','이수학기','과목코드','과목명','과목학점','성적','등급','교수명','비고']
    column_len = len(column_names)
    table_texts = inner_texts.split('\t')
    text_by_rows = [table_texts[i:i + len(column_names)] for i in range(column_len + 2, len(table_texts), column_len + 1)]
    grade_info = [{col:value for col, value in zip(column_names,row)} for row in text_by_rows]
    return grade_info



def get_inner_texts(page):
    # "tr > td:not(:first-child):not(:last-child)"
    selector = 'tbody[id^="WD0"]'
    loc = page.locator(selector)
    expect(loc).to_be_visible()
    inner_texts = loc.inner_text()
    assert inner_texts, "Locator can't locate table"
    return inner_texts



if __name__ == '__main__':
    cookie_list = max_retry(get_login_cookie)
    page = max_retry(load_main_page, cookie_list)
    inner_texts = get_inner_texts(page)
    grade_info = parse_grade(inner_texts)
    print(grade_info)