from fastapi import APIRouter, Request
from src.core.dependencies.dependencies import SqlUoWDep
from src.schemas.schemas import UserUpdateRequestSchema, UserUpdateInternalSchema
from src.services.UserService import UserService

AccountRouter = APIRouter(prefix='/account', tags=['Account'])

'''
/account/self GET
/account/self/update PATCH
/account/delete DELETE
/account/activity GET
/account/laptops GET
'''

@AccountRouter.get('/self')
async def get_profile(request: Request, uow: SqlUoWDep):
	user_id = request.state.user_id
	user = await UserService().get_by_id(uow, user_id)
	return user.model_dump(exclude={'id', 'active', 'laptop_templates', 'user_activity'})

@AccountRouter.patch('/self/update')
async def change_username(request: Request, uow: SqlUoWDep, data: UserUpdateRequestSchema):
	user_id = request.state.user_id
	user_update_dict = data.model_dump()
	user_update_dict['id'] = user_id
	user_update_schema = UserUpdateInternalSchema(**user_update_dict)
	await UserService().update(uow, user_update_schema)
	return {'status': 'success'}


