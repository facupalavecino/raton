"""Flight domain models.

Core domain models representing flight offers, itineraries, segments, and pricing.
These models are separate from Amadeus API models to maintain clean architecture.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, Field, computed_field


class FlightSegment(BaseModel):
    """A single flight segment within an itinerary.

    Represents one leg of a journey from departure to arrival on a single flight.

    Attributes:
        departure_airport: IATA airport code for departure (e.g., "JFK")
        departure_time: Scheduled departure datetime (should be timezone-aware)
        departure_terminal: Airport terminal for departure (optional)
        arrival_airport: IATA airport code for arrival (e.g., "LAX")
        arrival_time: Scheduled arrival datetime (should be timezone-aware)
        arrival_terminal: Airport terminal for arrival (optional)
        airline: IATA airline code (e.g., "AA" for American Airlines)
        flight_number: Flight number as string (e.g., "123")
        aircraft: Aircraft type description (optional, e.g., "Boeing 737-800")
        duration: Flight duration as timedelta
    """

    departure_airport: str
    departure_time: datetime
    departure_terminal: str | None = None
    arrival_airport: str
    arrival_time: datetime
    arrival_terminal: str | None = None
    airline: str
    flight_number: str
    aircraft: str | None = None
    duration: timedelta


class Price(BaseModel):
    """Pricing information for a flight offer.

    Uses Decimal for all monetary values to avoid floating-point precision issues.

    Attributes:
        total: Total price including all fees and taxes
        currency: ISO 4217 currency code (e.g., "USD", "EUR")
        base: Base fare before fees and taxes
        fees: Total fees and taxes
    """

    total: Decimal
    currency: str
    base: Decimal
    fees: Decimal


class Itinerary(BaseModel):
    """A collection of flight segments forming one direction of travel.

    For a round-trip, there would be two itineraries (outbound and return).
    For a one-way, there would be one itinerary.

    Attributes:
        segments: List of flight segments in travel order (at least one required)
    """

    segments: list[FlightSegment] = Field(min_length=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stops(self) -> int:
        """Number of stops (connections) in this itinerary.

        A direct flight has 0 stops. One connection means 1 stop.

        Returns:
            Number of stops (len(segments) - 1)
        """
        return len(self.segments) - 1

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_duration(self) -> timedelta:
        """Total duration of all segments in this itinerary.

        Returns:
            Sum of all segment durations
        """
        return sum((segment.duration for segment in self.segments), timedelta())


class FlightOffer(BaseModel):
    """A complete flight offer representing a bookable combination of itineraries.

    Attributes:
        id: Unique identifier for this offer
        itineraries: List of itineraries (1 for one-way, 2 for round-trip)
        price: Pricing information
        validating_airline: IATA airline code for the validating carrier
    """

    id: str
    itineraries: list[Itinerary] = Field(min_length=1)
    price: Price
    validating_airline: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_round_trip(self) -> bool:
        """Whether this is a round-trip offer.

        Returns:
            True if there are 2 or more itineraries, False otherwise
        """
        return len(self.itineraries) > 1

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_duration(self) -> timedelta:
        """Total duration of all itineraries in this offer.

        For round-trips, this sums both outbound and return durations.

        Returns:
            Sum of all itinerary durations
        """
        return sum((itinerary.total_duration for itinerary in self.itineraries), timedelta())

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_stops(self) -> int:
        """Total number of stops across all itineraries.

        Returns:
            Sum of stops in all itineraries
        """
        return sum(itinerary.stops for itinerary in self.itineraries)
