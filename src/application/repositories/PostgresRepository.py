from typing import List, Optional
from src.interfaces.AbstractDatabase import ReadRepository, WriteRepository, FullRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.schemas import LaptopAddSchema, LaptopDeleteSchema, LaptopUpdateSchema, UserAddSchema, UserDeleteSchema, UserUpdateSchema, ActivityAddInternalSchema
from src.utils.logger import logger
from datetime import datetime
from src.entities.entities import Activity, User, Laptop, Activity


class UserPostgresRepository(FullRepository):
    
    def __init__(self, _session: AsyncSession, model: Type[UserModel]):
        self._session = _session
		  self.model = model

    async def get_by_id(self, user_id: int) -> User | None:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_all(self, offset: int, limit: int, only_active: bool) -> List[User]:
		query = select(self.model)

		if only_active:
			 query = query.where(self.model.is_active == True)

		query = query.limit(limit).offset(offset)
		result = await self._session.execute(query)
		return result.scalars().all()
    
    async def add(self, user_data: dict) -> None:
        new_user = self.model(
            **user_data
        )
        self._session.add(new_user)
        
    async def update(self, user_id, update_data: dict) -> None:
        query = update(self.model).where(self.model.id == user_id).values(**update_data)
        await self._session.execute(query)
        

    async def delete(self, user_id: int) -> None:
        query = delete(self.model).where(self.model.id == user_id)
        await self._session.execute(query)
        

class LaptopPostgresRepository(FullRepository):
    
    def __init__(self, _session: AsyncSession, model: Type[LaptopModel]):
        self._session = _session
        self.model = model 

    async def get_by_id(self, user_id: int) -> Optional[Laptop]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def add(self, laptop_data: dict) -> None:
        new_laptop = self.model(
            **data
		  )
        self._session.add(new_laptop)
        
    async def update(self, user_id, update_data: dict) -> None:
        query = update(self.model)
        .where(self.model.user_id == user_id)
        .values(**update_data)
		  await self._session.execute(query)
        

    async def delete(self, user_id: int) -> None:
        query = delete(self.model).where(self.model.user_id == user_id)
        await self._session.execute(query)


class ActivityPostgresRepository(ReadRepository, WriteRepository):

    def __init__(self, _session: AsyncSession, model: Type[ActivityModel]):
        self.model = model
        self._session = _session

    async def get_by_id(self, user_id: int, offset: int, limit: int) -> List[Activity]:
        query = select(self.model).where(self.model.user_id == user_id).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_all(self, offset: int, limit: int) -> List[Activity]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def add(self, activity_data: dict):
        new_activity = self.model(
            **activity_data
        )
        self._session.add(new_activity)




	

