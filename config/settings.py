from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Any, Dict, Union
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class AppSettings(BaseSettings):
    rmq_host: str = Field(..., env='rmq_host')
    rmq_port: int = Field(..., env='rmq_port')
    rmq_user: str = Field(..., env='rmq_user')
    rmq_password: str = Field(..., env='rmq_password')
    rmq_url: Any = Field(..., env='rmq_url')
    
    s3_bucket_name: str = Field(..., env='s3_bucket_name')
    s3_endpoint_url: str = Field(..., env='s3_endpoint_url')
    s3_access_key: str = Field(..., env='s3_access_key')
    s3_secret_key: str = Field(..., env='s3_secret_key')
    
    @property
    def s3_config(self) -> dict:
        return {
            
            'aws_access_key_id': self.s3_access_key,
            'aws_secret_access_key': self.s3_secret_key,
            'endpoint_url': self.s3_endpoint_url
        }
    
    postgres_url: Any = Field(..., env="postgres_url")
    postgres_name: str = Field(..., env="postgres_name")
    postgres_password: str = Field(..., env="postgres_password")
    postgres_user: str = Field(..., env="postgres_user")

    admin_username: str = Field(..., env="admin_username")
    admin_password: str = Field(..., env="admin_password")

    jwt_secret_key: str = Field(..., env="jwt_secret_key")
    jwt_cookie_name: str = Field(..., env="jwt_cookie_name")
    jwt_secure: bool = Field(..., env="jwt_secure")
    jwt_algorithm: str = Field(..., env="jwt_algorithm")
    
    @property
    def jwt_private_key_path():
        return BASE_DIR / "certs" / "jwt-private.pem"
    
    @property
    def jwt_public_key_path():
        return BASE_DIR / "certs" / "jwt-public.pem"

    redis_url: str = Field(..., env="redis_url")
    redis_host: str = Field(..., env="redis_host")
    redis_port: int = Field(..., env="redis_port")
    redis_timeout: int = Field(..., env="redis_timeout")

    kafka_broker_url: str = Field(..., env="kafka_broker_url")
    kafka_host: str = Field(..., env="kafka_host")
    kafka_port: int = Field(..., env="kafka_port")
    kafka_topics: Dict[str, str] = Field(..., env="kafka_topics")

    app_name: str = Field(..., env="app_name")
    app_version: str = Field(..., env="app_version")
    log_level: str = Field("INFO", env="log_level")
    log_file: str = Field("logs/app.log", env="log_file")
    external_api_url: str = Field(..., env="external_api_url")

    @field_validator("kafka_topics", mode="before")
    @classmethod
    def decode_kafka_topics(cls, v: Union[str, Dict]) -> Dict[str, str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('KAFKA_TOPICS environment variable is not a valid JSON string')
        elif isinstance(v, dict):
            return v
        raise ValueError('KAFKA_TOPICS must be a JSON string or a dictionary')

    model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore"
	)


SAppSettings = AppSettings()
print(SAppSettings)
