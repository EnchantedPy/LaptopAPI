import asyncio
import datetime
from functools import wraps
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import redis.asyncio as redis
from fastapi import HTTPException
import json
from config.logging_config import laptop_logger
import json
from functools import wraps
from config.settings import SAppSettings


redis_client = redis.from_url(SAppSettings.redis_url, decode_responses=True)

async def get_response_from_cache(request_id: str) -> dict:
    response = await redis_client.get(request_id)
    if response:
        laptop_logger.info(f'Awaited response from Redis: {response}')
        try:
            return json.loads(response)
        except Exception as e:
            laptop_logger.error(f"Error deserializing response from Redis: {e}")
    return None


async def wait_for_response(request_id: str, timeout: int = SAppSettings.redis_timeout) -> dict:
    start = datetime.datetime.now()
    while (datetime.datetime.now() - start).total_seconds() < timeout:
        response_data = await get_response_from_cache(request_id)
        if response_data:
            return response_data
        await asyncio.sleep(0.1)

    raise HTTPException(status_code=504, detail="Timeout waiting for response to appear in Redis")


def generate_cache_key(func_name, **kwargs):
    key = f"{func_name}"
    for param_name, param_value in sorted(kwargs.items()):
        key += f":{param_value}"
    return key


def cache_result(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        
        key = generate_cache_key(func.__name__, **kwargs)
        laptop_logger.info(f'Generated cache key: {key}')
        
        cached_result = await redis_client.get(key)
        if cached_result:
            laptop_logger.info(f'Using cached result: {cached_result}')
            return json.loads(cached_result)
            
        result = await func(*args, **kwargs)
        
        if isinstance(result, (list, int, dict)):
            laptop_logger.info(f'Caching result: {result}')
            await redis_client.set(key, json.dumps(result), ex=60)
        elif isinstance(result, str):
            laptop_logger.info('No users found to cache') # later union
        else:
            laptop_logger.info(f'Result type {type(result)} not cached')
        
        return result
    
    return wrapper



async def send_message_to_redis(producer: AIOKafkaProducer, message: str | dict, producer_name: str):
    topic_key = 'add_info_to_redis'
    try:
        async with producer:
             await producer.send_message(topic_key, message)
             laptop_logger.info(f'{producer_name} sent message to add info to Redis')
             
    except KafkaError as e:
        laptop_logger.error(f'Error sending message to Kafka: {e}')
        raise HTTPException(status_code=500, detail="Error sending message to Kafka to add info to Redis")
