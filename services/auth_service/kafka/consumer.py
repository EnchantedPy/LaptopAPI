# FastAPI and related imports
from fastapi import HTTPException

# Logging
from backend.src.utils.logger import laptop_logger

# External libraries
import json
from aiokafka import AIOKafkaConsumer

# Services and dependencies
from services.auth_service.service.depends import decode_jwt_token, extract_token
from services.auth_service.kafka.producer import auth_kafka_producer

# Configuration
from config.settings import SAppSettings


LOCAL_TOPICS = {
    'get_user_id': 'get-user-id-topic'
}


class KafkaConsumerClient:
    def __init__(self, topics: dict, broker_url: str = SAppSettings.kafka_broker_url):
        self.broker_url = broker_url
        self.topics = topics
        self.consumer = None

    async def start(self, topics: list):

        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.broker_url,
            value_deserializer=self.deserializer
        )
        
        await self.consumer.start()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    def deserializer(self, serialized):
        if isinstance(serialized, dict):
            laptop_logger.debug(f"Received msg as dict: {serialized}")
            return serialized
        else:
            laptop_logger.debug(f"Received msg as string: {serialized}")
            return json.loads(serialized)

    async def event_handler(self, value, topic: str):
        if topic == 'get-user-id-topic':
            laptop_logger.info(f"Handling get-user-id: {value}")
            value = self.deserializer(value)
            await self.handle_get_user_id(value)
        else:
            laptop_logger.warning(f"Received message from unknown topic: {topic}")

    async def handle_get_user_id(self, value):
         try:
              request_id = value.get('request_id')
              cookies = value.get('http_request_cookies')
              token = await extract_token(cookies)
              laptop_logger.debug(f'{token} {cookies} {request_id}')
              
              payload = await decode_jwt_token(token)
              laptop_logger.debug(payload)
              user_id = payload.get('sub')
              laptop_logger.debug(user_id)
              
              if user_id:
                   response_data = {
                		'request_id': request_id,
                		'user': user_id,
                		'data': 'valid'
                                   }
                   
              else:
                   response_data = {
                		'request_id': request_id,
                		'data': 'invalid'
                                   }
              topic_key = 'add_info_to_redis'
              
              async with auth_kafka_producer as producer:
                   await producer.send_message(topic_key, response_data)
                   laptop_logger.debug(f'Sent response for get-user-id - {user_id} to redis service')
                   
         except Exception as e:
              laptop_logger.error(f"An error fetching user id from token: {e}")
              raise HTTPException(status_code=401, detail="Error fetching user ID from token")


    async def consume_messages(self):
        await self.start(list(self.topics.values()))

        try:
            async for msg in self.consumer:
                topic_key = msg.topic
                await self.event_handler(msg.value, topic_key)
        finally:
            await self.stop()


auth_kafka_consumer = KafkaConsumerClient(LOCAL_TOPICS)

async def run_auth_consumer():
    laptop_logger.info('Auth consumer started')
    await auth_kafka_consumer.consume_messages()
    laptop_logger.info('Stopping auth kafka consumer')
