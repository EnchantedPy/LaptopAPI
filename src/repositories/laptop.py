from src.utils.PostgresRepository import LaptopPostgresRepository
from models.models import LaptopTemplateModel

class LaptopRepository(LaptopPostgresRepository):
	model = LaptopTemplateModel