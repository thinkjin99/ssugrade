from playwright.async_api import Page
import page_action
import page_load
import parse
from constant import *
from cookies import get_cookies


async def scrap_all_grades(page: Page, attendence_info: dict) -> list[dict]:
    total_grades = []
    click_semester = await page_action.click_semeseter_dropdown(page)  # wrapper 함수 반환

    for year, semesters in attendence_info.items():
        if year != USAINT_YEAR:
            await page_action.click_year_dropdown(page, year)

        for semester in semesters:
            await click_semester(semester)
            grades = {
                "year": year,
                "semester": semester,
                "grades": await parse.parse_grade(page),
            }
            total_grades.append(grades)

    return total_grades


async def run_single_browser_scrap_now(student_number: str, fcm_token: str):
    cookie_list = get_cookies(student_number, fcm_token)
    async with page_load.open_browser() as browser:
        page = await page_load.load_usaint_page(browser, cookie_list)
        click_semester = await page_action.click_semeseter_dropdown(page)
        await click_semester(SSURADE_SEMESTER)
        grades = await parse.parse_grade(page)
        return grades


async def run_single_browser_scrap_all(student_number: str, fcm_token: str) -> list:
    cookie_list = get_cookies(student_number, fcm_token)
    async with page_load.open_browser() as browser:
        page = await page_load.load_usaint_page(browser, cookie_list)
        grade_summaries: dict = await parse.parse_grade_summary(page)
        grades: list = await scrap_all_grades(page, grade_summaries)
        return grades


# async def new_tab_scrap_year_grades(
#     cookie_list: list[dict], year: str, semesters: list
# ):
#     async with page_load.open_browser() as browser:
#         page = await page_load.load_usaint_page(browser, cookie_list)
#         await page_action.click_year_dropdown(page, year)
#         grade = await scrap_year_grades(page, year, semesters)
#         return grade


# async def new_tab_scrap_all_grades(
#     attendence_info: dict, cookie_list: list[dict]
# ) -> list:
#     """
#     복수 개의 브라우저에서 해당 년도의 성적을 가져온다.
#     """
#     total_grades = []
#     tasks = [
#         asyncio.create_task(new_tab_scrap_year_grades(cookie_list, year, semesters))
#         for year, semesters in attendence_info.items()
#     ]
#     total_grades = await asyncio.gather(*tasks)
#     return total_grades


# async def run_multy_browser_scrapl_all_grades(fcm_token: str):
#     total_grades = []
#     async with page_load.open_browser() as browser:
#         cookie_list = get_cookies(fcm_token)  # 로그인에 필요한 쿠키 데이터
#         page = await page_load.load_usaint_page(browser, cookie_list)
#         stats = await scrap_attendance_stat(page)  # 현재까지의 학적 정보 가져옴
#         attendence_info = parse.parse_attenedence(stats)
#         years = list(attendence_info.keys())
#         first_year = years[0]

#         task = asyncio.create_task(
#             scrap_year_grades(page, first_year, attendence_info[first_year])
#         )

#         if len(years) > 1:
#             attendence_info = {
#                 k: v for k, v in attendence_info.items() if k != first_year
#             }
#             grades = await new_tab_scrap_all_grades(attendence_info, cookie_list)
#             total_grades.extend(grades)

#         total_grades.extend(await task)
#         return total_grades
