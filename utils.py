import time
async def max_retry(function, **kwargs):
    for _ in range(3):
        try:
            res = await function(**kwargs) if kwargs else await function()
            if res: break
        
        except TimeoutError: continue

    if not res: raise AssertionError(f"{function} occurs error!")
    return res


def parse_grade(inner_texts:str):
    column_names = ['이수학년도','이수학기','과목코드','과목명','과목학점','성적','등급','교수명','비고']
    column_len = len(column_names)
    table_texts = inner_texts.split('\t')
    text_by_rows = [table_texts[i:i + len(column_names)] for i in range(column_len + 2, len(table_texts), column_len + 1)]
    grade_info = [{col:value for col, value in zip(column_names,row)} for row in text_by_rows]
    return grade_info
