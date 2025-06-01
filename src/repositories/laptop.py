from src.utils.PostgresRepository import LaptopPostgresRepository
from src.models.models import LaptopOrm

class LaptopRepository(LaptopPostgresRepository):
	model = LaptopOrm