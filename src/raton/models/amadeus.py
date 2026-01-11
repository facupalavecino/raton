"""Amadeus API response models.

These models map directly to the Amadeus Flight Offers Search API response structure.
They are intentionally separate from domain models to allow switching flight APIs
in the future without changing core business logic.

API Reference: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AmadeusSegment(BaseModel):
    """A single flight segment within an itinerary.

    Represents one leg of a journey, including departure/arrival details,
    carrier information, and duration.

    Attributes:
        departure: Departure details (iataCode, terminal, at)
        arrival: Arrival details (iataCode, terminal, at)
        carrier_code: IATA airline code (e.g., "AA" for American Airlines)
        number: Flight number
        aircraft: Aircraft details (optional, contains code)
        duration: Flight duration in ISO 8601 format (e.g., "PT2H30M")
    """

    model_config = ConfigDict(populate_by_name=True)

    departure: dict[str, Any]
    arrival: dict[str, Any]
    carrier_code: str = Field(alias="carrierCode")
    number: str
    aircraft: dict[str, Any] | None = None
    duration: str


class AmadeusItinerary(BaseModel):
    """A collection of flight segments forming one direction of travel.

    For a round-trip, there would be two itineraries (outbound and return).
    For a one-way, there would be one itinerary.

    Attributes:
        duration: Total duration of all segments in ISO 8601 format
        segments: List of flight segments in travel order
    """

    model_config = ConfigDict(populate_by_name=True)

    duration: str
    segments: list[AmadeusSegment]


class AmadeusPrice(BaseModel):
    """Pricing information for a flight offer.

    Attributes:
        currency: ISO 4217 currency code (e.g., "USD", "EUR")
        total: Total price as string (to preserve precision)
        base: Base fare as string (before fees and taxes)
        fees: List of fee details (amount, type)
        grand_total: Final total price including all fees (optional)
    """

    model_config = ConfigDict(populate_by_name=True)

    currency: str
    total: str
    base: str
    fees: list[dict[str, Any]]
    grand_total: str | None = Field(default=None, alias="grandTotal")


class AmadeusFlightOffer(BaseModel):
    """A complete flight offer from Amadeus API.

    Represents a bookable combination of itineraries at a specific price.

    Attributes:
        type: Always "flight-offer"
        id: Unique offer identifier
        source: Source of the offer (typically "GDS")
        instant_ticketing_required: Whether instant ticketing is required
        non_homogeneous: Whether fare is non-homogeneous
        one_way: Whether this is a one-way offer
        last_ticketing_date: Last date to purchase (YYYY-MM-DD)
        number_of_bookable_seats: Number of seats available at this price
        itineraries: List of itineraries (1 for one-way, 2 for round-trip)
        price: Pricing details
        validating_airline_codes: Airlines that validate the ticket
    """

    model_config = ConfigDict(populate_by_name=True)

    type: str
    id: str
    source: str
    instant_ticketing_required: bool = Field(alias="instantTicketingRequired")
    non_homogeneous: bool = Field(alias="nonHomogeneous")
    one_way: bool = Field(alias="oneWay")
    last_ticketing_date: str = Field(alias="lastTicketingDate")
    number_of_bookable_seats: int = Field(alias="numberOfBookableSeats")
    itineraries: list[AmadeusItinerary]
    price: AmadeusPrice
    validating_airline_codes: list[str] = Field(alias="validatingAirlineCodes")


class AmadeusFlightSearchResponse(BaseModel):
    """Complete response from Amadeus Flight Offers Search API.

    Contains metadata, a list of flight offers, and reference dictionaries.

    Attributes:
        meta: Response metadata (count, pagination links)
        data: List of flight offers
        dictionaries: Reference data (locations, aircraft, currencies, carriers)
    """

    model_config = ConfigDict(populate_by_name=True)

    meta: dict[str, Any]
    data: list[AmadeusFlightOffer]
    dictionaries: dict[str, Any] | None = None
