# Standart libararies
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List

# FastAPI
from fastapi import Depends, FastAPI, status

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr
from .models import Base, UserModel, LaptopTemplateModel
from .schemas import UserAddSchema, LaptopSchema

# Logger
from backend.src.utils.logger import laptop_logger

# Exceptions
from .exc import DatabaseException, create_exception_handler


# Settings
from config.settings import SAppSettings



engine = create_async_engine(SAppSettings.db_url, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def with_session(func):
    async def wrapper(*args, **kwargs):
         async with SessionLocal() as session:
              laptop_logger.debug('Sqlalchemy created a new session in wrapper')
              return await func(*args, session=session, **kwargs)
    return wrapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    laptop_logger.info('Starting Database service')

    try:
        laptop_logger.info('Setting up the database...')

        '''
        Optional[Commented] to not drop all tables after restarting app
        '''

        async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.drop_all)
             await conn.run_sync(Base.metadata.create_all)


        laptop_logger.debug('Database successfully set up')
        yield

    except SQLAlchemyError as e:
        laptop_logger.error(f"Database setup failed: {e}")
        raise DatabaseException("Error setting up the database")

    finally:
        pass



db_service_holder = FastAPI(lifespan=lifespan, title='Database Service')

db_service_holder.add_exception_handler(
        DatabaseException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Database error"
            }
        )
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        laptop_logger.debug('Sqlalchemy created a new session')
        async with SessionLocal() as session:
            yield session
    except SQLAlchemyError as e:
        laptop_logger.error(f"Error creating a new session: {e}")
        raise DatabaseException('Error creating a new session')



'''DB Managing USERS'''

@with_session
async def verify_user_credentials(username: str, password: str, session: AsyncSession) -> Dict:
    try:
          query = select(UserModel).where(
					 UserModel.name == username,
					 UserModel.password == password
				)
          result = await session.execute(query)
          user = result.scalar_one_or_none()
          if user:
                    laptop_logger.info(f"User {username} verified successfully")
                    return {
                    'id': user.id,
						  'name': user.name,
					 }
          
          else:
                    laptop_logger.error(f"Invalid credentials for user {username}")
                    return None
          
    except SQLAlchemyError as e:
          laptop_logger.error(f"Error verifying user credentials: {e}")
          return None

@with_session
async def add_user(data: UserAddSchema, session: AsyncSession):
    try:
        new_user = UserModel(
            name=data.name,
            password=data.password,
            email=data.email
        )
        session.add(new_user)
        await session.commit()

        laptop_logger.info(f"User {data.name} added to database")
        return {'status': 'success'}

    except SQLAlchemyError as e:
        laptop_logger.error(f"Error adding user to DB: {e}")
        return None


@with_session
async def delete_user(
          id: int, session: AsyncSession):
    try:
        user_to_delete = await session.execute(
            select(UserModel).filter(UserModel.id == id)
        )
        user = user_to_delete.scalar_one_or_none()

        if user:
            await session.delete(user)
            await session.commit()
            laptop_logger.info(f'User with id {id} was deleted')
            return {'status': 'success'}
        
        else:
            laptop_logger.error('User to delete not found')
            return None

    except SQLAlchemyError as e:
        laptop_logger.error(f"Error deleting user from DB: {e}")
        return None
    

@with_session
async def update_user_sensitive_data(user_id: int, new_password: str | None, new_email: EmailStr | None, session: AsyncSession):
    if new_password is None and new_email is None:
        laptop_logger.error('No new sensitive data provided for user update')
        return None
    try:
        user_to_update = await session.execute(
            select(UserModel).filter(UserModel.id == user_id)
        )
        user = user_to_update.scalar_one_or_none()

        if user:
            if new_password:
                 user.password = new_password
            elif new_email:
                user.email = new_email
            await session.commit()

            laptop_logger.info(f'User sensitive data updated. User id: {user_id}')
            return {'status': 'success'}
        
        else:
            laptop_logger.error('User to update sensitive data not found')
            return None

    except SQLAlchemyError as e:
        laptop_logger.error(f"Error updating user in DB: {e}")
        return None


@with_session
async def update_username(user_id: int, new_name: str, session: AsyncSession):
    try:
         user_to_update = await session.execute(
             select(UserModel).filter(UserModel.id == user_id)
                          )
         user = user_to_update.scalar_one_or_none()
         
         if user:
                    user.name = new_name
                    await session.commit()
                    laptop_logger.info(f'User name updated. User id: {user_id}')
                    return {'status': 'success'}
         
         else:
              laptop_logger.error('User to update not found')
              return None
         
    except SQLAlchemyError as e:
        laptop_logger.error(f"Error updating user in DB: {e}")
        return None


