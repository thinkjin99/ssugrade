from page_action import *
from page_load import *
import parse as parse
from constant import *


async def get_page_grades(page: Page):
    grade_table_selector = 'tbody[id^="WD0"]'
    inner_texts = await get_inner_texts(page, grade_table_selector)

    columns = ["이수학년도", "이수학기", "과목코드", "과목명", "과목학점", "성적", "등급", "교수명", "비고"]
    unused_coumnls = set(("비고"))  # 사용 안하는 속성들

    res = parse.parse_table(
        inner_texts, columns, unused_coumnls
    )  # 텍스트를 JSON형식의 딕셔너리로 파싱합니다.
    return res


async def scrap_stat(page: Page):
    status_table_selector = 'tbody[id^="WD5"]'
    columns = [
        "학년도",
        "학기",
        "신청학점",
        "취득학점",
        "P/F학점",
        "평점평균",
        "평점계",
        "산술평균",
        "학기별석차",
        "전체석차",
        "상담여부",
        "유급",
    ]
    inner_texts = await get_inner_texts(page, status_table_selector)
    res = parse.parse_table(inner_texts, columns)
    return res


async def scrap_year_grades(page: Page, semesters: list) -> list[dict]:
    year_grades = []
    for semester in semesters:
        await click_semeseter_dropdown(page, semester)
        year_grades.append(await get_page_grades(page))

    return year_grades


async def run_single_browser_scrap_now(cookie: list):
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie)
        grades = await get_page_grades(page)
        return grades
