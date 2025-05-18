# Standard Library
import uuid
import datetime
from typing import Any, Dict
import secrets

# Third Party
import jwt
from fastapi import FastAPI, Request, Security, Response, HTTPException
from aiokafka.errors import KafkaError

# Internal Modules
from backend.src.utils.logger import laptop_logger
from config.settings import SAppSettings

# Auth Ecosystem
from .schemas import RegiesterUserSchema, LoginUserSchema
from .depends import decode_jwt_token, not_authorizied, auth_required, admin_required, extract_token
from .exc import (
    AdminCredsException,
    UserCredsException,
    RegiesterException,
    InvalidTokenException,
    add_all_auth_exceptions
)

# Integrations
from etc.cache import wait_for_response

# Kafka
from services.auth_service.kafka.producer import auth_kafka_producer



auth_service_holder = FastAPI(title="Authorization Service")

add_all_auth_exceptions(auth_service_holder)


@auth_service_holder.post(
    '/register',
    summary='Registration Route',
    tags=['General Routes'],
    dependencies=[Security(not_authorizied)]
)
async def add_user(data: RegiesterUserSchema) -> dict:
    try:
        request_id = str(uuid.uuid4())
        topic_key = 'user_registration'
        message = {'request_id': request_id, 'data': data.model_dump()}
        laptop_logger.info(message)
        async with auth_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info('Message sent to Kafka')
        response = await wait_for_response(request_id)
        if response == 'valid':
            return {'status': 'success'}
    except Exception as e:
        laptop_logger.error(f"Error in Kafka producer: {e}")
        raise RegiesterException


@auth_service_holder.post(
    '/admin_login',
    tags=['Authorization'],
    dependencies=[Security(not_authorizied)]
)
async def admin_login(creds: LoginUserSchema, response: Response) -> Dict[str, Any]:
    admin_name = SAppSettings.admin_name
    admin_password = SAppSettings.admin_password

    if creds.username == admin_name and creds.password == admin_password:
        payload = {
            'sub': '1209',
            'role': 'admin',
            'username': creds.username,
            'jti': secrets.token_hex(16),
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.now(datetime.UTC)
        }

        token = jwt.encode(payload, SAppSettings.jwt_secret_key, algorithm="HS256")
        laptop_logger.info('Admin token created')

        response.set_cookie(SAppSettings.jwt_cookie_name, token)
        return {
            'access_token': token,
            'user_info': {
                'role': 'admin'
            }
        }
    else:
        laptop_logger.error('Admin name or password is incorrect')
        raise AdminCredsException


@auth_service_holder.post(
    '/user_login',
    tags=['Authorization'],
    dependencies=[Security(not_authorizied)]
)
async def user_login(creds: LoginUserSchema, response: Response, request: Request) -> Dict[str, Any]:
    request_id = str(uuid.uuid4())
    message = {'request_id': request_id, 'data': creds.model_dump()}
    topic_key = 'user_logging_in'
    
    try:
        async with auth_kafka_producer as producer:
            await producer.send_message(topic_key, message)
            laptop_logger.info(f"Login request sent to Kafka with request_id: {request_id}")

        response_data = await wait_for_response(request_id)
        laptop_logger.info(f"Response from cache in auth: {response_data}")

        if response_data.get('name') and response_data.get('id'):
            user_name = response_data.get('name')
            user_id = response_data.get('id')
            
            payload = {
                'sub': str(user_id),
                'role': 'user',
                'username': user_name,
                'jti': secrets.token_hex(16),
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30),
                'iat': datetime.datetime.now(datetime.UTC)
            }

            token = jwt.encode(payload, SAppSettings.jwt_secret_key, algorithm="HS256")
            response.set_cookie(SAppSettings.jwt_cookie_name, token)

            laptop_logger.info(f'Login successful for user: {user_name}')

            return {
                'access_token': token,
                'user_info': {
                    'name': user_name,
                    'id': user_id
                }
            }
        else:
            laptop_logger.warning(f"Invalid login credentials for request_id: {request_id}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        laptop_logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@auth_service_holder.post(
    '/logout',
    tags=['Authorization'],
    dependencies=[Security(auth_required)]
)
async def logout(response: Response) -> Dict[str, Any]:
    try:
        response.delete_cookie(
            key=SAppSettings.jwt_cookie_name,
            path='/',
            secure=SAppSettings.jwt_secure,
            httponly=True
        )

        laptop_logger.info('Someone successfully logged out')

        return {
            'status': 'success',
            'message': 'You logged out'
        }
    except Exception as e:
        laptop_logger.error(f'Unexpected error during logout: {e}')
        raise InvalidTokenException