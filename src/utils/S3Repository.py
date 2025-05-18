from functools import wraps
from io import BytesIO
import json
from typing import Any
from src.interfaces.AbstractStorage import StorageInterface
from aiobotocore.client import AioBaseClient
from botocore.exceptions import BotoCoreError
from src.utils.logger import logger
from src.utils.helpers import json_to_dict


def handle_exc(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BotoCoreError as e:
            logger.error(f"AioBotoCore error in {func.__name__}: {e}")
            return e  # _test_ for adding middleware later
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return e  # _test_ for adding middleware later
    return wrapper


class S3JsonDataRepository(StorageInterface):
    bucket_name = None

    def __init__(self, _client: AioBaseClient):
        self._client = _client

    @handle_exc
    async def put(self, object_name: str, data: Any) -> None:
         json_bytes = json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')
         byte_stream = BytesIO(json_bytes)
         
         await self._client.put_object(Bucket=self.bucket_name, Key=object_name, Body=byte_stream)
    

    @handle_exc
    async def get(self, object_name: str) -> Any:
        response = await self._client.get_object(Bucket=self.bucket_name, Key=object_name)
        raw_bytes = await response['Body'].read()
        data = raw_bytes.decode('utf-8')
        dict_data = await json_to_dict(data)
        return dict_data

    @handle_exc
    async def delete(self, object_name: str) -> None:
        await self._client.delete_object(Bucket=self.bucket_name, Key=object_name)

    @handle_exc
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
