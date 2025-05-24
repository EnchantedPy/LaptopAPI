from fastapi import HTTPException, Request, Response, status, APIRouter

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
from src.utils.logger import logger
from src.services.UserService import UserService
from config.settings import SAppSettings

auth = APIRouter(prefix='/auth', tags=['Auth'])


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
	user = await UserService().get_by_username(uow, data.username)
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

@auth.post('/logout')
async def logout(response: Response):
	response.delete_cookie('Bearer-token')
	response.delete_cookie('Refresh-token')
	return {'status': 'success'}

@auth.get('/users/me')
async def get_profile(request: Request):
     return {'payload': request.state.user_payload}

@auth.get('/admin/test')
async def test_admin_middleware():
     return {'msg': 'seems like you are admin'}

