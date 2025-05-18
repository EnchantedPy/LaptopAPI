from services.db_service.kafka.consumer import run_db_consumer
from services.auth_service.kafka.consumer import run_auth_consumer
from services.redis_service.kafka.consumer import run_redis_consumer
import asyncio

# Logger
from config.logging_config import laptop_logger

funcs = [run_db_consumer, run_auth_consumer, run_redis_consumer]

async def run_all_consumers():
    for func in funcs:
        await func()
        laptop_logger.info(f'Starting consumer {func.__name__.removeprefix('run_')
}')

if __name__ == '__main__':
    asyncio.run(run_all_consumers())