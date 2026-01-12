"""Preferences repository for persisting user preferences.

This module provides storage and retrieval of user preferences to/from YAML files.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import yaml
from pydantic import ValidationError

from raton.config import Settings
from raton.models.preferences import UserPreferences
from raton.services.exceptions import PreferencesNotFoundError, PreferencesStorageError


class PreferencesRepository:
    """Repository for persisting user preferences to YAML files.

    Each user's preferences are stored in a separate file named by their
    Telegram chat ID: {preferences_dir}/{chat_id}.yaml

    Args:
        preferences_dir: Directory path for storing preference files

    Example:
        >>> repo = PreferencesRepository(Path("./data/preferences"))
        >>> await repo.save(12345, user_preferences)
        >>> prefs = await repo.load(12345)
    """

    def __init__(self, preferences_dir: Path) -> None:
        """Initialize the preferences repository.

        Args:
            preferences_dir: Directory path for storing preference files
        """
        self.preferences_dir = preferences_dir

    @classmethod
    def from_settings(cls, settings: Settings) -> PreferencesRepository:
        """Create a PreferencesRepository from application settings.

        Args:
            settings: Application settings containing preferences directory path

        Returns:
            PreferencesRepository instance configured from settings
        """
        return cls(preferences_dir=settings.preferences_dir)

    def _get_file_path(self, chat_id: int) -> Path:
        """Get the file path for a user's preferences.

        Args:
            chat_id: Telegram chat ID

        Returns:
            Path to the user's preferences file
        """
        return self.preferences_dir / f"{chat_id}.yaml"

    async def save(self, chat_id: int, preferences: UserPreferences) -> None:
        """Save user preferences to a YAML file.

        Creates the preferences directory if it doesn't exist.
        Overwrites existing preferences if present.

        Args:
            chat_id: Telegram chat ID
            preferences: User preferences to save

        Raises:
            PreferencesStorageError: If there's an error writing to storage
        """

        def _save_sync() -> None:
            try:
                self.preferences_dir.mkdir(parents=True, exist_ok=True)

                data = preferences.model_dump(mode="json")

                file_path = self._get_file_path(chat_id)
                with open(file_path, "w") as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            except OSError as e:
                raise PreferencesStorageError(
                    f"Failed to save preferences for user {chat_id}: {e}"
                ) from e

        await asyncio.to_thread(_save_sync)

    async def load(self, chat_id: int) -> UserPreferences:
        """Load user preferences from a YAML file.

        Args:
            chat_id: Telegram chat ID

        Returns:
            UserPreferences object loaded from storage

        Raises:
            PreferencesNotFoundError: If preferences don't exist for the user
            PreferencesStorageError: If there's an error reading from storage or parsing the file
        """

        def _load_sync() -> UserPreferences:
            file_path = self._get_file_path(chat_id)

            if not file_path.exists():
                raise PreferencesNotFoundError(f"No preferences found for user {chat_id}")

            try:
                with open(file_path) as f:
                    data = yaml.safe_load(f)

                return UserPreferences.model_validate(data)
            except yaml.YAMLError as e:
                raise PreferencesStorageError(
                    f"Failed to parse corrupted preferences file for user {chat_id}: {e}"
                ) from e
            except ValidationError as e:
                raise PreferencesStorageError(
                    f"Invalid preferences data for user {chat_id}: {e}"
                ) from e
            except OSError as e:
                raise PreferencesStorageError(
                    f"Failed to load preferences for user {chat_id}: {e}"
                ) from e

        return await asyncio.to_thread(_load_sync)

    async def update(self, chat_id: int, preferences: UserPreferences) -> None:
        """Update existing user preferences.

        This is an alias for save() as the operation is the same.

        Args:
            chat_id: Telegram chat ID
            preferences: Updated user preferences

        Raises:
            PreferencesStorageError: If there's an error writing to storage
        """
        await self.save(chat_id, preferences)

    async def delete(self, chat_id: int) -> None:
        """Delete user preferences.

        Args:
            chat_id: Telegram chat ID

        Raises:
            PreferencesNotFoundError: If preferences don't exist for the user
            PreferencesStorageError: If there's an error deleting the file
        """

        def _delete_sync() -> None:
            file_path = self._get_file_path(chat_id)

            if not file_path.exists():
                raise PreferencesNotFoundError(f"No preferences found for user {chat_id}")

            try:
                file_path.unlink()
            except OSError as e:
                raise PreferencesStorageError(
                    f"Failed to delete preferences for user {chat_id}: {e}"
                ) from e

        await asyncio.to_thread(_delete_sync)

    async def list_users(self) -> list[int]:
        """List all users with saved preferences.

        Returns:
            List of chat IDs for all users with preferences.
            Returns empty list if no preferences exist.

        Raises:
            PreferencesStorageError: If there's an error reading the directory
        """

        def _list_sync() -> list[int]:
            if not self.preferences_dir.exists():
                return []

            try:
                chat_ids = []
                for file_path in self.preferences_dir.glob("*.yaml"):
                    try:
                        chat_id = int(file_path.stem)
                        chat_ids.append(chat_id)
                    except ValueError:
                        continue
                return chat_ids
            except OSError as e:
                raise PreferencesStorageError(
                    f"Failed to list users in preferences directory: {e}"
                ) from e

        return await asyncio.to_thread(_list_sync)

    async def exists(self, chat_id: int) -> bool:
        """Check if preferences exist for a user.

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if preferences exist, False otherwise
        """

        def _exists_sync() -> bool:
            return self._get_file_path(chat_id).exists()

        return await asyncio.to_thread(_exists_sync)
