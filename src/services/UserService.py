from src.core.exceptions.exceptions import NoChangesProvidedException, UserNotFoundException
from src.schemas.schemas import UserAddSchema, UserDeleteSchema, UserUpdateSchema
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger
from src.core.auth_service.utils import hash_password


class UserService:

    async def add(self, uow: SQLAlchemyUoW, data: UserAddSchema):
        data.password = hash_password(data.password)
        async with uow:
            result = await uow.users.add(data)
            logger.info(f"User created with username: {data.username}")
            return result

    async def get_all(self, uow: SQLAlchemyUoW, offset: int = 0, limit: int = 20):
        async with uow:
            result = await uow.users.get_all(offset, limit)
            logger.info("Fetched all users successfully.")
            return result

    async def get_by_name(self, uow: SQLAlchemyUoW, name: str):
        async with uow:
            result = await uow.users.get_by_name(name)
            logger.info(f"Users fetched by name: {name}")
            return result

    async def get_by_username(self, uow: SQLAlchemyUoW, username: str):
        async with uow:
            result = await uow.users.get_by_username(username)
            if result:
                logger.info(f"User fetched by username: {username}")
                return result
            logger.debug(f"No user found with username: {username}")
            raise UserNotFoundException(f'No user found with username {username}')

    async def get_by_id(self, uow: SQLAlchemyUoW, user_id: int):
        async with uow:
            result = await uow.users.get_by_id(user_id)
            if result:
                logger.info(f"User fetched by ID: {user_id}")
                return result
            logger.debug(f"No user found with ID: {user_id}")
            raise UserNotFoundException(f'No user found with ID {user_id}')

    async def update(self, uow: SQLAlchemyUoW, data: UserUpdateSchema):
        async with uow:
            existing_user_full_model = await uow.users.get_by_id(data.id)
            if not existing_user_full_model:
                logger.warning(f"Update attempt for non-existent user ID: {data.id}")
                raise UserNotFoundException(f'No user found with ID {data.id}')

            update_data_dict = data.model_dump(exclude_unset=True, exclude={'id'})

            if not update_data_dict:
                logger.debug(f"Update request for user ID {data.id} received with no updatable fields.")
                raise NoChangesProvidedException('No updatable fields provided for user update')

            has_actual_changes = False
            for field, new_value in update_data_dict.items():
                current_value = getattr(existing_user_full_model, field, None)
                if current_value != new_value:
                    has_actual_changes = True
                    break

            if not has_actual_changes:
                logger.debug(f"Update request for user ID {data.id} had no actual changes.")
                raise NoChangesProvidedException('No changes provided for user update')

            result = await uow.users.update(data)
            logger.info(f"User with ID {data.id} successfully updated.")
            return result

    async def delete(self, uow: SQLAlchemyUoW, data: UserDeleteSchema):
        async with uow:
            user_to_delete = await uow.users.get_by_id(data.id)
            if user_to_delete:
                result = await uow.users.delete(data)
                logger.info(f"User with ID {data.id} successfully deleted.")
                return result
            logger.warning(f"Delete attempt for non-existent user ID: {data.id}")
            raise UserNotFoundException(f'User not found with ID {data.id}')
