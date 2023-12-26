from typing import Callable

from playwright.async_api import expect, Page
from constant import *


async def click_popup(page: Page) -> bool:
    """
    팝업 버튼을 클릭합니다.

    Args:
        page (Page): 페이지

    Returns:
        bool: 팝업 클릭 성공 여부
    """
    try:
        await page.click(".urPWFloatRight", timeout=1000)
        print("Click popup..")
        return True

    except Exception:
        print("No pop up...")
        return False


async def click_button(page: Page, selector: str) -> bool:
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
        return True

    except Exception as e:
        raise Exception("Click is not possible", selector, e)


async def click_dropdown(
    page: Page, dropdown_selector: str, value_selector: str
) -> bool:
    """
    드랍다운 버튼을 클릭합니다. 드랍다운 메뉴 클릭 -> 값 클릭
    두 가지의 과정을 하나로 통합한 함수 입니다.
    클릭에 실패할 경우 팝업 클릭을 시도합니다.

    Args:
        page (Page): 현재 페이지
        dropdown_selector (str): 드랍 다운 버튼 셀렉터
        value_selector (str): 드랍 다운 값 셀렉터

    Returns:
        bool: 클릭 성공 여부
    """
    for _ in range(3):  # 3번 시도
        try:
            await click_button(page, dropdown_selector)  # 드랍다운 버튼 클릭
            async with page.expect_request_finished(
                lambda request: request.method == "POST", timeout=4000
            ) as req:  # 요청 완료까지 대기
                await click_button(page, value_selector)  # 드랍 다운에서 값 클릭
            print("Request Value: ", await req.value)
            return True

        except Exception:
            if await click_popup(page):  # 에러 발생 시 팝업 클릭 시도
                continue

    return False


async def create_semeseter_dropdown_clicker(page: Page) -> Callable:
    """
    학기 드랍다운을 클릭하는 함수를 생성합니다.

    년도 이동시 학기는 고정된 경우가 있기 때문에 동일한 학기 이동을 방지하기 위해서
    직전 클릭한 학기를 저장해둔다.
    2022-2학기를 진행한 이후엔 2021-2학기를 학기 이동 없이 진행할 수 있게 한다.

    Args:
        page (Page): 현재 페이지

    Returns:
        Callable: 드랍다운 클릭 함수
    """
    semester_drop_selector = 'input[role="combobox"][value$="학기"]'  # 학기 드랍다운 셀렉터
    last_semester = USAINT_SEMESTER  # 초기 학기 값은 유세인트의 디폴트 값

    # 현재 로딩된 년도와 쿼리한 년도가 다른 경우
    async def wrapper(semester: int | str):
        semester_selector = (
            f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'  # 드랍다운 값 셀렉터
        )
        nonlocal last_semester
        if semester != last_semester:  # 현재 수집해야할 학기와 직전 학기가 다를 경우
            click_res: bool = await click_dropdown(
                page, semester_drop_selector, semester_selector
            )  # 학기 드랍다운 클릭

            if click_res:
                last_semester = semester
                return

            else:
                raise Exception(f"Semester:{semester} Click failed")

    return wrapper


async def click_year_dropdown(page: Page, year: int | str):
    """
    년도 드랍다운 버튼을 클릭한다.

    Args:
        page (Page): 현재 페이지
        year (int, optional): 년도.
    """

    year_drop_selector = 'input[role="combobox"][value^="20"]'  # 년도의 드랍다운 버튼 셀렉터
    year_selector = (
        f'div[class~="lsListbox__value"][data-itemkey="{year}"]'  # 년도의 값 셀렉터
    )
    click_res: bool = await click_dropdown(
        page, year_drop_selector, year_selector
    )  # 년도 드랍다운 클릭
    if not click_res:
        raise Exception(f"Year:{year} Click failed")

    return
