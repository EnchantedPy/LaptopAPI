from src.utils.S3Repository import S3Repository
from config.settings import Settings

class JsonDataRepository(S3Repository):
	bucket_name = Settings.s3_bucket_name