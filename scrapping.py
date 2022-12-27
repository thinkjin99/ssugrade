from playwright.async_api import async_playwright
from playwright.async_api import expect

from constant import *
import logger
import utils
import login

class Usaint():
    """
    usaint에서 playwright를 통해 성적을 스크래핑 하는 클래스입니다.
    """

    def __init__(self, student_id:str, password:str) -> None:
        """
        스크래핑을 위한 입력 정보를 초기화 합니다.

        Args:
            student_id (str): 유세인트 아이디
            password (str): 유세인트 비밀번호
        """
        self.logger = logger.create_logger() #로깅을 위한 로거
        self.student_id = student_id
        self.password = password


    async def create_default_browser(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                args=[
                    '--headless', #백그라운드에서 실행
                    '--disable-gpu',#GPU 활용 하지 않음
                    '--single-process', #싱글 프로세스로 실행
                    '--no-sandbox',#GPU 사용안함
                    '--disable-extensions',
                    '--incognito',
                    '--v=99',
                    '--no-zygote', #자이고트 활용안함
                    '--deterministic-fetch',
                    '--disable-dev-shm-usage',#메모리 공유 비활성화
                    ]
            )
            self.context = await self.browser.new_context() #브라우저 생성
            self.page = await self.context.new_page() #페이지 생성
            return True #함수의 정상종료를 나타낸다.
        
        except Exception:
            raise Exception("Can't Start Browser")


    async def set_context_cookies(self):
        """
        크로니움 페이지에 쿠키를 로그인 쿠키를 세팅한다.
        """
        cookie_list = await utils.max_retry(login.get_login_cookie, student_id=self.student_id, password=self.password)
        await self.context.add_cookies(cookie_list) #브라우저 컨텍스트에 쿠키를 추가해준다.
        return True #함수의 정상 종료를 의미


    async def load_main_page(self):
        """
        로그인 쿠키가 추가된 브라우저로 성적 페이지를 로딩한다.
        """
        await self.set_context_cookies()
        goto_res = await utils.max_retry(self.page.goto, url=URL, timeout=3000)

        #goto에 실패하면 assertion 에러 발생
        assert goto_res, "Page Load Failed"
        return True #로딩이 완료됨.


    async def click_button(self, selector:str):
        """
        셀렉터로 전달된 버튼을 클릭한다.

        Args:
            selector (str): 버튼을 위한 선택자

        Returns:
            bool: 클릭이 정상적으로 진행되면 참
        """
        loc = self.page.locator(selector)
        await expect(loc).to_be_enabled(timeout=2000)
        await loc.click(timeout=2000) #클릭을 실시한다.
        return True #클릭이 정상적으로 진행됨


    async def wait_content_table(self):
        """
            성적 테이블 로딩을 대기한다.
        """
        try:
            tr_selector = 'tbody[id^="WD0"] tr:nth-child(2)' #성적 테이블 셀렉터
            tr_loc = self.page.locator(tr_selector)
            await expect(tr_loc).not_to_be_empty(timeout=5000) #테이블을 대기
            return True
        
        except AssertionError:
            return False #테이블이 비어있음
    


    async def click_year_semester(self, year:int=YEAR, semester:int=SEMESTER):
        """
        년도와 학기 설정을 위한 버튼을 클릭한다.

        Args:
            year (int, optional): 년도. Defaults to YEAR.
            semester (int, optional): 학기. Defaults to SEMESTER.
        """
        #년도의 드랍다운 버튼과 년도 원소 셀렉터
        year_drop_selector = 'input[role="combobox"][value^="20"]'
        year_selector = f'div[class~="lsListbox__value"][data-itemkey="{year}"]'

        semester_drop_selector = 'input[role="combobox"][value$="학기"]'
        semester_selector = f'div[class~="lsListbox__value"][data-itemkey="09{semester}"]'

        #현재 로딩된 년도와 쿼리한 년도가 다른 경우
        if year != YEAR:
            await self.click_button(year_drop_selector) 
            await self.click_button(year_selector)
            await self.wait_content_table() #페이지 테이블 로딩을 대기

        if semester != SEMESTER:
            await self.click_button(semester_drop_selector)
            await self.click_button(semester_selector)
            await self.wait_content_table() #페이지 테이블 로딩을 대기

        return True #클릭이 정상적으로 완료됨.


    async def get_inner_texts(self):
        """
        성적 테이블 내부의 텍스트를 추출한다.

        Raises:
            AssertionError: 성적 테이블을 못찾는 경우

        Returns:
            str: 성적 테이블 내에 존재하는 모든 텍스트
        """
        # "tr > td:not(:first-child):not(:last-child)"
        table_selector = 'tbody[id^="WD0"]'
        table_loc = self.page.locator(table_selector)
        await expect(table_loc).to_be_enabled(timeout=2000)
        inner_texts = await table_loc.inner_text()

        if not inner_texts: 
            #값이 빈 경우는 태그 자체를 탐색하지 못한 경우이다.
            raise AssertionError("Locator can't locate table")
        return inner_texts


    async def run(self, year:int=2022, semester:int=2):
        """
        유세인트 성적 스크래핑 전체 로직을 가동합니다.

        Args:
            year (int, optional): _description_. Defaults to 2022.
            semester (int, optional): _description_. Defaults to 2.

        Returns:
            _type_: _description_
        """
        res = None
        try:
            await utils.max_retry(self.create_default_browser) #브라우저를 가동합니다.
            await utils.max_retry(self.load_main_page) #로그인 및 성적 페이지를 로딩합니다.
            table_content = await self.click_year_semester(year=year, semester=semester) #원하는 년도와 학기를 설정합니다.
            
            if table_content:
                inner_texts = await utils.max_retry(self.get_inner_texts) #성적 테이블의 텍스트를 추출합니다.
                res = utils.parse_grade(inner_texts) #텍스트를 JSON형식의 딕셔너리로 파싱합니다.

        except AssertionError as e:
            self.logger.error(e)

        except TimeoutError as e:
            self.logger.error(e)
        
        except Exception as e:
            self.logger.error(e)
            
        finally:
            await self.close_browser()
            return res
    

    async def close_browser(self):
        await self.browser.close()


# if __name__ == '__main__':
#     import asyncio
#     from user import *
#     my_saint = Usaint(USER_ID, PASSWORD)
#     res = asyncio.run(my_saint.run(2022, 2))
#     print(res)


