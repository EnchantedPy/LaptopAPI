from src.utils.PostgresRepository import ActivityPostgresRepository
from src.models.models import ActivityOrm

class ActivityRepository(ActivityPostgresRepository):
	model = ActivityOrm