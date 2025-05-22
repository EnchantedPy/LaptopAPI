from fastapi import HTTPException, middleware, FastAPI, Request, Response, status
from typing import Awaitable, Callable, Optional
from jwt import ExpiredSignatureError
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.auth_service.utils import (
	create_access_token,
	create_refresh_token,
	validate_password,
	hash_password,
	decode_jwt,
   create_admin_access_token,
   create_admin_refresh_token
)
from src.schemas.schemas import AdminLoginSchema, UserAddSchema, UserLoginSchema
from src.services.UserService import UserService
from src.core.dependencies.dependencies import SqlUoWDep
from jwt.exceptions import InvalidTokenError
from src.utils.logger import logger
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.services.UserService import UserService
from src.entities.entities import TokenPayload
from config.settings import SAppSettings

auth = FastAPI(title='Auth Service')

def get_sqla_uow() -> SQLAlchemyUoW:
	return SQLAlchemyUoW()

PUBLIC_PATHS = [
    "/login/user",
    "/logout",
    "/register",
    "/docs",
    "/redoc",
    "/openapi.json"
]

async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    
    if request.url.path in PUBLIC_PATHS:
        logger.debug(f"Path {request.url.path} is public. Skipping authentication.")
        return await call_next(request)
    
    access_token = request.cookies.get('Bearer-token')
    refresh_token = request.cookies.get('Refresh-token')
    
    current_payload: Optional[TokenPayload] = None
    new_access_token: Optional[str] = None

    # Порядок проверки: Access Token -> Refresh Token -> Отказ

    # 1. Проверка Access Token
    if access_token:
        try:
            current_payload = decode_jwt(access_token)
            logger.debug(f"Access token valid for user {current_payload['sub']}.")

        except ExpiredSignatureError:
            logger.warning("Access token expired. Attempting to refresh using refresh token.")

        except InvalidTokenError as e:
            logger.warning(f"Invalid access token ({e}). Attempting to refresh using refresh token.")
            
    # 2. Если Access Token недействителен/отсутствует, но есть Refresh Token
    if not current_payload and refresh_token:
        payload = decode_jwt(refresh_token)
        user_id = payload.get('sub')
        try:
            uow = get_sqla_uow()
            async with uow:
                user = await uow.users.get_by_id(user_id)
                new_access_token = create_access_token(user, admin=False)
                current_payload = decode_jwt(new_access_token)
                logger.info(f"Access token refreshed for user {current_payload['sub']}.")
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Authentication required. Failed to refresh token: {e}'
            )
        except Exception as e:
            logger.error(f"Unexpected error during refresh token processing: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Internal server error during refreshing access token'
            )

    # 3. Если после всех попыток payload всё ещё нет
    if not current_payload:
        logger.warning("No valid tokens found. Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required. No valid tokens found.'
        )

    # Если мы дошли до этого места, значит, у нас есть действительный payload
    request.state.user_id = current_payload['sub']
    request.state.user_payload = current_payload

    response = await call_next(request)

    if new_access_token:
        response.set_cookie(
            key="Bearer-token",
            value=new_access_token,
            httponly=True,
            samesite="lax",
            # secure=True,
            max_age=SAppSettings.access_token_expire_minutes * 60
        )
        logger.debug("New access token set in response cookie.")

    return response


auth.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)

'''
/login/user
/login/admin
/logout
/register
'''


@auth.post('/register')
async def register(data: UserAddSchema, uow: SqlUoWDep):
	await UserService().add(uow, data)
	return {'status': 'success'}


@auth.post('/login/user')
async def login_user(data: UserLoginSchema, uow: SqlUoWDep, response: Response):
	user = await UserService().get_by_name(uow, data.name)
	if not validate_password(data.password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
	access_token = create_access_token(user)
	refresh_token = create_refresh_token(user)
	response.set_cookie('Bearer-token', access_token)
	response.set_cookie('Refresh-token', refresh_token)
	return {'status': 'success'}


@auth.post('/login/admin')
async def login_user(data: AdminLoginSchema, response: Response):
	if not data.password == SAppSettings.admin_password and not data.name == SAppSettings.admin_name and not data.admin_secret == SAppSettings.admin_secret:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
	access_token = create_admin_access_token()
	refresh_token = create_admin_refresh_token()
	response.set_cookie('Bearer-token', access_token)
	response.set_cookie('Refresh-token', refresh_token)
	return {'status': 'success'}

@auth.get('/logout')
async def logout():
	pass

@auth.get('/users/me')
async def get_profile(request: Request):
     return {'payload': request.state.user_payload}

