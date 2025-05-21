from src.utils.PostgresRepository import UserPostgresRepository
from src.models.models import UserModel

class UserRepository(UserPostgresRepository):
	model = UserModel