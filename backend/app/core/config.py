from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NVD Jobs API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://nvd:nvd@localhost:5432/nvd_jobs"
    seed_data_dir: Path = Path("/app/nvd-source")
    scraper_data_dir: Path = Path("/app/imported")
    enable_scheduler: bool = True
    scheduler_timezone: str = "Europe/Skopje"
    scraper_schedule_hour: int = 0
    scraper_schedule_minute: int = 0
    scraper_default_limit: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
