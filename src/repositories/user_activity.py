from src.utils.PostgresRepository import UserActivityPostgresRepository
from src.models.sql_models import UserActivityModel

class UserActivityRepository(UserActivityPostgresRepository):
	model = UserActivityModel