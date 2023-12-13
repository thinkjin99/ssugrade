from playwright.async_api import expect, Page
from code.constant import *


async def click_button(page: Page, selector: str):
    """
    셀렉터로 지정한 버튼을 클릭한다.

    Args:
        selector (str): 버튼을 위한 선택자

    Returns:
        bool: 클릭이 정상적으로 진행되면 참
    """
    loc = page.locator(selector)
    for _ in range(3):
        try:
            print(f"try click.. {selector}")
            await expect(loc).to_be_enabled(timeout=1000)  # 버튼이 클릭 가능한 상태가 될때 까지 대기
            await loc.click(timeout=500)  # 클릭 실시.
            break

        except Exception as e:
            print("Click is not possible", selector)
            await click_popup(page, ".urPWFloatRight")
            continue


async def check_is_empty_semester(page: Page) -> bool:
    try:
        first_row_selector = 'tbody[id^="WD0"] tr:nth-child(2)'  # 성적 테이블의 첫 행 선택
        first_row = page.locator(first_row_selector)
        await expect(first_row).not_to_be_empty(timeout=3000)
        return False

    except AssertionError:
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
    await click_button(page, value_selector)  # 드랍 다운에서 값 클릭


async def click_semeseter_dropdown(page: Page, semester: int | str):
    semester_drop_selector = 'input[role="combobox"][value$="학기"]'
    semester_selector = f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'

    semester_update_selector = (
        'tbody[id^="WD0"] tr:nth-child(2) td:nth-child(3)'  # 로딩된 성적의 학기 셀렉터
    )

    # 현재 로딩된 년도와 쿼리한 년도가 다른 경우

    await click_dropdown(page, semester_drop_selector, semester_selector)
    await wait_for_update(
        page, semester_update_selector, SEMESTER_MAP[str(semester)]
    )  # 페이지 테이블 로딩을 대기


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
    year_update_selector = (
        'tbody[id^="WD0"] tr:nth-child(2) td:nth-child(2)'  # 로딩된 성적의 년도 셀렉터
    )
    await click_dropdown(page, year_drop_selector, year_selector)
    await wait_for_update(page, year_update_selector, str(year))  # 페이지 테이블 로딩을 대기


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


async def click_popup(page: Page, selector: str):
    try:
        await page.click(selector, timeout=1000)
        print("Click popup..")
    except Exception as e:
        print("No popup...")
