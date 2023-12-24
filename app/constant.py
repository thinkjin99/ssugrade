USAINT_YEAR = "2023"  # 현재 유세인트의 기본 년도
USAINT_SEMESTER = "3"  # 현재 유세인트의 기본 학기
SSURADE_SEMESTER = "2"  # 서비스가 수집할 현재 학기

URL = "https://ecc.ssu.ac.kr/sap/bc/webdynpro/sap/ZCMB3W0017"

SEMESTER_MAP = {
    "0": "1 학기",
    "1": "여름학기",
    "2": "2 학기",
    "3": "겨울학기",
}  # semester 값과 드랍다운 값 매핑

LOGIN_HEADER = {
    "Accept": "text/html",
    "Accept-Language": "ko-KR",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
}

PAYLOAD = {
    "FOCUS_ID": "sap-user",
    "sap-system-login-oninputprocessing": "onLogin",
    "sap-urlscheme": None,
    "sap-system-login": "onLogin",
    "sap-system-login-basic_auth": None,
    "sap-accessibility": None,
    "sap-system-login-cookie_disabled": None,
    "sysid": "SSP",
    "sap-client": "100",
    "sap-user": "",
    "sap-password": "",
    "sap-language": "KO",
    "sap-language-dropdown": "한국어",
}
