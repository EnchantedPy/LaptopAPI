from src.utils.PostgresRepository import UserActivityPostgresRepository
from models.models import UserActivityModel

class UserActivityRepository(UserActivityPostgresRepository):
	model = UserActivityModel