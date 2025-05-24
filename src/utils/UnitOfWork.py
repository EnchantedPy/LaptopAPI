from abc import ABC, abstractmethod
from redis.asyncio import Redis, from_url
from src.core.exceptions.exceptions import DatabaseError
from src.db.realtional_db import async_session_maker
from src.repositories.user import UserRepository
from src.repositories.laptop import LaptopRepository
from aiobotocore.session import get_session
from src.s3.s3_client_factory import s3_client_maker
from src.repositories.jsondata import JsonDataRepository
from src.repositories.user_activity import UserActivityRepository
from src.utils.logger import logger


class S3UoWInterface(ABC):
	@abstractmethod
	async def __aenter__(self):
		...

	@abstractmethod
	async def __aexit__(self, exc_type, exc_value, exc_tb):
		...


class SQLAlchemyUoWInterface(ABC):

	@abstractmethod
	async def __aenter__(self):
		...

	@abstractmethod
	async def __aexit__(self, exc_type, exc_value, exc_tb):
		...

	@abstractmethod
	async def commit(self):
		...
		
	@abstractmethod
	async def rollback(self):
		...


class S3UoW:
	def __init__(self):
		self._client_factory = s3_client_maker
	
	async def __aenter__(self):
		self._client_context = await self._client_factory()
		self._client = await self._client_context.__aenter__()
		self.json_data = JsonDataRepository(self._client)
		return self
	
	async def __aexit__(self, exc_type, exc_value, exc_tb):
		await self._client_context.__aexit__(exc_type, exc_value, exc_tb)


class SQLAlchemyUoW:
	def __init__(self, 
				  ):
		self._session_factory = async_session_maker

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
			logger.error(f"Unexdected error in SQLAUoW: {e}")
			raise DatabaseError