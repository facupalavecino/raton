"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from raton.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Create test settings with mock values.

    Returns:
        Settings instance with test configuration.
    """
    return Settings(
        telegram_bot_token="test_token",
        anthropic_api_key="test_anthropic_key",
        amadeus_api_key="test_amadeus_key",
        amadeus_api_secret="test_amadeus_secret",
    )
