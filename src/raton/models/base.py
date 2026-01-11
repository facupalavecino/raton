"""Base types and enums used across multiple models.

This module contains foundational types that are shared across flight offers
and user preferences.
"""

from __future__ import annotations

from enum import Enum


class CabinClass(str, Enum):
    """Flight cabin class options.

    Attributes:
        ECONOMY: Standard economy class
        PREMIUM_ECONOMY: Premium economy with extra legroom
        BUSINESS: Business class with lie-flat seats
        FIRST: First class with maximum luxury
    """

    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class TripType(str, Enum):
    """Flight trip type options.

    Attributes:
        ONE_WAY: One-way flight from origin to destination
        ROUND_TRIP: Round-trip flight with return journey
    """

    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"


class StopPreference(str, Enum):
    """User preferences for flight stops/connections.

    Attributes:
        ANY: Accept flights with any number of stops
        DIRECT_ONLY: Only accept direct flights with no stops
        MAX_ONE_STOP: Accept flights with at most one stop
    """

    ANY = "any"
    DIRECT_ONLY = "direct_only"
    MAX_ONE_STOP = "max_one_stop"
