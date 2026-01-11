"""Tests for base types and enums.

Tests the foundation types used across multiple models.
"""

from __future__ import annotations

import json

from raton.models.base import CabinClass, StopPreference, TripType


def test_cabin_class_enum_values():
    """
    GIVEN the CabinClass enum
    WHEN checking its values
    THEN all expected cabin classes are present with correct string values
    """
    assert CabinClass.ECONOMY.value == "economy"
    assert CabinClass.PREMIUM_ECONOMY.value == "premium_economy"
    assert CabinClass.BUSINESS.value == "business"
    assert CabinClass.FIRST.value == "first"


def test_cabin_class_from_string():
    """
    GIVEN a string representation of a cabin class
    WHEN creating a CabinClass enum from it
    THEN the correct enum member is returned
    """
    assert CabinClass("economy") == CabinClass.ECONOMY
    assert CabinClass("premium_economy") == CabinClass.PREMIUM_ECONOMY
    assert CabinClass("business") == CabinClass.BUSINESS
    assert CabinClass("first") == CabinClass.FIRST


def test_cabin_class_json_serialization():
    """
    GIVEN a CabinClass enum member
    WHEN serializing to JSON
    THEN it serializes as its string value
    """
    data = {"cabin": CabinClass.BUSINESS}
    json_str = json.dumps(data, default=str)
    assert "business" in json_str


def test_trip_type_enum_values():
    """
    GIVEN the TripType enum
    WHEN checking its values
    THEN all expected trip types are present with correct string values
    """
    assert TripType.ONE_WAY.value == "one_way"
    assert TripType.ROUND_TRIP.value == "round_trip"


def test_trip_type_from_string():
    """
    GIVEN a string representation of a trip type
    WHEN creating a TripType enum from it
    THEN the correct enum member is returned
    """
    assert TripType("one_way") == TripType.ONE_WAY
    assert TripType("round_trip") == TripType.ROUND_TRIP


def test_trip_type_json_serialization():
    """
    GIVEN a TripType enum member
    WHEN serializing to JSON
    THEN it serializes as its string value
    """
    data = {"trip": TripType.ROUND_TRIP}
    json_str = json.dumps(data, default=str)
    assert "round_trip" in json_str


def test_stop_preference_enum_values():
    """
    GIVEN the StopPreference enum
    WHEN checking its values
    THEN all expected stop preferences are present with correct string values
    """
    assert StopPreference.ANY.value == "any"
    assert StopPreference.DIRECT_ONLY.value == "direct_only"
    assert StopPreference.MAX_ONE_STOP.value == "max_one_stop"


def test_stop_preference_from_string():
    """
    GIVEN a string representation of a stop preference
    WHEN creating a StopPreference enum from it
    THEN the correct enum member is returned
    """
    assert StopPreference("any") == StopPreference.ANY
    assert StopPreference("direct_only") == StopPreference.DIRECT_ONLY
    assert StopPreference("max_one_stop") == StopPreference.MAX_ONE_STOP


def test_stop_preference_json_serialization():
    """
    GIVEN a StopPreference enum member
    WHEN serializing to JSON
    THEN it serializes as its string value
    """
    data = {"stops": StopPreference.DIRECT_ONLY}
    json_str = json.dumps(data, default=str)
    assert "direct_only" in json_str
