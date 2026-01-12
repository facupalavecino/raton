"""Tests for package exports.

Verifies that all public models and functions can be imported from the
raton.models package.
"""

from __future__ import annotations

import raton.models


def test_all_base_types_importable():
    """
    GIVEN the raton.models package
    WHEN importing base types
    THEN all enums are available
    """
    from raton.models import CabinClass, StopPreference, TripType

    assert CabinClass is not None
    assert StopPreference is not None
    assert TripType is not None


def test_all_flight_models_importable():
    """
    GIVEN the raton.models package
    WHEN importing flight models
    THEN all flight models are available
    """
    from raton.models import FlightOffer, FlightSegment, Itinerary, Price

    assert FlightSegment is not None
    assert Itinerary is not None
    assert Price is not None
    assert FlightOffer is not None


def test_all_preference_models_importable():
    """
    GIVEN the raton.models package
    WHEN importing preference models
    THEN all preference models are available
    """
    from raton.models import DateRange, Route, UserPreferences

    assert Route is not None
    assert DateRange is not None
    assert UserPreferences is not None


def test_all_mappers_importable():
    """
    GIVEN the raton.models package
    WHEN importing mapper functions
    THEN all mappers are available
    """
    from raton.models import amadeus_to_flight_offer, parse_iso8601_duration

    assert amadeus_to_flight_offer is not None
    assert parse_iso8601_duration is not None


def test_all_matches_actual_exports():
    """
    GIVEN the raton.models package
    WHEN checking __all__
    THEN it matches actual exports
    """
    expected = {
        "CabinClass",
        "CheckResult",
        "StopPreference",
        "TripType",
        "FlightSegment",
        "Itinerary",
        "Price",
        "FlightOffer",
        "Route",
        "DateRange",
        "UserPreferences",
        "amadeus_to_flight_offer",
        "parse_iso8601_duration",
    }

    assert set(raton.models.__all__) == expected


def test_no_internal_modules_in_all():
    """
    GIVEN the raton.models package
    WHEN checking __all__
    THEN it does not include internal module names
    """
    # __all__ should not include module names like 'base', 'flight', etc.
    internal_modules = {"base", "flight", "preferences", "amadeus", "mappers", "results"}

    assert not internal_modules.intersection(set(raton.models.__all__))
