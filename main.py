from typing import Awaitable, Callable, Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from config.settings import SAppSettings
from src.core.auth_service.utils import create_access_token, decode_jwt
from src.core.routers import apply_routers
from src.core.exceptions.exceptions import (
	IncorrectSubmitPassword, NoChangesProvidedException, UserNotFoundException, LaptopTemplatesLimitException, LaptopNotFoundException, ActivityNotFoundException,
    #FailedTokenRefreshException, NoValidTokensFoundException, InvalidTokenException, AdminPrivilegesRequiredException, AlreadyLoggedInException, AuthRequiredException
)
import uvicorn
from src.core.exceptions.exceptions import DatabaseDataException, DatabaseConfigurationException, DatabaseException, DatabaseIntegrityException, DatabaseOperationalException, S3ClientException, S3ConnectionException, S3Exception, S3NoCredentialsException, S3ParameterValidationException
from src.entities.entities import TokenPayload
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI(title='Laptop API')
apply_routers(app)


# -------- Service exception handlers --------

# @app.exception_handler(FailedTokenRefreshException)
# async def failed_token_refresh_handler(request: Request, exc: FailedTokenRefreshException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @app.exception_handler(NoValidTokensFoundException)
# async def no_valid_tokens_found_handler(request: Request, exc: NoValidTokensFoundException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @app.exception_handler(InvalidTokenException)
# async def invalid_or_expired_admin_token_handler(request: Request, exc: InvalidTokenException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @app.exception_handler(AdminPrivilegesRequiredException)
# async def admin_privileges_required_handler(request: Request, exc: AdminPrivilegesRequiredException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @app.exception_handler(AlreadyLoggedInException)
# async def already_logged_in_handler(request: Request, exc: AlreadyLoggedInException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @app.exception_handler(AuthRequiredException)
# async def auth_required_handler(request: Request, exc: AuthRequiredException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

