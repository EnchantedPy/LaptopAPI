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
    "/openapi.json",
    "/login/admin"
]

ADMIN_PATHS = [
    "/admin/test",
]

async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    path = request.url.path

    # 1. Проверка на публичный путь
    if path in PUBLIC_PATHS:
        logger.debug(f"Path {path} is public. Skipping authentication.")
        return await call_next(request)

    access_token = request.cookies.get('Bearer-token')
    refresh_token = request.cookies.get('Refresh-token')

    current_payload: Optional[TokenPayload] = None
    new_access_token: Optional[str] = None

    # 2. Проверка на админский путь
    if path in ADMIN_PATHS:
        if not access_token:
            logger.warning(f"Admin path {path} accessed without access token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authentication required for admin access.'
            )
        try:
            current_payload = decode_jwt(access_token)
            # Проверяем роль
            if current_payload.get('role') != 'admin':
                logger.warning(f"User {current_payload.get('sub')} attempted admin access to {path} without admin role.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Access denied. Admin privileges required.'
                )
            logger.debug(f"Admin access token valid for user {current_payload['sub']} to {path}.")
            
        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.warning(f"Admin access token invalid or expired for {path}: {e}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Authentication required for admin access. Token invalid or expired: {e}'
            )

    # 3. Если путь не админский и не публичный, то это обычный авторизованный путь
    else: # Path is not public and not admin-specific, implies general authenticated access
        # Порядок проверки: Access Token -> Refresh Token -> Отказ

        # 3.1. Проверка Access Token
        if access_token:
            try:
                current_payload = decode_jwt(access_token)
                logger.debug(f"Access token valid for user {current_payload.get('sub')}.")

            except ExpiredSignatureError:
                logger.warning("Access token expired. Attempting to refresh using refresh token.")

            except InvalidTokenError as e:
                logger.warning(f"Invalid access token ({e}). Attempting to refresh using refresh token.")

        # 3.2. Если Access Token недействителен/отсутствует, но есть Refresh Token
        if not current_payload and refresh_token:
            try:
                payload = decode_jwt(refresh_token)
                user_id = payload.get('sub')

                uow = get_sqla_uow()
                async with uow:
                    user = await uow.users.get_by_id(user_id)
                    new_access_token = create_access_token(user)
                    current_payload = decode_jwt(new_access_token)
                    logger.info(f"Access token refreshed for user {current_payload.get('sub')}.")
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

    # 4. Если после всех попыток payload всё ещё нет
    if not current_payload:
        logger.warning(f"No valid tokens found for path {path}. Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required. No valid tokens found.'
        )

    request.state.user_id = current_payload['sub']
    request.state.user_payload = current_payload
    request.state.user_role = current_payload.get('role')

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

@auth.get('/admin/test')
async def test_admin_middleware():
     return {'msg': 'seems like you are admin'}

