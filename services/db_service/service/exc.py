from typing import Any, Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class DatabaseServiceException(Exception):
    '''Base exception for database service'''


class AddingUserToDBException(DatabaseServiceException):
    '''Error when adding new user to database'''
    pass


class DeleteUserFromDBException(DatabaseServiceException):
    '''User cannot be deleted from DB due to some error'''
    pass


class UpdateUserInDBException(DatabaseServiceException):
    '''User cannot be updated in DB due to some error'''
    pass


class GetUserByIdException(DatabaseServiceException):
    ''''''
    pass


class NoSavedLaptopConfigException(DatabaseServiceException):
    '''User does\'t have saved laptop template'''
    pass


class UserNotFoundException(DatabaseServiceException):
    '''User not found in database'''
    pass


class DatabaseException(DatabaseServiceException):
    '''Database exception'''


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: DatabaseServiceException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )

    return exception_handler


def add_all_db_exceptions(app: FastAPI):
    app.add_exception_handler(
        DeleteUserFromDBException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Error with deleting user from database"
            }
        )
    )

    app.add_exception_handler(
        UpdateUserInDBException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Error while updating user in DB"
            }
        )
    )

    app.add_exception_handler(
        GetUserByIdException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Could not get user information by id"
            }
        )
    )

    app.add_exception_handler(
        UserNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found"
            }
        )
    )

    app.add_exception_handler(
        NoSavedLaptopConfigException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "You have no saved laptop configuration"
            }
        )
    )

    app.add_exception_handler(
        DatabaseException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Database error"
            }
        )
    )