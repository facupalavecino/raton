"""Main entry point for the Raton bot."""

from __future__ import annotations

import asyncio
import logging
import signal

from raton.config import get_settings
from raton.logging_config import setup_logging
from raton.services import AmadeusClient, CheckOrchestrator, PreferencesRepository, TelegramNotifier

logger = logging.getLogger(__name__)


async def run() -> None:
    """Run the bot application.

    Initializes all components and runs the main check loop. The loop
    runs immediately on startup and then waits for the configured interval
    between checks.

    The loop continues until a shutdown signal (SIGTERM/SIGINT) is received.
    """
    shutdown_event = asyncio.Event()

    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting Raton bot...")

    settings.preferences_dir.mkdir(parents=True, exist_ok=True)
    settings.history_dir.mkdir(parents=True, exist_ok=True)

    amadeus = AmadeusClient.from_settings(settings)
    preferences = PreferencesRepository.from_settings(settings)
    notifier = TelegramNotifier.from_settings(settings)
    orchestrator = CheckOrchestrator(
        amadeus=amadeus,
        preferences=preferences,
        notifier=notifier,
    )

    loop = asyncio.get_running_loop()

    def handle_shutdown(sig: signal.Signals) -> None:
        logger.info(f"Received {sig.name}, initiating shutdown...")
        shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_shutdown, sig)

    interval_seconds = settings.check_interval_hours * 3600
    logger.info(
        f"Raton started, checking every {settings.check_interval_hours} hours ({interval_seconds} seconds)"
    )

    while not shutdown_event.is_set():
        try:
            result = await orchestrator.run_check_cycle()
            logger.info(f"Check cycle complete: {result}")
        except Exception:
            logger.exception("Unexpected error in check cycle")

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=interval_seconds)
        except TimeoutError:
            pass

    logger.info("Raton bot shutdown complete")


def main() -> None:
    """Entry point for the application."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
