from datetime import datetime
from typing import List
from src.core.exceptions.exceptions import ActivityNotFoundException, UserNotFoundException
from src.entities.entities import UserActivity
from src.utils.logger import logger
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.schemas.schemas import UserActivityAddSchema, UserActivityDeleteSchema
from models.models import UserActivityModel

class UserActivityService:
    async def add(self, uow: SQLAlchemyUoW, data: UserActivityAddSchema) -> None:
        async with uow:
            user = await uow.users.get_by_id(data.user_id)
            if not user:
                raise UserNotFoundException(f'User with ID {data.user_id} not found')
            result = await uow.user_activity.add(data)
            return result

    async def get_by_user_id(self, uow: SQLAlchemyUoW, user_id: int, limit: int = 20, offset: int = 0) -> List[UserActivity]:
        async with uow:
            user_owner = await uow.users.get_by_id(user_id)
            if not user_owner:
                raise UserNotFoundException(f'User with ID {user_id} not found')
            result = await uow.user_activity.get_list_by_owner_id(user_id, offset, limit)
            return result

    async def get_by_timestamp(self, uow: SQLAlchemyUoW, timestamp: datetime, limit: int = 20, offset: int = 0) -> List[UserActivity]:
        async with uow:
            result = await uow.user_activity.get_by_timestamp(timestamp)
            return result

    async def get_all(self, uow: SQLAlchemyUoW, offset: int = 0, limit: int = 20) -> List[UserActivityModel]:
        async with uow:
            result = await uow.user_activity.get_all(offset, limit)
            return result

    async def delete(self, uow: SQLAlchemyUoW, data: UserActivityDeleteSchema) -> None:
        async with uow:
            user_owner = await uow.users.get_by_id(data.user_id)
            if not user_owner:
                raise UserNotFoundException(f'User with ID {data.user_id} not found')
            activity = await uow.user_activity.get_by_id_and_owner_id(data.user_id, data.activity_id)
            if not activity:
                raise ActivityNotFoundException(f'Activity with ID {data.activity_id} for user with ID {data.user_id} not found')
            result = await uow.user_activity.delete(data)
            return result

    async def update(self) -> None:
        raise NotImplemented('User activity doesn\'t have an update method')