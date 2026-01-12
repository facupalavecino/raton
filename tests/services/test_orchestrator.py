"""Tests for the check orchestrator service.

This module tests the CheckOrchestrator which coordinates flight check cycles.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from raton.models import (
    DateRange,
    FlightOffer,
    FlightSegment,
    Itinerary,
    Price,
    Route,
    UserPreferences,
)
from raton.services.exceptions import AmadeusApiError, TelegramDeliveryError
from raton.services.orchestrator import CheckOrchestrator


@pytest.fixture
def mock_amadeus():
    """Create a mock AmadeusClient."""
    return AsyncMock()


@pytest.fixture
def mock_preferences():
    """Create a mock PreferencesRepository."""
    return AsyncMock()


@pytest.fixture
def mock_notifier():
    """Create a mock TelegramNotifier."""
    return AsyncMock()


@pytest.fixture
def orchestrator(mock_amadeus, mock_preferences, mock_notifier):
    """Create a CheckOrchestrator with mocked dependencies."""
    return CheckOrchestrator(
        amadeus=mock_amadeus,
        preferences=mock_preferences,
        notifier=mock_notifier,
    )


@pytest.fixture
def sample_preferences() -> UserPreferences:
    """Create sample user preferences for testing."""
    return UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(earliest=date(2026, 3, 1), latest=date(2026, 3, 31)),
        max_price=Decimal("500.00"),
        currency="USD",
    )


@pytest.fixture
def sample_flight() -> FlightOffer:
    """Create a sample flight offer that matches preferences."""
    return FlightOffer(
        id="offer-1",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 11, 30),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=5, minutes=30),
                    )
                ]
            )
        ],
        price=Price(
            total=Decimal("400.00"),
            currency="USD",
            base=Decimal("350.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )


@pytest.fixture
def expensive_flight() -> FlightOffer:
    """Create a sample flight offer that exceeds price limit."""
    return FlightOffer(
        id="offer-2",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 11, 30),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=5, minutes=30),
                    )
                ]
            )
        ],
        price=Price(
            total=Decimal("600.00"),  # Over the $500 limit
            currency="USD",
            base=Decimal("550.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )


# Happy Path Tests


@pytest.mark.asyncio
async def test_run_check_cycle_with_one_user_finds_deal(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    sample_flight: FlightOffer,
):
    """
    GIVEN one user with preferences and a matching flight
    WHEN running a check cycle
    THEN it searches flights, evaluates rules, and sends notification
    """
    # Setup
    chat_id = 12345
    mock_preferences.list_users.return_value = [chat_id]
    mock_preferences.load.return_value = sample_preferences
    mock_amadeus.search_flights.return_value = [sample_flight]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 1
    assert result.routes_searched == 1
    assert result.flights_found == 1
    assert result.deals_matched == 1
    assert result.notifications_sent == 1
    assert result.errors == 0

    mock_preferences.list_users.assert_called_once()
    mock_preferences.load.assert_called_once_with(chat_id)
    mock_amadeus.search_flights.assert_called_once()
    mock_notifier.send_flight_deal.assert_called_once()


@pytest.mark.asyncio
async def test_run_check_cycle_with_multiple_users(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    sample_flight: FlightOffer,
):
    """
    GIVEN multiple users with preferences
    WHEN running a check cycle
    THEN it processes all users
    """
    # Setup
    chat_ids = [12345, 67890]
    mock_preferences.list_users.return_value = chat_ids
    mock_preferences.load.return_value = sample_preferences
    mock_amadeus.search_flights.return_value = [sample_flight]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 2
    assert result.routes_searched == 2  # 1 route per user
    assert result.notifications_sent == 2  # 1 deal per user
    assert result.errors == 0

    assert mock_preferences.load.call_count == 2
    assert mock_amadeus.search_flights.call_count == 2
    assert mock_notifier.send_flight_deal.call_count == 2


@pytest.mark.asyncio
async def test_run_check_cycle_with_multiple_routes(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_flight: FlightOffer,
):
    """
    GIVEN a user with multiple routes in preferences
    WHEN running a check cycle
    THEN it searches all routes
    """
    # Setup
    prefs = UserPreferences(
        routes=[
            Route(origin="JFK", destination="LAX"),
            Route(origin="JFK", destination="SFO"),
        ],
        date_range=DateRange(earliest=date(2026, 3, 1), latest=date(2026, 3, 31)),
        max_price=Decimal("500.00"),
        currency="USD",
    )
    mock_preferences.list_users.return_value = [12345]
    mock_preferences.load.return_value = prefs
    mock_amadeus.search_flights.return_value = [sample_flight]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 1
    assert result.routes_searched == 2
    assert mock_amadeus.search_flights.call_count == 2


# Edge Cases


@pytest.mark.asyncio
async def test_run_check_cycle_no_users(
    orchestrator: CheckOrchestrator,
    mock_preferences: AsyncMock,
):
    """
    GIVEN no users have saved preferences
    WHEN running a check cycle
    THEN it returns empty result with no errors
    """
    # Setup
    mock_preferences.list_users.return_value = []

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 0
    assert result.routes_searched == 0
    assert result.flights_found == 0
    assert result.deals_matched == 0
    assert result.notifications_sent == 0
    assert result.errors == 0


@pytest.mark.asyncio
async def test_run_check_cycle_no_flights_found(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
):
    """
    GIVEN a user with preferences but no flights available
    WHEN running a check cycle
    THEN it completes without sending notifications
    """
    # Setup
    mock_preferences.list_users.return_value = [12345]
    mock_preferences.load.return_value = sample_preferences
    mock_amadeus.search_flights.return_value = []  # No flights

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 1
    assert result.routes_searched == 1
    assert result.flights_found == 0
    assert result.deals_matched == 0
    assert result.notifications_sent == 0
    assert result.errors == 0

    mock_notifier.send_flight_deal.assert_not_called()


@pytest.mark.asyncio
async def test_run_check_cycle_no_deals_match(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    expensive_flight: FlightOffer,
):
    """
    GIVEN flights that don't match user preferences (too expensive)
    WHEN running a check cycle
    THEN it completes without sending notifications
    """
    # Setup
    mock_preferences.list_users.return_value = [12345]
    mock_preferences.load.return_value = sample_preferences
    mock_amadeus.search_flights.return_value = [expensive_flight]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify
    assert result.users_checked == 1
    assert result.routes_searched == 1
    assert result.flights_found == 1
    assert result.deals_matched == 0  # Didn't match
    assert result.notifications_sent == 0
    assert result.errors == 0

    mock_notifier.send_flight_deal.assert_not_called()


# Error Handling Tests


@pytest.mark.asyncio
async def test_run_check_cycle_amadeus_error_continues(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    sample_flight: FlightOffer,
):
    """
    GIVEN an Amadeus API error for one route
    WHEN running a check cycle
    THEN it logs the error and continues to the next route/user
    """
    # Setup - Two users, first one's search fails
    prefs_with_two_routes = UserPreferences(
        routes=[
            Route(origin="JFK", destination="LAX"),
            Route(origin="JFK", destination="SFO"),
        ],
        date_range=DateRange(earliest=date(2026, 3, 1), latest=date(2026, 3, 31)),
        max_price=Decimal("500.00"),
        currency="USD",
    )
    mock_preferences.list_users.return_value = [12345]
    mock_preferences.load.return_value = prefs_with_two_routes
    # First search fails, second succeeds
    mock_amadeus.search_flights.side_effect = [
        AmadeusApiError("API error"),
        [sample_flight],
    ]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify - Continued despite error
    assert result.users_checked == 1
    assert result.routes_searched == 2
    assert result.errors == 1  # One error recorded
    assert result.flights_found == 1  # From second search
    assert result.deals_matched == 1
    assert result.notifications_sent == 1


@pytest.mark.asyncio
async def test_run_check_cycle_telegram_error_continues(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    sample_flight: FlightOffer,
):
    """
    GIVEN a Telegram notification failure
    WHEN running a check cycle
    THEN it logs the error and continues
    """
    # Setup
    mock_preferences.list_users.return_value = [12345]
    mock_preferences.load.return_value = sample_preferences
    mock_amadeus.search_flights.return_value = [sample_flight]
    mock_notifier.send_flight_deal.side_effect = TelegramDeliveryError("Failed")

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify - Recorded error but continued
    assert result.users_checked == 1
    assert result.routes_searched == 1
    assert result.flights_found == 1
    assert result.deals_matched == 1
    assert result.notifications_sent == 0  # Failed
    assert result.errors == 1


@pytest.mark.asyncio
async def test_run_check_cycle_preferences_load_error_continues(
    orchestrator: CheckOrchestrator,
    mock_amadeus: AsyncMock,
    mock_preferences: AsyncMock,
    mock_notifier: AsyncMock,
    sample_preferences: UserPreferences,
    sample_flight: FlightOffer,
):
    """
    GIVEN a corrupted preferences file for one user
    WHEN running a check cycle
    THEN it logs the error and continues to the next user
    """
    from raton.services.exceptions import PreferencesStorageError

    # Setup - Two users, first one has corrupted preferences
    mock_preferences.list_users.return_value = [11111, 22222]
    mock_preferences.load.side_effect = [
        PreferencesStorageError("Corrupted file"),
        sample_preferences,
    ]
    mock_amadeus.search_flights.return_value = [sample_flight]

    # Execute
    result = await orchestrator.run_check_cycle()

    # Verify - Continued to second user
    assert result.users_checked == 1  # Only second user was successfully checked
    assert result.routes_searched == 1
    assert result.errors == 1  # Error loading first user's prefs
    assert result.notifications_sent == 1  # Second user got notification
