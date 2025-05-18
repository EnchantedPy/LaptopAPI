from typing import Any
from src.utils.UnitOfWork import S3UoW

class JsonDataService:
    async def put(self, uow: S3UoW, object_name: str, data: Any) -> Any:
        async with uow:
            result = await uow.json_data.put(object_name, data)
            return result

    async def get(self, uow: S3UoW, object_name: str) -> Any:
        async with uow:
            result = await uow.json_data.get(object_name)
            return result

    async def delete(self, uow: S3UoW, object_name: str) -> None:
        async with uow:
            result = await uow.json_data.delete(object_name)
            return result

    async def get_all(self, uow: S3UoW) -> list[str]:
        async with uow:
            result = await uow.json_data.get_all()
            return result
