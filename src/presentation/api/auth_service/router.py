from fastapi import HTTPException, Request, Response, status, APIRouter

from src.presentation.api.auth_service.utils import (
	create_access_token,
	create_refresh_token,
	validate_password,
	hash_password,
	decode_jwt,
   create_admin_access_token,
   create_admin_refresh_token
)

from src.presentation.dto.schemas import AdminLoginSchema, UserAddSchema, UserLoginSchema
from src.application.services.UserService import UserService
from src.presentation.dependencies import UoWDep
from src.utils.logger import logger
from config.settings import Settings

AuthRouter = APIRouter(prefix='/auth', tags=['Auth'])


'''
/login/user
/login/admin
/logout
/register
'''


@AuthRouter.post('/register')
async def register(data: UserAddSchema, uow: UoWDep):
	await UserService().add(uow, data)
	return {'status': 'success'}


@AuthRouter.post('/login/user')
async def login_user(data: UserLoginSchema, uow: UoWDep, response: Response):
	user = await UserService().get_by_username(uow, data.username)
	if not validate_password(data.password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
	access_token = create_access_token(user)
	refresh_token = create_refresh_token(user)
	response.set_cookie('Bearer-token', access_token)
	response.set_cookie('Refresh-token', refresh_token)
	return {'status': 'success'}


@AuthRouter.post('/login/admin')
async def login_user(data: AdminLoginSchema, response: Response):
	if not data.password == Settings.admin_password and not data.name == Settings.admin_name and not data.admin_secret == Settings.admin_secret:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
	access_token = create_admin_access_token()
	refresh_token = create_admin_refresh_token()
	response.set_cookie('Bearer-token', access_token)
	response.set_cookie('Refresh-token', refresh_token)
	return {'status': 'success'}

@AuthRouter.post('/logout')
async def logout(response: Response):
	response.delete_cookie('Bearer-token')
	response.delete_cookie('Refresh-token')
	return {'status': 'success'}

@AuthRouter.get('/users/me')
async def get_profile(request: Request):
     return {'payload': request.state.user_payload}

@AuthRouter.get('/admin/test')
async def test_admin_middleware():
     return {'msg': 'seems like you are admin'}

