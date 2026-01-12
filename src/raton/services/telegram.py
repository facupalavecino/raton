"""Telegram notification service.

This module provides functionality for sending flight deal notifications to users
via the Telegram Bot API.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

import telegram

from raton.config import Settings
from raton.models.flight import FlightOffer
from raton.services.exceptions import (
    TelegramAuthError,
    TelegramChatNotFoundError,
    TelegramDeliveryError,
    TelegramNetworkError,
)
from raton.services.rules import MatchResult


class TelegramNotifier:
    """Async client for sending Telegram notifications.

    Sends formatted flight deal notifications to users via Telegram Bot API.
    Supports both production and test environments.

    Args:
        bot_token: Telegram bot token from @BotFather
        use_test_environment: If True, use Telegram's test environment

    Example:
        >>> notifier = TelegramNotifier(bot_token="token", use_test_environment=True)
        >>> await notifier.send_flight_deal(chat_id=12345, flight=offer, match_result=result)
    """

    def __init__(self, bot_token: str, use_test_environment: bool = False):
        """Initialize the Telegram notifier.

        Args:
            bot_token: Telegram bot token
            use_test_environment: Whether to use test environment
        """
        if use_test_environment:
            # Telegram test environment uses /test/ suffix in the URL path
            # For test env we need: https://api.telegram.org/bot{token}/test/{method}
            # Use callable base_url to insert /test after the token
            def test_base_url(token: str) -> str:
                return f"https://api.telegram.org/bot{token}/test"

            def test_file_url(token: str) -> str:
                return f"https://api.telegram.org/file/bot{token}/test"

            self._bot = telegram.Bot(
                token=bot_token,
                base_url=test_base_url,
                base_file_url=test_file_url,
            )
        else:
            self._bot = telegram.Bot(token=bot_token)

    @classmethod
    def from_settings(cls, settings: Settings) -> TelegramNotifier:
        """Create a TelegramNotifier from application settings.

        Args:
            settings: Application settings

        Returns:
            Configured TelegramNotifier instance
        """
        return cls(
            bot_token=settings.telegram_bot_token,
            use_test_environment=settings.telegram_use_test_environment,
        )

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "MarkdownV2") -> None:
        """Send a text message to a Telegram chat.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            parse_mode: Telegram parse mode (default: MarkdownV2)

        Raises:
            TelegramAuthError: If bot token is invalid
            TelegramChatNotFoundError: If chat_id is invalid or bot blocked
            TelegramNetworkError: If network error occurs
            TelegramDeliveryError: If message cannot be delivered
        """
        try:
            await self._bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except telegram.error.InvalidToken as e:
            raise TelegramAuthError(f"Invalid bot token: {e}") from e
        except telegram.error.Forbidden as e:
            raise TelegramChatNotFoundError(f"Bot blocked or chat forbidden: {e}") from e
        except telegram.error.BadRequest as e:
            raise TelegramChatNotFoundError(f"Invalid chat_id or bad request: {e}") from e
        except telegram.error.NetworkError as e:
            raise TelegramNetworkError(f"Network error: {e}") from e
        except telegram.error.TelegramError as e:
            raise TelegramDeliveryError(f"Failed to deliver message: {e}") from e

    async def send_flight_deal(
        self, chat_id: int, flight: FlightOffer, match_result: MatchResult
    ) -> None:
        """Send a formatted flight deal notification.

        Args:
            chat_id: Telegram chat ID to notify
            flight: The flight offer to notify about
            match_result: Deal evaluation result with reasons

        Raises:
            TelegramDeliveryError: If notification cannot be sent
            TelegramAuthError: If bot token is invalid
            TelegramChatNotFoundError: If chat not found
            TelegramNetworkError: If network error occurs
        """
        message = self._format_flight_deal(flight, match_result)
        await self.send_message(chat_id, message)

    def _format_flight_deal(self, flight: FlightOffer, match_result: MatchResult) -> str:
        """Format a flight deal as a Telegram message.

        Creates a comprehensive, readable message with:
        - Route and flight type (one-way/round-trip)
        - Price with currency
        - Departure/arrival times
        - Duration and stops
        - Airline
        - Why it's a good deal (match reasons)
        - Booking link

        Args:
            flight: The flight offer
            match_result: Evaluation result with passed reasons

        Returns:
            Formatted message string with MarkdownV2 escaping
        """
        lines = ["✈️ *Great Deal Found\\!*", ""]

        first_segment = flight.itineraries[0].segments[0]
        last_segment = flight.itineraries[-1].segments[-1]
        origin = self._escape_markdown(first_segment.departure_airport)
        destination = self._escape_markdown(last_segment.arrival_airport)

        trip_type = "Round\\-trip" if flight.is_round_trip else "One\\-way"

        lines.append(f"*Route:* {origin} → {destination}")
        lines.append(f"*Type:* {trip_type}")

        price_str = self._escape_markdown(f"${flight.price.total} {flight.price.currency}")
        lines.append(f"*Price:* {price_str}")
        lines.append("")

        if flight.is_round_trip:
            lines.append("🛫 *Outbound*")
            lines.extend(self._format_itinerary(flight.itineraries[0]))
            lines.append("")

            lines.append("🛬 *Return*")
            lines.extend(self._format_itinerary(flight.itineraries[1]))
            lines.append("")
        else:
            lines.append("🛫 *Flight Details*")
            lines.extend(self._format_itinerary(flight.itineraries[0]))
            lines.append("")

        if match_result.passed_reasons:
            lines.append("📊 *Why this is a deal:*")
            for reason in match_result.passed_reasons:
                escaped_reason = self._escape_markdown(reason)
                lines.append(f"✓ {escaped_reason}")
            lines.append("")

        booking_link = self._generate_booking_link(flight)
        lines.append(f"[Book this flight]({booking_link})")

        return "\n".join(lines)

    def _format_itinerary(self, itinerary) -> list[str]:
        """Format a single itinerary for display.

        Args:
            itinerary: The Itinerary to format

        Returns:
            List of formatted lines
        """
        lines = []
        first_seg = itinerary.segments[0]
        last_seg = itinerary.segments[-1]

        dep_time = self._format_datetime(first_seg.departure_time)
        dep_airport = self._escape_markdown(first_seg.departure_airport)
        lines.append(f"• Departs: {dep_time} \\({dep_airport}\\)")

        arr_time = self._format_datetime(last_seg.arrival_time)
        arr_airport = self._escape_markdown(last_seg.arrival_airport)
        lines.append(f"• Arrives: {arr_time} \\({arr_airport}\\)")

        duration_str = self._escape_markdown(self._format_duration(itinerary.total_duration))
        lines.append(f"• Duration: {duration_str}")

        stops = itinerary.stops
        stop_text = "Direct flight" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        lines.append(f"• Stops: {stop_text}")

        airline = self._escape_markdown(first_seg.airline)
        lines.append(f"• Airline: {airline}")

        return lines

    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Telegram MarkdownV2.

        Telegram MarkdownV2 requires escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !

        Args:
            text: Text to escape

        Returns:
            Escaped text safe for MarkdownV2
        """
        special_chars = r"_*[]()~`>#+-=|{}.!"
        return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", str(text))

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for display in notifications.

        Args:
            dt: Datetime to format

        Returns:
            Formatted string (e.g., "Mar 15, 08:00 AM")
        """
        return dt.strftime("%b %d, %I:%M %p")

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display.

        Args:
            duration: Duration to format

        Returns:
            Human-readable duration (e.g., "5h 30m", "1d 2h 0m")
        """
        total_minutes, _ = divmod(int(duration.total_seconds()), 60)
        hours, minutes = divmod(total_minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"

        if hours > 0:
            return f"{hours}h {minutes}m"

        return f"{minutes}m"

    def _generate_booking_link(self, flight: FlightOffer) -> str:
        """Generate a booking link for the flight.

        Since Amadeus API doesn't provide direct booking links, generate a
        Google Flights search URL.

        Args:
            flight: The flight offer

        Returns:
            Booking/search URL
        """
        first_segment = flight.itineraries[0].segments[0]
        last_segment = flight.itineraries[0].segments[-1]

        origin = first_segment.departure_airport
        destination = last_segment.arrival_airport
        date = first_segment.departure_time.strftime("%Y-%m-%d")
        currency = flight.price.currency

        url = f"https://www.google.com/flights?hl=en#flt={origin}.{destination}.{date}"

        if flight.is_round_trip and len(flight.itineraries) > 1:
            return_date = flight.itineraries[1].segments[0].departure_time.strftime("%Y-%m-%d")
            url += f".{return_date}"

        url += f";c:{currency};e:1"

        return url
