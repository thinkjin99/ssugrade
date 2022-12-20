from user import *
URL = "https://ecc.ssu.ac.kr/sap/bc/webdynpro/sap/ZCMB3W0017"

LOGIN_HEADER = {
    'Accept': 'text/html',
    "Accept-Language": "ko-KR",
    'Connection': 'keep-alive',
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
}

PAYLOAD = {
    'FOCUS_ID': 'sap-user',
    'sap-system-login-oninputprocessing': "onLogin",
    'sap-urlscheme':None,
    'sap-system-login': "onLogin",
    'sap-system-login-basic_auth':None,
    'sap-accessibility': None,
    'sap-system-login-cookie_disabled':None, 
    'sysid': "SSP",
    'sap-client': "100",
    'sap-user': USER_ID,
    'sap-password': USER_PASS,
    'sap-language': "KO",
    'sap-language-dropdown': "한국어",
    }