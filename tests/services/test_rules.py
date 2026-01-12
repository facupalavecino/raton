"""Tests for deal detection rules engine.

This module tests the rules engine that evaluates flight offers against user preferences.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from raton.models import (
    DateRange,
    FlightOffer,
    FlightSegment,
    Itinerary,
    Price,
    Route,
    StopPreference,
    UserPreferences,
)
from raton.services.rules import (
    MatchResult,
    check_currency,
    check_duration,
    check_price,
    check_stops,
    evaluate_flight,
)


@pytest.fixture
def base_preferences() -> UserPreferences:
    """Create minimal valid preferences for testing.

    Returns:
        UserPreferences with basic requirements
    """
    return UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(earliest=date(2026, 3, 1), latest=date(2026, 3, 31)),
        max_price=Decimal("500.00"),
        currency="USD",
    )


@pytest.fixture
def base_flight() -> FlightOffer:
    """Create minimal valid flight offer for testing.

    Returns:
        FlightOffer with a single direct flight
    """
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


# Currency Rule Tests


def test_check_currency_matches(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight with USD currency and preferences with USD currency
    WHEN checking currency rule
    THEN the rule passes
    """
    passed, reason = check_currency(base_flight, base_preferences)

    assert passed is True
    assert "USD" in reason
    assert "matches" in reason.lower()


