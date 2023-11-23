from contextlib import asynccontextmanager

from page_action import *
from page_load import *
import parse
from constant import *
from read_cookies import get_cookies


async def get_page_grade(page: Page):
    grade_table_selector = 'tbody[id^="WD0"]'
    inner_texts = await get_inner_texts(page, grade_table_selector)

    columns = ["이수학년도", "이수학기", "과목코드", "과목명", "과목학점", "성적", "등급", "교수명", "비고"]
    unused_coumnls = set(("비고"))  # 사용 안하는 속성들

    res = parse.parse_table(
        inner_texts, columns, unused_coumnls
    )  # 텍스트를 JSON형식의 딕셔너리로 파싱합니다.
    return res


async def scrap_stat(page: Page):
    status_table_selector = 'tbody[id^="WD6"]'
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


async def scrap_all_grade(page: Page, attended_semester: dict):
    grades = []
    for year, semesters in attended_semester.items():
        await click_year_dropdown(page, year)
        for semester_value in semesters:
            await click_semeseter_dropdown(page, semester_value)
            grades.append(await get_page_grade(page))

    return grades


async def scrap_now_grade(page: Page):
    await click_year_dropdown(page, YEAR)
    await click_semeseter_dropdown(page, SEMESTER)
    now_grade = await get_page_grade(page)
    return now_grade


@asynccontextmanager
async def open_new_page(cookie_list: list[dict]):
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
        page = await load_usaint_page(browser, cookie_list)
        yield page

    except Exception as e:
        print(e)

    finally:
        await browser.close()


async def run(student_number: str):
    cookie_list = get_cookies(student_number)
    async with open_new_page(cookie_list) as page:
        stats = await scrap_stat(page)
        attened_semester = parse.parse_atteneded_semester(stats)
        grades = await scrap_all_grade(page, attened_semester)

    return grades


if __name__ == "__main__":
    import asyncio

    res = asyncio.run(run("20180811"))
    print(res)
