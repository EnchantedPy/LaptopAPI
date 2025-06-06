import asyncio
from contextlib import asynccontextmanager
import json
from config.settings import Settings
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractRobustConnection
from typing import AsyncGenerator

class RabbitMQPublisher:
    def __init__(self, url: str = Settings.rmq_url):
        self.url = url

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AbstractRobustConnection, None]:
        try:
            conn = await connect_robust(self.url)
            yield conn
        finally:
            if conn and not conn.is_closed:
                await conn.close()

    async def send_message(
        self,
        queue_name: str,
        message_body: dict,
        exchange_name: str = Settings.rmq_exchange,
        routing_key: str = "",
        delivery_mode: int = 2
    ):

        async with self.connect() as connection:
            async with connection.channel() as channel:
                if not exchange_name and queue_name:
                    await channel.declare_queue(
                        queue_name,
                        durable=True
                    )

                encoded_message = json.dumps(message_body).encode("utf-8")

                message = Message(
                    encoded_message,
                    content_type="application/json",
                    delivery_mode=delivery_mode
                )

                await channel.default_exchange.publish(
                    message,
                    routing_key=routing_key if routing_key else queue_name,
                )
                print(f" [x] Sent '{message_body}' to queue '{queue_name}'")