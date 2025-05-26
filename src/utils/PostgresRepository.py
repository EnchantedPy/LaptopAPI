from typing import Any, List, Optional
from src.interfaces.AbstractDatabase import DatabaseInterface
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.schemas import LaptopAddSchema, LaptopDeleteSchema, LaptopUpdateSchema, UserAddSchema, UserDeleteSchema, UserUpdateSchema, UserActivityAddSchema, UserActivityDeleteSchema
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from src.utils.logger import logger
from datetime import datetime
from src.entities.entities import User, Laptop, UserActivity
from sqlalchemy.orm import joinedload


class UserPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session
        
    async def get_by_username(self, username: str, offset: int = 0, limit: int = 10) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.username == username)
            .limit(limit)
            .offset(offset)
            .options(
                joinedload(self.model.laptop_templates),
                joinedload(self.model.user_activity)
            )
        )
        result = await self._session.execute(query)
        db_user = result.scalars().unique().first()

        if db_user:
            return User.model_validate(db_user)
        return None


    async def get_by_name(self, name: str) -> List[User]:
        query = (
            select(self.model)
            .where(self.model.name == name)
            .options(
                joinedload(self.model.laptop_templates),
                joinedload(self.model.user_activity)
            )
        )
        result = await self._session.execute(query)
        db_users = result.scalars().unique().all()

        if db_users:
            return [User.model_validate(db_user) for db_user in db_users]
        return None


    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(
                joinedload(self.model.laptop_templates),
                joinedload(self.model.user_activity)
            )
        )
        result = await self._session.execute(query)
        db_user = result.scalars().unique().first()

        if db_user:
            return User.model_validate(db_user)
        return None


    async def get_all(self, offset: int, limit: int) -> List[User]:
        query = (
            select(self.model)
            .limit(limit)
            .offset(offset)
            .options(
                joinedload(self.model.laptop_templates),
                joinedload(self.model.user_activity)
            )
        )
        result = await self._session.execute(query)
        db_users = result.scalars().unique().all()

        return [User.model_validate(user) for user in db_users]
    

    async def add(self, data: UserAddSchema):
        new_user = self.model(
            name=data.name,
            username=data.username,
            hashed_password=data.password,
            email=data.email,
            active=True
        )
        self._session.add(new_user)
        

    async def update(self, data: UserUpdateSchema):
        query = select(self.model).where(self.model.id == data.id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            if data.password:
                 user.password = data.password
            if data.email:
                user.email = data.email
            if data.name:
                user.name = data.name
            if data.username:
                user.username = data.username
        else:
            return None
        

    async def delete(self, data: UserDeleteSchema):
        query = select(self.model).where(self.model.id == data.user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
      #   if user:
      #       await self._session.delete(user)
      #   else:
      #       return None
        await self._session.delete(user)
        
    


class LaptopPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session
        
    async def get_list_by_owner_id(self, user_id: int) -> List[Laptop]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        db_laptops =  result.scalars().all()
        return [Laptop.model_validate(laptop) for laptop in db_laptops]
    

    async def get_by_id_and_owner_id(self, user_id: int, laptop_id: int) -> Optional[Laptop]:
        query = select(self.model).where((self.model.user_id == user_id) & (self.model.id == laptop_id))
        result = await self._session.execute(query)
        db_laptop = result.scalars().first()
        if db_laptop:
            return User.model_validate(db_laptop)
        return None
    

    async def get_all(self, limit: int, offset: int) -> List[Laptop]:
        query = (
            select(self.model)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        db_laptops =  result.scalars().all()
        return [Laptop.model_validate(laptop) for laptop in db_laptops]
    

    async def add(self, data: LaptopAddSchema):
        new_laptop = self.model(
            user_id=data.user_id,
            brand=data.brand,
            cpu=data.cpu,
            gpu=data.gpu,
            min_price=data.min_price,
            max_price=data.max_price
		  )
        self._session.add(new_laptop)
        

    async def update(self, data: LaptopUpdateSchema):
        query = select(self.model).where(
    		(self.model.user_id == data.user_id) & (self.model.id == data.laptop_id)
			)
        result = await self._session.execute(query)
        laptop_template = result.scalar_one_or_none()
        
        if laptop_template:
            
            if data.brand:
                laptop_template.brand = data.brand
            if data.cpu:
                laptop_template.cpu = data.cpu
            if data.gpu:
                laptop_template.gpu = data.gpu
            if data.min_price:
                laptop_template.min_price = data.min_price
            if data.max_price:
                laptop_template.max_price = data.max_price
            
        else:
            return None
        

    async def delete(self, data: LaptopDeleteSchema):
        query = select(self.model).where(
    		(self.model.user_id == data.user_id) & (self.model.id == data.laptop_id)
			)
        result = await self._session.execute(query)
        laptop_template = result.scalar_one_or_none()
        
      #   if laptop_template:
      #       await self._session.delete(laptop_template)
      #   else:
      #       return None
        await self._session.delete(laptop_template)


class UserActivityPostgresRepository(DatabaseInterface):
    model = None

    def __init__(self, _session: AsyncSession):
        self._session = _session


    async def get_list_by_owner_id(self, user_id: int, offset: int, limit: int) -> List[UserActivity]:
        query = select(self.model).where(self.model.user_id == user_id).limit(limit).offset(offset)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [UserActivity.model_validate(db_activity) for db_activity in db_activities]
    

    async def get_by_id_and_owner_id(self, user_id: int, activity_id: int):
        query = select(self.model).where((self.model.id == activity_id) & (self.model.user_id == user_id))
        result = await self._session.execute(query)
        db_activity = result.scalars().first()
        if db_activity:
            return UserActivity.model_validate(db_activity)
        return None


    async def get_by_timestamp(self, timestamp: datetime, limit: int, offset: int):
        query = select(self.model).where(self.model.timestamp == timestamp).limit(limit).offset(offset)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [UserActivity.model_validate(db_activity) for db_activity in db_activities]


    async def get_all(self, offset: int, limit: int) -> Any:
        query = select(self.model).offset(offset).limit(limit)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [UserActivity.model_validate(db_activity) for db_activity in db_activities]


    async def add(self, data: UserActivityAddSchema):
        new_user_activity = self.model(
            user_id=data.user_id,
            action=data.action,
            timestamp=data.timestamp,
            detail=data.detail
        )
        self._session.add(new_user_activity)


    async def update(self, data: Any):
        raise NotImplemented('User activity doesn\'t have an update method')


    async def delete(self, data: UserActivityDeleteSchema):
        query = select(self.model).where((self.model.user_id == data.user_id) & (self.model.id == data.activity_id))
        result = await self._session.execute(query)
        activity = result.scalar_one_or_none()

      #   if activity:
      #       await self._session.delete(activity)
      #   else:
      #       return None
        await self._session.delete(activity)




	

