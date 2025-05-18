from src.utils.PostgresRepository import LaptopPostgresRepository
from src.models.sql_models import LaptopTemplateModel

class LaptopRepository(LaptopPostgresRepository):
	model = LaptopTemplateModel