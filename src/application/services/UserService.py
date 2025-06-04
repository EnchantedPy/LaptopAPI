from typing import List

from fastapi import HTTPException, status
from src.presentation.dto.schemas import RegisterRequestSchema, UserResponseDto, UserUpdateSchema
from src.utils.UnitOfWork import UnitOfWork
from src.utils.logger import logger
from src.presentation.api.auth_service.utils import hash_password, validate_password


USER_ROLE = 'user'

class UserService:

    async def add(self, uow: UnitOfWork, data: RegisterRequestSchema):
          register_data = data.model_dump()
          register_data.password = hash_password(data.password)
          register_data.role = USER_ROLE
          register_data.active = True
          async with uow:
                await uow.users.add(register_data)
          logger.info(f"User created with username: {data.username}")

    async def get_all(self, uow: UnitOfWork, offset: int = 0, limit: int = 10) -> List[UserResponseDto]:
        async with uow:
            db_users = await uow.users.get_all(offset, limit)
            logger.info("Fetched all users successfully.")
            return [UserResponseDto.model_validate(user) for user in db_users]

    async def get_by_id(self, uow: UnitOfWork, user_id: int) -> UserResponseDto | None:
        async with uow:
            db_user = await uow.users.get_by_id(user_id)
            if not db_user:
                logger.debug(f"No user found with ID: {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            user = UserResponseDto.model_validate(db_user)
            logger.info(f"User fetched by ID: {user_id}")
            if not user.active:
                logger.error(f"User with ID {user_id} inactive.")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
            return user

    async def update(self, uow: UnitOfWork, data: UserUpdateSchema):
        async with uow:
            user = await uow.users.get_by_id(data.id)
            
            if not user:
                 logger.warning(f"Update attempt for non-existent user ID: {data.id}")
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if not user.active:
                 logger.warning(f"Update attempt for inactive user ID: {data.id}")
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
         
            update_data_dict = data.model_dump(
                exclude_unset=True, 
                exclude={'id'}
            )
            
            if not update_data_dict:
                 logger.debug(f"Update request for user ID {data.id} received with no updatable fields.")
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
            
            if 'password' in update_data_dict:
                 hashed_password = hash_password(update_data_dict.get('password'))
                 update_data_dict['hashed_password'] = hashed_password
                 del update_data_dict['password']
                 
            has_actual_changes = False
            for field, new_value in update_data_dict.items():
                 current_value = getattr(user, field, None)
                 if current_value != new_value:
                      has_actual_changes = True
                      break
                 
            if not has_actual_changes:
                 logger.debug(f"Update request for user ID {data.id} had no actual changes.")
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No actual changes provided") 
            
            await uow.users.update(data.id, update_data_dict)
            logger.info(f"User with ID {data.id} successfully updated. Changed fields: {list(update_data_dict.keys())}")

    async def delete(self, uow: UnitOfWork, user_id: int):
        async with uow:
            user_to_delete = await uow.users.get_by_id(user_id)
            if not user_to_delete:
                logger.warning(f"Delete attempt for non-existent user ID: {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if not user_to_delete.active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
            await uow.users.delete(user_id)
            await uow.commit()
            logger.info(f"User with ID {user_id} successfully deleted.")