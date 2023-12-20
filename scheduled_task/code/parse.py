from constant import SEMESTER_MAP, YEAR, SEMESTER
from collections import defaultdict


def parse_table(inner_texts: str, columns: list, unused_columns: set | list = []):
    column_len = len(columns)
    table_texts = [t if t != "\xa0" else "" for t in inner_texts.split("\t")]
    text_by_rows = [
        table_texts[i : i + len(columns)]
        for i in range(column_len + 1, len(table_texts), column_len)
    ]  # 행 단위로 성적 가져옴
    grade_info = [
        {col: value for col, value in zip(columns, row) if col not in unused_columns}
        for row in text_by_rows
    ]
    return grade_info


def parse_attenedence(stats: list[dict]) -> dict[str, list]:
    attended_semesters = defaultdict(list)
    attended_semesters[YEAR].append(SEMESTER)
    reversed_semester_map = {v: k for k, v in SEMESTER_MAP.items()}
    for stat in stats:
        year, semester = (stat.get("학년도"), stat.get("학기"))
        if year and semester:
            semester_value = reversed_semester_map[semester]
            attended_semesters[year].append(semester_value)

    for i, year in enumerate(attended_semesters.keys()):
        if i % 2 != 0:
            attended_semesters[year].sort()

    return attended_semesters


def parse_grade(year: str, sesmster: str, grades: list[dict]):
    for grade in grades:
        grade.update({"학년도": year, "학기": sesmster})
    return grades