@app.exception_handler(LaptopTemplatesLimitException)
async def no_credentials_s3_error_handler(request: Request, exc: LaptopTemplatesLimitException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(IncorrectSubmitPassword)
async def no_credentials_s3_error_handler(request: Request, exc: IncorrectSubmitPassword):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(ActivityNotFoundException)
async def no_credentials_s3_error_handler(request: Request, exc: ActivityNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(LaptopNotFoundException)
async def no_credentials_s3_error_handler(request: Request, exc: LaptopNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(UserNotFoundException)
async def no_credentials_s3_error_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(NoChangesProvidedException)
async def no_credentials_s3_error_handler(request: Request, exc: NoChangesProvidedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# -------- S3 exception handlers --------

@app.exception_handler(S3NoCredentialsException)
async def no_credentials_s3_error_handler(request: Request, exc: S3NoCredentialsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(S3ConnectionException)
async def connection_s3_error_handler(request: Request, exc: S3ConnectionException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(S3Exception)
async def s3_error_handler(request: Request, exc: S3Exception):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(S3ClientException)
async def client_s3_error_handler(request: Request, exc: S3ClientException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(S3ParameterValidationException)
async def param_validation_s3_error_handler(request: Request, exc: S3ParameterValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# -------- Database exception handlers --------

@app.exception_handler(DatabaseException)
async def db_error_hablder(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseConfigurationException)
async def configuration_db_error_handler(request: Request, exc: DatabaseConfigurationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseDataException)
async def data_db_error_handler(request: Request, exc: DatabaseDataException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseIntegrityException)
async def integrity_db_error_handler(request: Request, exc: DatabaseIntegrityException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(DatabaseOperationalException)
async def operational_db_error_handler(request: Request, exc: DatabaseOperationalException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# ------------ App ------------


def get_sqla_uow() -> SQLAlchemyUoW:
	return SQLAlchemyUoW()


PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc"}
ADMIN_PATHS = {"/auth/admin/test"}
UNAUTHENTICATED_ONLY_PATHS = {"/auth/login/admin", "/auth/login/user", "/auth/register"}
AUTHENTICATED_ONLY_PATHS = {"/auth/logout", "/auth/users/me" "/account/self", "/account/self/update", "/account/delete", "/account/activity", "/account/laptops"}

# rm /auth/users/me && /auth/admin/test

async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    path = request.url.path

    access_token = request.cookies.get('Bearer-token')
    refresh_token = request.cookies.get('Refresh-token')

    current_payload: Optional[TokenPayload] = None
    new_access_token: Optional[str] = None

    if access_token:
        try:
            current_payload = decode_jwt(access_token)
        except (ExpiredSignatureError, InvalidTokenError):
            pass

    # Handle Unauthenticated-Only Paths
    if path in UNAUTHENTICATED_ONLY_PATHS:
        if current_payload:
            logger.info(f"Logged-in user {current_payload.get('sub')} attempted to access {path}")
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": 'Already logged in'}
            )

        logger.debug(f"Path {path} is for unauthenticated users. Proceeding.")
        return await call_next(request)
    
    # Handle Public Paths
    if path in PUBLIC_PATHS:
        logger.debug(f"Path {path} is public. Skipping authentication.")
        return await call_next(request)

    # Authenticated path request with no tokens
    if path in AUTHENTICATED_ONLY_PATHS:
        if not access_token and not refresh_token:
            logger.warning(f"Unauthenticated user attempted to access {path}.")
            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": 'Authentication required to access'}
            )

        logger.debug(f"Authenticated user attempting to access authenticated path {path}.")
        
    # Handle Admin Paths
    if path in ADMIN_PATHS:
        if not access_token:
            logger.warning(f"Admin path {path} request without access token.")
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": 'Admin privileges required'}
            )
        try:
            current_payload = decode_jwt(access_token)
            if current_payload.get('role') != 'admin':
                logger.warning(f"User {current_payload.get('sub')} attempted admin access to {path} without admin role.")
                
                return JSONResponse(
                		status_code=status.HTTP_403_FORBIDDEN,
                		content={"detail": 'Admin privileges required'}
                )
            logger.debug(f"Admin access token valid for user {current_payload.get('sub')} to {path}.")

        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.warning(f"Admin access token invalid or expired for {path}: {e}.")
            
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": 'Admin access token invalid or expired'}
                     )
        
    # Handle General Authenticated Paths
    else:
        if not current_payload and refresh_token:
            try:
                payload = decode_jwt(refresh_token)
                user_id = payload.get('sub')

                uow = get_sqla_uow()
                async with uow:
                    user = await uow.users.get_by_id(user_id)
                    if user:
                        new_access_token = create_access_token(user)
                        current_payload = decode_jwt(new_access_token)
                        logger.info(f"Access token refreshed for user {current_payload.get('sub')}.")
                    else:
                        raise UserNotFoundException('User not found to refresh access token')
            except InvalidTokenError as e:
                logger.warning(f"Failed to refresh token. Clearing tokens.")
                response.delete_cookie(key="Bearer-token")
                response.delete_cookie(key="Refresh-token")
                
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": 'Couldn\'t refresh access token'}
                           )
            
            except Exception as e:
                logger.error(f"Unexpected error during refresh token processing: {e}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": 'Couldn\'t refresh access token'}
                           )

    #Final Check and Request State Update
    if not current_payload:
        logger.warning(f"No valid tokens found for path {path}. Unauthorized access attempt.")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": 'No valid tokens found, access denied'}
                )

    request.state.user_id = current_payload.get('sub')
    request.state.user_payload = current_payload
    request.state.user_role = current_payload.get('role')

    response = await call_next(request)

    #Set New Access Token if Refreshed

    if new_access_token:
        response.set_cookie(
            key="Bearer-token",
            value=new_access_token,
            httponly=True,
            samesite="lax",
            # secure=True, # Uncomment in production with HTTPS
            max_age=SAppSettings.access_token_expire_minutes * 60
        )
        logger.debug("New access token set in response cookie.")

    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)



@app.get('/healthcheck', tags=['Healthcheck'])
def healthcheck():
    return {'Status': 'healthy'}

@app.get('/error', tags=['Troubleshoot'])
def error():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='This is an autoerror endpoint'
	 )


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)