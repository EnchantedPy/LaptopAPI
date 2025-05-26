from src.utils.S3Repository import S3Repository
from config.settings import SAppSettings

class JsonDataRepository(S3Repository):
	bucket_name = SAppSettings.s3_bucket_name