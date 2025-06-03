from typing import Any
from src.utils.UnitOfWork import S3UoW
from io import BytesIO
import json

class S3Service:
	 def __init__(self, repository: S3Repository):
        self._repository = repository

    async def save_json(self, object_name: str, data: dict) -> None:
		 await self._repository.put(object_name, json.dumps(data).encode('utf-8'))

    async def get(self, uow: S3UoW, object_name: str) -> Any:
        async with uow:
            result = await uow.s3.get(object_name)
				data = result.decode('utf-8')
				dict_data = json.loads(data)
				return dict_data

    async def delete(self, uow: S3UoW, object_name: str) -> None:
        async with uow:
            result = await uow.json_data.delete(object_name)
            return result
