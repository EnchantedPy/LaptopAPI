from src.utils.RedisRepository import AsyncRedisRepository
from config.settings import SAppSettings
from redis.asyncio import from_url

class CacheRepository(AsyncRedisRepository):
	_redis = from_url(SAppSettings.redis_url, decode_responses=True)

# await CacheRepository().set_ttl(*args, **kwargs)