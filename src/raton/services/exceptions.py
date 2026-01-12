"""Custom exceptions for service layer operations.

This module defines domain-specific exceptions for handling various error
scenarios in service operations including Amadeus API and preferences storage.
"""

from __future__ import annotations


class AmadeusError(Exception):
    """Base exception for all Amadeus-related errors.

    This is the parent class for all Amadeus exceptions. Catching this
    exception will catch all Amadeus-specific errors.
    """

    pass


class AmadeusAuthError(AmadeusError):
    """Authentication or authorization failure with Amadeus API.

    Raised when API credentials are invalid, expired, or when the API
    returns a 401 or 403 status code.
    """

    pass


class AmadeusRateLimitError(AmadeusError):
    """Rate limit exceeded for Amadeus API.

    Raised when the API returns a 429 status code, indicating that
    the quota has been exceeded.
    """

    pass


class AmadeusNetworkError(AmadeusError):
    """Network or connectivity error when calling Amadeus API.

    Raised when there are connection timeouts, DNS failures, or other
    network-related issues preventing communication with the API.
    """

    pass


class AmadeusApiError(AmadeusError):
    """General API error from Amadeus.

    Raised when the API returns an error response (4xx or 5xx status codes)
    that doesn't fall into more specific error categories.
    """

    pass


class PreferencesError(Exception):
    """Base exception for all preferences-related errors.

    This is the parent class for all preferences exceptions. Catching this
    exception will catch all preferences-specific errors.
    """

    pass


class PreferencesNotFoundError(PreferencesError):
    """User preferences not found.

    Raised when attempting to load, update, or delete preferences for a user
    that doesn't exist in the storage.
    """

    pass


class PreferencesStorageError(PreferencesError):
    """Error reading or writing preferences to storage.

    Raised when there are I/O errors, permission issues, or data corruption
    when interacting with the preferences storage system.
    """

    pass


class TelegramError(Exception):
    """Base exception for all Telegram-related errors.

    This is the parent class for all Telegram exceptions. Catching this
    exception will catch all Telegram-specific errors.
    """

    pass


class TelegramAuthError(TelegramError):
    """Bot token is invalid or unauthorized.

    Raised when the Telegram bot token is invalid, expired, or lacks
    necessary permissions to perform the requested action.
    """

    pass


class TelegramChatNotFoundError(TelegramError):
    """Chat ID is invalid or bot was blocked by user.

    Raised when attempting to send a message to a chat that doesn't exist,
    or when the user has blocked the bot.
    """

    pass


class TelegramDeliveryError(TelegramError):
    """Failed to deliver message to Telegram.

    Raised when the Telegram API returns an error that prevents message
    delivery but doesn't fall into more specific error categories.
    """

    pass


class TelegramNetworkError(TelegramError):
    """Network error communicating with Telegram API.

    Raised when there are connection timeouts, DNS failures, or other
    network-related issues preventing communication with Telegram servers.
    """

    pass
