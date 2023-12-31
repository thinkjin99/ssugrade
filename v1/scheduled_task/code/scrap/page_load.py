from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext, Browser, Page
from constant import *
from scrap.page_action import click_popup


async def create_default_browser() -> Browser:
    """
    가상 브라우저를 생성한다.
    headless는 반드시 참이여야 한다.

    Returns:
        Browser: 브라우저
    """
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
    브라우저용 컨텍스트 매니저를 생성한다.

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


async def load_page(context: BrowserContext):
    page = await context.new_page()  # 페이지 생성
    await page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
    goto_res = await page.goto(url=URL, timeout=3000)
    # goto에 실패하면 assertion 에러 발생
    assert goto_res, "Page Load Failed"
    return page  # 로딩이 완료됨.


async def is_usaint_cookie_valid(page: Page) -> bool:
    """
    유세인트 로그인 토큰이 유효한지 검증한다.
    로그온 페이지로 리다이렉트 될 경우 쿠키가 만료된 상황을 의미한다.

    Args:
        page (Page): 페이지

    Returns:
        bool: True일 경우 로그인 성공
    """
    title = await page.locator("title").text_content(timeout=3000)  # 페이지 제목
    return title != "로그온"  # 쿠키 유효여부 확인


async def load_usaint_page(browser: Browser, cookie_list: list[dict]) -> Page:
    """
    usaint 성적 페이지에 접속합니다. 이후 팝업이 존재할 경우 팝업을 클릭합니다.

    Args:
        browser (Browser): 브라우저
        cookie_list (list[dict]): 로그인에 활용할 토큰 값

    Raises:
        AssertionError: 로그인 에러

    Returns:
        Page: 성적 페이지
    """

    context = await browser.new_context()  # 브라우저 생성
    await context.add_cookies(cookie_list)  # 브라우저 쿠키를 추가한다.

    page = await context.new_page()  # 새 탭 생성
    await page.route(
        "**/*.{png,jpg,jpeg}", lambda route: route.abort()
    )  # 이미지 파일은 로딩하지 않는다

    await page.goto(url=URL, timeout=3000)  # 유세인트 페이지로 이동한다.

    if not await is_usaint_cookie_valid(page):  # 로그인 실패
        raise AssertionError("Login Error!")  # TODO 로그인 에러 객체 생성

    await click_popup(page)  # 팝업 클릭
    return page
