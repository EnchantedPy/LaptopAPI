import pytest
from fastapi import HTTPException
from src.core.exceptions.exceptions import DatabaseDataException, DatabaseConfigurationException, DatabaseException, DatabaseIntegrityException, DatabaseOperationalException
from src.utils.logger import test_logger
from src.utils.UnitOfWork import SQLAlchemyUoW
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.models.models import Base
from config.TestSettings import STestSettings
from src.repositories.laptop import LaptopRepository
from src.repositories.user import UserRepository
from src.repositories.user_activity import UserActivityRepository
from sqlalchemy.exc import (
	IntegrityError,
	OperationalError,
	DataError,
	SQLAlchemyError,
   ArgumentError
)

fake_engine = create_async_engine(STestSettings.test_pg_url, echo=True)
fake_async_session_maker = async_sessionmaker(fake_engine, expire_on_commit=False)


@pytest.fixture
def user():
    return {
        'name': 'Danila',
        'username': 'oovrkill',
        'email': 'ddanila@example.com',
        'password': '123'
    }

        
class FakeSQLAlchemyUoW:
    def __init__(self):
        self._session_factory = fake_async_session_maker

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        try:
            self._session = self._session_factory()
            self.users = UserRepository(self._session)
            self.laptops = LaptopRepository(self._session)
            self.user_activity = UserActivityRepository(self._session)
            return self
        except OperationalError as e:
            test_logger.error(f"OperationalError in SQLAlchemyUoW.__aenter__ (DB connection issue): {e}")
            raise DatabaseOperationalException

        except ArgumentError as e:
            test_logger.error(f"ArgumentError in SQLAlchemyUoW.__aenter__ (Session/Engine config issue): {e}")
            raise DatabaseConfigurationException

        except SQLAlchemyError as e:
            test_logger.error(f"Unhandled SQLAlchemyError in SQLAlchemyUoW.__aenter__: {e}")
            raise DatabaseException

        except Exception as e:
            test_logger.critical(f"Critical unexpected error in SQLAlchemyUoW.__aenter__: {e}")
            raise DatabaseException

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type is None:
                 await self.commit()

        except IntegrityError as e:
            await self.rollback()
            test_logger.error(f"An integrity error in SQLAlchemyUoW: {e}")
            raise DatabaseIntegrityException

        except DataError as e:
            await self.rollback()
            test_logger.error(f"Data error in SQLAlchemyUoW: {e}")
            raise DatabaseDataException

        except OperationalError as e:
            await self.rollback()
            test_logger.error(f"An operational error in SQLAlchemyUoW: {e}")
            raise DatabaseOperationalException

        except SQLAlchemyError as e:
            await self.rollback()
            test_logger.error(f"Unexpected SQLAlchemy error in SQLAlchemyUoW: {e}")
            raise DatabaseException

        except Exception as e:
            await self.rollback()
            test_logger.error(f"Unexpected error in SQLAlchemyUoW: {e}")
            raise DatabaseException


def get_test_uow():
    return FakeSQLAlchemyUoW()


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():

    app.dependency_overrides[SQLAlchemyUoW] = get_test_uow
    
    sync_url = STestSettings.test_pg_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
    from sqlalchemy import create_engine
    sync_engine = create_engine(sync_url)

    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)

    yield
    
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()
    
    app.dependency_overrides.clear()


@pytest.fixture(scope='function')
def client(setup_test_db):
    with TestClient(app) as test_client:
        yield test_client
        
@pytest.fixture
def get_cookies(client):
    def _get_cookies():
        return dict(client.cookies)
    return _get_cookies


@pytest.fixture
def http(client):
    
    def _perform_request(method, url, json):

        client_method = getattr(client, method.lower())

        if json is not None:
            res = client_method(url, json=json, follow_redirects=False)
        else:
            res = client_method(url, follow_redirects=False)
        return res

    def _http_request(method: str, url: str, json: dict = None, raises: bool = False):
        
        """
        Args:
            method (str): HTTP-метод (GET, POST, PUT, PATCH, DELETE).
            url (str): URL для запроса.
            json (dict, optional): Тело запроса в формате JSON. По умолчанию None.
            raises (bool, optional): Если True, оборачивает запрос в pytest.raises(HTTPException)
                                     и возвращает объект исключения (exc).
                                     Если False, возвращает объект ответа (res). По умолчанию False.
        Returns:
            res: Объект ответа, если raises=False.
            exc: Объект исключения от pytest.raises, если raises=True.
        """
        
        if raises:
            with pytest.raises(HTTPException) as exc:
                _perform_request(method, url, json)
            
            test_logger.error(
                f'Intended error at {url}, method = {method}, json = {json}, '
                f'response status is {exc.value.status_code}, response content is {exc.value.detail!r}\n'
            )
            return exc
        
        else:
            res = _perform_request(method, url, json)

            res.json = res.json()
            
            test_logger.info(
                f'Request to {url}, method = {method}, json = {json}, '
                f'response status is {res.status_code}, response content is {res.text!r}\n'
            )
            
            return res

    class HttpRequestHelpers:
        
        def get(self, url: str, raises: bool = False):
            return _http_request('GET', url, raises=raises)
        
        def post(self, url: str, json: dict = None, raises: bool = False):
            return _http_request('POST', url, json=json, raises=raises)
        
        def put(self, url: str, json: dict = None, raises: bool = False):
            return _http_request('PUT', url, json=json, raises=raises)
        
        def patch(self, url: str, json: dict = None, raises: bool = False):
            return _http_request('PATCH', url, json=json, raises=raises)
        
        def delete(self, url: str, json: dict = None, raises: bool = False):
            return _http_request('DELETE', url, json=json, raises=raises)
    
    return HttpRequestHelpers()