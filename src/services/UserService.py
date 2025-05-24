from src.schemas.schemas import UserAddSchema, UserDeleteSchema, UserUpdateSchema
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger
from src.core.auth_service.utils import hash_password


class UserService:

	async def add(self, uow: SQLAlchemyUoW, data: UserAddSchema):
		data.password = hash_password(data.password)
		async with uow:
			result = await uow.users.add(data)
			return result
		
	async def get_all(self, uow: SQLAlchemyUoW):
		async with uow:
			result = await uow.users.get_all()
			return result
		
	async def get_by_name(self, uow: SQLAlchemyUoW, value: str):
		async with uow:
			result = await uow.users.get_by_name(value)
			return result
		
	async def get_by_username(self, uow: SQLAlchemyUoW, value: str):
		async with uow:
			result = await uow.users.get_by_username(value)
			return result
		
	async def get_by_id(self, uow: SQLAlchemyUoW, value: int):
		async with uow:
			result = await uow.users.get_by_id(value)
			logger.info(result)
			return result
		
	async def update(self, uow: SQLAlchemyUoW, data: UserUpdateSchema):
		async with uow:
			result = await uow.users.update(data)
			return result
		
	async def delete(self, uow: SQLAlchemyUoW, data: UserDeleteSchema):
		async with uow:
			result = await uow.users.delete(data)
			return result