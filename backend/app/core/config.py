from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Diabetes Analysis API"

    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "dataset_analysis"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    # Analysis settings
    ANALYSIS_INTERVAL_MINUTES: int = 10000
    ALERT_THRESHOLD: float = 0.3  # 30% threshold for alerts

    # Notification settings
    ENABLE_NOTIFICATIONS: bool = True
    NOTIFICATION_CHANNEL: str = "email"  # or "slack"

    # Email settings
    EMAIL_USER: str = ""  # Gmail address
    EMAIL_PASSWORD: str = ""  # Gmail app password
    EMAIL_RECIPIENT: str = ""  # Recipient email address

    # LLM settings
    HUGGINGFACE_API_KEY: str = ""  # Hugging Face API key
    LLM_RATE_LIMIT: int = 5  # requests per minute

    # Kaggle settings
    KAGGLE_USERNAME: str = "test_username"
    KAGGLE_KEY: str = "test_password"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
