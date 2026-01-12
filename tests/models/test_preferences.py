"""Tests for user preference models.

Tests the models that represent user search criteria and preferences.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
import yaml

from raton.models.base import CabinClass, StopPreference, TripType
from raton.models.preferences import DateRange, Route, UserPreferences


def test_route_creation():
    """
    GIVEN valid origin and destination airports
    WHEN creating a Route
    THEN it stores both values
    """
    route = Route(origin="JFK", destination="LAX")
    assert route.origin == "JFK"
    assert route.destination == "LAX"


def test_route_validates_origin_not_equal_destination():
    """
    GIVEN a route where origin equals destination
    WHEN creating a Route
    THEN it raises a validation error
    """
    with pytest.raises(ValueError, match="Origin and destination must be different"):
        Route(origin="JFK", destination="JFK")


def test_route_case_sensitive():
    """
    GIVEN origin and destination with different cases
    WHEN creating a Route
    THEN validation is case-sensitive
    """
    # "jfk" != "JFK" so this should be valid
    route = Route(origin="jfk", destination="JFK")
    assert route.origin == "jfk"
    assert route.destination == "JFK"


def test_date_range_creation():
    """
    GIVEN valid earliest and latest dates
    WHEN creating a DateRange
    THEN it stores both dates
    """
    date_range = DateRange(
        earliest=date(2026, 3, 1),
        latest=date(2026, 3, 15),
    )
    assert date_range.earliest == date(2026, 3, 1)
    assert date_range.latest == date(2026, 3, 15)


def test_date_range_validates_earliest_before_latest():
    """
    GIVEN a date range where earliest is after latest
    WHEN creating a DateRange
    THEN it raises a validation error
    """
    with pytest.raises(ValueError, match="Earliest date must be before or equal to latest"):
        DateRange(
            earliest=date(2026, 3, 15),
            latest=date(2026, 3, 1),
        )


def test_date_range_allows_same_date():
    """
    GIVEN a date range where earliest equals latest
    WHEN creating a DateRange
    THEN it is valid (specific date search)
    """
    date_range = DateRange(
        earliest=date(2026, 3, 15),
        latest=date(2026, 3, 15),
    )
    assert date_range.earliest == date_range.latest


def test_user_preferences_minimal():
    """
    GIVEN minimal user preferences (routes, dates, price)
    WHEN creating UserPreferences
    THEN it uses default values for optional fields
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
    )
    assert len(prefs.routes) == 1
    assert prefs.max_price == Decimal("500")
    assert prefs.currency == "USD"
    # Check defaults
    assert prefs.passengers == 1
    assert prefs.cabin_class == CabinClass.ECONOMY
    assert prefs.stop_preference == StopPreference.ANY
    assert prefs.trip_type == TripType.ROUND_TRIP


def test_user_preferences_complete():
    """
    GIVEN complete user preferences with all fields specified
    WHEN creating UserPreferences
    THEN all values are preserved
    """
    prefs = UserPreferences(
        routes=[
            Route(origin="JFK", destination="LAX"),
            Route(origin="JFK", destination="SFO"),
        ],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("800"),
        currency="USD",
        passengers=2,
        cabin_class=CabinClass.BUSINESS,
        stop_preference=StopPreference.DIRECT_ONLY,
        trip_type=TripType.ONE_WAY,
    )
    assert len(prefs.routes) == 2
    assert prefs.passengers == 2
    assert prefs.cabin_class == CabinClass.BUSINESS
    assert prefs.stop_preference == StopPreference.DIRECT_ONLY
    assert prefs.trip_type == TripType.ONE_WAY


def test_user_preferences_validates_at_least_one_route():
    """
    GIVEN preferences with an empty routes list
    WHEN creating UserPreferences
    THEN it raises a validation error
    """
    with pytest.raises(ValueError, match="at least 1 item"):
        UserPreferences(
            routes=[],
            date_range=DateRange(
                earliest=date(2026, 3, 1),
                latest=date(2026, 3, 15),
            ),
            max_price=Decimal("500"),
            currency="USD",
        )


