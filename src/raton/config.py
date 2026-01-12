"""Application configuration using pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        telegram_bot_token: Bot token from @BotFather.
        telegram_use_test_environment: Use Telegram test environment.
        anthropic_api_key: API key for Anthropic Claude.
        amadeus_api_key: API key for Amadeus.
        amadeus_api_secret: API secret for Amadeus.
        amadeus_hostname: Amadeus environment ("test" or "production").
        check_interval_hours: How often to check for flight deals.
        log_level: Logging level.
        data_dir: Directory for storing user data.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str
    telegram_use_test_environment: bool = False

    anthropic_api_key: str

    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_hostname: Literal["test", "production"] = "test"

    check_interval_hours: int = 1
    log_level: str = "INFO"
    data_dir: Path = Path("./data")

    @property
    def preferences_dir(self) -> Path:
        """Directory for user preference files."""
        return self.data_dir / "preferences"

    @property
    def history_dir(self) -> Path:
        """Directory for chat history files."""
        return self.data_dir / "history"


def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Settings instance loaded from environment.
    """
    return Settings()
