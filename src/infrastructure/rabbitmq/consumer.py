from contextlib import asynccontextmanager
import json

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException
from config.settings import Settings
from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage
from typing import AsyncGenerator, Callable
from src.infrastructure.elasticsearch.client import es_clientfactory, EsClientFactory

class RabbitMQConsumer:
    def __init__(self, es_client_factory: EsClientFactory = es_clientfactory, url: str = Settings.rmq_url):
        self.url = url
        self.es_client_factory = es_client_factory

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AbstractRobustConnection, None]:
        conn = None
        try:
            conn = await connect_robust(self.url)
            yield conn
        finally:
            if conn and not conn.is_closed:
                await conn.close()
                
    async def callback(self, message: AbstractIncomingMessage):
        try:
             es = self.es_client_factory()
             resp = await es.index(index='User-activity-index', document=message)
             await message.ack()
             
        except Exception as e:
             raise HTTPException(status_code=500, detail='Error sending data to elasticsearch')

    async def consume_messages(
        self,
        queue_name: str,
        message_handler: Callable[[AbstractIncomingMessage], None] = None,
        exchange_name: str = Settings.rmq_exchange,
        routing_key_pattern: str = "#",
        exchange_type: ExchangeType = ExchangeType.TOPIC,
        queue_durable: bool = True,
        auto_ack: bool = False
    ):
        if not message_handler:
            message_handler = self.callback
        async with self.connect() as connection:
            async with connection.channel() as channel:
                exchange = await channel.declare_exchange(
                    exchange_name,
                    type=exchange_type,
                    durable=True
                )

                queue = await channel.declare_queue(
                    queue_name,
                    durable=queue_durable
                )

                await queue.bind(
                    exchange,
                    routing_key=routing_key_pattern
                )
                print(f" [*] Waiting for messages in queue '{queue_name}' bound to exchange '{exchange_name}' with pattern '{routing_key_pattern}'. To exit press CTRL+C")

                consumer_tag = await queue.consume(message_handler, no_ack=auto_ack)
                print(f"Consumer started with tag: {consumer_tag}")