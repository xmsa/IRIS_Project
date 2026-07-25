from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR: Path = Path(__file__).parents[3]
ENV_PATH: Path = ROOT_DIR / ".env"


class Base(BaseSettings):
    """Base class for all application settings."""
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
