from functools import wraps
import json
import logging
from typing import Any
from src.interfaces.AbstractCache import CacheInterface
from redis.asyncio import Redis
from redis.exceptions import RedisError
from src.utils.logger import logger


class AsyncRedisRepository(CacheInterface):
     _redis: Redis = None

     async def get(self, key: str):
         value = await json.loads(self._redis.get(key))
         return value
     
     async def put(self, key: str, value: Any, ttl: int):
         await self._redis.set(key, json.dumps(value))
         await self.set_ttl(key, ttl)

     async def delete(self, key: str):
         await self._redis.delete(key)

     async def clear(self):
         await self._redis.flushall()

     async def set_ttl(self, key: str, ttl: int):
          await self._redis.expire(key, ttl)