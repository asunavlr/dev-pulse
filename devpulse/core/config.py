from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    api_key: str = "dev-only-change-me"
    database_url: str = "sqlite:///./devpulse.db"
    default_timeout_seconds: float = Field(default=5, gt=0, le=30)
    max_timeout_seconds: float = Field(default=30, gt=0, le=60)
    check_history_limit: int = Field(default=100, ge=1, le=1000)
    scheduler_enabled: bool = False
    check_interval_seconds: int = Field(default=60, ge=10, le=3600)
    max_targets_per_cycle: int = Field(default=100, ge=1, le=1000)

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if (
            self.environment.lower() == "production"
            and (self.api_key == "dev-only-change-me" or len(self.api_key) < 32)
        ):
            raise ValueError("Set a unique API_KEY with at least 32 characters in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
