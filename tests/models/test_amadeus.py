"""Tests for Amadeus API response models.

Tests the models that parse Amadeus Flight Offers Search API responses.
"""

from __future__ import annotations

from raton.models.amadeus import (
    AmadeusFlightOffer,
    AmadeusFlightSearchResponse,
    AmadeusItinerary,
    AmadeusPrice,
    AmadeusSegment,
)


def test_amadeus_segment_minimal_fields():
    """
    GIVEN minimal segment data from Amadeus API
    WHEN creating an AmadeusSegment
    THEN it parses successfully
    """
    segment_data = {
        "departure": {
            "iataCode": "JFK",
            "at": "2026-03-15T10:30:00",
        },
        "arrival": {
            "iataCode": "LAX",
            "at": "2026-03-15T13:45:00",
        },
        "carrierCode": "AA",
        "number": "123",
        "duration": "PT5H15M",
    }
    segment = AmadeusSegment.model_validate(segment_data)
    assert segment.departure["iataCode"] == "JFK"
    assert segment.arrival["iataCode"] == "LAX"
    assert segment.carrier_code == "AA"
    assert segment.number == "123"
    assert segment.duration == "PT5H15M"


def test_amadeus_segment_with_optional_fields():
    """
    GIVEN segment data with optional aircraft and terminal info
    WHEN creating an AmadeusSegment
    THEN all fields parse successfully
    """
    segment_data = {
        "departure": {
            "iataCode": "JFK",
            "terminal": "4",
            "at": "2026-03-15T10:30:00",
        },
        "arrival": {
            "iataCode": "LAX",
            "terminal": "B",
            "at": "2026-03-15T13:45:00",
        },
        "carrierCode": "AA",
        "number": "123",
        "aircraft": {"code": "73H"},
        "duration": "PT5H15M",
    }
    segment = AmadeusSegment.model_validate(segment_data)
    assert segment.departure["terminal"] == "4"
    assert segment.arrival["terminal"] == "B"
    assert segment.aircraft == {"code": "73H"}


def test_amadeus_itinerary_single_segment():
    """
    GIVEN an itinerary with a single segment (direct flight)
    WHEN creating an AmadeusItinerary
    THEN it parses successfully
    """
    itinerary_data = {
        "duration": "PT5H15M",
        "segments": [
            {
                "departure": {
                    "iataCode": "JFK",
                    "at": "2026-03-15T10:30:00",
                },
                "arrival": {
                    "iataCode": "LAX",
                    "at": "2026-03-15T13:45:00",
                },
                "carrierCode": "AA",
                "number": "123",
                "duration": "PT5H15M",
            }
        ],
    }
    itinerary = AmadeusItinerary.model_validate(itinerary_data)
    assert itinerary.duration == "PT5H15M"
    assert len(itinerary.segments) == 1


def test_amadeus_itinerary_multiple_segments():
    """
    GIVEN an itinerary with multiple segments (connecting flight)
    WHEN creating an AmadeusItinerary
    THEN it parses all segments
    """
    itinerary_data = {
        "duration": "PT8H30M",
        "segments": [
            {
                "departure": {
                    "iataCode": "JFK",
                    "at": "2026-03-15T10:30:00",
                },
                "arrival": {
                    "iataCode": "ORD",
                    "at": "2026-03-15T12:00:00",
                },
                "carrierCode": "AA",
                "number": "100",
                "duration": "PT2H30M",
            },
            {
                "departure": {
                    "iataCode": "ORD",
                    "at": "2026-03-15T14:00:00",
                },
                "arrival": {
                    "iataCode": "LAX",
                    "at": "2026-03-15T16:00:00",
                },
                "carrierCode": "AA",
                "number": "200",
                "duration": "PT4H0M",
            },
        ],
    }
    itinerary = AmadeusItinerary.model_validate(itinerary_data)
    assert len(itinerary.segments) == 2
    assert itinerary.segments[0].carrier_code == "AA"
    assert itinerary.segments[1].carrier_code == "AA"


def test_amadeus_price_structure():
    """
    GIVEN price data from Amadeus API
    WHEN creating an AmadeusPrice
    THEN it parses all price fields
    """
    price_data = {
        "currency": "USD",
        "total": "299.99",
        "base": "250.00",
        "fees": [
            {
                "amount": "49.99",
                "type": "SUPPLIER",
            }
        ],
    }
    price = AmadeusPrice.model_validate(price_data)
    assert price.currency == "USD"
    assert price.total == "299.99"
    assert price.base == "250.00"
    assert len(price.fees) == 1
    assert price.fees[0]["amount"] == "49.99"


