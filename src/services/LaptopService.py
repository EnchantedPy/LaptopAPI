from src.schemas.schemas import LaptopAddSchema, LaptopUpdateSchema, LaptopDeleteSchema
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger


class LaptopService:
	async def add(self, uow: SQLAlchemyUoW, data: LaptopAddSchema):
		async with uow:
			result = await uow.laptops.add(data)
			return result
		
	async def get_all(self, uow: SQLAlchemyUoW):
		async with uow:
			result = await uow.laptops.get_all()
			return result
		
	async def get_one_or_multiple(self, uow: SQLAlchemyUoW, value: int):
		async with uow:
			result = await uow.laptops.get_one_or_multiple(value)
			return result
		
	async def update(self, uow: SQLAlchemyUoW, data: LaptopUpdateSchema):
		async with uow:
			result = await uow.laptops.update(data)
			return result
		
	async def delete(self, uow: SQLAlchemyUoW, data: LaptopDeleteSchema):
		async with uow:
			result = await uow.laptops.delete(data)
			return result