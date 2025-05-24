from typing import Any, List, Optional, Type
from src.interfaces.AbstractDatabase import DatabaseInterface
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from functools import singledispatchmethod
from src.models.models import UserModel, LaptopTemplateModel, UserActivityModel
from src.schemas.schemas import LaptopAddSchema, LaptopDeleteSchema, LaptopUpdateSchema, UserAddSchema, \
    UserDeleteSchema, UserUpdateSchema, UserActivityAddSchema, UserActivityDeleteSchema
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from src.utils.logger import logger
from src.models.models import Base
from datetime import datetime
from src.entities.entities import User
from sqlalchemy.orm import joinedload


def handle_exc(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexdected error in {func.__name__}: {e}")
            raise e
    return wrapper


class UserPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session
        
    @handle_exc
    async def get_by_username(self, value: str, offset: int = 0, limit: int = 10) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.username == value)
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

    @handle_exc
    async def get_by_name(self, value: str) -> List[User]:
        query = (
            select(self.model)
            .where(self.model.name == value)
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

    @handle_exc
    async def get_by_id(self, value: int) -> Optional[User]:
        query = (
            select(self.model)
            .where(self.model.id == value)
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

    @handle_exc
    async def get_all(self, offset: int = 0, limit: int = 10) -> List[User]:
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
    
    @handle_exc
    async def add(self, data: UserAddSchema):
        new_user = self.model(
            name=data.name,
            username=data.username,
            hashed_password=data.password,
            email=data.email,
            active=True
        )
        self._session.add(new_user)
        
    @handle_exc
    async def update(self, data: UserUpdateSchema):
        query = select(self.model).where(self.model.id == data.user_id)
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
        
    @handle_exc
    async def delete(self, data: UserDeleteSchema):
        query = select(self.model).where(self.model.id == data.user_id)
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            await self._session.delete(user)
        else:
            return None
        
    


class LaptopPostgresRepository(DatabaseInterface):
    model = None
    
    def __init__(self, _session: AsyncSession):
        self._session = _session
        
    @handle_exc
    async def get_by_owner_id(self, value: int) -> LaptopTemplateModel:
        query = select(self.model).where(self.model.user_id == value)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    @handle_exc
    async def get_all(self):
        query = select(self.model)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    @handle_exc
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
        
    @handle_exc
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
        
    @handle_exc
    async def delete(self, data: LaptopDeleteSchema):
        query = select(self.model).where(
    		(self.model.user_id == data.user_id) & (self.model.id == data.laptop_id)
			)
        result = await self._session.execute(query)
        laptop_template = result.scalar_one_or_none()
        
        if laptop_template:
            await self._session.delete(laptop_template)
        else:
            return None


class UserActivityPostgresRepository(DatabaseInterface):
    model = None

    def __init__(self, _session: AsyncSession):
        self._session = _session

    @handle_exc
    async def get_by_user_id(self, value: int) -> Any:
        query = select(self.model).where(self.model.user_id == value)
        result = await self._session.execute(query)
        return result.scalars().all()

    @handle_exc
    async def get_by_timestamp(self, value: datetime):
        query = select(self.model).where(self.model.timestamp == value)
        result = await self._session.execute(query)
        return result.scalars().all()

    @handle_exc
    async def get_all(self, offset: int = 0, limit: int = 10) -> Any:
        query = select(self.model).offset(offset).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    @handle_exc
    async def add(self, data: UserActivityAddSchema):
        new_user_activity = self.model(
            user_id=data.user_id,
            action=data.action,
            timestamp=data.timestamp,
            detail=data.detail
        )
        self._session.add(new_user_activity)

    @handle_exc
    async def update(self, data: Any):
        pass

    @handle_exc
    async def delete(self, data: UserActivityDeleteSchema):
        query = select(self.model).where((self.model.user_id == data.user_id) & (self.model.id == data.activity_id))
        result = await self._session.execute(query)
        activity = result.scalar_one_or_none()

        if activity:
            await self._session.delete(activity)
        else:
            return None




	

