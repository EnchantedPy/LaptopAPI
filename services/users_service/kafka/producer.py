from etc.producer import KafkaProducerClient
from config.settings import SAppSettings

LOCAL_TOPICS = {
    'add_info_to_redis': 'add-info-to-redis',
    'user_get_profile': 'user-get-profile-topic',
	 'get_user_id': 'get-user-id-topic',
	 'delete_user_account': 'delete-user-account-topic',
	 'update_username': 'update-username-topic',
	 'update_user_password': 'update-user-password-topic',
	 'update_user_email': 'update-user-email-topic',
	 'check_user_password': 'check-user-password-topic',
}


users_kafka_producer = KafkaProducerClient(LOCAL_TOPICS)