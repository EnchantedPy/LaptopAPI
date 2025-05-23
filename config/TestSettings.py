from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class TestSettings(BaseSettings):
    log_level: str = Field(..., validation_alias="LOG_LEVEL")
    test_pg_host: str = Field(..., validation_alias="POSTGRES_HOST")
    test_pg_port: int = Field(..., validation_alias="POSTGRES_PORT")
    test_pg_db: str = Field(..., validation_alias="POSTGRES_DB")
    test_pg_user: str = Field(..., validation_alias="POSTGRES_USER")
    test_pg_password: str = Field(..., validation_alias="POSTGRES_PASSWORD")

    model_config = ConfigDict(env_file=".env.test")

    @property
    def test_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.test_pg_user}:{self.test_pg_password}"
            f"@{self.test_pg_host}:{self.test_pg_port}/{self.test_pg_db}"
        )
    
def get_test_settings() -> TestSettings:
    return TestSettings()

STestSettings = TestSettings()