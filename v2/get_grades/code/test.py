import requests

cookies = {
    "JSESSIONID": "AF006F949FD3FAF56F77C12E8C6F6542",
    # "_gid": "GA1.3.177728885.1704264066",
    # "_gat_gtag_UA_117423596_1": "1",
    "loginCookie": "fY2JfGwYYo7ipMyojCZRB38eZ5B2YrchxajjQR1ejUpTUTmHaZGDEmO4bqaccuwe",
    # "_ga_Q5J3KXLTHG": "GS1.1.1704264065.1.1.1704264077.0.0.0",
    # "_ga": "GA1.1.324998951.1704264066",
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    # 'Cookie': 'JSESSIONID=AF006F949FD3FAF56F77C12E8C6F6542; _gid=GA1.3.177728885.1704264066; _gat_gtag_UA_117423596_1=1; loginCookie=fY2JfGwYYo7ipMyojCZRB38eZ5B2YrchxajjQR1ejUpTUTmHaZGDEmO4bqaccuwe; _ga_Q5J3KXLTHG=GS1.1.1704264065.1.1.1704264077.0.0.0; _ga=GA1.1.324998951.1704264066',
    "Origin": "https://mobile.ssu.ac.kr",
    "Referer": "https://mobile.ssu.ac.kr/student/gradeGrade.do",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

data = {
    "IN_HAKJUM": "16",
    "IN_SUKCHA": "101/114",
    "IN_YEAR": "2022",
    "IN_HAKGI": "2 학기",
    "IN_COURSE": "",
    "REQ_USER_ID": "",
}

response = requests.post(
    "https://mobile.ssu.ac.kr/student/gradeGradeInfo.do",
    cookies=cookies,
    headers=headers,
    data=data,
)
print(response.text)
