from services.db_service.kafka.consumer import run_db_consumer
import asyncio

if __name__ == '__main__':
    asyncio.run(run_db_consumer())