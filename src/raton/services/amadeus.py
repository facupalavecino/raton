"""Amadeus API client for flight search.

This module provides an async wrapper around the Amadeus Python SDK
for searching flight offers.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import TYPE_CHECKING, Literal

from amadeus import Client
from amadeus.client.errors import NetworkError, ResponseError

from raton.models import CabinClass, FlightOffer
from raton.models.mappers import amadeus_to_flight_offer
from raton.services.exceptions import (
    AmadeusApiError,
    AmadeusAuthError,
    AmadeusNetworkError,
    AmadeusRateLimitError,
)

if TYPE_CHECKING:
    from raton.config import Settings


class AmadeusClient:
    """Async client for searching flights via Amadeus API.

    This client wraps the synchronous Amadeus SDK and provides an async
    interface for flight searches. It handles authentication automatically
    and transforms API responses into domain models.

    Args:
        api_key: Amadeus API key
        api_secret: Amadeus API secret
        base_url: Base URL for API (defaults to test environment)

    Example:
        >>> client = AmadeusClient(api_key="key", api_secret="secret")
        >>> offers = await client.search_flights(
        ...     origin="JFK",
        ...     destination="LAX",
        ...     departure_date=date(2026, 3, 15),
        ...     adults=1,
        ... )
    """

    def __init__(
        self, api_key: str, api_secret: str, hostname: Literal["test", "production"] = "test"
    ):
        """Initialize the Amadeus client.

        Args:
            api_key: Amadeus API key
            api_secret: Amadeus API secret
            hostname: Amadeus environment - "test" or "production" (default: "test")
        """
        self._client = Client(client_id=api_key, client_secret=api_secret, hostname=hostname)

    @classmethod
    def from_settings(cls, settings: Settings) -> AmadeusClient:
        """Create an AmadeusClient from application settings.

        Args:
            settings: Application settings containing Amadeus credentials

        Returns:
            AmadeusClient: Initialized client
        """
        return cls(
            api_key=settings.amadeus_api_key,
            api_secret=settings.amadeus_api_secret,
            hostname=settings.amadeus_hostname,
        )

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        adults: int = 1,
        return_date: date | None = None,
        cabin_class: CabinClass | None = None,
        non_stop: bool = False,
        max_results: int = 10,
    ) -> list[FlightOffer]:
        """Search for flight offers matching the given criteria.

        This method searches for flights (one-way or round-trip) and transforms
        the API response into domain FlightOffer objects.

        Args:
            origin: Origin airport IATA code (e.g., "JFK")
            destination: Destination airport IATA code (e.g., "LAX")
            departure_date: Departure date
            adults: Number of adult passengers (default: 1)
            return_date: Return date for round-trip searches (default: None for one-way)
            cabin_class: Preferred cabin class (default: None for any class)
            non_stop: If True, return only direct flights (default: False)
            max_results: Maximum number of results to return (default: 10)

        Returns:
            list[FlightOffer]: List of flight offers matching criteria.
                Returns empty list if no flights found.

        Example:
            >>> offers = await client.search_flights(
            ...     origin="JFK",
            ...     destination="LAX",
            ...     departure_date=date(2026, 3, 15),
            ...     adults=2,
            ...     return_date=date(2026, 3, 22),
            ...     cabin_class=CabinClass.ECONOMY,
            ...     non_stop=True,
            ... )
        """
        # Build parameters for the SDK call
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date.isoformat(),
            "adults": adults,
            "max": max_results,
        }

        if return_date:
            params["returnDate"] = return_date.isoformat()

        if cabin_class:
            params["travelClass"] = cabin_class.value.upper()

        if non_stop:
            params["nonStop"] = True

        try:
            response = await asyncio.to_thread(
                self._client.shopping.flight_offers_search.get,
                **params,
            )
        except Exception as e:
            if isinstance(e, NetworkError):
                raise AmadeusNetworkError(f"Network error: {e}") from e

            if isinstance(e, ResponseError):
                status = e.response.status_code

                if status in (401, 403):
                    raise AmadeusAuthError(f"Authentication failed with status {status}") from e

                if status == 429:
                    raise AmadeusRateLimitError("Rate limit exceeded") from e

                raise AmadeusApiError(f"API error with status {status}") from e

            raise

        return [amadeus_to_flight_offer(offer) for offer in response.data]
