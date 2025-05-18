import os
import jwt

# FastAPI
from fastapi import APIRouter, Request, Security
from fastapi.responses import FileResponse

# SQLAlchemy
from sqlalchemy import select

# Local modules
from authorization_routes import auth_required, config
from backend.database_restart import SessionDep, UserModel

# Exceptions
from custom_exceptions import FileNotFoundException, NotAuthorizedUserException, UserNotFoundException

# Logger
from logging_system import custom_logger

file_router = APIRouter()


@file_router.get('/get_result_file', summary='Get file with searching results', tags=['Laptop Routes'],
                 dependencies=[Security(auth_required)])
async def get_result_file(request: Request, session: SessionDep):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

    if not token:
        custom_logger.info('No token provided for protected route')
        raise NotAuthorizedUserException
    try:
        secret_key = config.JWT_SECRET_KEY or os.environ.get("JWT_SECRET_KEY", "secret")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload["username"]

        query = select(UserModel).where(UserModel.name == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            custom_logger.error(f'User {username} not found in database')
            raise UserNotFoundException

        custom_logger.info(f'User {username} found in database')

        file_path = f"storage/{user.id}_result.json"

        if not os.path.exists(file_path):
            raise FileNotFoundException
        custom_logger.info(f'User {username} downloaded result.json')
        return FileResponse(
            file_path,
            filename=f"{user.id}_result.json",
            #  media_type="application/json",
            #  headers={"Content-Disposition": "attachment"}
        )

    except jwt.ExpiredSignatureError:
        custom_logger.error('Token has expired')
        raise NotAuthorizedUserException

    except jwt.InvalidTokenError:
        custom_logger.error('Invalid token')
        raise NotAuthorizedUserException