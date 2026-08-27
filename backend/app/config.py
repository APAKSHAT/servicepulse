from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/servicepulse"
    poll_interval_seconds: int = 30
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    request_timeout_seconds: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
