from typing import List, Optional, Type
from src.core.interfaces.AbstractDatabase import ReadRepository, WriteRepository, FullRepository
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.logger import logger
from src.infrastructure.db.models import UserOrm, LaptopOrm


class UserRepository(FullRepository):
    
    def __init__(self, _session: AsyncSession, model: Type[UserOrm]):
        self._session = _session
        self.model = model

    async def get_by_id(self, user_id: int) -> UserOrm | None:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def get_all(self, offset: int, limit: int, only_active: bool) -> List[UserOrm]:
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
        

class LaptopRepository(FullRepository):
    
    def __init__(self, _session: AsyncSession, model: Type[LaptopOrm]):
        self._session = _session
        self.model = model 

    async def get_by_id(self, user_id: int) -> LaptopOrm | None:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def add(self, laptop_data: dict) -> None:
        new_laptop = self.model(
            **laptop_data
		  )
        self._session.add(new_laptop)
        
    async def update(self, user_id, update_data: dict) -> None:
        query = update(self.model).where(self.model.user_id == user_id).values(**update_data)
        await self._session.execute(query)
        

    async def delete(self, user_id: int) -> None:
        query = delete(self.model).where(self.model.user_id == user_id)
        await self._session.execute(query)

	

