from typing import List, Optional
from src.interfaces.AbstractDatabase import DatabaseInterface
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.schemas import LaptopAddSchema, LaptopDeleteSchema, LaptopUpdateSchema, UserAddSchema, UserDeleteSchema, UserUpdateSchema, ActivityAddInternalSchema
from src.utils.logger import logger
from datetime import datetime
from src.entities.entities import Activity, User, Laptop, Activity


class UserPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session
        
    async def get_by_username(self, username: str) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.username == username)
        )
        result = await self._session.execute(query)
        db_user = result.scalars().first()

        if db_user:
            return User.model_validate(db_user)
        return None

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
        )
        result = await self._session.execute(query)
        db_user = result.scalars().first()

        if db_user:
            return User.model_validate(db_user)
        return None

    async def get_all(self, offset: int, limit: int) -> List[User]:
        query = (
            select(self.model)
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        db_users = result.scalars().all()

        return [User.model_validate(user) for user in db_users]
    

    async def add(self, data: UserAddSchema) -> None:
        new_user = self.model(
            username=data.username,
            hashed_password=data.password,
            email=data.email,
            active=True,
            role='user'
        )
        self._session.add(new_user)
        

    async def update(self, data: UserUpdateSchema) -> None:
        query = select(self.model).where(self.model.id == data.id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            if data.password:
                 user.hashed_password = data.hashed_password
            if data.email:
                user.email = data.email
            if data.username:
                user.username = data.username
        else:
            return None
        

    async def delete(self, data: UserDeleteSchema):
        query = select(self.model).where(self.model.id == data.id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        await self._session.delete(user)
        

class LaptopPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session  

    async def get_by_owner_id(self, user_id: int) -> Optional[Laptop]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        db_laptop = result.scalars().first()
        if db_laptop:
            return Laptop.model_validate(db_laptop)
        return None

    async def add(self, data: LaptopAddSchema) -> None:
        new_laptop = self.model(
            user_id=data.user_id,
            brand=data.brand,
            cpu=data.cpu,
            gpu=data.gpu,
            igpu=data.igpu,
            ram=data.ram,
            storage=data.storage,
            diagonal=data.diagonal,
            min_price=data.min_price,
            max_price=data.max_price
		  )
        self._session.add(new_laptop)
        

    async def update(self, data: LaptopUpdateSchema) -> None:
        query = select(self.model).where(self.model.user_id == data.user_id)
        result = await self._session.execute(query)
        laptop = result.scalar_one_or_none()
        
        if laptop:
            
            if data.brand:
                laptop.brand = data.brand
            if data.cpu:
                laptop.cpu = data.cpu
            if data.gpu:
                laptop.gpu = data.gpu
            if data.igpu:
                laptop.igpu = data.igpu
            if data.ram:
                laptop.ram = data.ram
            if data.storage:
                laptop.storage = data.storage
            if data.diagonal:
                laptop.diagonal = data.diagonal
            if data.min_price:
                laptop.min_price = data.min_price
            if data.max_price:
                laptop.max_price = data.max_price
            
        else:
            return None
        

    async def delete(self, data: LaptopDeleteSchema) -> None:
        query = select(self.model).where(self.model.user_id == data.user_id)
        result = await self._session.execute(query)
        laptop = result.scalar_one_or_none()
        await self._session.delete(laptop)



class ActivityPostgresRepository(DatabaseInterface):
    model = None

    def __init__(self, _session: AsyncSession):
        self._session = _session

    async def get_list_by_owner_id(self, user_id: int, offset: int, limit: int) -> List[Activity]:
        query = select(self.model).where(self.model.user_id == user_id).limit(limit).offset(offset)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [Activity.model_validate(db_activity) for db_activity in db_activities]


    async def get_by_timestamp(self, timestamp: datetime, limit: int, offset: int):
        query = select(self.model).where(self.model.timestamp == timestamp).limit(limit).offset(offset)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [Activity.model_validate(db_activity) for db_activity in db_activities]


    async def get_all(self, offset: int, limit: int) -> List[Activity]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self._session.execute(query)
        db_activities = result.scalars().all()
        return [Activity.model_validate(db_activity) for db_activity in db_activities]


    async def add(self, data: ActivityAddInternalSchema):
        new_activity = self.model(
            user_id=data.user_id,
            detail=data.detail,
            timestamp=data.timestamp
        )
        self._session.add(new_activity)


    async def update(self) -> ...:
        raise NotImplemented('User activity doesn\'t have an update method')


    async def delete(self) -> ...:
        raise NotImplemented('User activity doesn\'t have a delete method')




	

