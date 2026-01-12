"""Result models for check operations.

This module provides dataclasses for capturing results of flight check cycles.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """Result of a single flight check cycle.

    Captures statistics from running a complete check cycle across all users.

    Attributes:
        users_checked: Number of users whose preferences were checked
        routes_searched: Number of route searches performed
        flights_found: Total number of flights returned from searches
        deals_matched: Number of flights that matched user preferences
        notifications_sent: Number of notifications successfully sent
        errors: Number of errors encountered (API failures, etc.)

    Example:
        >>> result = await orchestrator.run_check_cycle()
        >>> logger.info("Checked %d users, found %d deals", result.users_checked, result.deals_matched)
    """

    users_checked: int
    routes_searched: int
    flights_found: int
    deals_matched: int
    notifications_sent: int
    errors: int

    def __str__(self) -> str:
        """Return human-readable summary of the check result."""
        return (
            f"users={self.users_checked}, "
            f"routes={self.routes_searched}, "
            f"flights={self.flights_found}, "
            f"deals={self.deals_matched}, "
            f"notifications={self.notifications_sent}, "
            f"errors={self.errors}"
        )
