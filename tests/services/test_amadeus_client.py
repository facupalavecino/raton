"""Tests for Amadeus client.

This module tests the AmadeusClient for fetching flight offers from the API.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock

import pytest

from raton.models import CabinClass, FlightOffer
from raton.services.amadeus import AmadeusClient


@pytest.fixture
def mock_amadeus_sdk(mocker):
    """Mock the Amadeus SDK Client.

    Returns:
        Mock: A mock of the flight_offers_search endpoint.
    """
    mock_client = Mock()
    mock_search = Mock()
    mock_client.shopping.flight_offers_search = mock_search
    mocker.patch("raton.services.amadeus.Client", return_value=mock_client)
    return mock_search


@pytest.fixture
def sample_amadeus_response():
    """Sample Amadeus API response.

    Returns:
        dict: A minimal valid Amadeus API response.
    """
    return {
        "data": [
            {
                "type": "flight-offer",
                "id": "1",
                "source": "GDS",
                "instantTicketingRequired": False,
                "nonHomogeneous": False,
                "oneWay": False,
                "lastTicketingDate": "2026-02-01",
                "numberOfBookableSeats": 9,
                "itineraries": [
                    {
                        "duration": "PT5H30M",
                        "segments": [
                            {
                                "departure": {
                                    "iataCode": "JFK",
                                    "at": "2026-02-15T08:00:00",
                                },
                                "arrival": {
                                    "iataCode": "LAX",
                                    "at": "2026-02-15T11:30:00",
                                },
                                "carrierCode": "AA",
                                "number": "100",
                                "aircraft": {"code": "738"},
                                "duration": "PT5H30M",
                                "id": "1",
                                "numberOfStops": 0,
                            }
                        ],
                    }
                ],
                "price": {
                    "currency": "USD",
                    "total": "250.00",
                    "base": "200.00",
                    "grandTotal": "250.00",
                },
                "pricingOptions": {
                    "fareType": ["PUBLISHED"],
                    "includedCheckedBagsOnly": True,
                },
                "validatingAirlineCodes": ["AA"],
                "travelerPricings": [
                    {
                        "travelerId": "1",
                        "fareOption": "STANDARD",
                        "travelerType": "ADULT",
                        "price": {
                            "currency": "USD",
                            "total": "250.00",
                            "base": "200.00",
                        },
                        "fareDetailsBySegment": [
                            {
                                "segmentId": "1",
                                "cabin": "ECONOMY",
                                "fareBasis": "KZBR",
                                "class": "K",
                                "includedCheckedBags": {"weight": 23, "weightUnit": "KG"},
                            }
                        ],
                    }
                ],
            }
        ]
    }


@pytest.mark.asyncio
async def test_search_flights_returns_flight_offers(mock_amadeus_sdk, sample_amadeus_response):
    """
    GIVEN a valid Amadeus API response with flight offers
    WHEN searching for flights
    THEN a list of FlightOffer objects is returned
    """
    mock_response = Mock()
    mock_response.data = sample_amadeus_response["data"]
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    offers = await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
    )

    assert isinstance(offers, list)
    assert len(offers) == 1
    assert isinstance(offers[0], FlightOffer)
    assert offers[0].price.total == Decimal("250.00")
    assert offers[0].price.currency == "USD"


@pytest.mark.asyncio
async def test_search_flights_empty_results(mock_amadeus_sdk):
    """
    GIVEN an Amadeus API response with no flight offers
    WHEN searching for flights
    THEN an empty list is returned
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    offers = await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
    )

    assert offers == []


@pytest.mark.asyncio
async def test_search_flights_passes_correct_parameters(mock_amadeus_sdk):
    """
    GIVEN search parameters (origin, destination, date, adults)
    WHEN calling search_flights
    THEN the SDK is called with the correct parameters
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date(2026, 3, 15)

    await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=2,
    )

    mock_amadeus_sdk.get.assert_called_once()
    call_kwargs = mock_amadeus_sdk.get.call_args.kwargs

    assert call_kwargs["originLocationCode"] == "JFK"
    assert call_kwargs["destinationLocationCode"] == "LAX"
    assert call_kwargs["departureDate"] == "2026-03-15"
    assert call_kwargs["adults"] == 2


@pytest.mark.asyncio
async def test_search_flights_with_return_date(mock_amadeus_sdk):
    """
    GIVEN a return date for round-trip search
    WHEN calling search_flights with return_date
    THEN the SDK is called with returnDate parameter
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date(2026, 3, 15)
    return_date = date(2026, 3, 22)

    await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
        return_date=return_date,
    )

    call_kwargs = mock_amadeus_sdk.get.call_args.kwargs
    assert call_kwargs["returnDate"] == "2026-03-22"


