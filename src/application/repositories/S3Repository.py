import json
from typing import Any
from src.core.interfaces.AbstractStorage import FullRepository
from aiobotocore.client import AioBaseClient
from src.utils.logger import logger
from config.settings import Settings

class S3Repository(FullRepository):
    bucket_name = Settings.s3_bucket_name

    def __init__(self, _client: AioBaseClient):
        self._client = _client

    async def put(self, key: str, data: bytes) -> None:
         await self._client.put_object(Bucket=self.bucket_name, Key=key, Body=data)
    
    async def get(self, object_name: str) -> Any:
          response = await self._client.get_object(Bucket=self.bucket_name, Key=object_name)
          return await response['Body'].read()

    async def delete(self, object_name: str) -> None:
        await self._client.delete_object(Bucket=self.bucket_name, Key=object_name)
