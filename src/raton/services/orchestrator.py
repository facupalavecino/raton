"""Flight check orchestrator service.

This module provides the CheckOrchestrator which coordinates complete flight
check cycles: loading preferences, searching flights, evaluating rules, and
sending notifications.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from raton.models import CheckResult
from raton.services.exceptions import (
    AmadeusError,
    PreferencesError,
    TelegramError,
)
from raton.services.rules import evaluate_flight

if TYPE_CHECKING:
    from raton.services.amadeus import AmadeusClient
    from raton.services.preferences import PreferencesRepository
    from raton.services.telegram import TelegramNotifier

logger = logging.getLogger(__name__)


class CheckOrchestrator:
    """Orchestrates flight check cycles across all users.

    Coordinates the complete check flow:
    1. List all users with saved preferences
    2. For each user, load their preferences
    3. For each route in preferences, search for flights
    4. Evaluate each flight against user rules
    5. Send notifications for matching deals

    Handles errors gracefully - API failures or notification errors don't
    crash the cycle, they're logged and processing continues.

    Args:
        amadeus: Client for searching flights
        preferences: Repository for loading user preferences
        notifier: Service for sending Telegram notifications

    Example:
        >>> orchestrator = CheckOrchestrator(amadeus, preferences, notifier)
        >>> result = await orchestrator.run_check_cycle()
        >>> logger.info("Check complete: %s", result)
    """

    def __init__(
        self,
        amadeus: AmadeusClient,
        preferences: PreferencesRepository,
        notifier: TelegramNotifier,
    ) -> None:
        """Initialize the orchestrator with required services.

        Args:
            amadeus: Amadeus API client for flight searches
            preferences: Repository for user preferences
            notifier: Telegram notification service
        """
        self._amadeus = amadeus
        self._preferences = preferences
        self._notifier = notifier

    async def run_check_cycle(self) -> CheckResult:
        """Run a complete flight check cycle for all users.

        Iterates through all users, searches flights for their routes,
        evaluates matches, and sends notifications for deals found.

        Returns:
            CheckResult with statistics from the cycle

        Note:
            This method never raises exceptions - all errors are logged
            and the cycle continues. Check the `errors` field in the
            result to see if any errors occurred.
        """
        users_checked = 0
        routes_searched = 0
        flights_found = 0
        deals_matched = 0
        notifications_sent = 0
        errors = 0

        chat_ids = await self._preferences.list_users()

        if not chat_ids:
            logger.info("No users with preferences found")
            return CheckResult(
                users_checked=0,
                routes_searched=0,
                flights_found=0,
                deals_matched=0,
                notifications_sent=0,
                errors=0,
            )

        logger.info(f"Starting check cycle for {len(chat_ids)} users")

        for chat_id in chat_ids:
            try:
                prefs = await self._preferences.load(chat_id)
            except PreferencesError as e:
                logger.error(f"Failed to load preferences for user {chat_id}: {e}")
                errors += 1
                continue

            users_checked += 1
            logger.debug(f"Checking user {chat_id} with {len(prefs.routes)} routes")

            for route in prefs.routes:
                routes_searched += 1

                try:
                    flights = await self._amadeus.search_flights(
                        origin=route.origin,
                        destination=route.destination,
                        departure_date=prefs.date_range.earliest,
                        return_date=(
                            prefs.date_range.latest
                            if prefs.trip_type.value == "round_trip"
                            else None
                        ),
                        adults=prefs.passengers,
                        cabin_class=prefs.cabin_class,
                    )
                except AmadeusError:
                    logger.exception(
                        f"Amadeus search failed for {route.origin}->{route.destination}"
                    )
                    errors += 1
                    continue

                flights_found += len(flights)
                logger.debug(
                    f"Found {len(flights)} flights for {route.origin}->{route.destination}"
                )

                for flight in flights:
                    match_result = evaluate_flight(flight, prefs)

                    if match_result.is_match:
                        deals_matched += 1
                        logger.info(
                            f"Deal found for user {chat_id}: {flight.id} {route.origin}->{route.destination} at {flight.price.total} {flight.price.currency}"
                        )

                        try:
                            await self._notifier.send_flight_deal(
                                chat_id=chat_id,
                                flight=flight,
                                match_result=match_result,
                            )
                            notifications_sent += 1
                        except TelegramError as e:
                            logger.error(f"Failed to send notification to user {chat_id}: {e}")
                            errors += 1

        result = CheckResult(
            users_checked=users_checked,
            routes_searched=routes_searched,
            flights_found=flights_found,
            deals_matched=deals_matched,
            notifications_sent=notifications_sent,
            errors=errors,
        )

        logger.info(f"Check cycle complete: {result}")
        return result
