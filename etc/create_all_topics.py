import asyncio
import logging
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError, KafkaConnectionError
from config.settings import SAppSettings


NUM_PARTITIONS = 1
REPLICATION_FACTOR = 1

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def create_kafka_topics():
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=SAppSettings.kafka_broker_url
    )
    try:
        log.info(f"Connecting to Kafka ({SAppSettings.kafka_broker_url}) for topic creation...")
        await admin_client.start()
        log.info("Succesfully connected to Kafka.")

        topic_names = list(SAppSettings.kafka_topics.values())
        log.info(f"Topics to create: {topic_names}")

        new_topics = []
        for topic_name in topic_names:
            new_topics.append(
                NewTopic(
                    name=topic_name,
                    num_partitions=NUM_PARTITIONS,
                    replication_factor=REPLICATION_FACTOR
                )
            )

        if not new_topics:
            log.info("All topics already exist")
            return

        log.info(f"Trying to create topics: {[t.name for t in new_topics]}...")
        try:
            log.info(f"Creating: {new_topics}")
            await admin_client.create_topics(new_topics=new_topics, validate_only=False)
            log.info("Succesfully created topics")
        except TopicAlreadyExistsError:
            log.warning("Some of topics already existed")
        except Exception as e:
            log.error(f"An error when adding topics: {e}", exc_info=True)
            raise

    except KafkaConnectionError:
        log.error(f"Cant connect to kafka {SAppSettings.kafka_broker_url}")
        raise
    finally:
        if admin_client:
            log.info("Closing AdminClient...")
            await admin_client.close()
            log.info("Connection AdminClient closed.")

async def main():
    try:
        await create_kafka_topics()
        log.info("Initialized topics")

    except (KafkaConnectionError, Exception) as e:
        log.error(f"Critical error while creating topics: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())