def test_amadeus_flight_offer_complete():
    """
    GIVEN a complete flight offer from Amadeus API
    WHEN creating an AmadeusFlightOffer
    THEN it parses successfully with all fields
    """
    offer_data = {
        "type": "flight-offer",
        "id": "1",
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": False,
        "lastTicketingDate": "2026-03-14",
        "numberOfBookableSeats": 9,
        "itineraries": [
            {
                "duration": "PT5H15M",
                "segments": [
                    {
                        "departure": {
                            "iataCode": "JFK",
                            "at": "2026-03-15T10:30:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T13:45:00",
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
            "fees": [],
        },
        "validatingAirlineCodes": ["AA"],
    }
    offer = AmadeusFlightOffer.model_validate(offer_data)
    assert offer.id == "1"
    assert offer.type == "flight-offer"
    assert len(offer.itineraries) == 1
    assert offer.price.currency == "USD"
    assert offer.validating_airline_codes == ["AA"]


def test_amadeus_flight_offer_round_trip():
    """
    GIVEN a round-trip flight offer with two itineraries
    WHEN creating an AmadeusFlightOffer
    THEN both itineraries are parsed
    """
    offer_data = {
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
                            "at": "2026-03-15T10:30:00",
                        },
                        "arrival": {
                            "iataCode": "LAX",
                            "at": "2026-03-15T13:45:00",
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
                            "at": "2026-03-20T14:00:00",
                        },
                        "arrival": {
                            "iataCode": "JFK",
                            "at": "2026-03-20T22:30:00",
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
    offer = AmadeusFlightOffer.model_validate(offer_data)
    assert len(offer.itineraries) == 2
    assert offer.itineraries[0].segments[0].departure["iataCode"] == "JFK"
    assert offer.itineraries[1].segments[0].departure["iataCode"] == "LAX"


def test_amadeus_search_response():
    """
    GIVEN a complete flight search response from Amadeus API
    WHEN creating an AmadeusFlightSearchResponse
    THEN it parses successfully with metadata and offers
    """
    response_data = {
        "meta": {
            "count": 2,
            "links": {"self": "https://test.api.amadeus.com/v2/shopping/flight-offers?..."},
        },
        "data": [
            {
                "type": "flight-offer",
                "id": "1",
                "source": "GDS",
                "instantTicketingRequired": False,
                "nonHomogeneous": False,
                "oneWay": False,
                "lastTicketingDate": "2026-03-14",
                "numberOfBookableSeats": 9,
                "itineraries": [
                    {
                        "duration": "PT5H15M",
                        "segments": [
                            {
                                "departure": {
                                    "iataCode": "JFK",
                                    "at": "2026-03-15T10:30:00",
                                },
                                "arrival": {
                                    "iataCode": "LAX",
                                    "at": "2026-03-15T13:45:00",
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
                    "fees": [],
                },
                "validatingAirlineCodes": ["AA"],
            }
        ],
        "dictionaries": {
            "locations": {
                "JFK": {"cityCode": "NYC", "countryCode": "US"},
                "LAX": {"cityCode": "LAX", "countryCode": "US"},
            },
            "aircraft": {"73H": "Boeing 737-800"},
            "currencies": {"USD": "US Dollar"},
            "carriers": {"AA": "American Airlines"},
        },
    }
    response = AmadeusFlightSearchResponse.model_validate(response_data)
    assert response.meta["count"] == 2
    assert len(response.data) == 1
    assert response.data[0].id == "1"
    assert response.dictionaries["carriers"]["AA"] == "American Airlines"


def test_amadeus_search_response_serialization():
    """
    GIVEN a parsed Amadeus response
    WHEN serializing back to JSON
    THEN it roundtrips successfully
    """
    response_data = {
        "meta": {"count": 1},
        "data": [
            {
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
                                    "at": "2026-03-15T10:30:00",
                                },
                                "arrival": {
                                    "iataCode": "LAX",
                                    "at": "2026-03-15T13:45:00",
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
                    "fees": [],
                },
                "validatingAirlineCodes": ["AA"],
            }
        ],
        "dictionaries": {},
    }
    response = AmadeusFlightSearchResponse.model_validate(response_data)
    serialized = response.model_dump()

    # Verify key fields are present
    assert serialized["meta"]["count"] == 1
    assert len(serialized["data"]) == 1
    assert serialized["data"][0]["id"] == "1"