@pytest.mark.asyncio
async def test_search_flights_with_cabin_class(mock_amadeus_sdk):
    """
    GIVEN a cabin class preference
    WHEN calling search_flights with cabin_class
    THEN the SDK is called with travelClass parameter
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date(2026, 3, 15)

    await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
        cabin_class=CabinClass.BUSINESS,
    )

    call_kwargs = mock_amadeus_sdk.get.call_args.kwargs
    assert call_kwargs["travelClass"] == "BUSINESS"


@pytest.mark.asyncio
async def test_search_flights_with_non_stop(mock_amadeus_sdk):
    """
    GIVEN non_stop=True to request direct flights only
    WHEN calling search_flights
    THEN the SDK is called with nonStop=true
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date(2026, 3, 15)

    await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
        non_stop=True,
    )

    call_kwargs = mock_amadeus_sdk.get.call_args.kwargs
    assert call_kwargs["nonStop"] is True


@pytest.mark.asyncio
async def test_search_flights_with_max_results(mock_amadeus_sdk):
    """
    GIVEN a max_results limit
    WHEN calling search_flights
    THEN the SDK is called with max parameter
    """
    mock_response = Mock()
    mock_response.data = []
    mock_amadeus_sdk.get.return_value = mock_response

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date(2026, 3, 15)

    await client.search_flights(
        origin="JFK",
        destination="LAX",
        departure_date=departure_date,
        adults=1,
        max_results=5,
    )

    call_kwargs = mock_amadeus_sdk.get.call_args.kwargs
    assert call_kwargs["max"] == 5


@pytest.mark.asyncio
async def test_search_flights_handles_auth_error_401(mock_amadeus_sdk, mocker):
    """
    GIVEN an API that returns 401 Unauthorized
    WHEN searching for flights
    THEN AmadeusAuthError is raised
    """
    from amadeus.client.errors import ResponseError

    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.parsed = False
    mock_response.result = {}
    error = ResponseError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusAuthError

    with pytest.raises(AmadeusAuthError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error


@pytest.mark.asyncio
async def test_search_flights_handles_auth_error_403(mock_amadeus_sdk, mocker):
    """
    GIVEN an API that returns 403 Forbidden
    WHEN searching for flights
    THEN AmadeusAuthError is raised
    """
    from amadeus.client.errors import ResponseError

    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.parsed = False
    mock_response.result = {}
    error = ResponseError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusAuthError

    with pytest.raises(AmadeusAuthError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error


@pytest.mark.asyncio
async def test_search_flights_handles_rate_limit_error(mock_amadeus_sdk, mocker):
    """
    GIVEN an API that returns 429 Too Many Requests
    WHEN searching for flights
    THEN AmadeusRateLimitError is raised
    """
    from amadeus.client.errors import ResponseError

    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.parsed = False
    mock_response.result = {}
    error = ResponseError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusRateLimitError

    with pytest.raises(AmadeusRateLimitError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error


@pytest.mark.asyncio
async def test_search_flights_handles_api_error_400(mock_amadeus_sdk, mocker):
    """
    GIVEN an API that returns 400 Bad Request
    WHEN searching for flights
    THEN AmadeusApiError is raised
    """
    from amadeus.client.errors import ResponseError

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.parsed = False
    mock_response.result = {}
    error = ResponseError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusApiError

    with pytest.raises(AmadeusApiError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error


@pytest.mark.asyncio
async def test_search_flights_handles_api_error_500(mock_amadeus_sdk, mocker):
    """
    GIVEN an API that returns 500 Internal Server Error
    WHEN searching for flights
    THEN AmadeusApiError is raised
    """
    from amadeus.client.errors import ResponseError

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.parsed = False
    mock_response.result = {}
    error = ResponseError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusApiError

    with pytest.raises(AmadeusApiError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error


@pytest.mark.asyncio
async def test_search_flights_handles_network_error(mock_amadeus_sdk, mocker):
    """
    GIVEN a network connectivity issue
    WHEN searching for flights
    THEN AmadeusNetworkError is raised
    """
    from amadeus.client.errors import NetworkError

    mock_response = Mock()
    mock_response.parsed = False
    mock_response.result = {}
    error = NetworkError(mock_response)
    mock_amadeus_sdk.get.side_effect = error

    client = AmadeusClient(api_key="test_key", api_secret="test_secret")
    departure_date = date.today() + timedelta(days=30)

    from raton.services.exceptions import AmadeusNetworkError

    with pytest.raises(AmadeusNetworkError) as exc_info:
        await client.search_flights(
            origin="JFK",
            destination="LAX",
            departure_date=departure_date,
            adults=1,
        )

    assert exc_info.value.__cause__ is error
