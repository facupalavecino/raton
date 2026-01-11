"""User preference models.

Models representing user search criteria and preferences for flight deals.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from raton.models.base import CabinClass, StopPreference, TripType


class Route(BaseModel):
    """A flight route from origin to destination.

    Attributes:
        origin: Origin airport code
        destination: Destination airport code
    """

    origin: str
    destination: str

    @model_validator(mode="after")
    def validate_origin_destination_different(self) -> Route:
        """Validate that origin and destination are different.

        Returns:
            The validated Route instance

        Raises:
            ValueError: If origin equals destination
        """
        if self.origin == self.destination:
            raise ValueError("Origin and destination must be different")
        return self


class DateRange(BaseModel):
    """A date range for flexible flight searches.

    Attributes:
        earliest: Earliest acceptable departure date
        latest: Latest acceptable departure date
    """

    earliest: date
    latest: date

    @model_validator(mode="after")
    def validate_earliest_before_latest(self) -> DateRange:
        """Validate that earliest date is before or equal to latest date.

        Returns:
            The validated DateRange instance

        Raises:
            ValueError: If earliest is after latest
        """
        if self.earliest > self.latest:
            raise ValueError("Earliest date must be before or equal to latest date")
        return self


class UserPreferences(BaseModel):
    """User preferences for flight deal searches.

    Captures all search criteria including routes, dates, price limits,
    and travel preferences.

    Attributes:
        routes: List of acceptable routes (at least one required)
        date_range: Acceptable date range for departure
        max_price: Maximum acceptable price
        currency: Currency for price (ISO 4217 code)
        passengers: Number of passengers (1-9, default 1)
        cabin_class: Preferred cabin class (default ECONOMY)
        stop_preference: Preference for stops/connections (default ANY)
        trip_type: Type of trip (default ROUND_TRIP)
    """

    routes: list[Route] = Field(min_length=1)
    date_range: DateRange
    max_price: Decimal
    currency: str
    passengers: int = Field(default=1, ge=1, le=9)
    cabin_class: CabinClass = CabinClass.ECONOMY
    stop_preference: StopPreference = StopPreference.ANY
    trip_type: TripType = TripType.ROUND_TRIP
