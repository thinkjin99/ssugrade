from collections import namedtuple
import re
from typing import Callable, Any, Dict, Tuple, NamedTuple
from bs4 import BeautifulSoup, Tag


def create_soup_object(html_source: str) -> BeautifulSoup:
    """
    전달 받은 http response를 soup 객체로 변환 합니다.

    Args:
        html_source (str): 전달 받은 html source 문자열

    Returns:
        BeautifulSoup: bs4 객체
    """
    soup = BeautifulSoup(html_source, "html.parser")  # 파싱 진행
    return soup


def parsing_exception_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    파싱 함수 데코레이터로 셀렉팅이나 데이터 추출중
    예외 발생시 로깅이나 예러 핸들링을 처리하기 위해 사용

    Args:
        func (Callable[..., Any])): 셀렉팅을 진행하는 함수

    Returns:
        Callable[..., Any]: 로깅 및 예외처리
    """

    def wrapper(
        *args: Tuple[Any], raise_exception: bool = True, **kwargs: Dict[Any, Any]
    ) -> Any:
        res = func(*args, **kwargs)  # 파싱 함수 실행
        if not res and raise_exception:
            raise ValueError(
                f">> {func.__name__ } got error \n args: {args} \n kwargs:{kwargs}"
            )
        else:
            return res

    return wrapper


@parsing_exception_handler
def select_all(parsing_object: BeautifulSoup | Tag, selector: str) -> list[Tag]:
    """
    수프 객체로 부터 셀렉터로 선택 가능한 모든 엘리먼트를 리스트로 반환한다.
    만일 선택 가능한 객체가 없을 경우 예외가 발생한다.

    Args:
        parsing_object (BeautifulSoup | Tag): 수프를 통해 생성된 html 객체 or 수프 태그 객체
        selector (str): 새 요소 선택을 위해 활용하는 셀렉터

    Returns:
        list[Tag]: 선택된 엘리먼트들
    """
    elements = parsing_object.select(selector)  # 길이가 0인 배열은 거짓이다.
    return elements


@parsing_exception_handler
def select_one(parsing_object: BeautifulSoup | Tag, selector: str) -> Tag | None:
    """
    수프 객체로 부터 셀렉터로 선택 가능한 단일 엘리먼트를 반환한다.
    만일 선택 가능한 객체가 없을 경우 예외가 발생한다.

    Args:
        parsing_object (BeautifulSoup | Tag): 수프를 통해 생성된 html 객체 or 수프 태그 객체
        selector (str): 새 요소 선택을 위해 활용하는 셀렉터

    Returns:
        Tag | None: 선택한 엘리먼트
    """
    element = parsing_object.select_one(selector)
    return element


def parse_table(soup: BeautifulSoup, table_selector: str) -> list[NamedTuple]:
    """
    유세인트의 테이블을 파싱합니다.
    유세인트 테이블의 경우 맨 앞, 뒤의 컬럼은 사용하지 않습니다. (아이콘이 들어감)

    Args:
        page (Page): 현재 페이지
        selector (str): 테이블 셀렉터
        columns (list): 추출할 컬럼

    Returns:
        list[dict]: 테이블 파싱 정보 (성적, 학기별 성적 요약)
    """
    table = select_one(soup, table_selector)
    tr_tags = select_all(table, "tr")  # 모든 row 선택
    column_names = [col.text for col in select_all(table, "th")]  # 컬럼 가져오기

    rows = []  # 파싱한 테이블 데이터
    Row = namedtuple("Row", column_names)  # 파싱한 테이블 데이터

    for tr_tag in tr_tags:
        if cells := select_all(tr_tag, "td", raise_exception=False):  # 셀 추출
            row = Row._make(cells)
            rows.append(row)

    return rows


def parse_average_grade(soup: BeautifulSoup) -> dict:
    """
    전체 평균 정보를 파싱합니다.

    Args:
        soup (BeautifulSoup): 페이지 객체

    Returns:
        dict: 전체 이수 평균 및 이수 학점, {'신청학점': '119', '평균평점': '3.54'}
    """
    average_grades_selector = ".group2 > .tbl > table > tbody td"
    rows = select_all(soup, average_grades_selector)
    cols = ["신청학점", "평균평점"]
    datas = {col: row.text for row, col in zip(rows, cols)}
    return datas


def parse_hakgi_grade_summaries(soup: BeautifulSoup) -> list[dict]:
    """
    학기 별 성적 요약 데이터를 파싱합니다.

    Args:
        soup (BeautifulSoup): 파싱 페이지

    Returns:
        list[dict]: 학기별 성적 요약 데이터
        [{'학기구분': '2022년도 2 학기', '평균평점': '2.55', '년도': '2022', '학기': '2 학기',
        '이수학점': '16', '석차': '101/114'}, {'학기구분': '2022년도 여름학기', '평균평점': '0.00', '년도':
        '2022', '학기': '여름학기', '이수학점': '3', '석차': '0/0'}, {'학기구분': '2022년도 1 학기',
        '평균평점': '3.66', '년도': '2022', '학기': '1 학기', '이수학점': '19', '석차': '47/124'}, ...]
    """

    def parse_onclick(td: Tag) -> NamedTuple:
        """
        td 태그 내부에 존재하는 onclick 속성의 텍스트를 파싱합니다.

        Args:
            td (Tag): td 태그

        Returns:
            NamedTuple: 태그 내부의 세부 정보, tuple(년도 학기 이수학점 석차)
        """
        Detail = namedtuple("Detail", "년도 학기 이수학점 석차")  # onclick에 작성된 세부 정보
        detail_tag = select_one(td, "a")  # a 태그 추출
        patt = r'"([^"]*)","([^"]*)","([^"]*)","([^"]*)"'  # 문자열 매칭 패턴
        matches = re.search(patt, detail_tag.get("onclick"))
        assert matches
        matched_str = matches.group(0).replace('"', "")  # 문자열 추출 및 ""제거
        detail = Detail._make(matched_str.split(","))
        return detail

    grade_table_seletor = ".group > .tbl > table"
    rows: list[NamedTuple] = parse_table(soup, grade_table_seletor)

    grades = []
    for row in rows:
        semester_grades = {}
        for col, td in zip(row._fields, row):
            if col == "상세조회":
                semester_grades.update(parse_onclick(td)._asdict())
            else:
                semester_grades[col] = td.text.strip()
        grades.append(semester_grades)
    return grades


def parse_hakgi_detail_grades(soup: BeautifulSoup) -> list[dict]:
    """
    학기별 세부 성적 테이블의 정보를 파싱한다.

    Args:
        soup (BeautifulSoup): 세부 성적 페이지

    Returns:
        list[dict]: [{'교과목명': '앱프로그래밍기초및실습', '과목학점': '3', '성적': 'A0'},
                    {'교과목명': 'CHAPEL', '과목학점': '1', '성적': 'P'},
                    {'교과목명': '데이터베이스', '과목학점': '3', '성적': 'C+'},
                    {'교과목명': '운영체제', '과목학점': '3', '성적': 'F'}, ...]
    """
    detail_table_selector = ".group > .tbl > table"
    rows: list[NamedTuple] = parse_table(soup, detail_table_selector)
    datas = [
        {col: td.text for col, td in zip(row._fields, row)} for row in rows
    ]  # 각 행별로 리스트로 묶어 append 한다.

    return datas
