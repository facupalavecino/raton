"""Pydantic models and schemas.

This package provides domain models, API response models, and conversion utilities.

Public API:
- Base types: CabinClass, StopPreference, TripType
- Flight models: FlightSegment, Itinerary, Price, FlightOffer
- Preference models: Route, DateRange, UserPreferences
- Mappers: amadeus_to_flight_offer, parse_iso8601_duration
"""

from raton.models.base import CabinClass, StopPreference, TripType
from raton.models.flight import FlightOffer, FlightSegment, Itinerary, Price
from raton.models.mappers import amadeus_to_flight_offer, parse_iso8601_duration
from raton.models.preferences import DateRange, Route, UserPreferences

__all__ = [
    "CabinClass",
    "DateRange",
    "FlightOffer",
    "FlightSegment",
    "Itinerary",
    "Price",
    "Route",
    "StopPreference",
    "TripType",
    "UserPreferences",
    "amadeus_to_flight_offer",
    "parse_iso8601_duration",
]
