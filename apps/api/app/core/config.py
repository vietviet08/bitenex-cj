"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_port: int = 8000
    api_prefix: str = "/v1"
    debug: bool = False

    # Database - Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "customer_journey"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Database - ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_db: str = "customer_journey"

    @property
    def clickhouse_url(self) -> str:
        return f"clickhouse://{self.clickhouse_user}:{self.clickhouse_password}@{self.clickhouse_host}:{self.clickhouse_port}/{self.clickhouse_db}"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Event settings
    event_retention_days: int = 90
    max_event_payload_kb: int = 32

    # JWT Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
