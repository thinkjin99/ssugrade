from playwright.async_api import expect, Page
from constant import *


async def click_button(page: Page, selector: str):
    """
    셀렉터로 지정한 버튼을 클릭한다.

    Args:
        selector (str): 버튼을 위한 선택자

    Returns:
        bool: 클릭이 정상적으로 진행되면 참
    """
    loc = page.locator(selector)
    try:
        await expect(loc).to_be_enabled(timeout=500)  # 버튼이 클릭 가능한 상태가 될때 까지 대기
        await loc.click(timeout=500)  # 클릭 실시.
        print(f"click success {selector}")

    except Exception as e:
        raise Exception("Click is not possible", selector, e)


async def click_dropdown(page: Page, dropdown_selector: str, value_selector: str):
    for _ in range(3):
        try:
            await click_button(page, dropdown_selector)  # 드랍다운 버튼 클릭
            await click_button(page, value_selector)  # 드랍 다운에서 값 클릭
            break

        except Exception as e:
            if await click_popup(page):
                continue
            print(e)


async def click_semeseter_dropdown(page: Page):
    semester_drop_selector = 'input[role="combobox"][value$="학기"]'
    last_semester = SEMESTER

    # 현재 로딩된 년도와 쿼리한 년도가 다른 경우
    async def wrapper(semester: int | str):
        semester_selector = (
            f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'
        )
        try:
            nonlocal last_semester
            if semester == last_semester:
                print("skip semester click")
                return

            async with page.expect_request_finished(timeout=2000) as req:
                await click_dropdown(page, semester_drop_selector, semester_selector)
                print("value: ", await req.value)
                last_semester = semester

        except Exception as e:
            print(e)

    return wrapper


async def click_year_dropdown(page: Page, year: int | str):
    """
    년도와 학기 설정을 위한 버튼을 클릭한다.

    Args:
        year (int, optional): 년도. Defaults to YEAR.
        semester (int, optional): 학기. Defaults to SEMESTER.
    """
    # 년도의 드랍다운 버튼과 년도 원소 셀렉터
    year_drop_selector = 'input[role="combobox"][value^="20"]'
    year_selector = f'div[class~="lsListbox__value"][data-itemkey="{year}"]'
    async with page.expect_request_finished(timeout=2000) as req:
        await click_dropdown(page, year_drop_selector, year_selector)
        print("value: ", await req.value)
    await page.wait_for_load_state("domcontentloaded")

    # await wait_for_update(page, year_update_selector, str(year))  # 페이지 테이블 로딩을 대기


async def get_inner_texts(page: Page, selector: str):
    """
    성적 테이블 내부의 텍스트를 추출한다.

    Raises:
        AssertionError: 성적 테이블을 못찾는 경우

    Returns:
        str: 성적 테이블 내에 존재하는 모든 텍스트
    """

    table_loc = page.locator(selector)
    await expect(table_loc).to_be_attached(timeout=2000)
    inner_texts = await table_loc.inner_text()

    if not inner_texts:
        # 값이 빈 경우는 태그 자체를 탐색하지 못한 경우이다.
        raise AssertionError(">> Locator can't locate table")
    return inner_texts


async def click_popup(page: Page):
    try:
        await page.click(".urPWFloatRight", timeout=1000)
        print("Click popup..")
        return True

    except Exception as e:
        print("No pop up...")
        return False
