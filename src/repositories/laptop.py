from src.utils.PostgresRepository import LaptopPostgresRepository
from src.models.models import LaptopTemplateModel

class LaptopRepository(LaptopPostgresRepository):
	model = LaptopTemplateModel