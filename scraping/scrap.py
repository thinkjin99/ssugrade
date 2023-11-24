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


# async def scrap_one_grade(page: Page, year: str, semester: str):
#     await click_year_dropdown(page, year)
#     await click_semeseter_dropdown(page, semester)
#     now_grade = await get_page_grade(page)
#     return now_grade


async def multy_scrap_year(
    page: Page, year: str, semesters: list, cookie_list: list[dict]
) -> list[dict]:
    """
    별도의 브라우저에서 해당 년도의 성적을 가져온다.

    Args:
        page (Page): 브라우저 페이지 객체
        year (str): 년도
        semesters (list): 학기들
        cookie_list (list[dict]): 로그인에 활용되는 쿠키

    Returns:
        list: 해당 년도의 성적들
    """
    grades = []
    async with open_browser(cookie_list) as browser:
        page = await load_usaint_page(browser, cookie_list)
        await click_year_dropdown(page, year)
        for semester_value in semesters:
            await click_semeseter_dropdown(page, semester_value)
            grades.append(await get_page_grade(page))
    return grades


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

    finally:
        await browser.close()


async def run_multy(student_number: str):
    async with open_browser() as browser:
        cookie_list = get_cookies(student_number)  # 로그인에 필요한 쿠키 데이터
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)  # 현재까지의 학적 정보 가져옴
        attened_semester = parse.parse_atteneded_semester(stats)
        tasks = [
            multy_scrap_year(page, year, semesters, cookie_list)
            for year, semesters in attened_semester.items()
        ]  # 복수 개의 브라우저로 성적 스크래핑 실행
        grades = await asyncio.gather(*tasks)

    return grades


async def run_single(student_number: str):
    cookie_list = get_cookies(student_number)
    grades = []
    print(cookie_list)
    async with open_browser() as browser:
        page = await load_usaint_page(browser, cookie_list)
        stats = await scrap_stat(page)
        attened_semester = parse.parse_atteneded_semester(stats)
        print(attened_semester)
        grades = await scrap_all_grade(page, attened_semester)

    return grades


if __name__ == "__main__":
    import asyncio
    import time

    start = time.time()
    res = asyncio.run(run_single("20180811"))
    print(res)