def test_user_preferences_validates_passengers_range():
    """
    GIVEN preferences with invalid passenger count
    WHEN creating UserPreferences
    THEN it raises a validation error
    """
    # Test 0 passengers
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        UserPreferences(
            routes=[Route(origin="JFK", destination="LAX")],
            date_range=DateRange(
                earliest=date(2026, 3, 1),
                latest=date(2026, 3, 15),
            ),
            max_price=Decimal("500"),
            currency="USD",
            passengers=0,
        )

    # Test 10 passengers (over limit)
    with pytest.raises(ValueError, match="less than or equal to 9"):
        UserPreferences(
            routes=[Route(origin="JFK", destination="LAX")],
            date_range=DateRange(
                earliest=date(2026, 3, 1),
                latest=date(2026, 3, 15),
            ),
            max_price=Decimal("500"),
            currency="USD",
            passengers=10,
        )


def test_user_preferences_yaml_serialization():
    """
    GIVEN user preferences
    WHEN serializing to YAML and back
    THEN it roundtrips successfully
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
        passengers=2,
        cabin_class=CabinClass.BUSINESS,
        stop_preference=StopPreference.DIRECT_ONLY,
        trip_type=TripType.ONE_WAY,
    )

    # Serialize to YAML
    yaml_str = yaml.dump(prefs.model_dump(mode="json"))

    # Deserialize from YAML
    loaded_data = yaml.safe_load(yaml_str)
    loaded_prefs = UserPreferences.model_validate(loaded_data)

    # Verify equality
    assert loaded_prefs.routes[0].origin == prefs.routes[0].origin
    assert loaded_prefs.routes[0].destination == prefs.routes[0].destination
    assert loaded_prefs.date_range.earliest == prefs.date_range.earliest
    assert loaded_prefs.date_range.latest == prefs.date_range.latest
    assert loaded_prefs.max_price == prefs.max_price
    assert loaded_prefs.currency == prefs.currency
    assert loaded_prefs.passengers == prefs.passengers
    assert loaded_prefs.cabin_class == prefs.cabin_class
    assert loaded_prefs.stop_preference == prefs.stop_preference
    assert loaded_prefs.trip_type == prefs.trip_type


def test_user_preferences_yaml_human_readable():
    """
    GIVEN user preferences
    WHEN serializing to YAML
    THEN the output is human-readable
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
    )

    yaml_str = yaml.dump(prefs.model_dump(mode="json"))

    # Check that it contains human-readable keys
    assert "routes" in yaml_str
    assert "origin: JFK" in yaml_str
    assert "destination: LAX" in yaml_str
    assert "max_price" in yaml_str
    assert "currency: USD" in yaml_str


def test_user_preferences_price_as_string():
    """
    GIVEN preferences with price as string (from YAML)
    WHEN creating UserPreferences
    THEN it converts to Decimal
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price="500.00",  # string
        currency="USD",
    )
    assert isinstance(prefs.max_price, Decimal)
    assert prefs.max_price == Decimal("500.00")


def test_user_preferences_with_max_duration():
    """
    GIVEN preferences with max_duration specified
    WHEN creating UserPreferences
    THEN the max_duration is preserved
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
        max_duration=timedelta(hours=8),
    )
    assert prefs.max_duration == timedelta(hours=8)


def test_user_preferences_max_duration_optional():
    """
    GIVEN preferences without max_duration
    WHEN creating UserPreferences
    THEN max_duration defaults to None
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
    )
    assert prefs.max_duration is None


def test_user_preferences_max_duration_yaml_serialization():
    """
    GIVEN preferences with max_duration
    WHEN serializing to YAML and back
    THEN timedelta roundtrips correctly
    """
    prefs = UserPreferences(
        routes=[Route(origin="JFK", destination="LAX")],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 15),
        ),
        max_price=Decimal("500"),
        currency="USD",
        max_duration=timedelta(hours=10, minutes=30),
    )

    # Serialize to YAML
    yaml_str = yaml.dump(prefs.model_dump(mode="json"))

    # Deserialize from YAML
    loaded_data = yaml.safe_load(yaml_str)
    loaded_prefs = UserPreferences.model_validate(loaded_data)

    # Verify max_duration preserved
    assert loaded_prefs.max_duration == timedelta(hours=10, minutes=30)
