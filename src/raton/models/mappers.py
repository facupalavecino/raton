"""Mapper functions to convert Amadeus API responses to domain models.

These pure functions transform external API data structures into our internal
domain models, maintaining separation of concerns and enabling API switching.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from raton.models.flight import FlightOffer, FlightSegment, Itinerary, Price

# ISO 8601 duration pattern: PT2H30M, PT5H, PT45M, PT1H15M30S, etc.
_ISO8601_DURATION_PATTERN = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def parse_iso8601_duration(duration_str: str) -> timedelta:
    """Parse an ISO 8601 duration string into a timedelta.

    Amadeus API returns durations in ISO 8601 format like "PT2H30M" for 2 hours
    and 30 minutes. This parser handles hours (H), minutes (M), and seconds (S).

    Args:
        duration_str: ISO 8601 duration string (e.g., "PT2H30M", "PT5H15M")

    Returns:
        timedelta representing the duration

    Raises:
        ValueError: If duration_str is not a valid ISO 8601 duration

    Examples:
        >>> parse_iso8601_duration("PT2H30M")
        timedelta(hours=2, minutes=30)
        >>> parse_iso8601_duration("PT5H")
        timedelta(hours=5)
        >>> parse_iso8601_duration("PT45M")
        timedelta(minutes=45)
    """
    match = _ISO8601_DURATION_PATTERN.match(duration_str)
    if not match:
        raise ValueError(
            f"Invalid ISO 8601 duration format: {duration_str}. "
            "Expected format: PT[hours]H[minutes]M[seconds]S"
        )

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def amadeus_to_flight_offer(amadeus_data: dict[str, Any]) -> FlightOffer:
    """Convert an Amadeus flight offer dict to a FlightOffer domain model.

    Transforms the Amadeus API response structure into our internal domain model,
    handling nested structures, type conversions, and computed values.

    Args:
        amadeus_data: Flight offer dict from Amadeus API

    Returns:
        FlightOffer domain model instance

    Examples:
        >>> amadeus_offer = {
        ...     "id": "1",
        ...     "itineraries": [{
        ...         "segments": [{
        ...             "departure": {"iataCode": "JFK", "at": "2026-03-15T10:30:00-05:00"},
        ...             "arrival": {"iataCode": "LAX", "at": "2026-03-15T13:45:00-08:00"},
        ...             "carrierCode": "AA",
        ...             "number": "123",
        ...             "duration": "PT5H15M"
        ...         }]
        ...     }],
        ...     "price": {"currency": "USD", "total": "299.99", "base": "250.00", "fees": []},
        ...     "validatingAirlineCodes": ["AA"]
        ... }
        >>> offer = amadeus_to_flight_offer(amadeus_offer)
        >>> offer.price.total
        Decimal('299.99')
    """
    # Convert itineraries
    itineraries = []
    for amadeus_itin in amadeus_data["itineraries"]:
        segments = []
        for amadeus_seg in amadeus_itin["segments"]:
            # Parse departure and arrival times
            departure_time = datetime.fromisoformat(amadeus_seg["departure"]["at"])
            arrival_time = datetime.fromisoformat(amadeus_seg["arrival"]["at"])

            # Parse duration
            duration = parse_iso8601_duration(amadeus_seg["duration"])

            # Extract optional fields
            departure_terminal = amadeus_seg["departure"].get("terminal")
            arrival_terminal = amadeus_seg["arrival"].get("terminal")

            # Aircraft code (if present)
            aircraft = None
            if "aircraft" in amadeus_seg and "code" in amadeus_seg["aircraft"]:
                aircraft = amadeus_seg["aircraft"]["code"]

            segment = FlightSegment(
                departure_airport=amadeus_seg["departure"]["iataCode"],
                departure_time=departure_time,
                departure_terminal=departure_terminal,
                arrival_airport=amadeus_seg["arrival"]["iataCode"],
                arrival_time=arrival_time,
                arrival_terminal=arrival_terminal,
                airline=amadeus_seg["carrierCode"],
                flight_number=amadeus_seg["number"],
                aircraft=aircraft,
                duration=duration,
            )
            segments.append(segment)

        itinerary = Itinerary(segments=segments)
        itineraries.append(itinerary)

    # Convert price
    amadeus_price = amadeus_data["price"]

    # Calculate total fees
    total_fees = Decimal("0")
    for fee in amadeus_price.get("fees", []):
        total_fees += Decimal(fee["amount"])

    price = Price(
        total=Decimal(amadeus_price["total"]),
        currency=amadeus_price["currency"],
        base=Decimal(amadeus_price["base"]),
        fees=total_fees,
    )

    # Get validating airline (first one if multiple)
    validating_airline = amadeus_data["validatingAirlineCodes"][0]

    return FlightOffer(
        id=amadeus_data["id"],
        itineraries=itineraries,
        price=price,
        validating_airline=validating_airline,
    )
