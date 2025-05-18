from etc.producer import KafkaProducerClient
from config.settings import SAppSettings

LOCAL_TOPICS = {
    'user_registration': 'user-registration-topic',
    'user_logging_in': 'user-logging-in-topic',
    'add_info_to_redis': 'add-info-to-redis',
}

auth_kafka_producer = KafkaProducerClient(LOCAL_TOPICS)