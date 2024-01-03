import requests
from requests.adapters import HTTPAdapter, Retry


class SessionRequest:
    def __init__(self) -> None:
        self.session = self.create_session()

    def create_session(self):
        retries = Retry(
            allowed_methods=("POST", "GET"),
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))  # Retry 세션 생성
        session.mount("http://", HTTPAdapter(max_retries=retries))  # Retry 세션 생성
        return session

    def session_request(self, request: requests.Request):
        prepared_request = self.session.prepare_request(request)
        try:
            resp = self.session.send(prepared_request)  # send request
            resp.raise_for_status()  # HTTP 에러 발생시
            return resp

        except Exception as e:
            print(f"Request:{prepared_request} got error {str(e)}")
            return
