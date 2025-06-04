from typing import Any, Awaitable, Callable, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel
from config.settings import Settings
from src.infrastructure.s3.s3_client_factory import s3_client_maker
from src.application.repositories.S3Repository import S3Repository
from src.presentation.api.auth_service.utils import create_access_token, decode_jwt
#from src.presentation.api.routers import apply_routers
import uvicorn
from src.core.entities.entities import TokenPayload
from src.utils.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from src.presentation.dependencies import UoWDep, ElasticDep, get_uow
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from config.settings import Settings
from src.presentation.dependencies import RedisDep
from elasticsearch import AsyncElasticsearch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError


@asynccontextmanager
async def lifespan(app: FastAPI):
	app.state.redis = Redis(host=Settings.redis_host, port=Settings.redis_port, db=0)
	app.state.elastic = AsyncElasticsearch(hosts=[Settings.elastic_url], basic_auth=(Settings.elastic_user, Settings.elastic_password), verify_certs=False, headers={
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
        })
	s3_client = await s3_client_maker()
	app.state.s3_repository = S3Repository(s3_client)
	yield
	await app.state.redis.close()
	await s3_client.close()
	await app.state.elastic.close() 


app = FastAPI(title='Laptop API', lifespan=lifespan)
#apply_routers(app)

from botocore.exceptions import ClientError

@app.middleware("http")
async def s3_error_middleware(request: Request, call_next: Callable | Awaitable) -> Response:
    try:
        return await call_next(request)
    except ClientError as e:
        status_code = 500
        if e.response['Error']['Code'] == 'NoSuchKey':
            status_code = 404
        raise HTTPException(
            status_code=status_code,
            detail=e.response['Error']['Message']
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    status_code = 500
    detail = "Database error"
    
    if isinstance(exc, IntegrityError):
        status_code = 409
        detail = "Data conflict"
    elif isinstance(exc, OperationalError):
        status_code = 503
        detail = "Database unavailable"
    elif isinstance(exc, DataError):
        status_code = 400
        detail = "Invalid data format"
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail}
    )

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


# ------------ App ------------


PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc", '/documents/data', "/search/data"}
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

                uow = get_uow()
                async with uow:
                    user = await uow.users.get_by_id(user_id)
                    if user:
                        new_access_token = create_access_token(user)
                        current_payload = decode_jwt(new_access_token)
                        logger.info(f"Access token refreshed for user {current_payload.get('sub')}.")
                    else:
                        return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": 'User not found'}
                           )
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
            max_age=Settings.access_token_expire_minutes * 60
        )
        logger.debug("New access token set in response cookie.")

    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)



@app.get('/healthcheck', tags=['Healthcheck'])
def healthcheck():
    return {'Status': 'healthy'}

@app.get('/error', tags=['Troubleshoot'])
def error(es: ElasticDep):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='This is an autoerror endpoint'
	 )

class Document(BaseModel):
    data: Dict[str, Any]

@app.post("/documents/{index_name}")
async def add_document(
    index_name: str,
    doc: Document,
    es: ElasticDep
):
    try:
        resp = await es.index(index=index_name, document=doc.data)
        return {"result": resp["result"], "id": resp["_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Поиск по индексу с опциональным query (по умолчанию match_all)
@app.get("/search/{index_name}")
async def search_documents(
    es: ElasticDep,
    index_name: str,
    query: Optional[str] = None,
):
    body = {"query": {"match_all": {}}}
    if query:
        # простой поиск по всем полям с текстом query
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"]
                }
            }
        }
    try:
        resp = await es.search(index=index_name, body=body)
        hits = resp["hits"]["hits"]
        # возвращаем найденные документы с id и source
        return [{"id": hit["_id"], **hit["_source"]} for hit in hits]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)