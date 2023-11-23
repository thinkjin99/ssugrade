from contextlib import contextmanager
from functools import wraps

from sqlalchemy import create_engine, Select, Insert, Result
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.declarative import DeclarativeMeta

from sqlalchemy.dialects.mysql import insert
from typing import Callable, Iterator


@contextmanager
def create_session(is_read_session: bool = True):
    """
    세션 생성을 위한 함수

    Args:
        is_read_session (bool, optional): 세션 rw를 구분. Defaults to True.

    Raises:
        e: api콜을 처리하는 단계에서 발생하는 예외

    Yields:
        Session: DB 세션
    """
    # endpoint = READ_ENDPOINT if is_read_session else WRITE_ENDPOINT
    endpoint = f"mysql+pymysql://root:kidok0714@127.0.0.1/ssugrade"
    engine = create_engine(endpoint)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session  # 세션을 반환한다.
        session.commit()  # 세션 데이터 반영

    except Exception as e:
        session.rollback()  # 에러 발생시 롤백
        raise e

    finally:
        session.close()


def mapping_result(is_all: bool) -> Callable:
    def decorator(func: Callable) -> Callable:
        """
        쿼리를 전송하고 전송한 쿼리의 응답 결과를 매핑해 반환한다.
        is_all 매개변수를 통해 쿼리 응답의 개수를 설정할 수 있다.

        Args:
            func (Callable): 쿼리 생성 함수
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> list[RowMapping] | RowMapping | None:
            try:
                res: Result = func(*args, **kwargs)  # 쿼리를 실행한 결과가 저장된다.
                # is_all = kwargs["is_all"] if "is_all" in kwargs else False

                if is_all:
                    row = [row._mapping for row in res.all()]
                    mapped_result = row if len(row) > 0 else None

                else:
                    row = res.first()
                    mapped_result = row._mapping if row else None

                return mapped_result

            except Exception as e:
                print(f"MappingError: {func.__name__} ", e)
                raise e

        return wrapper

    return decorator


def execute_query(func: Callable) -> Callable:
    """
    쿼리를 실행한다.

    Args:
        func (Callable): 쿼리 생성할 함수
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Result:
        try:
            with create_session() as session:
                query = func(*args, **kwargs)
                rows = session.execute(query)
                print(f"{func.__name__}: Query completed")
            return rows  # 쿼리 실행 결과 반환

        except Exception as e:
            print(f"ExecutionError: {func.__name__} ", e)
            raise e

    return wrapper


@execute_query
def bulk_insert(
    model: DeclarativeMeta,
    datas: list[dict],
) -> Insert | None:
    """
    대규모로 데이터를 데이터베이스에 삽입한다,

    Args:
        model (DeclarativeMeta): 삽입을 진행할 테이블
        datas (list[dict]): 삽입을 진행할 데이터

    Raises:
        Exception: 집어 넣을 데이터가 존재하지 않는 경우

    Returns:
        Insert | None: 인서트 쿼리문 또는 None을 반환한다.
    """

    if len(datas) == 0:
        raise Exception("insert data")

    else:
        insert_stmt = insert(model).values(datas)
        # print(f">>len:{len(datas)} info:{datas[0]} is inserted!!")

        return insert_stmt  # DB에 추가


@execute_query
def bulk_upsert(
    model: DeclarativeMeta,
    datas: list[dict],
    update_columns: list[str],
) -> Insert:
    """
    특정 테이블의 데이터를 대규모로 데이터를 업서트 한다.

    Args:
        model (DeclarativeMeta): ORM 모델
        datas (list[dict]): 업서트를 실행할 데이터들
        update_column (list[str] | str): 중복시 업데이트를 진행할 컬럼명

    Raises:
        Exception: 집어 넣을 데이터가 존재하지 않는 경우

    Returns:
        Insert | None: 인서트 쿼리문 또는 None을 반환한다.
    """

    if len(datas) == 0:
        raise Exception("upsert data")

    insert_stmt = insert(model).values(datas)
    update_values = {
        name: value
        for name, value in insert_stmt.inserted.items()
        if name in update_columns  # 컬럼에 존재하는 값만 upsert
    }
    insert_stmt = insert_stmt.on_duplicate_key_update(**update_values)
    return insert_stmt


# @execute_query
# def check_duplicate(model:, datas:list[dict]) -> Select:
#     select(model).where()


@execute_query
def insert_product(model: DeclarativeMeta, data: dict) -> Insert | None:
    """
    벌크 인서트에 실패했을 경우 개별적으로 데이터를 삽입하는 작업을 수행합니다.

    Args:
        model (DeclarativeMeta): _description_
        data (dict): _description_

    Returns:
        Insert | None: _description_
    """
    inset_stmt = insert(model).values(data)
    return inset_stmt


def yield_chunk_datas(query: Select, chunk_size=3000) -> Iterator:
    """
    대용량 데이터를 청크 단위로 끊어 전송합니다.

    Args:
        query (Select): 끊어서 전송할 데이터 쿼리
        chunk_size (int, optional): 한번에 끊어서 가져올 데이터의 크기. Defaults to 3000.

    Yields:
        Iterator[RowMapping]: 매핑된 쿼리 결과 데이터
    """
    offset = 0
    while True:
        with create_session() as session:
            select_stmt = query.offset(offset).limit(
                chunk_size
            )  # 가져온 데이터 이후 부터 청크 사이즈 만큼 가져온다.
            offset += chunk_size
            result = [r._mapping for r in session.execute(select_stmt).all()]  # 데이터 매핑
            yield result

        if len(result) < chunk_size:  # 더 이상 가져올 데이터가 없으면 종료
            break
