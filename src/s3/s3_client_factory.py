from contextlib import asynccontextmanager
from typing import AsyncGenerator
from aiobotocore.session import get_session
from config.settings import SAppSettings
from aiobotocore.client import AioBaseClient
from contextlib import _AsyncGeneratorContextManager


class s3_clientmaker:
	def __init__(self, s3_config: dict, _bucket_name: str):
		self.config = s3_config

		self._bucket_name = _bucket_name
		self.session = get_session()

	@asynccontextmanager
	async def get_client(self):
		async with self.session.create_client('s3',  **self.config) as client:
			yield client

	async def __call__(self) -> _AsyncGeneratorContextManager[AioBaseClient]:
		 return self.get_client()

s3_client_maker = s3_clientmaker(SAppSettings.s3_config, SAppSettings.s3_bucket_name)