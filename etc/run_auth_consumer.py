from services.auth_service.kafka.consumer import run_auth_consumer
import asyncio

if __name__ == '__main__':
    asyncio.run(run_auth_consumer())