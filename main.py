from typing import Awaitable, Callable, Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from config.settings import SAppSettings
from src.core.auth_service.utils import create_access_token, decode_jwt
from src.core.auth_service.views import auth
import uvicorn
from src.core.exceptions.exceptions import DatabaseError
from src.entities.entities import TokenPayload
from src.utils.UnitOfWork import SQLAlchemyUoW
from src.utils.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI(title='Laptop API')
app.include_router(auth)

@app.exception_handler(DatabaseError)
async def user_already_exists_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

def get_sqla_uow() -> SQLAlchemyUoW:
	return SQLAlchemyUoW()


PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc"}
ADMIN_PATHS = {"/auth/admin/test"}
UNAUTHENTICATED_ONLY_PATHS = {"/auth/login/admin", "/auth/login/user", "/auth/register"}
AUTHENTICATED_ONLY_PATHS = {"/auth/logout", "/auth/users/me"}

async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    path = request.url.path

    access_token = request.cookies.get('Bearer-token')
    refresh_token = request.cookies.get('Refresh-token')

    current_payload: Optional[TokenPayload] = None
    new_access_token: Optional[str] = None

    # Attempt to decode access token to determine if user is logged in
    if access_token:
        try:
            current_payload = decode_jwt(access_token)
        except (ExpiredSignatureError, InvalidTokenError):
            pass  # We will try refresh token or deny access later if needed

    # --- Horizontal Rule ---
    ## 1. Handle Unauthenticated-Only Paths

    if path in UNAUTHENTICATED_ONLY_PATHS:
        if current_payload:
            logger.info(f"Logged-in user {current_payload.get('sub')} attempted to access {path}")
            # You might want to redirect to a user dashboard or home page
            # For simplicity, we'll raise an error, but a redirect is better UX
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Already logged in",
            )
        logger.debug(f"Path {path} is for unauthenticated users. Proceeding.")
        return await call_next(request)
    
    ## 2. Handle Public Paths
    if path in PUBLIC_PATHS:
        logger.debug(f"Path {path} is public. Skipping authentication.")
        return await call_next(request)

    ## 3. Handle Logout Path
    if path in AUTHENTICATED_ONLY_PATHS:
        if not access_token and not refresh_token:
            logger.warning(f"Unauthenticated user attempted to access {path}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authentication required for this path'
            )
        # If they have tokens, they can proceed to logout logic which will invalidate them
        logger.debug(f"Authenticated user attempting to log out from {path}.")
        # No return here, let the rest of the middleware try to validate access if needed,
        # or proceed to the logout endpoint directly if tokens exist.
        
    ## 4. Handle Admin Paths

    if path in ADMIN_PATHS:
        if not access_token:
            logger.warning(f"Admin path {path} accessed without access token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authentication required for admin access.'
            )
        try:
            current_payload = decode_jwt(access_token)
            if current_payload.get('role') != 'admin':
                logger.warning(f"User {current_payload.get('sub')} attempted admin access to {path} without admin role.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Access denied. Admin privileges required.'
                )
            logger.debug(f"Admin access token valid for user {current_payload['sub']} to {path}.")

        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.warning(f"Admin access token invalid or expired for {path}: {e}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Authentication required for admin access. Token invalid or expired: {e}'
            )
        
    ## 5. Handle General Authenticated Paths


    # If path is not public, unauthenticated-only, or admin-specific, it implies general authenticated access
    else:
        # If current_payload is still None (meaning access token was missing or invalid) and a refresh token exists
        if not current_payload and refresh_token:
            try:
                payload = decode_jwt(refresh_token)
                user_id = payload.get('sub')

                uow = get_sqla_uow()
                async with uow:
                    user = await uow.users.get_by_id(user_id)
                    if user: # Ensure user exists in DB
                        new_access_token = create_access_token(user)
                        current_payload = decode_jwt(new_access_token)
                        logger.info(f"Access token refreshed for user {current_payload.get('sub')}.")
                    else:
                        raise InvalidTokenError("User not found for refresh token")
            except InvalidTokenError as e:
                logger.warning(f"Failed to refresh token: {e}. Clearing tokens.")
                # If refresh token is invalid, clear both to force re-login
                response = Response(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required. Failed to refresh token.')
                response.delete_cookie(key="Bearer-token")
                response.delete_cookie(key="Refresh-token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f'Authentication required. Failed to refresh token: {e}'
                )
            except Exception as e:
                logger.error(f"Unexpected error during refresh token processing: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Internal server error during refreshing access token'
                )

    ## 6. Final Check and Request State Update

    if not current_payload:
        logger.warning(f"No valid tokens found for path {path}. Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required. No valid tokens found.'
        )

    request.state.user_id = current_payload['sub']
    request.state.user_payload = current_payload
    request.state.user_role = current_payload.get('role')

    response = await call_next(request)

    ## 7. Set New Access Token if Refreshed

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

@app.get('/errors')
def errors():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='This is an autoerror endpoint'
	 )


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)