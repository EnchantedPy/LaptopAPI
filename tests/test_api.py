from typing import Annotated, Any, AsyncGenerator
from fastapi import Depends
import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.core.dependencies.dependencies import SqlUoWDep
from src.models.models import Base
from httpx import AsyncClient, ASGITransport
from config.TestSettings import STestSettings
from src.repositories.laptop import LaptopRepository
from src.repositories.user import UserRepository
from src.repositories.user_activity import UserActivityRepository
from src.utils.logger import logger
from src.utils.UnitOfWork import SQLAlchemyUoW, SQLAlchemyUoWInterface


logger.info(STestSettings.model_dump())
logger.info(STestSettings.test_pg_url)
test_engine = create_async_engine(STestSettings.test_pg_url, echo=True)
test_async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
        
class TestSQLAlchemyUoW:
	def __init__(self, 
				  ):
		self._session_factory = test_async_session_maker

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
			await self.commit()
		except Exception as e:
			await self.rollback()
			logger.error(f"Unexdected error in test SQLAUoW: {e}")

@pytest.fixture(autouse=True, scope="session")
async def setup_test_db():
	app.dependency_overrides[SQLAlchemyUoW] = TestSQLAlchemyUoW

	async with test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)

	yield
	
	async with test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
	app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(setup_test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_auth_middleware(client):
    res = await client.post('/auth/register', json={
        'name': 'Danila',
        'username': 'ovrkill',
        'email': 'danila@example.com',
        'password': '123'
    })
    assert res.status_code == 200
    
    res = await client.post('/auth/login/user', json={
        'name': 'Danila',
        'password': '123'
	 })
    assert res.json == {'status': 'success'}
    
    res = await client.get('/auth/users/me')
    assert res.get('payload').get('role') == 'user'
