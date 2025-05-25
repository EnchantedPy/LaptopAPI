from src.schemas.schemas import LaptopAddSchema, LaptopUpdateSchema, LaptopDeleteSchema
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger
from src.core.exceptions.exceptions import LaptopNotFoundException, LaptopTemplatesLimitException, NoChangesProvidedException, UserNotFoundException


class LaptopService:
	async def add(self, uow: SQLAlchemyUoW, data: LaptopAddSchema):
		async with uow:
			user = uow.users.get_by_id(data.user_id)
			if not user:
				raise UserNotFoundException(f'User not found with ID {data.user_id}')
			user_laptops = await uow.laptops.get_by_owner_id(data.user_id)
			if len(user_laptops) == 3:
				raise LaptopTemplatesLimitException('You have maximum number of laptop templates saved')
			result = await uow.laptops.add(data)
			return result
		
	async def get_all(self, uow: SQLAlchemyUoW, offset: int = 20, limit: int = 0):
		async with uow:
			result = await uow.laptops.get_all()
			return result
		
	async def get_list_for_user(self, uow: SQLAlchemyUoW, user_id: int):
		async with uow:
			user_owner = await uow.users.get_by_id(user_id)
			if not user_owner:
				raise UserNotFoundException(f'User not found with ID {user_id}')
			result = await uow.laptops.get_list_by_owner_id(user_id)
			return result
		
	async def get_exact(self, uow: SQLAlchemyUoW, user_id: int, laptop_id: int):
		async with uow:
			user_owner = await uow.users.get_by_id(user_id)
			if not user_owner:
				raise UserNotFoundException(f'User not found with ID {user_id}')
			laptop = await uow.laptops.get_by_id_and_owner_id(user_id, laptop_id)
			if not laptop:
				raise LaptopNotFoundException(f'No laptop with ID {laptop_id} found for user with ID {user_id}')
			return laptop
		
	async def update(self, uow: SQLAlchemyUoW, data: LaptopUpdateSchema):
		async with uow:

			user_owner = await uow.users.get_by_id(data.user_id)
			if not user_owner:
				logger.warning(f"Update attempt for laptop with non-existent owner ID: {data.user_id}")
				raise UserNotFoundException(f'User not found with ID {data.user_id}')

			existing_laptop_full_model = await uow.laptops.get_by_id_and_owner_id(data.user_id, data.laptop_id)

			if not existing_laptop_full_model:
				raise LaptopNotFoundException(f'No laptop with ID {data.laptop_id} found for user with ID {data.user_id}')
			
			update_data_dict = data.model_dump(exclude_unset=True, exclude={'user_id', 'laptop_id'})

			if not update_data_dict:
				logger.info(f"Update request for laptop ID {data.laptop_id} received, but no updatable fields provided.")
				raise NoChangesProvidedException("No fields provided for update.")
			
			has_actual_changes = False
			for field, new_value in update_data_dict.items():
				current_value = getattr(existing_laptop_full_model, field, None)

				if current_value != new_value:
					has_actual_changes = True
					break

			if not has_actual_changes:
				logger.info(f"Update request for laptop ID {data.laptop_id} for user {data.user_id} received, but no actual changes detected.")
				raise NoChangesProvidedException("No changes detected. The provided data matches current values.")
			
			result = await uow.laptops.update(data)
			return result
		
	async def delete(self, uow: SQLAlchemyUoW, data: LaptopDeleteSchema):
		async with uow:
			user = await uow.users.get_by_id(data.user_id)
			if not user:
				raise UserNotFoundException(f'User not found with ID {data.user_id}')
			laptops = await uow.laptops.get_by_owner_id(data.user_id)
			laptop = [laptop.model_dump() for laptop in laptops if laptop.id == data.laptop_id] 
			if not laptop:
				raise LaptopNotFoundException(f'Laptop with ID {data.laptop_id} for user with ID {data.user_id} not found')
			result = await uow.laptops.delete(data)
			return result