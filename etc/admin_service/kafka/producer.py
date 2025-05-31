from etc.producer import KafkaProducerClient
from config.settings import SAppSettings

LOCAL_TOPICS = {
	'admin_get_all_users': 'admin-get-all-users-topic',
	'admin_search_users': 'admin-search-users-topic',
}


admin_kafka_producer = KafkaProducerClient(LOCAL_TOPICS)