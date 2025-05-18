import json
from aiokafka import AIOKafkaProducer
from config.logging_config import logger
from config.settings import SAppSettings

class KafkaProducerClient:
    def __init__(self, topics: dict, broker_url: str = SAppSettings.kafka_broker_url):
        self.broker_url = broker_url
        self.topics = topics
        self.producer = None
        
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker_url,
            value_serializer=self.serializer,
            compression_type='gzip'
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    def serializer(self, value: dict | object) -> bytes:
        if hasattr(value, 'model_dump'):
            value = value.model_dump()
        return json.dumps(value).encode()

    async def send_message(self, topic_key: str, message: dict):
        if not self.producer:
               logger.error("Producer: producer is not started")
               raise Exception("Producer: producer is not started or not initialized")
        
        topic = self.topics.get(topic_key)
        if topic:
            await self.producer.send(topic, message)
            logger.debug('Producer: message sent')
        else:
            logger.error(f"Producer: topic with key: {topic_key} not found while sending message")
            raise Exception(f"Producer: topic with key: {topic_key} not found while sending message")

    async def __aenter__(self):
        logger.debug('Starting producer')
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Exiting producer')
        await self.stop()