def test_check_currency_mismatch(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight with EUR currency and preferences with USD currency
    WHEN checking currency rule
    THEN the rule fails with clear explanation
    """
    # Modify flight to use EUR
    base_flight.price.currency = "EUR"

    passed, reason = check_currency(base_flight, base_preferences)

    assert passed is False
    assert "EUR" in reason
    assert "USD" in reason
    assert "mismatch" in reason.lower()


# Price Rule Tests


def test_check_price_under_budget(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight priced at $400 and max budget of $500
    WHEN checking price rule
    THEN the rule passes
    """
    passed, reason = check_price(base_flight, base_preferences)

    assert passed is True
    assert "400" in reason
    assert "500" in reason
    assert "within budget" in reason.lower()


def test_check_price_at_exact_budget(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight priced exactly at the max budget
    WHEN checking price rule
    THEN the rule passes
    """
    base_flight.price.total = Decimal("500.00")

    passed, reason = check_price(base_flight, base_preferences)

    assert passed is True
    assert "500" in reason


def test_check_price_over_budget(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight priced over the max budget
    WHEN checking price rule
    THEN the rule fails with clear explanation
    """
    base_flight.price.total = Decimal("600.00")

    passed, reason = check_price(base_flight, base_preferences)

    assert passed is False
    assert "600" in reason
    assert "500" in reason
    assert "exceeds" in reason.lower()


# Stops Rule Tests


def test_check_stops_any_with_direct_flight(
    base_flight: FlightOffer, base_preferences: UserPreferences
):
    """
    GIVEN a direct flight and ANY stop preference
    WHEN checking stops rule
    THEN the rule passes
    """
    base_preferences.stop_preference = StopPreference.ANY

    passed, reason = check_stops(base_flight, base_preferences)

    assert passed is True
    assert "0 stops" in reason or "any" in reason.lower()


def test_check_stops_any_with_connecting_flight(base_preferences: UserPreferences):
    """
    GIVEN a flight with 2 stops and ANY stop preference
    WHEN checking stops rule
    THEN the rule passes
    """
    base_preferences.stop_preference = StopPreference.ANY

    # Create flight with 2 stops (3 segments)
    flight = FlightOffer(
        id="offer-2",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="ORD",
                        arrival_time=datetime(2026, 3, 15, 10, 0),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        departure_time=datetime(2026, 3, 15, 11, 0),
                        arrival_airport="DEN",
                        arrival_time=datetime(2026, 3, 15, 13, 0),
                        airline="AA",
                        flight_number="101",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="DEN",
                        departure_time=datetime(2026, 3, 15, 14, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 16, 0),
                        airline="AA",
                        flight_number="102",
                        duration=timedelta(hours=2),
                    ),
                ]
            )
        ],
        price=Price(
            total=Decimal("300.00"),
            currency="USD",
            base=Decimal("250.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )

    passed, reason = check_stops(flight, base_preferences)

    assert passed is True
    assert "2 stops" in reason


def test_check_stops_direct_only_with_direct_flight(
    base_flight: FlightOffer, base_preferences: UserPreferences
):
    """
    GIVEN a direct flight and DIRECT_ONLY preference
    WHEN checking stops rule
    THEN the rule passes
    """
    base_preferences.stop_preference = StopPreference.DIRECT_ONLY

    passed, reason = check_stops(base_flight, base_preferences)

    assert passed is True
    assert "direct" in reason.lower()


def test_check_stops_direct_only_with_connecting_flight(base_preferences: UserPreferences):
    """
    GIVEN a flight with 1 stop and DIRECT_ONLY preference
    WHEN checking stops rule
    THEN the rule fails
    """
    base_preferences.stop_preference = StopPreference.DIRECT_ONLY

    # Create flight with 1 stop (2 segments)
    flight = FlightOffer(
        id="offer-3",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="ORD",
                        arrival_time=datetime(2026, 3, 15, 10, 0),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        departure_time=datetime(2026, 3, 15, 11, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 13, 0),
                        airline="AA",
                        flight_number="101",
                        duration=timedelta(hours=2),
                    ),
                ]
            )
        ],
        price=Price(
            total=Decimal("350.00"),
            currency="USD",
            base=Decimal("300.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )

    passed, reason = check_stops(flight, base_preferences)

    assert passed is False
    assert "1 stops" in reason
    assert "direct only" in reason.lower()


def test_check_stops_max_one_with_direct_flight(
    base_flight: FlightOffer, base_preferences: UserPreferences
):
    """
    GIVEN a direct flight and MAX_ONE_STOP preference
    WHEN checking stops rule
    THEN the rule passes
    """
    base_preferences.stop_preference = StopPreference.MAX_ONE_STOP

    passed, reason = check_stops(base_flight, base_preferences)

    assert passed is True
    assert "0 stops" in reason
    assert "max 1" in reason.lower()


def test_check_stops_max_one_with_one_stop(base_preferences: UserPreferences):
    """
    GIVEN a flight with 1 stop and MAX_ONE_STOP preference
    WHEN checking stops rule
    THEN the rule passes
    """
    base_preferences.stop_preference = StopPreference.MAX_ONE_STOP

    # Create flight with 1 stop
    flight = FlightOffer(
        id="offer-4",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="ORD",
                        arrival_time=datetime(2026, 3, 15, 10, 0),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        departure_time=datetime(2026, 3, 15, 11, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 13, 0),
                        airline="AA",
                        flight_number="101",
                        duration=timedelta(hours=2),
                    ),
                ]
            )
        ],
        price=Price(
            total=Decimal("350.00"),
            currency="USD",
            base=Decimal("300.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )

    passed, reason = check_stops(flight, base_preferences)

    assert passed is True
    assert "1 stops" in reason


def test_check_stops_max_one_with_two_stops(base_preferences: UserPreferences):
    """
    GIVEN a flight with 2 stops and MAX_ONE_STOP preference
    WHEN checking stops rule
    THEN the rule fails
    """
    base_preferences.stop_preference = StopPreference.MAX_ONE_STOP

    # Create flight with 2 stops
    flight = FlightOffer(
        id="offer-5",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="ORD",
                        arrival_time=datetime(2026, 3, 15, 10, 0),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        departure_time=datetime(2026, 3, 15, 11, 0),
                        arrival_airport="DEN",
                        arrival_time=datetime(2026, 3, 15, 13, 0),
                        airline="AA",
                        flight_number="101",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="DEN",
                        departure_time=datetime(2026, 3, 15, 14, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 16, 0),
                        airline="AA",
                        flight_number="102",
                        duration=timedelta(hours=2),
                    ),
                ]
            )
        ],
        price=Price(
            total=Decimal("300.00"),
            currency="USD",
            base=Decimal("250.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )

    passed, reason = check_stops(flight, base_preferences)

    assert passed is False
    assert "2 stops" in reason
    assert "max 1" in reason.lower()


# Duration Rule Tests


def test_check_duration_no_limit(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight and preferences with no max_duration set
    WHEN checking duration rule
    THEN the rule passes
    """
    assert base_preferences.max_duration is None

    passed, reason = check_duration(base_flight, base_preferences)

    assert passed is True
    assert "no duration limit" in reason.lower()


def test_check_duration_under_limit(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a 5.5-hour flight and 8-hour max duration
    WHEN checking duration rule
    THEN the rule passes
    """
    base_preferences.max_duration = timedelta(hours=8)

    passed, reason = check_duration(base_flight, base_preferences)

    assert passed is True
    assert "5:30:00" in reason
    assert "8:00:00" in reason
    assert "within limit" in reason.lower()


def test_check_duration_at_exact_limit(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a flight with duration exactly at the max limit
    WHEN checking duration rule
    THEN the rule passes
    """
    base_preferences.max_duration = timedelta(hours=5, minutes=30)

    passed, reason = check_duration(base_flight, base_preferences)

    assert passed is True
    assert "within limit" in reason.lower()


def test_check_duration_over_limit(base_flight: FlightOffer, base_preferences: UserPreferences):
    """
    GIVEN a 5.5-hour flight and 4-hour max duration
    WHEN checking duration rule
    THEN the rule fails
    """
    base_preferences.max_duration = timedelta(hours=4)

    passed, reason = check_duration(base_flight, base_preferences)

    assert passed is False
    assert "5:30:00" in reason
    assert "4:00:00" in reason
    assert "exceeds" in reason.lower()


# Integration Tests for evaluate_flight


def test_evaluate_flight_all_rules_pass(
    base_flight: FlightOffer, base_preferences: UserPreferences
):
    """
    GIVEN a flight that passes all rules
    WHEN evaluating the flight
    THEN is_match is True and all rules are in passed_reasons
    """
    result = evaluate_flight(base_flight, base_preferences)

    assert result.is_match is True
    assert len(result.passed_reasons) == 4  # currency, price, stops, duration
    assert len(result.failed_reasons) == 0


def test_evaluate_flight_one_rule_fails(
    base_flight: FlightOffer, base_preferences: UserPreferences
):
    """
    GIVEN a flight that fails the price rule
    WHEN evaluating the flight
    THEN is_match is False and price failure is in failed_reasons
    """
    base_flight.price.total = Decimal("600.00")  # Over budget

    result = evaluate_flight(base_flight, base_preferences)

    assert result.is_match is False
    assert len(result.passed_reasons) == 3  # currency, stops, duration pass
    assert len(result.failed_reasons) == 1  # price fails
    assert any("exceeds" in reason.lower() for reason in result.failed_reasons)


def test_evaluate_flight_multiple_rules_fail(base_preferences: UserPreferences):
    """
    GIVEN a flight that fails multiple rules
    WHEN evaluating the flight
    THEN is_match is False and all failures are captured
    """
    # Create a bad flight: wrong currency, over budget, has stops
    flight = FlightOffer(
        id="bad-offer",
        itineraries=[
            Itinerary(
                segments=[
                    FlightSegment(
                        departure_airport="JFK",
                        departure_time=datetime(2026, 3, 15, 8, 0),
                        arrival_airport="ORD",
                        arrival_time=datetime(2026, 3, 15, 10, 0),
                        airline="AA",
                        flight_number="100",
                        duration=timedelta(hours=2),
                    ),
                    FlightSegment(
                        departure_airport="ORD",
                        departure_time=datetime(2026, 3, 15, 11, 0),
                        arrival_airport="LAX",
                        arrival_time=datetime(2026, 3, 15, 13, 0),
                        airline="AA",
                        flight_number="101",
                        duration=timedelta(hours=2),
                    ),
                ]
            )
        ],
        price=Price(
            total=Decimal("700.00"),  # Over budget
            currency="EUR",  # Wrong currency
            base=Decimal("650.00"),
            fees=Decimal("50.00"),
        ),
        validating_airline="AA",
    )

    base_preferences.stop_preference = StopPreference.DIRECT_ONLY

    result = evaluate_flight(flight, base_preferences)

    assert result.is_match is False
    assert len(result.failed_reasons) == 3  # currency, price, stops
    assert len(result.passed_reasons) == 1  # only duration passes


def test_match_result_immutable():
    """
    GIVEN a MatchResult instance
    WHEN attempting to modify it
    THEN it raises a FrozenInstanceError or AttributeError (frozen dataclass)
    """
    result = MatchResult(
        is_match=True,
        passed_reasons=("test",),
        failed_reasons=(),
    )

    with pytest.raises((AttributeError, TypeError)):  # frozen dataclass error
        result.is_match = False  # type: ignore[misc]
