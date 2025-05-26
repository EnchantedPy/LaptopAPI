from typing import Any, Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AuthServiceException(Exception):
    '''Base exception for auth service'''
    pass


class NotAuthorizedUserException(AuthServiceException):
    '''User is not authorized'''
    pass


class AdminCredsException(AuthServiceException):
    '''Incorrect admin username or password'''
    pass


class UserCredsException(AuthServiceException):
    '''Incorrect username or password'''
    pass


class RegiesterException(AuthServiceException):
    '''Registration failed'''
    pass


class UserNotFoundException(AuthServiceException):
    '''User not found in database'''
    pass


class InvalidTokenException(AuthServiceException):
    '''Invalid token provided'''
    pass


class AdminRequiredDepException(AuthServiceException):
    '''Error in func admin_required'''
    pass


class AuthRequiredDepException(AuthServiceException):
    '''Error in func auth_required'''
    pass


class AlreadyLoggedInException(AuthServiceException):
    '''User is already logged in, he does\'t have access to requested route'''
    pass


class GetUserByIdException(AuthServiceException):
    '''Could not get user by id'''
    pass


class MissingCookieException(AuthServiceException):
    '''User is missing authorization cookie'''
    pass


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: AuthServiceException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )

    return exception_handler


exception_handlers = {
    MissingCookieException: "User is missing authorization cookie",
    NotAuthorizedUserException: "User is not authorized",
    AdminCredsException: "Incorrect admin username or password",
    UserCredsException: "Incorrect username or password",
    RegiesterException: "Registration failed",
    UserNotFoundException: "User not found in database",
    InvalidTokenException: "Invalid token provided",
    AdminRequiredDepException: "Error in func admin_required",
    AuthRequiredDepException: "Error in func auth_required (probably you don\'t have rights for this route",
    AlreadyLoggedInException: "User is already logged in, he doesn't have access to requested route",
    GetUserByIdException: "Could not get user by id"
}


def add_all_auth_exceptions(app: FastAPI):
    for exception, message in exception_handlers.items():
        app.add_exception_handler(
            exception,
            create_exception_handler(
                status_code=status.HTTP_401_UNAUTHORIZED if "auth" in message.lower() else status.HTTP_400_BAD_REQUEST,
                initial_detail={"message": message}
            )
        )