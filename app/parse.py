import re
from collections import defaultdict

from playwright.async_api import Page
from constant import SEMESTER_MAP, USAINT_YEAR, SSURADE_SEMESTER


async def parse_table(
    page: Page, selector: str, columns: list, unused_columns: set | list = []
) -> list[dict]:
    """
    유세인트의 테이블을 파싱합니다.
    유세인트 테이블의 경우 맨 앞, 뒤의 컬럼은 사용하지 않습니다. (아이콘이 들어감)

    Args:
        page (Page): 현재 페이지
        selector (str): 테이블 셀렉터
        columns (list): 추출할 컬럼
        unused_columns (set | list, optional): 사용하지 않는 컬럼. Defaults to [].

    Returns:
        list[dict]: 테이블 파싱 정보 (성적, 학기별 성적 요약)
    """
    table = page.locator(selector)
    rows = await table.locator("tr").all()  # 모든 row 선택
    pattern = re.compile(r"[\xa0\n\t]+")  # 공백을 기준으로 td를 추출
    parsed_table_datas = []  # 파싱한 테이블 데이터

    for row in rows[1:]:
        texts = pattern.split(await row.inner_text())  # 패턴을 기준으로 분할
        table_data = {
            col: value
            for col, value in zip(columns, texts[1:-1])  # 맨 앞,뒤의 컬럼은 사용하지 않는다.
            if col not in unused_columns and value != ""  # 빈 값과 사용하지 않는 컬럼은 버린다.
        }
        if any(table_data):  # 공백으로만 가득찬 행일 경우 버림
            parsed_table_datas.append(table_data)
    return parsed_table_datas


def sort_summary_semester(summaries: dict[str, list]):
    """
    성적 요약표의 학기를 년도 별로 내림-오름-내림-오름 으로 정렬합니다.
    유세인트는 학기의 경우 연도가 이동해도 유지되는 성질이 있어 이 점을 활용해 로딩 횟수를
    줄이기 위해 이러한 과정을 진행합니다.

    (2020:[2,1,0],2021:[0,1,2]..)과 같이 정렬합니다.

    Args:
        summaries (dict): 유세인트 학기별 성적 요약 테이블의 정보
    """
    for i, year in enumerate(summaries.keys()):
        if i % 2 != 0:  # 유세인트 기본이 내림차순 정렬이므로 오름차순 정렬만 진행.
            summaries[year].sort()


async def parse_grade_summary(page: Page) -> dict[str, list]:
    """
    학기별 성적 테이블에서 이수한 학기 정보를 추출합니다.
    추출한 정보는 이후 전체 성적 데이터를 수집할 때 수강 학기 파악을 위해 사용 됩니다.

    Args:
        page (Page): 현재 브라우저의 페이지

    Returns:
        dict[str, list]: {"2023":["2","1","0"],"2022":["0","1","2"],...}
        년도 별로 이수한 학기들을 저장한다. 추후에 학기별 성적 요약도 저장할 예정.
    """
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
        "학사경고여부",
        "상담여부",
        "유급",
    ]
    # inner_texts = await get_inner_texts(page, status_table_selector)  # 성적 요약 테이블 내부 텍스트
    summaries = defaultdict(list)
    summaries[USAINT_YEAR].append(SSURADE_SEMESTER)  # 가져올 학기에 현재 학기도 추가
    parsed_rows = await parse_table(page, status_table_selector, columns)

    for row in parsed_rows:  # 테이블 텍스트 추출
        # TODO 취득학점 및 평점 평균 추출
        summaries[row["학년도"]].append(
            SEMESTER_MAP[row["학기"]]
        )  # 1 학기,2 학기를 0,1,2 등 키 값으로 변환

    sort_summary_semester(summaries)  # 학기 정렬
    return summaries


async def parse_grade(page: Page) -> list[dict]:
    """
    성적 테이블의 텍스트를 추출한다.


    Args:
        page (Page): 현재 브라우저의 페이지

    Returns:
        list[dict]: 한 학기 성적 정보
    """
    grade_table_selector = 'tbody[id^="WD0"]'
    inner_texts = await get_inner_texts(page, grade_table_selector)  # 성적 테이블 텍스트 추출
    columns = ["성적", "등급", "과목명", "상세성적", "과목학점", "교수명", "비고", "과목코드"]
    unused_coumnls = set(("비고", "과목코드", "상세성적"))  # 사용 안하는 속성들

    grades = await parse_table(
        page, grade_table_selector, columns, unused_coumnls
    )  # 텍스트를 JSON형식의 딕셔너리로 파싱합니다.
    return grades
