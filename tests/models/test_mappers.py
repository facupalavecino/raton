"""Tests for mapper functions.

Tests the conversion functions that transform Amadeus API responses
into domain models.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from raton.models.flight import FlightOffer
from raton.models.mappers import amadeus_to_flight_offer, parse_iso8601_duration


def test_parse_iso8601_duration_hours_only():
    """
    GIVEN an ISO 8601 duration string with only hours
    WHEN parsing it
    THEN it returns the correct timedelta
    """
    assert parse_iso8601_duration("PT2H") == timedelta(hours=2)


def test_parse_iso8601_duration_minutes_only():
    """
    GIVEN an ISO 8601 duration string with only minutes
    WHEN parsing it
    THEN it returns the correct timedelta
    """
    assert parse_iso8601_duration("PT30M") == timedelta(minutes=30)


def test_parse_iso8601_duration_hours_and_minutes():
    """
    GIVEN an ISO 8601 duration string with hours and minutes
    WHEN parsing it
    THEN it returns the correct timedelta
    """
    assert parse_iso8601_duration("PT2H30M") == timedelta(hours=2, minutes=30)


def test_parse_iso8601_duration_with_seconds():
    """
    GIVEN an ISO 8601 duration string with hours, minutes, and seconds
    WHEN parsing it
    THEN it returns the correct timedelta
    """
    assert parse_iso8601_duration("PT1H15M30S") == timedelta(hours=1, minutes=15, seconds=30)


def test_parse_iso8601_duration_seconds_only():
    """
    GIVEN an ISO 8601 duration string with only seconds
    WHEN parsing it
    THEN it returns the correct timedelta
    """
    assert parse_iso8601_duration("PT45S") == timedelta(seconds=45)


def test_parse_iso8601_duration_invalid_format():
    """
    GIVEN an invalid ISO 8601 duration string
    WHEN parsing it
    THEN it raises a ValueError
    """
    with pytest.raises(ValueError, match="Invalid ISO 8601 duration"):
        parse_iso8601_duration("2H30M")  # Missing PT prefix


def test_parse_iso8601_duration_empty_components():
    """
    GIVEN an ISO 8601 duration with just PT
    WHEN parsing it
    THEN it returns zero timedelta
    """
    assert parse_iso8601_duration("PT0H") == timedelta()


def test_amadeus_to_flight_offer_one_way_direct():
    """
    GIVEN an Amadeus flight offer with one direct flight
    WHEN converting to domain model
    THEN it creates a valid FlightOffer
    """
    amadeus_offer = {
        "type": "flight-offer",
        "id": "1",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": True,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 9,
        "itineraries": [
            {
                "duration": "PT5H15M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "at": "2026-03-15T10:30:00-05:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T13:45:00-08:00",
                        },
                        "carrierCode": "AA",
                        "number": "123",
                        "duration": "PT5H15M",
                    }
                ],
            }
        ],
        "price": {
            "currency": "USD",
            "total": "299.99",
            "base": "250.00",
            "fees": [{"amount": "49.99", "type": "SUPPLIER"}],
        },
        "validatingAirlineCodes": ["AA"],
    }

    offer = amadeus_to_flight_offer(amadeus_offer)

    assert isinstance(offer, FlightOffer)
    assert offer.id == "1"
    assert offer.is_round_trip is False
    assert offer.total_stops == 0
    assert len(offer.itineraries) == 1
    assert len(offer.itineraries[0].segments) == 1
    assert offer.itineraries[0].segments[0].departure_airport == "JFK"
    assert offer.itineraries[0].segments[0].arrival_airport == "LAX"
    assert offer.itineraries[0].segments[0].airline == "AA"
    assert offer.itineraries[0].segments[0].flight_number == "123"
    assert offer.price.total == Decimal("299.99")
    assert offer.price.currency == "USD"
    assert offer.price.base == Decimal("250.00")
    assert offer.validating_airline == "AA"


def test_amadeus_to_flight_offer_round_trip():
    """
    GIVEN an Amadeus flight offer with round-trip itineraries
    WHEN converting to domain model
    THEN it creates a valid round-trip FlightOffer
    """
    amadeus_offer = {
        "type": "flight-offer",
        "id": "2",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": False,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 5,
        "itineraries": [
            {
                "duration": "PT5H15M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "at": "2026-03-15T10:30:00-05:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T13:45:00-08:00",
                        },
                        "carrierCode": "AA",
                        "number": "123",
                        "duration": "PT5H15M",
                    }
                ],
            },
            {
                "duration": "PT5H30M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "LAX",
                            "at": "2026-03-20T14:00:00-08:00",
                        },
                        "arrival": {
                            "iataCode": "JFK",
                            "at": "2026-03-20T22:30:00-05:00",
                        },
                        "carrierCode": "AA",
                        "number": "456",
                        "duration": "PT5H30M",
                    }
                ],
            },
        ],
        "price": {
            "currency": "USD",
            "total": "499.99",
            "base": "420.00",
            "fees": [],
        },
        "validatingAirlineCodes": ["AA"],
    }

    offer = amadeus_to_flight_offer(amadeus_offer)

    assert offer.is_round_trip is True
    assert len(offer.itineraries) == 2
    assert offer.itineraries[0].segments[0].departure_airport == "JFK"
    assert offer.itineraries[1].segments[0].departure_airport == "LAX"
    assert offer.price.total == Decimal("499.99")


def test_amadeus_to_flight_offer_with_connection():
    """
    GIVEN an Amadeus flight offer with a connection (2 segments)
    WHEN converting to domain model
    THEN it creates a FlightOffer with correct stops
    """
    amadeus_offer = {
        "type": "flight-offer",
        "id": "3",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": True,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 7,
        "itineraries": [
            {
                "duration": "PT8H30M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "at": "2026-03-15T10:30:00-05:00",
                        },
                        "arrival": {
                            "iataCode": "ORD",
                            "at": "2026-03-15T12:00:00-06:00",
                        },
                        "carrierCode": "AA",
                        "number": "100",
                        "duration": "PT2H30M",
                    },
                    {
                        "departure": {
                            "iataCode": "ORD",
                            "at": "2026-03-15T14:00:00-06:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T16:00:00-08:00",
                        },
                        "carrierCode": "AA",
                        "number": "200",
                        "duration": "PT4H0M",
                    },
                ],
            }
        ],
        "price": {
            "currency": "USD",
            "total": "350.00",
            "base": "300.00",
            "fees": [{"amount": "50.00", "type": "TICKETING"}],
        },
        "validatingAirlineCodes": ["AA"],
    }

    offer = amadeus_to_flight_offer(amadeus_offer)

    assert offer.total_stops == 1
    assert len(offer.itineraries[0].segments) == 2
    assert offer.itineraries[0].segments[0].arrival_airport == "ORD"
    assert offer.itineraries[0].segments[1].departure_airport == "ORD"


def test_amadeus_to_flight_offer_with_optional_fields():
    """
    GIVEN an Amadeus offer with optional terminal and aircraft info
    WHEN converting to domain model
    THEN optional fields are preserved
    """
    amadeus_offer = {
        "type": "flight-offer",
        "id": "4",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": True,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 9,
        "itineraries": [
            {
                "duration": "PT5H15M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "terminal": "4",
                            "at": "2026-03-15T10:30:00-05:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "terminal": "B",
                            "at": "2026-03-15T13:45:00-08:00",
                        },
                        "carrierCode": "AA",
                        "number": "123",
                        "aircraft": {"code": "73H"},
                        "duration": "PT5H15M",
                    }
                ],
            }
        ],
        "price": {
            "currency": "USD",
            "total": "299.99",
            "base": "250.00",
            "fees": [],
        },
        "validatingAirlineCodes": ["AA"],
    }

    offer = amadeus_to_flight_offer(amadeus_offer)

    segment = offer.itineraries[0].segments[0]
    assert segment.departure_terminal == "4"
    assert segment.arrival_terminal == "B"
    assert segment.aircraft == "73H"


def test_amadeus_to_flight_offer_calculates_total_fees():
    """
    GIVEN an Amadeus offer with multiple fees
    WHEN converting to domain model
    THEN total fees are calculated correctly
    """
    amadeus_offer = {
        "type": "flight-offer",
        "id": "5",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": True,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 9,
        "itineraries": [
            {
                "duration": "PT5H15M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "at": "2026-03-15T10:30:00-05:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T13:45:00-08:00",
                        },
                        "carrierCode": "AA",
                        "number": "123",
                        "duration": "PT5H15M",
                    }
                ],
            }
        ],
        "price": {
            "currency": "USD",
            "total": "299.99",
            "base": "250.00",
            "fees": [
                {"amount": "30.00", "type": "SUPPLIER"},
                {"amount": "19.99", "type": "TICKETING"},
            ],
        },
        "validatingAirlineCodes": ["AA"],
    }

    offer = amadeus_to_flight_offer(amadeus_offer)

    assert offer.price.fees == Decimal("49.99")
