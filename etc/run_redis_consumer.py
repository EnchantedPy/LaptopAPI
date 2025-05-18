from services.redis_service.kafka.consumer import run_redis_consumer
import asyncio

if __name__ == '__main__':
    asyncio.run(run_redis_consumer())