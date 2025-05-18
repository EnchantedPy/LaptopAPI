from functools import wraps
import json
import logging
from typing import Any
from src.interfaces.AbstractCache import CacheInterface
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger('Logger')

def handle_exc(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            logger.debug(f'Redis func {func.__name__} exited no errors')
            return result
        except RedisError as e:
            logger.error(f"Redis error in {func.__name__}: {e}")
            return e # _test_ for adding middleware later
        except Exception as e:
            logger.error(f"Unexdected error in {func.__name__}: {e}")
            return e # _test_ for adding middleware later
    return wrapper


class AsyncRedisRepository(CacheInterface):
     _redis: Redis = None
     
     @handle_exc
     async def get(self, key: str):
         value = await self._redis.get(key)
         return value
     
     @handle_exc
     async def put(self, key: str, value: Any, ttl: int):
         await self._redis.set(key, json.dumps(value))
         await self.set_ttl(key, ttl)
         
     @handle_exc
     async def delete(self, key: str):
         await self._redis.delete(key)
         
     @handle_exc
     async def clear(self):
         await self._redis.flushall()
         
     @handle_exc
     async def set_ttl(self, key: str, ttl: int):
          await self._redis.expire(key, ttl)