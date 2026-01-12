"""Deal detection rules engine.

This module provides functionality to evaluate flight offers against user
preferences to determine if they qualify as good deals.
"""

from __future__ import annotations

from dataclasses import dataclass

from raton.models.base import StopPreference
from raton.models.flight import FlightOffer
from raton.models.preferences import UserPreferences


@dataclass(frozen=True)
class MatchResult:
    """Result of evaluating a flight offer against user preferences.

    A flight matches user preferences only if ALL rules pass. This class
    captures both the overall match status and detailed reasons for each rule.

    Attributes:
        is_match: True if the flight passes all rules, False otherwise
        passed_reasons: Tuple of human-readable reasons for rules that passed
        failed_reasons: Tuple of human-readable reasons for rules that failed

    Example:
        >>> result = evaluate_flight(flight, preferences)
        >>> if result.is_match:
        ...     print("Deal found!")
        ...     for reason in result.passed_reasons:
        ...         print(f"  ✓ {reason}")
        ... else:
        ...     print("Not a match:")
        ...     for reason in result.failed_reasons:
        ...         print(f"  ✗ {reason}")
    """

    is_match: bool
    passed_reasons: tuple[str, ...]
    failed_reasons: tuple[str, ...]


def check_currency(flight: FlightOffer, prefs: UserPreferences) -> tuple[bool, str]:
    """Check if flight currency matches user's preferred currency.

    Args:
        flight: The flight offer to evaluate
        prefs: The user's preferences

    Returns:
        Tuple of (passed, reason) where passed is True if currencies match
    """
    if flight.price.currency == prefs.currency:
        return True, f"Currency matches ({prefs.currency})"
    return (
        False,
        f"Currency mismatch: flight is {flight.price.currency}, expected {prefs.currency}",
    )


def check_price(flight: FlightOffer, prefs: UserPreferences) -> tuple[bool, str]:
    """Check if flight price is within user's maximum price.

    Args:
        flight: The flight offer to evaluate
        prefs: The user's preferences

    Returns:
        Tuple of (passed, reason) where passed is True if price is acceptable
    """
    if flight.price.total <= prefs.max_price:
        return (
            True,
            f"Price {flight.price.total} {flight.price.currency} is within budget of {prefs.max_price}",
        )
    return (
        False,
        f"Price {flight.price.total} {flight.price.currency} exceeds max {prefs.max_price}",
    )


def check_stops(flight: FlightOffer, prefs: UserPreferences) -> tuple[bool, str]:
    """Check if flight stops match user's stop preference.

    Args:
        flight: The flight offer to evaluate
        prefs: The user's preferences

    Returns:
        Tuple of (passed, reason) where passed is True if stops are acceptable
    """
    total_stops = flight.total_stops

    match prefs.stop_preference:
        case StopPreference.ANY:
            return True, f"Any stops allowed ({total_stops} stops)"

        case StopPreference.DIRECT_ONLY:
            if total_stops == 0:
                return True, "Direct flight as required"
            return False, f"Flight has {total_stops} stops, but direct only required"

        case StopPreference.MAX_ONE_STOP:
            if total_stops <= 1:
                return True, f"Flight has {total_stops} stops (max 1 allowed)"
            return False, f"Flight has {total_stops} stops, but max 1 allowed"


def check_duration(flight: FlightOffer, prefs: UserPreferences) -> tuple[bool, str]:
    """Check if flight duration is within user's maximum duration (if specified).

    Args:
        flight: The flight offer to evaluate
        prefs: The user's preferences

    Returns:
        Tuple of (passed, reason) where passed is True if duration is acceptable
    """
    if prefs.max_duration is None:
        return True, "No duration limit specified"

    if (total := flight.total_duration) <= prefs.max_duration:
        return True, f"Duration {total} is within limit of {prefs.max_duration}"

    return False, f"Duration {total} exceeds max {prefs.max_duration}"


def evaluate_flight(flight: FlightOffer, prefs: UserPreferences) -> MatchResult:
    """Evaluate a flight offer against user preferences.

    Runs all rules and aggregates results. A flight is considered a match only
    if ALL rules pass.

    Args:
        flight: The flight offer to evaluate
        prefs: The user's preferences

    Returns:
        MatchResult with is_match=True only if all rules pass

    Example:
        >>> result = evaluate_flight(flight, preferences)
        >>> if result.is_match:
        ...     send_notification(user, flight)
    """
    rules = [check_currency, check_price, check_stops, check_duration]

    passed: list[str] = []
    failed: list[str] = []

    for rule in rules:
        passed_rule, reason = rule(flight, prefs)
        if passed_rule:
            passed.append(reason)
        else:
            failed.append(reason)

    return MatchResult(
        is_match=len(failed) == 0,
        passed_reasons=tuple(passed),
        failed_reasons=tuple(failed),
    )
