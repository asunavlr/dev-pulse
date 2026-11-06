from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./devpulse.db"
    default_timeout_seconds: float = Field(default=5, gt=0, le=30)
    max_timeout_seconds: float = Field(default=30, gt=0, le=60)
    check_history_limit: int = Field(default=100, ge=1, le=1000)

@lru_cache
def get_settings() -> Settings:
    return Settings()
