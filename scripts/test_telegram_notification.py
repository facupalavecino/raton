"""Manual test script for Telegram notifications.

Run this to send a real notification to your test bot.

Usage:
    uv run python scripts/test_telegram_notification.py

Requirements:
    - TELEGRAM_BOT_TOKEN set in .env
    - TELEGRAM_USE_TEST_ENVIRONMENT=true for test environment
    - Your test chat ID

This script will:
1. Create a sample flight deal
2. Prompt for your chat ID
3. Send a formatted notification to your Telegram
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from raton.config import get_settings
from raton.models import FlightOffer, FlightSegment, Itinerary, Price
from raton.services.rules import MatchResult
from raton.services.telegram import TelegramNotifier

# Change to project root directory
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Add src to path for imports
sys.path.insert(0, str(project_root / "src"))


async def main():
    """Send a test flight deal notification."""
    print("=" * 60)
    print("Telegram Notification Test Script")
    print("=" * 60)
    print()

    # Load settings
    print(f"Working directory: {os.getcwd()}")
    print(f".env file exists: {Path('.env').exists()}")
    print()

    try:
        settings = get_settings()
        print("✓ Settings loaded successfully")

        # Debug: Check if token is loaded
        if not settings.telegram_bot_token:
            print("✗ TELEGRAM_BOT_TOKEN is empty!")
            print("\nDebugging info:")
            print(f"  TELEGRAM_BOT_TOKEN env var: {os.getenv('TELEGRAM_BOT_TOKEN', 'NOT SET')}")
            print("\nMake sure your .env file has:")
            print("  TELEGRAM_BOT_TOKEN=your_bot_token")
            print("  TELEGRAM_USE_TEST_ENVIRONMENT=true")
            return

        print(
            f"  Bot token: {settings.telegram_bot_token[:20]}... ({len(settings.telegram_bot_token)} chars)"
        )
        print(f"  Test environment: {settings.telegram_use_test_environment}")
        print()
    except Exception as e:
        print(f"✗ Error loading settings: {e}")
        print("\nDebugging info:")
        print(f"  TELEGRAM_BOT_TOKEN env var: {os.getenv('TELEGRAM_BOT_TOKEN', 'NOT SET')}")
        print(
            f"  TELEGRAM_USE_TEST_ENVIRONMENT env var: {os.getenv('TELEGRAM_USE_TEST_ENVIRONMENT', 'NOT SET')}"
        )
        print("\nMake sure you have a .env file with:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_USE_TEST_ENVIRONMENT=true  # for test environment")
        return

    # Create notifier
    notifier = TelegramNotifier.from_settings(settings)
    print("✓ TelegramNotifier created")
    print()

    # Create sample flight - JFK to LAX round-trip
    print("Creating sample flight deal...")
    outbound = Itinerary(
        segments=[
            FlightSegment(
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_time=datetime(2026, 3, 15, 8, 0),
                arrival_time=datetime(2026, 3, 15, 11, 30),
                airline="AA",
                flight_number="100",
                aircraft="Boeing 737-800",
                duration=timedelta(hours=5, minutes=30),
            )
        ]
    )

    inbound = Itinerary(
        segments=[
            FlightSegment(
                departure_airport="LAX",
                arrival_airport="JFK",
                departure_time=datetime(2026, 3, 22, 14, 0),
                arrival_time=datetime(2026, 3, 22, 22, 30),
                airline="AA",
                flight_number="101",
                aircraft="Boeing 737-800",
                duration=timedelta(hours=5, minutes=30),
            )
        ]
    )

    flight = FlightOffer(
        id="test-12345",
        itineraries=[outbound, inbound],
        price=Price(
            total=Decimal("250.00"),
            base=Decimal("200.00"),
            fees=Decimal("50.00"),
            currency="USD",
        ),
        validating_airline="AA",
    )

    match_result = MatchResult(
        is_match=True,
        passed_reasons=(
            "Price $250.00 USD is within budget of $500.00",
            "Direct flight as required",
            "Duration 5h 30m is within limit of 8h 0m",
        ),
        failed_reasons=(),
    )

    print("✓ Sample flight created:")
    print("  Route: JFK → LAX (round-trip)")
    print(f"  Price: ${flight.price.total} {flight.price.currency}")
    print(f"  Airline: {flight.validating_airline}")
    print()

    # Get chat ID from user
    print("=" * 60)
    print("To get your test chat ID:")
    print("1. In Telegram test environment, send a message to your bot")
    print("2. Run: curl https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("3. Look for 'chat':{'id':123456} in the response")
    print("=" * 60)
    print()

    try:
        chat_id_input = input("Enter your Telegram test chat ID: ")
        chat_id = int(chat_id_input.strip())
        print()
    except ValueError:
        print("✗ Invalid chat ID. Please enter a number.")
        return
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return

    # Send notification
    print(f"Sending test notification to chat ID {chat_id}...")
    try:
        await notifier.send_flight_deal(chat_id, flight, match_result)
        print()
        print("=" * 60)
        print("✓ Notification sent successfully!")
        print("=" * 60)
        print()
        print("Check your Telegram test environment for the message.")
        print()
        print("Verify:")
        print("  ☐ Message arrived in the specified chat")
        print("  ☐ Formatting is correct and readable")
        print("  ☐ Markdown renders properly (bold, links)")
        print("  ☐ Emoji display correctly (✈️ 🛫 🛬 ✓ 📊)")
        print("  ☐ All flight details are present")
        print("  ☐ Booking link is clickable")
        print("  ☐ Match reasons are listed")
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Error sending notification: {e}")
        print("=" * 60)
        print()
        print("Common issues:")
        print("  - Invalid bot token")
        print("  - Invalid chat ID")
        print("  - Bot not started in Telegram")
        print("  - Network connectivity issues")
        print()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
