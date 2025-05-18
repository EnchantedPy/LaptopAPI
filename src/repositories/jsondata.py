from src.utils.S3Repository import S3JsonDataRepository
from config.settings import SAppSettings

class JsonDataRepository(S3JsonDataRepository):
	bucket_name = SAppSettings.s3_bucket_name