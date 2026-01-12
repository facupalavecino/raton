"""Integration tests for Amadeus API.

These tests call the real Amadeus test environment API to verify end-to-end
functionality. They require valid API credentials in .env and can be skipped
in CI using: pytest -m "not integration"
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from raton.config import get_settings
from raton.models import FlightOffer
from raton.services import AmadeusClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_flights_real_api():
    """
    GIVEN valid Amadeus API credentials
    WHEN searching for flights from JFK to LAX
    THEN a list of FlightOffer objects is returned
    """
    settings = get_settings()

    client = AmadeusClient.from_settings(settings)

    departure_date = date.today() + timedelta(days=30)

    offers = await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
    )

    assert isinstance(offers, list)
    if offers:
        offer = offers[0]
        assert isinstance(offer, FlightOffer)
        assert offer.price.total > 0
        assert offer.price.currency in ("USD", "EUR", "GBP")
        assert len(offer.itineraries) > 0
        first_itinerary = offer.itineraries[0]
        assert len(first_itinerary.segments) > 0
        assert first_itinerary.segments[0].departure_airport == "JFK"
        assert first_itinerary.segments[-1].arrival_airport == "LAX"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_round_trip_real_api():
    """
    GIVEN valid Amadeus API credentials
    WHEN searching for round-trip flights from JFK to LAX
    THEN a list of FlightOffer objects with 2 itineraries is returned
    """
    settings = get_settings()

    client = AmadeusClient.from_settings(settings)

    departure_date = date.today() + timedelta(days=30)
    return_date = date.today() + timedelta(days=37)

    offers = await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        return_date=return_date,
        adults=1,
    )

    assert isinstance(offers, list)
    if offers:
        offer = offers[0]
        assert isinstance(offer, FlightOffer)
        assert len(offer.itineraries) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_with_filters_real_api():
    """
    GIVEN valid Amadeus API credentials
    WHEN searching with max_results filter
    THEN filtered results are returned
    """
    settings = get_settings()

    client = AmadeusClient.from_settings(settings)

    departure_date = date.today() + timedelta(days=30)

    offers = await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
        max_results=5,
    )

    assert isinstance(offers, list)
    assert len(offers) <= 5