@with_session
async def get_all_users(session: AsyncSession, limit: int = 100, offset: int = 0) -> List[dict]:
    try:

        result = await session.execute(select(UserModel).limit(limit).offset(offset))
        users = result.scalars().all()

        laptop_logger.debug(f"Extracted {len(users)} users from database")
        return users

    except SQLAlchemyError as e:
        laptop_logger.error(f"Error retrieving users from DB: {e}")
        return None

    
@with_session
async def check_data_coincidence(user_id: int, new_data: str, data_type: str, session: AsyncSession):
        result = await get_user_by_id(user_id, session)
        if not result:
            return None
        
        if data_type == 'password':
            user_password = result.get('password')
            if new_data == user_password:
                return True
            return False
        
        elif data_type == 'email':
            user_email = result.get('email')
            if new_data == user_email:
                return True
            return False
        
        else:
            return None
    

@with_session
async def get_user_by_id(id: int, session: AsyncSession) -> Dict:
    try:
        query = select(UserModel).where(UserModel.id == id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            laptop_logger.error(f'User with ID {id} not found')
            return None

        return {
            'name': user.name,
            'email': user.email,
            'password': user.password
        }

    except SQLAlchemyError as e:
        laptop_logger.info(f'Error when trying to access user info: {e}')
        return None


'''DB managing LAPTOPS'''


# accessed by laptop_service
# @db_service_holder.post('/laptop_template_add/{user_id}')
@with_session
async def add_laptop_template(user_id: int, data: LaptopSchema, session: AsyncSession):
    try:
        existing_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user_id)
        existing_templates = await session.execute(existing_query)
        existing_template = existing_templates.scalar_one_or_none()

        if existing_template:
            await session.delete(existing_template)
            laptop_logger.info(f"Existing laptop template for user {user_id} deleted before adding new one")

        template_json = json.dumps({
            'brand': data.brand,
            'cpu': data.cpu,
            'gpu': data.gpu,
            'price_range': data.price_range
        })

        laptop_logger.info(f"Creating new laptop template for user {user_id}: {template_json}")

        new_template = LaptopTemplateModel(
            user_id=user_id,
            template_data=template_json
        )
        session.add(new_template)
        await session.commit()

        laptop_logger.info(f"New laptop template added for user {user_id}: {template_json}")

        return {
            'status': 'success',
            'message': f"Laptop template added for user {user_id}"
        }

    except SQLAlchemyError as e:
        laptop_logger.error(f"Unexpected error while adding new laptop template: {e}")
        raise DatabaseException


# route, coz accessed from UI, Bad idea (isolated service)
@with_session
#@db_service_holder.get('/get_laptop_template/{user_id}')
async def get_laptop_template(user_id: int, session: AsyncSession) -> Dict:
    try:
        template_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user_id)
        template_result = await session.execute(template_query)
        template = template_result.scalar_one_or_none()

        if not template:
            laptop_logger.error(f'No saved laptop template found for user {user_id}')
            return None

        laptop_logger.info(f'Found saved laptop config for user {user_id}')

        template_data = json.loads(template.template_data)

        return {
            'brand': template_data.get('brand'),
            'cpu': template_data.get('cpu'),
            'gpu': template_data.get('gpu'),
            'price_range': template_data.get('price_range')
        }

    except SQLAlchemyError as e:
        laptop_logger.error(f"Error when trying to access user's laptop template: {e}")
        raise DatabaseException


# accessed by laptop_service
# @db_service_holder.delete('/laptop_template_delete/{user_id}')
@with_session
async def delete_laptop_template(user_id: int, session: AsyncSession):
    try:

        del_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user_id)
        existing_templates = await session.execute(del_query)
        template_to_delete = existing_templates.scalar_one_or_none()

        if not template_to_delete:
            laptop_logger.error(f'No saved laptop template found for user {user_id}')
            return None

        await session.delete(template_to_delete)
        await session.commit()

        laptop_logger.info(f'Laptop template deleted for user {user_id}')

        return {
            'status': 'success',
            'message': f'Laptop template deleted for user {user_id}'
        }
    
    except SQLAlchemyError as e:
        laptop_logger.error(f"Unexpected error while deleting laptop template: {e}")
        raise DatabaseException