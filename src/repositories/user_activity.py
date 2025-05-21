from src.utils.PostgresRepository import UserActivityPostgresRepository
from src.models.models import UserActivityModel

class UserActivityRepository(UserActivityPostgresRepository):
	model = UserActivityModel