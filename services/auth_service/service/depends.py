import jwt
from typing import Dict, Any, Optional
import os
from functools import singledispatch

# FastAPI
from fastapi import Depends, Request, HTTPException

# AuthX
#from .authx import configure_config

from config.settings import SAppSettings

#config = configure_config()

# Logger
from backend.src.utils.logger import laptop_logger

# Exceptions
from .exc import (
    AlreadyLoggedInException, NotAuthorizedUserException, InvalidTokenException
)


@singledispatch
async def extract_token(source) -> Optional[str]:
    raise NotImplementedError(f"Cannot extract token from object of type {type(source)}")

@extract_token.register
async def _(request: Request) -> Optional[str]:
    try:
        cookie_name = SAppSettings.jwt_cookie_name
        token = request.cookies.get(cookie_name)
        laptop_logger.info('Token extracted from Request.cookies')
        laptop_logger.debug(token)
        return token
    except Exception as e:
        laptop_logger.error(f'Error extracting token from Request: {e}')
        return None

@extract_token.register
async def _(cookies: dict) -> Optional[str]:
    try:
        cookie_name = SAppSettings.jwt_cookie_name
        token = cookies.get(cookie_name)
        laptop_logger.info('Token extracted from dict')
        return token
    except Exception as e:
        laptop_logger.error(f'Error extracting token from dict: {e}')
        return None
        

async def decode_jwt_token(token: str) -> Dict[str, Any]:
    secret_key = SAppSettings.jwt_secret_key
    laptop_logger.debug(f'{token} {secret_key}')
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        laptop_logger.info('Token successfully decoded')
        return payload
    
    except Exception as e:
        laptop_logger.error(f'Error decoding token: {e}')
        raise #TokenDecodeException
    

async def not_authorizied(request: Request) -> None:
    token = await extract_token(request)
    
    if token:
        laptop_logger.error('Auth check: User is already logged in')
        raise AlreadyLoggedInException
    return None


async def auth_required(request: Request) -> Dict[str, Any]:
    token = await extract_token(request)
    
    if not token:
        laptop_logger.error('Auth check: User is not authorizied')
        raise NotAuthorizedUserException
    
    payload = await decode_jwt_token(token)
    
    if payload:
        return payload
    
    laptop_logger.error('Some error with token')
    raise HTTPException(status_code=400, detail='Error with authorization token')


async def admin_required(user_data: Dict[str, Any] = Depends(auth_required)) -> Dict[str, Any]:

    role = user_data.get('role')
    laptop_logger.debug(f"Checking admin role. Extracted role: {role}")

    if role != "admin":
        laptop_logger.info(f'Admin rights check: User is not admin')
        raise HTTPException(
            status_code=403,
            detail="This route requires admin rights"
        ) #AdminRightsException

    return user_data