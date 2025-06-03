from abc import ABC, abstractmethod
from src.core.exceptions.exceptions import DatabaseDataException, DatabaseConfigurationException, DatabaseException, DatabaseIntegrityException, DatabaseOperationalException, S3ClientException, S3ConnectionException, S3Exception, S3NoCredentialsException, S3ParameterValidationException
from src.db.db import async_session_maker
from src.core.repositories.user import UserRepository
from src.core.repositories.laptop import LaptopRepository
from src.core.repositories.activity import ActivityRepository
from src.utils.logger import logger
from sqlalchemy.exc import (
	IntegrityError,
	OperationalError,
	DataError,
	SQLAlchemyError,
   ArgumentError
)
from typing import Self


class IUnitOfWork(ABC):

	@abstractmethod
	async def __aenter__(self) -> Self:
		...

	@abstractmethod
	async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
		...

	@abstractmethod
	async def commit(self) -> None:
		...
		
	@abstractmethod
	async def rollback(self) -> None:
		...


class UnitOfWork:
    def __init__(self):
        self._session_factory = async_session_maker

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        try:
            self._session = self._session_factory()
            self.users = UserRepository(self._session)
            self.laptops = LaptopRepository(self._session)
            self.user_activity = ActivityRepository(self._session)
            return self
		  except Exception:
			await self._session.close()
			raise

    async def __aexit__(self, exc_type, exc_value, exc_tb):
		try:
			if exc_type is None:
				await self.commit()
			else:
				await self._session.rollback()
		finally:
			await self._session.close()