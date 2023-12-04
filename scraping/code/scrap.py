import asyncio
from contextlib import asynccontextmanager

from page_action import *
from page_load import *
import parse
from constant import *
from read_cookies import get_cookies


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


async def new_tab_scrap_year_grades(
    cookie_list: list[dict], year: str, semesters: list
):
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        await click_year_dropdown(page, year)
        grade = await scrap_year_grades(page, semesters)
        return grade


async def scrap_all_grade(page: Page, attendence_info: dict):
    total_grades = []
    for year, semesters in attendence_info.items():
        if year != YEAR:
            await click_year_dropdown(page, year)
        year_grades = await scrap_year_grades(page, semesters)
        total_grades.append(year_grades)
    return total_grades


async def new_tab_scrap_all_grade(
    attendence_info: dict, cookie_list: list[dict]
) -> list[dict]:
    """
    복수 개의 브라우저에서 해당 년도의 성적을 가져온다.
    """
    total_grades = []
    tasks = [
        asyncio.create_task(new_tab_scrap_year_grades(cookie_list, year, semesters))
        for year, semesters in attendence_info.items()
    ]
    total_grades = await asyncio.gather(*tasks)
    return total_grades


async def run_multy(student_number: str):
    total_grades = []
    async with open_browser() as browser:
        cookie_list = get_cookies(student_number)  # 로그인에 필요한 쿠키 데이터
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)  # 현재까지의 학적 정보 가져옴
        attendence_info = parse.parse_attenedence(stats)
        years = list(attendence_info.keys())
        first_year = years[0]

        task = asyncio.create_task(scrap_year_grades(page, attendence_info[first_year]))

        if len(years) > 1:
            attendence_info = {
                k: v for k, v in attendence_info.items() if k != first_year
            }
            grades = await new_tab_scrap_all_grade(attendence_info, cookie_list)
            total_grades.extend(grades)

        total_grades.extend(await task)
        return total_grades


async def run_single_browser_scrap_now(student_number: str):
    cookie_list = get_cookies(student_number)
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        await click_year_dropdown(page, "2023")
        await click_semeseter_dropdown(page, "0")
        grades = await get_page_grades(page)
        return grades


async def run_single_browser_scrap_all(student_number: str):
    cookie_list = get_cookies(student_number)
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)
        attened_semester = parse.parse_attenedence(stats)
        grades = await scrap_all_grade(page, attened_semester)
        return grades


if __name__ == "__main__":
    #     import time

    #     start = time.time()
    res = asyncio.run(run_single_all("20180811"))
    # res = asyncio.run(run_multy("20180811"))

    print(*res)
#     print(res)
