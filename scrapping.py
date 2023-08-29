from playwright.async_api import async_playwright, BrowserContext, expect, Page


from constant import *
import logger
import utils
from login import get_login_cookie


async def create_default_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        args=[
            "--headless",  # 백그라운드에서 실행
            "--disable-gpu",  # GPU 활용 하지 않음
            "--single-process",  # 싱글 프로세스로 실행
            "--no-sandbox",  # GPU 사용안함
            "--disable-extensions",
            "--incognito",
            "--deterministic-fetch",
            "--disable-http-cache",
            "--disable-dev-shm-usage",  # 메모리 공유 비활성화
        ],
    )

    return browser  # 함수의 정상종료를 나타낸다.


async def load_page(context: BrowserContext):
    """
    로그인 쿠키가 추가된 브라우저로 성적 페이지를 로딩한다.
    """
    # await set_context_cookies(context, )
    page = await context.new_page()  # 페이지 생성
    goto_res = await utils.max_retry(page.goto, url=URL, timeout=3000)
    # goto에 실패하면 assertion 에러 발생
    assert goto_res, "Page Load Failed"
    return page  # 로딩이 완료됨.


async def click_button(page: Page, selector: str):
    """
    셀렉터로 지정한 버튼을 클릭한다.

    Args:
        selector (str): 버튼을 위한 선택자

    Returns:
        bool: 클릭이 정상적으로 진행되면 참
    """
    loc = page.locator(selector)
    await expect(loc).to_be_enabled(timeout=3000)  # 버튼이 클릭 가능한 상태가 될때 까지 대기
    await loc.click(timeout=3000)  # 클릭 실시.


async def check_is_empty_semester(page: Page) -> bool:
    try:
        first_row_selector = 'tbody[id^="WD0"] tr:nth-child(2)'  # 성적 테이블의 첫 행 선택
        first_row = page.locator(first_row_selector)
        await expect(first_row).not_to_be_empty(timeout=3000)
        return False

    except AssertionError as e:
        return True


async def wait_for_update(page: Page, check_selector: str, change_value: str):
    """
    성적 테이블 로딩을 대기한다.
    """
    try:
        if await check_is_empty_semester(page):
            print(">> Data is empty", change_value)
            return

        wait_selector = page.locator(check_selector).filter(
            has_text=change_value
        )  # 로딩이 완료될 때까지 대기

        await expect(wait_selector).to_be_attached(timeout=3000)
        return True

    except AssertionError:
        print(">> Can't find", change_value)
        return False  # 테이블이 비어있음


async def click_dropdown(page: Page, dropdown_selector: str, value_selector: str):
    await click_button(page, dropdown_selector)  # 드랍다운 버튼 클릭
    await click_button(page, value_selector)  # 드랍 다운에서 년도 클릭


async def set_year_semester_dropdown(page: Page, year: str, semester: str):
    """
    년도와 학기 설정을 위한 버튼을 클릭한다.

    Args:
        year (int, optional): 년도. Defaults to YEAR.
        semester (int, optional): 학기. Defaults to SEMESTER.
    """
    # 년도의 드랍다운 버튼과 년도 원소 셀렉터
    year_drop_selector = 'input[role="combobox"][value^="20"]'
    year_selector = f'div[class~="lsListbox__value"][data-itemkey="{year}"]'

    semester_drop_selector = 'input[role="combobox"][value$="학기"]'
    semester_selector = f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'
    semester_map = {
        "0": "1 학기",
        "1": "여름학기",
        "2": "2 학기",
        "3": "겨울학기",
    }  # semester 값과 드랍다운 값 매핑

    year_update_selector = (
        'tbody[id^="WD0"] tr:nth-child(2) td:nth-child(2)'  # 로딩된 성적의 년도 셀렉터
    )
    semester_update_selector = (
        'tbody[id^="WD0"] tr:nth-child(2) td:nth-child(3)'  # 로딩된 성적의 학기 셀렉터
    )

    # 현재 로딩된 년도와 쿼리한 년도가 다른 경우

    if year != YEAR:
        await click_dropdown(page, year_drop_selector, year_selector)
        await wait_for_update(page, year_update_selector, year)  # 페이지 테이블 로딩을 대기

    if semester != SEMESTER:
        await click_dropdown(page, semester_drop_selector, semester_selector)
        await wait_for_update(
            page, semester_update_selector, semester_map[semester]
        )  # 페이지 테이블 로딩을 대기


async def get_inner_texts(page: Page):
    """
    성적 테이블 내부의 텍스트를 추출한다.

    Raises:
        AssertionError: 성적 테이블을 못찾는 경우

    Returns:
        str: 성적 테이블 내에 존재하는 모든 텍스트
    """
    # "tr > td:not(:first-child):not(:last-child)"
    table_selector = 'tbody[id^="WD0"]'
    table_loc = page.locator(table_selector)
    await expect(table_loc).to_be_enabled(timeout=2000)
    inner_texts = await table_loc.inner_text()

    if not inner_texts:
        # 값이 빈 경우는 태그 자체를 탐색하지 못한 경우이다.
        raise AssertionError(">> Locator can't locate table")
    return inner_texts


async def run(student_id: str, password: str, year: str, semester: str):
    """
    유세인트 성적 스크래핑 전체 로직을 가동합니다.

    Args:
        year (int, optional): _description_. Defaults to 2022.
        semester (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    res = None
    browser = await create_default_browser()  # 브라우저를 가동합니다.
    try:
        # 로그인 및 성적 페이지를 로딩합니다.
        context = await browser.new_context()  # 브라우저 생성
        cookie_list = await get_login_cookie(student_id, password)
        await context.add_cookies(cookie_list)  # 매개변수가 SetCookieParam 형식이여야 한다.

        page = await load_page(context)
        # 원하는 년도와 학기를 설정합니다.
        await set_year_semester_dropdown(page, year=year, semester=semester)

        # if click_res:
        inner_texts = await get_inner_texts(page)
        res = utils.parse_grade(inner_texts)  # 텍스트를 JSON형식의 딕셔너리로 파싱합니다.

    except Exception as e:
        print(e)
    #     self.logger.error(e)

    finally:
        await browser.close()
        return res


async def close_browser(self):
    await self.browser.close()


if __name__ == "__main__":
    import asyncio

    res = asyncio.run(run("20180806", "wjdaudwls123!", "2023", "0"))
    print(res)
