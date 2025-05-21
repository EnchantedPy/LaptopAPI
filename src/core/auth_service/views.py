from fastapi import HTTPException, middleware, FastAPI, Request, Response, status
from typing import Awaitable, Callable
from fastapi.responses import JSONResponse
from src.core.auth_service.utils import (
	create_access_token,
	create_refresh_token,
	validate_password,
	hash_password,
	decode_jwt
)
from src.schemas.schemas import UserAddSchema, UserLoginSchema
from src.services.UserService import UserService
from src.core.dependencies.dependencies import SqlUoWDep
from jwt.exceptions import InvalidTokenError
from src.utils.logger import logger
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.services.UserService import UserService

auth = FastAPI(title='Auth Service')

def get_sqla_uow() -> SQLAlchemyUoW:
	return SQLAlchemyUoW

@auth.middleware('http')
async def check_auth_middleware(
	request: Request,
	response: Response,
	call_next: Awaitable | Callable
) -> None:
	access_token = request.cookies.get('Bearer-token')
	refresh_token = request.cookies.get('Refresh-token')
	if access_token:
		try:
			payload = decode_jwt(access_token)
		except InvalidTokenError as e:
			logger.error('Error: Invalid access token')
			raise
		response = await call_next(request)
	elif refresh_token:
		try:
			payload = decode_jwt(refresh_token)
			user_id = payload.get('sub')
			uow = get_sqla_uow()
			async with uow:
				user = await uow.users.get_by_id(user_id)
				new_access_token = create_access_token(user)
		except InvalidTokenError as e:
			logger.error('Error: Invalid refresh token')
			raise
	else:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail = 'Error: No refresh and access tokens'
		)

	return response
		

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
