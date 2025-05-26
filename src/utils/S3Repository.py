from functools import wraps
from io import BytesIO
import json
from typing import Any
from src.interfaces.AbstractStorage import StorageInterface
from aiobotocore.client import AioBaseClient
from botocore.exceptions import BotoCoreError
from src.utils.logger import logger
from src.utils.helpers import json_to_dict


class S3Repository(StorageInterface):
    bucket_name = None

    def __init__(self, _client: AioBaseClient):
        self._client = _client

    async def put(self, object_name: str, data: Any) -> None:
         json_bytes = json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')
         byte_stream = BytesIO(json_bytes)
         
         await self._client.put_object(Bucket=self.bucket_name, Key=object_name, Body=byte_stream)
    
    async def get(self, object_name: str) -> Any:
        response = await self._client.get_object(Bucket=self.bucket_name, Key=object_name)
        raw_bytes = await response['Body'].read()
        data = raw_bytes.decode('utf-8')
        dict_data = await json_to_dict(data)
        return dict_data

    async def delete(self, object_name: str) -> None:
        await self._client.delete_object(Bucket=self.bucket_name, Key=object_name)

    async def get_all(self) -> list[str]:
        keys = []
        continuation_token = None

        while True:
            params = {
                "Bucket": self.bucket_name,
                "MaxKeys": 20,
            }

            if continuation_token:
                params["ContinuationToken"] = continuation_token

            response = await self._client.list_objects_v2(**params)
            contents = response.get("Contents", [])
            keys.extend(obj["Key"] for obj in contents)

            if response.get("IsTruncated"):
                continuation_token = response.get("NextContinuationToken")
            else:
                break

        return keys
