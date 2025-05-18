import json
import os
from typing import List, Optional, Tuple
import aiohttp
import aiofiles

# FastAPI & Pydantic
from fastapi import APIRouter, Request, Security
import jwt
from pydantic import BaseModel
from sqlalchemy import select

# Exceptions
from backend.database_restart import LaptopTemplateModel, SessionDep, UserModel
from custom_exceptions import (
    LaptopConfigurationException,
    LaptopRequestException,
    NoLaptopsFoundException,
    NoSavedLaptopConfigException,
    NotAuthorizedUserException,
    UserNotFoundException,
)

# External API requester
from requester import collect_data, filter_by_something, save_filtered_products

# Local modules
from authorization_routes import auth_required, config

# Logger
from logging_system import custom_logger

laptop_router = APIRouter()

last_config: Optional[Tuple[List[str], List[str], List[str], int, int]] = None


# ['acer'] ['core i7'] ['geforce rtx 4060'] 20000.0 60000.0


class LaptopSchema(BaseModel):
    brand: str
    cpu: str
    gpu: str
    price_range: list[int, int]


import os
import json
import aiohttp
import aiofiles

from typing import List, Optional
from fastapi import APIRouter, Request, Security
from sqlalchemy import select
import jwt

# Local imports
from backend.database_restart import SessionDep, UserModel, LaptopTemplateModel
from authorization_routes import auth_required, config
from custom_exceptions import (
    LaptopRequestException,
    NoLaptopsFoundException,
    NotAuthorizedUserException,
    UserNotFoundException,
    NoSavedLaptopConfigException
)
from requester import collect_data, filter_by_something
from logging_system import custom_logger


@laptop_router.post('/process_laptop', tags=['Laptop Routes'], dependencies=[Security(auth_required)])
async def process_laptop(request: Request, session: SessionDep):
    try:
        # Extract token from cookies
        token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
        custom_logger.info('Token extracted from cookies')

        if not token:
            custom_logger.info('No token provided for protected route')
            raise NotAuthorizedUserException

        # Decode token and find user
        try:
            secret_key = config.JWT_SECRET_KEY or os.environ.get("JWT_SECRET_KEY", "secret")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            username = payload["username"]

            # Find the user
            query = select(UserModel).where(UserModel.name == username)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                custom_logger.error(f'User {username} not found in database')
                raise UserNotFoundException

            custom_logger.info(f'User {username} found in database')

            # Find the user's last laptop template
            template_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user.id)
            template_result = await session.execute(template_query)
            template = template_result.scalar_one_or_none()

            if not template:
                custom_logger.error('No saved laptop template found')
                raise NoSavedLaptopConfigException
            custom_logger.info(f'Found saved laptop config for user {username}')

            # Parse the JSON template data
            template_data = json.loads(template.template_data)

            # Extract filtering parameters
            brand = template_data['brand']
            cpu = template_data['cpu']
            gpu = template_data['gpu']
            min_price = template_data['min_price']
            max_price = template_data['max_price']

            # Collect and filter laptops
            custom_logger.info('Collecting data from source...')
            try:
                products = await collect_data()
            except aiohttp.ClientError as e:
                custom_logger.exception('Network error while collecting data')
                raise LaptopRequestException from e
            except Exception as e:
                custom_logger.exception('Unexpected error while collecting data')
                raise LaptopRequestException from e

            custom_logger.info('Filtering products...')
            filtered_products = await filter_by_something(products, brand, cpu, gpu, min_price, max_price)

            # Save results
            if filtered_products:

                if not isinstance(filtered_products, str):
                    filtered_products = json.dumps(filtered_products, indent=4, ensure_ascii=False)
                    custom_logger.info('Formatted results to json')

                async with aiofiles.open(f'storage/{user.id}_result.json', "w", encoding="utf-8") as f:
                    custom_logger.info(f'Opened {f.name}')
                    await f.write(filtered_products)

                custom_logger.info(f'Successfully saved filtered products, {len(json.loads(filtered_products))}')

                return {
                    "status": "success",
                    "message": f"Найдено {len(json.loads(filtered_products))} ноутбуков с заданными характеристиками"
                }
            else:
                custom_logger.error('No products found with provided properties')
                raise NoLaptopsFoundException

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            custom_logger.error('Invalid or expired token')
            raise NotAuthorizedUserException

    except Exception as e:
        custom_logger.error(f'Error in process_laptop: {str(e)}')
        raise


