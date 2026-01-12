"""Tests for Telegram notification service.

This module tests the TelegramNotifier for sending flight deal notifications
via the Telegram Bot API.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest
import telegram

from raton.models import FlightOffer, FlightSegment, Itinerary, Price
from raton.services.exceptions import (
    TelegramAuthError,
    TelegramChatNotFoundError,
    TelegramDeliveryError,
    TelegramNetworkError,
)
from raton.services.rules import MatchResult
from raton.services.telegram import TelegramNotifier


@pytest.fixture
def mock_telegram_bot(mocker):
    """Mock telegram.Bot for testing.

    Returns:
        Mock: A mock Bot instance with async send_message method.
    """
    mock_bot = Mock(spec=telegram.Bot)
    mock_bot.send_message = AsyncMock()
    mocker.patch("raton.services.telegram.telegram.Bot", return_value=mock_bot)
    return mock_bot


@pytest.fixture
def sample_flight_offer():
    """Create a sample one-way FlightOffer for testing.

    Returns:
        FlightOffer: JFK to LAX direct flight.
    """
    segment = FlightSegment(
        departure_airport="JFK",
        arrival_airport="LAX",
        departure_time=datetime(2026, 2, 15, 8, 0),
        arrival_time=datetime(2026, 2, 15, 11, 30),
        airline="AA",
        flight_number="100",
        aircraft="Boeing 737-800",
        duration=timedelta(hours=5, minutes=30),
    )

    itinerary = Itinerary(segments=[segment])

    return FlightOffer(
        id="test-offer-123",
        itineraries=[itinerary],
        price=Price(
            total=Decimal("250.00"),
            base=Decimal("200.00"),
            fees=Decimal("50.00"),
            currency="USD",
        ),
        validating_airline="AA",
    )


@pytest.fixture
def sample_round_trip_flight():
    """Create a sample round-trip FlightOffer for testing.

    Returns:
        FlightOffer: JFK to LAX and back, both direct.
    """
    outbound_segment = FlightSegment(
        departure_airport="JFK",
        arrival_airport="LAX",
        departure_time=datetime(2026, 2, 15, 8, 0),
        arrival_time=datetime(2026, 2, 15, 11, 30),
        airline="AA",
        flight_number="100",
        aircraft="Boeing 737-800",
        duration=timedelta(hours=5, minutes=30),
    )

    return_segment = FlightSegment(
        departure_airport="LAX",
        arrival_airport="JFK",
        departure_time=datetime(2026, 2, 22, 14, 0),
        arrival_time=datetime(2026, 2, 22, 22, 30),
        airline="AA",
        flight_number="101",
        aircraft="Boeing 737-800",
        duration=timedelta(hours=5, minutes=30),
    )

    outbound = Itinerary(segments=[outbound_segment])
    inbound = Itinerary(segments=[return_segment])

    return FlightOffer(
        id="test-rt-456",
        itineraries=[outbound, inbound],
        price=Price(
            total=Decimal("450.00"),
            base=Decimal("380.00"),
            fees=Decimal("70.00"),
            currency="USD",
        ),
        validating_airline="AA",
    )


@pytest.fixture
def sample_flight_with_stops():
    """Create a sample FlightOffer with one stop.

    Returns:
        FlightOffer: JFK to LAX with connection in ORD.
    """
    first_segment = FlightSegment(
        departure_airport="JFK",
        arrival_airport="ORD",
        departure_time=datetime(2026, 2, 15, 8, 0),
        arrival_time=datetime(2026, 2, 15, 10, 0),
        airline="UA",
        flight_number="200",
        aircraft="Boeing 737",
        duration=timedelta(hours=2),
    )

    second_segment = FlightSegment(
        departure_airport="ORD",
        arrival_airport="LAX",
        departure_time=datetime(2026, 2, 15, 11, 30),
        arrival_time=datetime(2026, 2, 15, 13, 30),
        airline="UA",
        flight_number="201",
        aircraft="Boeing 737",
        duration=timedelta(hours=4),
    )

    itinerary = Itinerary(segments=[first_segment, second_segment])

    return FlightOffer(
        id="test-stops-789",
        itineraries=[itinerary],
        price=Price(
            total=Decimal("180.00"),
            base=Decimal("150.00"),
            fees=Decimal("30.00"),
            currency="USD",
        ),
        validating_airline="UA",
    )


@pytest.fixture
def sample_match_result():
    """Create a sample MatchResult with passed reasons.

    Returns:
        MatchResult: A successful match with reasons.
    """
    return MatchResult(
        is_match=True,
        passed_reasons=(
            "Price $250.00 USD is within budget of $500.00",
            "Direct flight as required",
            "Duration 5h 30m is within limit of 8h 0m",
        ),
        failed_reasons=(),
    )


# Happy Path Tests


@pytest.mark.asyncio
async def test_send_message_delivers_to_telegram(mock_telegram_bot):
    """
    GIVEN a valid chat_id and message text
    WHEN calling send_message
    THEN telegram.Bot.send_message is called with correct parameters
    """
    notifier = TelegramNotifier(bot_token="test_token")
    chat_id = 12345
    text = "Test message"

    await notifier.send_message(chat_id, text)

    mock_telegram_bot.send_message.assert_called_once_with(
        chat_id=chat_id, text=text, parse_mode="MarkdownV2"
    )


@pytest.mark.asyncio
async def test_send_flight_deal_formats_and_sends_message(
    mock_telegram_bot, sample_flight_offer, sample_match_result
):
    """
    GIVEN a flight offer and match result
    WHEN calling send_flight_deal
    THEN a formatted message is sent via send_message
    """
    notifier = TelegramNotifier(bot_token="test_token")
    chat_id = 12345

    await notifier.send_flight_deal(chat_id, sample_flight_offer, sample_match_result)

    assert mock_telegram_bot.send_message.call_count == 1
    call_args = mock_telegram_bot.send_message.call_args

    assert call_args.kwargs["chat_id"] == chat_id
    assert call_args.kwargs["parse_mode"] == "MarkdownV2"

    message = call_args.kwargs["text"]
    assert "JFK" in message
    assert "LAX" in message
    assert "250" in message  # Price


def test_format_flight_deal_one_way(sample_flight_offer, sample_match_result):
    """
    GIVEN a one-way flight offer
    WHEN formatting the deal
    THEN message contains route, price, times, duration, stops, airline, and reasons
    """
    notifier = TelegramNotifier(bot_token="test_token")
    message = notifier._format_flight_deal(sample_flight_offer, sample_match_result)

    assert "JFK" in message
    assert "LAX" in message
    assert "One\\-way" in message or "one\\-way" in message

    assert "250" in message
    assert "USD" in message

    assert "AA" in message
    assert "Direct" in message or "0 stop" in message

    assert "within budget" in message
    assert "Direct flight" in message


def test_format_flight_deal_round_trip(sample_round_trip_flight, sample_match_result):
    """
    GIVEN a round-trip flight offer
    WHEN formatting the deal
    THEN message contains both outbound and return legs
    """
    notifier = TelegramNotifier(bot_token="test_token")
    message = notifier._format_flight_deal(sample_round_trip_flight, sample_match_result)

    assert "Round\\-trip" in message or "round\\-trip" in message

    assert "Outbound" in message
    assert "Return" in message

    assert message.count("JFK") >= 2
    assert message.count("LAX") >= 2


def test_format_flight_deal_with_stops(sample_flight_with_stops, sample_match_result):
    """
    GIVEN a flight with 1 stop
    WHEN formatting the deal
    THEN message indicates "1 stop" correctly
    """
    notifier = TelegramNotifier(bot_token="test_token")
    message = notifier._format_flight_deal(sample_flight_with_stops, sample_match_result)

    assert "1 stop" in message


def test_format_flight_deal_escapes_markdown(sample_flight_offer, sample_match_result):
    """
    GIVEN a flight offer with special characters
    WHEN formatting the deal
    THEN all MarkdownV2 special characters are escaped
    """
    notifier = TelegramNotifier(bot_token="test_token")
    message = notifier._format_flight_deal(sample_flight_offer, sample_match_result)

    assert "\\." in message

    assert "\\-" in message


def test_from_settings_creates_notifier(mocker):
    """
    GIVEN application settings with bot token
    WHEN calling from_settings
    THEN TelegramNotifier is created with correct configuration
    """
    mock_settings = mocker.Mock()
    mock_settings.telegram_bot_token = "test_token"
    mock_settings.telegram_use_test_environment = False

    mocker.patch("raton.services.telegram.telegram.Bot")

    notifier = TelegramNotifier.from_settings(mock_settings)

    assert notifier is not None
    assert isinstance(notifier, TelegramNotifier)


@pytest.mark.asyncio
async def test_send_message_handles_invalid_token(mock_telegram_bot):
    """
    GIVEN an invalid bot token
    WHEN sending a message
    THEN TelegramAuthError is raised
    """
    mock_telegram_bot.send_message.side_effect = telegram.error.InvalidToken()

    notifier = TelegramNotifier(bot_token="invalid_token")

    with pytest.raises(TelegramAuthError):
        await notifier.send_message(12345, "Test")


@pytest.mark.asyncio
async def test_send_message_handles_chat_not_found(mock_telegram_bot):
    """
    GIVEN an invalid chat_id
    WHEN sending a message
    THEN TelegramChatNotFoundError is raised
    """
    mock_telegram_bot.send_message.side_effect = telegram.error.BadRequest("Chat not found")

    notifier = TelegramNotifier(bot_token="test_token")

    with pytest.raises(TelegramChatNotFoundError):
        await notifier.send_message(999999999, "Test")


@pytest.mark.asyncio
async def test_send_message_handles_blocked_by_user(mock_telegram_bot):
    """
    GIVEN a chat where bot is blocked
    WHEN sending a message
    THEN TelegramChatNotFoundError is raised
    """
    mock_telegram_bot.send_message.side_effect = telegram.error.Forbidden("Bot was blocked")

    notifier = TelegramNotifier(bot_token="test_token")

    with pytest.raises(TelegramChatNotFoundError):
        await notifier.send_message(12345, "Test")


@pytest.mark.asyncio
async def test_send_message_handles_network_error(mock_telegram_bot):
    """
    GIVEN a network connectivity issue
    WHEN sending a message
    THEN TelegramNetworkError is raised
    """
    mock_telegram_bot.send_message.side_effect = telegram.error.NetworkError("Connection timeout")

    notifier = TelegramNotifier(bot_token="test_token")

    with pytest.raises(TelegramNetworkError):
        await notifier.send_message(12345, "Test")


@pytest.mark.asyncio
async def test_send_message_handles_general_telegram_error(mock_telegram_bot):
    """
    GIVEN an unexpected Telegram API error
    WHEN sending a message
    THEN TelegramDeliveryError is raised
    """
    mock_telegram_bot.send_message.side_effect = telegram.error.TelegramError("Unknown error")

    notifier = TelegramNotifier(bot_token="test_token")

    with pytest.raises(TelegramDeliveryError):
        await notifier.send_message(12345, "Test")


def test_format_duration_handles_various_lengths():
    """
    GIVEN durations from minutes to days
    WHEN formatting duration
    THEN readable format is returned
    """
    notifier = TelegramNotifier(bot_token="test_token")

    assert notifier._format_duration(timedelta(minutes=45)) == "45m"

    assert notifier._format_duration(timedelta(hours=2)) == "2h 0m"

    assert notifier._format_duration(timedelta(hours=5, minutes=30)) == "5h 30m"

    assert notifier._format_duration(timedelta(days=1, hours=2)) == "1d 2h 0m"


def test_format_datetime_handles_timezone_aware():
    """
    GIVEN a timezone-aware datetime
    WHEN formatting datetime
    THEN timezone info is preserved in output
    """
    notifier = TelegramNotifier(bot_token="test_token")

    # Timezone-naive for simplicity in test
    dt = datetime(2026, 3, 15, 8, 30)
    formatted = notifier._format_datetime(dt)

    assert "Mar" in formatted or "03" in formatted
    assert "15" in formatted
    assert "08" in formatted or "8" in formatted
    assert "30" in formatted


def test_escape_markdown_escapes_all_special_chars():
    """
    GIVEN text with all MarkdownV2 special characters
    WHEN escaping
    THEN all special chars are properly escaped
    """
    notifier = TelegramNotifier(bot_token="test_token")

    text = "Test_text*with[special]chars(and)more~symbols`here"
    escaped = notifier._escape_markdown(text)

    assert "\\_" in escaped
    assert "\\*" in escaped
    assert "\\[" in escaped
    assert "\\]" in escaped
    assert "\\(" in escaped
    assert "\\)" in escaped
    assert "\\~" in escaped
    assert "\\`" in escaped


def test_generate_booking_link_creates_valid_url(sample_flight_offer):
    """
    GIVEN a flight offer
    WHEN generating booking link
    THEN a valid URL is returned
    """
    notifier = TelegramNotifier(bot_token="test_token")
    link = notifier._generate_booking_link(sample_flight_offer)

    assert link.startswith("http")
    assert "JFK" in link
    assert "LAX" in link


def test_uses_test_environment_base_url(mocker):
    """
    GIVEN use_test_environment=True
    WHEN creating TelegramNotifier
    THEN Bot is initialized with test API base URL callable
    """
    mock_bot_class = mocker.patch("raton.services.telegram.telegram.Bot")

    TelegramNotifier(bot_token="test_token_123", use_test_environment=True)

    mock_bot_class.assert_called_once()
    call_kwargs = mock_bot_class.call_args.kwargs

    assert "base_url" in call_kwargs
    assert callable(call_kwargs["base_url"])

    test_url = call_kwargs["base_url"]("test_token_123")
    assert test_url == "https://api.telegram.org/bottest_token_123/test"

    assert "base_file_url" in call_kwargs
    assert callable(call_kwargs["base_file_url"])
    test_file_url = call_kwargs["base_file_url"]("test_token_123")
    assert test_file_url == "https://api.telegram.org/file/bottest_token_123/test"
