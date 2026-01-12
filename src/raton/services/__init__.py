"""Business logic services."""

from raton.services.amadeus import AmadeusClient
from raton.services.exceptions import (
    AmadeusApiError,
    AmadeusAuthError,
    AmadeusError,
    AmadeusNetworkError,
    AmadeusRateLimitError,
    PreferencesError,
    PreferencesNotFoundError,
    PreferencesStorageError,
)
from raton.services.preferences import PreferencesRepository
from raton.services.rules import MatchResult, evaluate_flight

__all__ = [
    "AmadeusApiError",
    "AmadeusAuthError",
    "AmadeusClient",
    "AmadeusError",
    "AmadeusNetworkError",
    "AmadeusRateLimitError",
    "MatchResult",
    "PreferencesError",
    "PreferencesNotFoundError",
    "PreferencesRepository",
    "PreferencesStorageError",
    "evaluate_flight",
]
