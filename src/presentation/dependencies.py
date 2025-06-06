from fastapi import Depends
from typing import Annotated
from src.application.repositories.S3Repository import S3Repository
from src.utils.UnitOfWork import IUnitOfWork, UnitOfWork
from redis.asyncio import Redis
from fastapi import Request

def get_s3_repository(request: Request) -> S3Repository:
    return request.app.state.s3_repository

async def get_redis(request: Request) -> Redis:
    return request.app.state.redis

def get_uow() -> UnitOfWork:
	return UnitOfWork()

UoWDep = Annotated[IUnitOfWork, Depends(get_uow)]

RedisDep = Annotated[Redis, Depends(get_redis)]

S3Dep = Annotated[S3Repository, Depends(get_s3_repository)]