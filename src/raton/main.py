"""Main entry point for the Raton bot."""

from __future__ import annotations

import asyncio
import logging

from raton.config import get_settings
from raton.logging_config import setup_logging


async def run() -> None:
    """Run the bot application."""
    settings = get_settings()
    setup_logging(settings.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting Raton bot...")

    # Ensure data directories exist
    settings.preferences_dir.mkdir(parents=True, exist_ok=True)
    settings.history_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Initialize and run bot components
    logger.info("Raton bot started successfully")


def main() -> None:
    """Entry point for the application."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
