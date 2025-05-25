from abc import ABC, abstractmethod
from redis.asyncio import Redis, from_url
from src.core.exceptions.exceptions import DatabaseDataException, DatabaseConfigurationException, DatabaseException, DatabaseIntegrityException, DatabaseOperationalException, S3ClientException, S3ConnectionException, S3Exception, S3NoCredentialsException, S3ParameterValidationException
from src.db.realtional_db import async_session_maker
from src.repositories.user import UserRepository
from src.repositories.laptop import LaptopRepository
from aiobotocore.session import get_session
from src.s3.s3_client_factory import s3_client_maker
from src.repositories.jsondata import JsonDataRepository
from src.repositories.user_activity import UserActivityRepository
from src.utils.logger import logger
from sqlalchemy.exc import (
	IntegrityError,
	OperationalError,
	DataError,
	SQLAlchemyError,
   ArgumentError
)

from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    EndpointConnectionError,
    ParamValidationError,
    BotoCoreError
)


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
        try:
            self._client_context = await self._client_factory()
            self._client = await self._client_context.__aenter__()
            self.json_data = JsonDataRepository(self._client)
            return self
        except NoCredentialsError as e:
            logger.error(f"No credentials error in S3UoW during __aenter__: {e}")
            raise S3NoCredentialsException

        except EndpointConnectionError as e:
            logger.error(f"Endpoint connection error in S3UoW during __aenter__: {e}")
            raise S3ConnectionException

        except BotoCoreError as e:
            logger.error(f"Botocore error during S3UoW __aenter__: {e}")
            raise S3Exception

        except Exception as e:
            logger.critical(f"Critical unexpected error in S3UoW during __aenter__: {e}", exc_info=True)
            raise S3Exception

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            if self._client_context:
                await self._client_context.__aexit__(exc_type, exc_value, exc_tb)

        except ClientError as e:
            logger.error(f"Client error in S3UoW: {e}")
            raise S3ClientException

        except NoCredentialsError as e:
            logger.error(f"No credentials error in S3UoW: {e}")
            raise S3NoCredentialsException

        except EndpointConnectionError as e:
            logger.error(f"Endpoint connection error in S3UoW: {e}")
            raise S3ConnectionException

        except ParamValidationError as e:
            logger.error(f"Param validation error in S3UoW: {e}")
            raise S3ParameterValidationException

        except BotoCoreError as e:
            logger.error(f"Unexpected S3 error occurred: {e}")
            raise S3Exception

        except Exception as e:
            logger.critical(f"Critical unexpected error in S3UoW: {e}")
            raise S3Exception




class SQLAlchemyUoW:
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
            self.user_activity = UserActivityRepository(self._session)
            return self
        except OperationalError as e:
            logger.error(f"OperationalError in SQLAlchemyUoW.__aenter__ (DB connection issue): {e}")
            raise DatabaseOperationalException

        except ArgumentError as e:
            logger.error(f"ArgumentError in SQLAlchemyUoW.__aenter__ (Session/Engine config issue): {e}")
            raise DatabaseConfigurationException

        except SQLAlchemyError as e:
            logger.error(f"Unhandled SQLAlchemyError in SQLAlchemyUoW.__aenter__: {e}")
            raise DatabaseException

        except Exception as e:
            logger.critical(f"Critical unexpected error in SQLAlchemyUoW.__aenter__: {e}")
            raise DatabaseException

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        try:
            await self.commit()

        except IntegrityError as e:
            await self.rollback()
            logger.error(f"An integrity error in SQLAlchemyUoW: {e}")
            raise DatabaseIntegrityException

        except DataError as e:
            await self.rollback()
            logger.error(f"Data error in SQLAlchemyUoW: {e}")
            raise DatabaseDataException

        except OperationalError as e:
            await self.rollback()
            logger.error(f"An operational error in SQLAlchemyUoW: {e}")
            raise DatabaseOperationalException

        except SQLAlchemyError as e:
            await self.rollback()
            logger.error(f"Unexpected SQLAlchemy error in SQLAlchemyUoW: {e}")
            raise DatabaseException

        except Exception as e:
            await self.rollback()
            logger.error(f"Unexpected error in SQLAlchemyUoW: {e}")
            raise DatabaseException