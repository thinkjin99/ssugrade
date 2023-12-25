from typing import Callable

from playwright.async_api import Page
import page_action
import page_load
import parse
from constant import *
from cookies import get_cookies


async def scrap_all_grades(page: Page, attendence_info: dict) -> list[dict]:
    """
    전체 학기 성적을 수집합니다.

    Args:
        page (Page): 현재 페이지
        attendence_info (dict):

    Returns:
        list[dict]: _description_
    """
    total_grades = []
    click_semester_dropdown: Callable = (
        await page_action.create_semeseter_dropdown_clicker(page)
    )  # wrapper 함수 반환

    for year, semesters in attendence_info.items():
        if year != USAINT_YEAR:  # 년도가 다를 경우 클릭
            await page_action.click_year_dropdown(page, year)

        for semester in semesters:
            await click_semester_dropdown(semester)  # 학기 클릭
            grades = {
                "year": year,
                "semester": semester,
                "grades": await parse.parse_grade(page),
            }
            total_grades.append(grades)

    return total_grades


async def run_single_browser_scrap_now(
    student_number: str, fcm_token: str
) -> list[dict]:
    """
    현재 학기의 성적을 수집합니다.

    Args:
        student_number (str): 학번
        fcm_token (str): fcm 토큰

    Returns:
        list[dict]: 성적 데이터
    """
    cookie_list = get_cookies(student_number, fcm_token)  # 로그인에 활용할 쿠키
    async with page_load.open_browser() as browser:
        page = await page_load.load_usaint_page(browser, cookie_list)  # 유세인트 로딩
        click_semester_dropdown: Callable = (
            await page_action.create_semeseter_dropdown_clicker(page)
        )
        await click_semester_dropdown(SSURADE_SEMESTER)  # 학기 클릭
        grades: list = await parse.parse_grade(page)  # 성적 파싱
        return grades


async def run_single_browser_scrap_all(
    student_number: str, fcm_token: str
) -> list[dict]:
    """
    전체 학기 성적을 수집합니다.

    Args:
        student_number (str): 학번
        fcm_token (str): fcm 토큰

    Returns:
        list[dict]: 전체 학기 성적
    """
    cookie_list = get_cookies(student_number, fcm_token)
    async with page_load.open_browser() as browser:
        page = await page_load.load_usaint_page(browser, cookie_list)
        grade_summaries: dict = await parse.parse_grade_summary(
            page
        )  # 현재까지 이수한 학기 성적 요약 (현재는 학기 정보만 존재)
        grades: list = await scrap_all_grades(page, grade_summaries)  # 전체 성적 수집
        return grades
