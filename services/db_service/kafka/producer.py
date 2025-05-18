from etc.producer import KafkaProducerClient
from config.settings import AppSettings

LOCAL_TOPICS = {
    'add_info_to_redis': 'add-info-to-redis',
}

db_kafka_producer = KafkaProducerClient(LOCAL_TOPICS)

