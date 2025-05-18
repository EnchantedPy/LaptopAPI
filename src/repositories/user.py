from src.utils.PostgresRepository import UserPostgresRepository
from src.models.sql_models import UserModel

class UserRepository(UserPostgresRepository):
	model = UserModel