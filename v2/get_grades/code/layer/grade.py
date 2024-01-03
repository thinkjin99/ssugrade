from concurrent.futures import ThreadPoolExecutor

from layer.request import get_hakgi_grade_summary, post_hakgi_detail_grade
from layer.session import RequestSession
from layer.parse import (
    parse_average_grade,
    parse_hakgi_grade_summaries,
    parse_hakgi_detail_grades,
    create_soup_object,
)


def scrap_hakgi_grade_summary(session: RequestSession) -> dict:
    """
    학기 별 요약 성적 정보를 반환한다.

    Args:
        session (RequestSession): 로그인 세션 정보

    Returns:

        dict: {
            '신청학점': '119',
            '평균평점': '3.54',
            '학기별 요약': [
                {'학기구분': '2022년도 2 학기', '평균평점': '2.55', '년도': '2022', '학기': '2 학기', '이수학점': '16', '석차': '101/114'},
                {'학기구분': '2021년도 2 학기', '평균평점': '3.48', '년도': '2021', '학기': '2 학기', '이수학점': '18', '석차': '69/116'},
                ...
            ]
    """
    grade_summary_response = session.send_request(get_hakgi_grade_summary())
    assert grade_summary_response
    grade_summary_page = create_soup_object(grade_summary_response.text)

    total_average_grade: dict = parse_average_grade(grade_summary_page)  # 전체 평점 추출
    grade_summaries: list[dict] = parse_hakgi_grade_summaries(
        grade_summary_page
    )  # 학기별 요약 추출

    summary = {**total_average_grade}  # copy dict
    summary["요약성적들"] = grade_summaries  # 요약 정보 업데이트
    return summary


def scrap_hakgi_detail_grades(
    session: RequestSession, year: str | None, hakgi: str | None
) -> dict:
    """
    한 학기의 세부 성적 정보를 가져온다.

    Args:
        session (RequestSession): 세션 객체
        year (str | None): 년도
        hakgi (str | None): 학기

    Raises:
        KeyError: 년도나 학기가 존재하지 않을 경우

    Returns:
        dict: {
            '년도': '2022',
            '학기': '2 학기',
            '성적들': [
                {'교과목명': '앱프로그래밍기초및실습', '과목학점': '3', '성적': 'A0'},
                {'교과목명': 'CHAPEL', '과목학점': '1', '성적': 'P'},
                ...
            ]
    """
    if year and hakgi:
        grade_response = session.send_request(post_hakgi_detail_grade(year, hakgi))
        assert grade_response
        grade_page = create_soup_object(grade_response.text)
        grades = parse_hakgi_detail_grades(grade_page)
        return {"년도": year, "학기": hakgi, "성적들": grades}
    else:
        raise KeyError(f"Key is not available year:{year} hakgi:{hakgi}")


def scrap_all_hakgi_grades(
    session: RequestSession, grade_summaries: list[dict]
) -> list[dict]:
    """
    전체 세부 성적을 가져온다. (스마트 포털에 존재하는)

    Args:
        session (RequestSession): 로그인 세션 객체
        grade_summaries (list[dict]): 학기 별 성적 요약 정보 (이수 학기 추출을 위해 사용)

    Returns:
        list[dict]: 전체 세부 성적
    """
    with ThreadPoolExecutor(max_workers=4) as executor:  # 동시 요청 수 과할 경우 학교 서버가 못견딤
        futures = [
            executor.submit(
                scrap_hakgi_detail_grades,
                session,
                summary.get("년도"),
                summary.get("학기"),
            )
            for summary in grade_summaries
        ]
    grades = [future.result() for future in futures]
    return grades
