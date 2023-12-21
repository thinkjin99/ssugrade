from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext, Browser, Page
from constant import *
from page_action import click_popup


async def create_default_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        args=[
            "--disable-gpu",  # GPU 활용 하지 않음
            "--disable-extensions",
            "--disable-http-cache",
            "--disable-dev-shm-usage",  # 메모리 공유 비활성화
            "--single-process",
            "--disable-images",
            "--disable-extensions",
            "--disable-translate",
            "--disable-default-apps",
        ],
        headless=True,
    )

    return browser  # 함수의 정상종료를 나타낸다.


@asynccontextmanager
async def open_browser():
    """
    유세인트 성적 스크래핑 전체 로직을 가동합니다.

    Args:
        year (int, optional): _description_. Defaults to 2022.
        semester (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    browser = await create_default_browser()  # 브라우저를 가동합니다.

    try:
        # 로그인 및 성적 페이지를 로딩합니다.
        yield browser

    except Exception as e:
        print(e)
        raise e

    finally:
        await browser.close()


async def load_usaint_page(browser: Browser, cookie_list: list[dict]) -> Page:
    context = await browser.new_context()  # 브라우저 생성
    await context.add_cookies(cookie_list)  # 매개변수가 SetCookieParam 형식이여야 한다.
    page = await load_page(context)

    title = await page.locator("title").text_content(timeout=3000)
    if title == "로그온":  # 쿠키 유효여부 확인
        raise AssertionError("Login Error!")

    for _ in range(3):
        is_popup = await click_popup(page)  # 팝업 클릭
        if is_popup:
            break

    return page


async def load_page(context: BrowserContext):
    """
    로그인 쿠키가 추가된 브라우저로 성적 페이지를 로딩한다.
    """
    page = await context.new_page()  # 페이지 생성
    # await page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
    goto_res = await page.goto(url=URL, timeout=5000)
    # goto에 실패하면 assertion 에러 발생
    assert goto_res, "Page Load Failed"
    return page  # 로딩이 완료됨.
