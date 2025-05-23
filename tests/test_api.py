import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.models.models import Base
from config.TestSettings import STestSettings
from src.repositories.laptop import LaptopRepository
from src.repositories.user import UserRepository
from src.repositories.user_activity import UserActivityRepository
from src.utils.logger import test_logger
from src.utils.UnitOfWork import SQLAlchemyUoW

# https://claude.ai/chat/ecb821c3-0879-4d31-8b81-83af4dd1e602


test_logger.info(STestSettings.model_dump())
test_logger.info(STestSettings.test_pg_url)
fake_engine = create_async_engine(STestSettings.test_pg_url, echo=True)
fake_async_session_maker = async_sessionmaker(fake_engine, expire_on_commit=False)

        
class FakeSQLAlchemyUoW:
    def __init__(self):
        self._session_factory = fake_async_session_maker

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.laptops = LaptopRepository(self._session)
        self.user_activity = UserActivityRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        except Exception as e:
            await self.rollback()
            test_logger.error(f"Unexpected error in test SQLAlchemyUoW: {e}")
        finally:
            if self._session:
                await self._session.close()


def get_test_uow():
    return FakeSQLAlchemyUoW()


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():

    app.dependency_overrides[SQLAlchemyUoW] = get_test_uow
    
    sync_url = STestSettings.test_pg_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
    from sqlalchemy import create_engine
    sync_engine = create_engine(sync_url, echo=True)

    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)

    yield
    
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()
    
    app.dependency_overrides.clear()


@pytest.fixture
def client(setup_test_db):
    with TestClient(app) as test_client:
        yield test_client
        
@pytest.fixture
def get_cookies(client):
    def _get_cookies():
        return dict(client.cookies)
    return _get_cookies


def test_auth_middleware(client, get_cookies):

    res = client.post('/auth/register', json={
        'name': 'Danila',
        'username': 'ovrkill',
        'email': 'danila@example.com',
        'password': '123'
    })
    test_logger.info(f"Register response: {res.status_code}, {res.text}")
    assert res.status_code == 200
    

    res = client.post('/auth/login/user', json={
        'name': 'Danila',
        'password': '123'
    })
    test_logger.info(f"Login response: {res.status_code}, {res.text}")
    assert res.status_code == 200
    response_data = res.json()
    assert response_data.get('status') == 'success'
    
    res = client.get('/auth/users/me')
    test_logger.info(f"User info response: {res.status_code}, {res.text}")
    assert res.status_code == 200
    response_data = res.json()
    assert response_data.get('payload', {}).get('role') == 'user'
    cookies = get_cookies()
    assert cookies.get('Bearer-token') != None
    assert cookies.get('Refresh-token') != None
    
    res = client.get('/auth/logout')
    test_logger.info(f"User info response: {res.status_code}, {res.text}")
    assert res.status_code == 200
    cookies = get_cookies()
    assert len(cookies) == 0