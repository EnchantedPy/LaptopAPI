from src.utils.PostgresRepository import UserPostgresRepository
from models.models import UserModel

class UserRepository(UserPostgresRepository):
	model = UserModel