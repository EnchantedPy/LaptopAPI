from src.utils.RedisRepository import AsyncRedisRepository
from config.settings import Settings
from redis.asyncio import from_url

class CacheRepository(AsyncRedisRepository):
	_redis = from_url(Settings.redis_url, decode_responses=True)

# await CacheRepository().set_ttl(*args, **kwargs)