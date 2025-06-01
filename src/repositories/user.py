from src.utils.PostgresRepository import UserPostgresRepository
from src.models.models import UserOrm

class UserRepository(UserPostgresRepository):
	model = UserOrm