from datetime import datetime
from typing import List
from src.utils.logger import logger
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.schemas.schemas import UserActivityAddSchema, UserActivityDeleteSchema
from models.models import UserActivityModel

class UserActivityService:
    async def add(self, uow: SQLAlchemyUoW, data: UserActivityAddSchema) -> None:
        async with uow:
            result = await uow.user_activity.add(data)
            return result

    async def get_by_user_id(self, uow: SQLAlchemyUoW, key: int) -> UserActivityModel:
        async with uow:
            result = await uow.user_activity.get_by_user_id(key)
            return result

    async def get_by_timestamp(self, uow: SQLAlchemyUoW, key: datetime) -> List[UserActivityModel]:
        async with uow:
            result = await uow.user_activity.get_by_timestamp(key)
            return result

    async def get_all(self, uow: SQLAlchemyUoW, offset: int = 0, limit: int = 10) -> List[UserActivityModel]:
        async with uow:
            result = await uow.user_activity.get_all(offset, limit)
            return result

    async def delete(self, uow: SQLAlchemyUoW, data: UserActivityDeleteSchema) -> None:
        async with uow:
            result = await uow.user_activity.delete(data)
            return result

    async def update(self) -> None:
        pass