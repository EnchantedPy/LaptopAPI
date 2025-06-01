from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict, Field, field_validator
from typing import Any, Dict, Union
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseSettings):
    rmq_host: str = Field(..., env='rmq_host')
    rmq_port: int = Field(..., env='rmq_port')
    rmq_user: str = Field(..., env='rmq_user')
    rmq_password: str = Field(..., env='rmq_password')
    
    @property
    def rmq_url(self) -> str:
         return f'amqp://{self.rmq_user}:{self.rmq_password}@{self.rmq_host}:{self.rmq_port}//'
    
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
    postgres_host: str = Field(..., env="postgres_host")
    
    @property
    def postgres_async_url(self) -> str:
         return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}'
    
    @property
    def postgres_sync_url(self) -> str:
        return f'postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}'


    admin_name: str = Field(..., env="admin_username")
    admin_password: str = Field(..., env="admin_password")

    jwt_cookie_name: str = Field(..., env="jwt_cookie_name")
    jwt_secure: bool = Field(..., env="jwt_secure")
    jwt_algorithm: str = Field(..., env="jwt_algorithm")
    access_token_expire_minutes: int = Field(..., env="access_token_expire_minutes")
    refresh_token_expire_minutes: int = Field(..., env="refresh_token_expire_minutes")
    
    @property
    def jwt_private_key_path(*args, **kwargs):
        return BASE_DIR / "certs" / "jwt-private.pem"
    
    @property
    def jwt_public_key_path(*args, **kwargs):
        return BASE_DIR / "certs" / "jwt-public.pem"

    redis_host: str = Field(..., env="redis_host")
    redis_port: int = Field(..., env="redis_port")
    redis_timeout: int = Field(..., env="redis_timeout")
    
    @property
    def redis_url(self) -> str:
         return f'redis://{self.redis_host}:{self.redis_port}'

    app_name: str = Field(..., env="app_name")
    app_version: str = Field(..., env="app_version")
    log_level: str = Field("INFO", env="log_level")
    log_file: str = Field("logs/app.log", env="log_file")
    external_api_url: str = Field(..., env="external_api_url")

    model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore"
	)


class TestAppSettings(BaseSettings):
    log_level: str = Field(..., validation_alias="log_level")
    test_pg_host: str = Field(..., validation_alias="postgres_host")
    test_pg_port: int = Field(..., validation_alias="postgres_port")
    test_pg_db: str = Field(..., validation_alias="postgres_db")
    test_pg_user: str = Field(..., validation_alias="postgres_user")
    test_pg_password: str = Field(..., validation_alias="postgres_password")

    model_config = ConfigDict(env_file=".env.test")

    @property
    def test_async_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.test_pg_user}:{self.test_pg_password}"
            f"@{self.test_pg_host}:{self.test_pg_port}/{self.test_pg_db}"
        )

    @property 
    def test_sync_pg_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.test_pg_user}:{self.test_pg_password}"
            f"@{self.test_pg_host}:{self.test_pg_port}/{self.test_pg_db}"
        )

def get_test_settings() -> TestAppSettings:
    return TestAppSettings()


TestSettings = get_test_settings()

Settings = AppSettings()