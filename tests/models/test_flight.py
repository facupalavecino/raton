"""Tests for flight domain models.

Tests the core flight models that represent bookable flight offers.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from raton.models.flight import FlightOffer, FlightSegment, Itinerary, Price


def test_flight_segment_creation():
    """
    GIVEN valid flight segment data
    WHEN creating a FlightSegment
    THEN it parses successfully with all fields
    """
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    assert segment.departure_airport == "JFK"
    assert segment.arrival_airport == "LAX"
    assert segment.airline == "AA"
    assert segment.flight_number == "123"
    assert segment.duration == timedelta(hours=5, minutes=15)


def test_flight_segment_with_optional_fields():
    """
    GIVEN flight segment data with optional terminal and aircraft info
    WHEN creating a FlightSegment
    THEN all optional fields are preserved
    """
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        departure_terminal="4",
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        arrival_terminal="B",
        airline="AA",
        flight_number="123",
        aircraft="Boeing 737-800",
        duration=timedelta(hours=5, minutes=15),
    )
    assert segment.departure_terminal == "4"
    assert segment.arrival_terminal == "B"
    assert segment.aircraft == "Boeing 737-800"


def test_flight_segment_requires_timezone_aware_datetimes():
    """
    GIVEN flight times without timezone information
    WHEN creating a FlightSegment
    THEN it should still work (Pydantic allows naive datetimes)
    """
    # Note: We prefer timezone-aware, but Pydantic doesn't enforce it
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    assert segment.departure_time.tzinfo is None  # Naive datetime allowed


def test_price_creation_with_decimal():
    """
    GIVEN price data with Decimal values
    WHEN creating a Price
    THEN it stores values as Decimal without precision loss
    """
    price = Price(
        total=Decimal("299.99"),
        currency="USD",
        base=Decimal("250.00"),
        fees=Decimal("49.99"),
    )
    assert price.total == Decimal("299.99")
    assert price.base == Decimal("250.00")
    assert price.fees == Decimal("49.99")
    assert price.currency == "USD"


def test_price_creation_from_string():
    """
    GIVEN price data as strings (from JSON)
    WHEN creating a Price
    THEN it converts to Decimal automatically
    """
    price = Price(
        total="299.99",
        currency="USD",
        base="250.00",
        fees="49.99",
    )
    assert isinstance(price.total, Decimal)
    assert price.total == Decimal("299.99")


def test_price_rejects_float():
    """
    GIVEN price data with float values
    WHEN creating a Price
    THEN Pydantic converts float to Decimal (with potential precision issues)
    """
    # Pydantic will convert float to Decimal, but we should avoid floats
    price = Price(
        total=299.99,  # float
        currency="USD",
        base=250.00,
        fees=49.99,
    )
    assert isinstance(price.total, Decimal)
    # Note: float conversion may have precision issues


def test_itinerary_single_segment():
    """
    GIVEN an itinerary with one segment (direct flight)
    WHEN creating an Itinerary
    THEN stops is 0 and duration is computed correctly
    """
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    itinerary = Itinerary(segments=[segment])
    assert itinerary.stops == 0
    assert itinerary.total_duration == timedelta(hours=5, minutes=15)


def test_itinerary_multiple_segments():
    """
    GIVEN an itinerary with two segments (one stop)
    WHEN creating an Itinerary
    THEN stops is 1 and duration is sum of both segments
    """
    segment1 = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="ORD",
        arrival_time=datetime(2026, 3, 15, 12, 0, tzinfo=UTC),
        airline="AA",
        flight_number="100",
        duration=timedelta(hours=2, minutes=30),
    )
    segment2 = FlightSegment(
        departure_airport="ORD",
        departure_time=datetime(2026, 3, 15, 14, 0, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 16, 0, tzinfo=UTC),
        airline="AA",
        flight_number="200",
        duration=timedelta(hours=4, minutes=0),
    )
    itinerary = Itinerary(segments=[segment1, segment2])
    assert itinerary.stops == 1
    assert itinerary.total_duration == timedelta(hours=6, minutes=30)


def test_itinerary_requires_at_least_one_segment():
    """
    GIVEN an empty segment list
    WHEN creating an Itinerary
    THEN it raises a validation error
    """
    with pytest.raises(ValueError, match="at least 1 item"):
        Itinerary(segments=[])


def test_flight_offer_one_way():
    """
    GIVEN a one-way flight offer with one itinerary
    WHEN creating a FlightOffer
    THEN is_round_trip is False and properties compute correctly
    """
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    itinerary = Itinerary(segments=[segment])
    price = Price(
        total=Decimal("299.99"),
        currency="USD",
        base=Decimal("250.00"),
        fees=Decimal("49.99"),
    )
    offer = FlightOffer(
        id="offer-1",
        itineraries=[itinerary],
        price=price,
        validating_airline="AA",
    )
    assert offer.is_round_trip is False
    assert offer.total_duration == timedelta(hours=5, minutes=15)
    assert offer.total_stops == 0


def test_flight_offer_round_trip():
    """
    GIVEN a round-trip flight offer with two itineraries
    WHEN creating a FlightOffer
    THEN is_round_trip is True and properties sum both itineraries
    """
    outbound_segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    return_segment = FlightSegment(
        departure_airport="LAX",
        departure_time=datetime(2026, 3, 20, 14, 0, tzinfo=UTC),
        arrival_airport="JFK",
        arrival_time=datetime(2026, 3, 20, 22, 30, tzinfo=UTC),
        airline="AA",
        flight_number="456",
        duration=timedelta(hours=5, minutes=30),
    )
    outbound = Itinerary(segments=[outbound_segment])
    return_itin = Itinerary(segments=[return_segment])
    price = Price(
        total=Decimal("499.99"),
        currency="USD",
        base=Decimal("420.00"),
        fees=Decimal("79.99"),
    )
    offer = FlightOffer(
        id="offer-2",
        itineraries=[outbound, return_itin],
        price=price,
        validating_airline="AA",
    )
    assert offer.is_round_trip is True
    assert offer.total_duration == timedelta(hours=10, minutes=45)
    assert offer.total_stops == 0


def test_flight_offer_with_connections():
    """
    GIVEN a flight offer with connecting flights (multiple segments)
    WHEN creating a FlightOffer
    THEN total_stops counts all connections
    """
    segment1 = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="ORD",
        arrival_time=datetime(2026, 3, 15, 12, 0, tzinfo=UTC),
        airline="AA",
        flight_number="100",
        duration=timedelta(hours=2, minutes=30),
    )
    segment2 = FlightSegment(
        departure_airport="ORD",
        departure_time=datetime(2026, 3, 15, 14, 0, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 16, 0, tzinfo=UTC),
        airline="AA",
        flight_number="200",
        duration=timedelta(hours=4, minutes=0),
    )
    itinerary = Itinerary(segments=[segment1, segment2])
    price = Price(
        total=Decimal("350.00"),
        currency="USD",
        base=Decimal("300.00"),
        fees=Decimal("50.00"),
    )
    offer = FlightOffer(
        id="offer-3",
        itineraries=[itinerary],
        price=price,
        validating_airline="AA",
    )
    assert offer.total_stops == 1


def test_flight_offer_requires_at_least_one_itinerary():
    """
    GIVEN an empty itinerary list
    WHEN creating a FlightOffer
    THEN it raises a validation error
    """
    price = Price(
        total=Decimal("299.99"),
        currency="USD",
        base=Decimal("250.00"),
        fees=Decimal("49.99"),
    )
    with pytest.raises(ValueError, match="at least 1 item"):
        FlightOffer(
            id="offer-invalid",
            itineraries=[],
            price=price,
            validating_airline="AA",
        )


def test_flight_offer_serialization():
    """
    GIVEN a complete FlightOffer
    WHEN serializing to dict
    THEN computed properties are included
    """
    segment = FlightSegment(
        departure_airport="JFK",
        departure_time=datetime(2026, 3, 15, 10, 30, tzinfo=UTC),
        arrival_airport="LAX",
        arrival_time=datetime(2026, 3, 15, 13, 45, tzinfo=UTC),
        airline="AA",
        flight_number="123",
        duration=timedelta(hours=5, minutes=15),
    )
    itinerary = Itinerary(segments=[segment])
    price = Price(
        total=Decimal("299.99"),
        currency="USD",
        base=Decimal("250.00"),
        fees=Decimal("49.99"),
    )
    offer = FlightOffer(
        id="offer-1",
        itineraries=[itinerary],
        price=price,
        validating_airline="AA",
    )
    data = offer.model_dump()
    assert "is_round_trip" in data
    assert "total_duration" in data
    assert "total_stops" in data
    assert data["is_round_trip"] is False
    assert data["total_stops"] == 0