@laptop_router.get('/get_last_config', summary='Get Last Configuration', tags=['Laptop Routes'],
                   dependencies=[Security(auth_required)])
async def get_last_config(session: SessionDep, request: Request):
    try:
        # Extract token from cookies
        token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

        if not token:
            custom_logger.info('No token provided for protected route')
            raise NotAuthorizedUserException

        # Decoding
        secret_key = config.JWT_SECRET_KEY or os.environ.get("JWT_SECRET_KEY", "secret")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload["username"]

        # Find the user
        query = select(UserModel).where(UserModel.name == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            custom_logger.error(f'User {username} not found in database')
            raise UserNotFoundException

        # Find the user's last laptop template
        template_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user.id)
        template_result = await session.execute(template_query)
        template = template_result.scalar_one_or_none()

        if not template:
            custom_logger.info('No saved laptop template found for user')
            raise NoSavedLaptopConfigException

        # Parse the JSON template data
        template_data = json.loads(template.template_data)

        # Convert back to the expected tuple format
        last_config = (
            template_data['brand'],
            template_data['cpu'],
            template_data['gpu'],
            template_data['min_price'],
            template_data['max_price']
        )

        custom_logger.info('Returned last laptop template')
        return last_config

    except NoSavedLaptopConfigException:
        # This exception is already defined in your custom exceptions
        raise
    except Exception as e:
        custom_logger.error(f'Error in get_last_config: {str(e)}')
        raise LaptopConfigurationException


@laptop_router.post('/configure_laptop', summary='Configure Laptop Route', tags=['Laptop Routes'],
                    dependencies=[Security(auth_required)])
async def configure_laptop(
        request: Request,
        data: LaptopSchema,
        session: SessionDep
):
    try:
        # Extract token from cookies
        token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

        if not token:
            custom_logger.info('No token provided for protected route')
            raise NotAuthorizedUserException

        # Decoding
        secret_key = config.JWT_SECRET_KEY or os.environ.get("JWT_SECRET_KEY", "secret")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload["username"]

        # Find the user
        query = select(UserModel).where(UserModel.name == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            custom_logger.error(f'User {username} not found in database')
            raise UserNotFoundException

        # Prepare template data
        global last_config

        brand = [data.brand]
        cpu = [data.cpu]
        gpu = [data.gpu]
        min_price = data.price_range[0]
        max_price = data.price_range[1]

        last_config = (brand, cpu, gpu, min_price, max_price)
        custom_logger.info(last_config)

        # Convert template to JSON string
        template_json = json.dumps({
            'brand': brand,
            'cpu': cpu,
            'gpu': gpu,
            'min_price': min_price,
            'max_price': max_price
        })
        custom_logger.info(template_json)

        # Create or update laptop template for the user
        # First, remove any existing templates for this user
        del_query = select(LaptopTemplateModel).where(LaptopTemplateModel.user_id == user.id)
        existing_templates = await session.execute(del_query)
        for template in existing_templates.scalars():
            await session.delete(template)

        # Create new template
        new_template = LaptopTemplateModel(
            user_id=user.id,
            template_data=template_json
        )
        session.add(new_template)
        await session.commit()

        custom_logger.info('New laptop template created and saved')

        return {
            "status": "success",
            "data": last_config
        }
    except Exception as e:
        custom_logger.error(f'Error in configure_laptop: {str(e)}')
        raise LaptopConfigurationException