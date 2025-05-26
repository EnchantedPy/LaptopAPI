import json
import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer
from typing import Dict, Any
from backend.src.utils.logger import laptop_logger
from config.settings import SAppSettings


class KafkaConsumerClient:
    def __init__(self, broker_url: str = SAppSettings.kafka_broker_url, redis_url: str = SAppSettings.redis_url):
        self.broker_url = broker_url
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.consumer = None
        self.topic = 'add-info-to-redis'

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.broker_url,
            value_deserializer=self.deserializer
        )
        await self.consumer.start()
        laptop_logger.info(f"Redis consumer started for topic {self.topic}")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            laptop_logger.info("Redis consumer stopped")

    def deserializer(self, serialized: bytes) -> Dict[str, Any]:
        try:
            if isinstance(serialized, dict):
                laptop_logger.info(f"Redis consumer received msg as dict: {serialized}")
                return serialized
            else:
                laptop_logger.info(f"Redis consumer received msg as string: {serialized}")
                return json.loads(serialized.decode('utf-8'))
        except Exception as e:
            laptop_logger.error(f"Redis consumer thrown error deserializing message: {e}")
            return {}
      
    async def event_handler(self, value: Dict[str, Any]):
        laptop_logger.info(f"Handling Redis data: {value}")
        key = value.get("request_id")
        status = value.get("data")
        laptop_logger.info(f'Redis service recieved {key} and response status is {status}')
        if key:
               if value.get('special'):
                       special = value.get('special')
                       laptop_logger.info(f'Handling special adding to redis: {special}, {status}')
                       await self.redis_client.set(key, json.dumps(status))
                       laptop_logger.info(f"SPECIAL: Stored in Redis: {key} -> {status}")
                       
               elif value.get('user'):
                      user_data = value.get('user')
                      laptop_logger.info(f'Handling user-data adding to redis: {user_data}, {status}')
                      await self.redis_client.set(key, json.dumps(user_data))
                      laptop_logger.info(f"Stored in Redis: {key} -> {user_data}")
                      
               elif value.get('users'):
                                    users_data = value.get('users')
                                    laptop_logger.info(f'Handling users-data adding to redis: {users_data}, {status}')
                                    await self.redis_client.set(key, json.dumps(users_data))
                                    laptop_logger.info(f"Stored in Redis: {key} -> {users_data}")
                       
               else:
                     laptop_logger.warning(f"Received incomplete data for Redis: {value}")


    async def consume_messages(self):
        laptop_logger.info('Redis consumer is running')
        await self.start()
        try:
            async for msg in self.consumer:
                data = self.deserializer(msg.value)
                if data:
                    await self.event_handler(data)
        finally:
            await self.stop()


async def run_redis_consumer():
    redis_consumer = KafkaConsumerClient()
    await redis_consumer.consume_messages()
