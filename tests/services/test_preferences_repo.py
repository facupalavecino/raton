"""Tests for preferences repository.

This module tests the PreferencesRepository for persisting user preferences to YAML files.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from raton.models import CabinClass, DateRange, Route, StopPreference, TripType, UserPreferences
from raton.services.exceptions import PreferencesNotFoundError, PreferencesStorageError
from raton.services.preferences import PreferencesRepository


@pytest.fixture
def preferences_repo(tmp_path: Path) -> PreferencesRepository:
    """Create a PreferencesRepository with a temporary directory.

    Args:
        tmp_path: Pytest's temporary directory fixture

    Returns:
        PreferencesRepository instance for testing
    """
    return PreferencesRepository(preferences_dir=tmp_path)


@pytest.fixture
def sample_preferences() -> UserPreferences:
    """Create sample user preferences for testing.

    Returns:
        UserPreferences instance with test data
    """
    return UserPreferences(
        routes=[
            Route(origin="JFK", destination="LAX"),
            Route(origin="JFK", destination="SFO"),
        ],
        date_range=DateRange(
            earliest=date(2026, 3, 1),
            latest=date(2026, 3, 31),
        ),
        max_price=Decimal("500.00"),
        currency="USD",
        passengers=2,
        cabin_class=CabinClass.ECONOMY,
        stop_preference=StopPreference.DIRECT_ONLY,
        trip_type=TripType.ROUND_TRIP,
    )


@pytest.mark.asyncio
async def test_save_creates_yaml_file_for_user(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
    tmp_path: Path,
):
    """
    GIVEN a user's preferences and chat ID
    WHEN saving the preferences
    THEN a YAML file is created with the correct content
    """
    chat_id = 12345

    await preferences_repo.save(chat_id, sample_preferences)

    expected_file = tmp_path / f"{chat_id}.yaml"
    assert expected_file.exists()

    with open(expected_file) as f:
        saved_data = yaml.safe_load(f)

    assert saved_data["max_price"] == "500.00"
    assert saved_data["currency"] == "USD"
    assert saved_data["passengers"] == 2
    assert len(saved_data["routes"]) == 2
    assert saved_data["routes"][0]["origin"] == "JFK"
    assert saved_data["routes"][0]["destination"] == "LAX"


@pytest.mark.asyncio
async def test_save_creates_directory_if_not_exists(
    sample_preferences: UserPreferences,
    tmp_path: Path,
):
    """
    GIVEN a preferences directory that doesn't exist
    WHEN saving preferences
    THEN the directory is created automatically
    """
    nonexistent_dir = tmp_path / "nested" / "preferences"
    repo = PreferencesRepository(preferences_dir=nonexistent_dir)
    chat_id = 12345

    await repo.save(chat_id, sample_preferences)

    assert nonexistent_dir.exists()
    assert (nonexistent_dir / f"{chat_id}.yaml").exists()


@pytest.mark.asyncio
async def test_load_returns_preferences_for_existing_user(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
):
    """
    GIVEN preferences saved for a user
    WHEN loading the preferences
    THEN the correct UserPreferences object is returned
    """
    chat_id = 12345
    await preferences_repo.save(chat_id, sample_preferences)

    loaded_preferences = await preferences_repo.load(chat_id)

    assert loaded_preferences == sample_preferences
    assert loaded_preferences.max_price == Decimal("500.00")
    assert loaded_preferences.currency == "USD"
    assert loaded_preferences.passengers == 2
    assert len(loaded_preferences.routes) == 2


@pytest.mark.asyncio
async def test_load_raises_not_found_for_nonexistent_user(
    preferences_repo: PreferencesRepository,
):
    """
    GIVEN no preferences saved for a user
    WHEN attempting to load preferences
    THEN PreferencesNotFoundError is raised
    """
    chat_id = 99999

    with pytest.raises(PreferencesNotFoundError) as exc_info:
        await preferences_repo.load(chat_id)

    assert str(chat_id) in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_modifies_existing_preferences(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
):
    """
    GIVEN existing preferences for a user
    WHEN updating with new preferences
    THEN the file is updated with new values
    """
    chat_id = 12345
    await preferences_repo.save(chat_id, sample_preferences)

    updated_preferences = UserPreferences(
        routes=[Route(origin="LAX", destination="NYC")],
        date_range=DateRange(
            earliest=date(2026, 4, 1),
            latest=date(2026, 4, 30),
        ),
        max_price=Decimal("800.00"),
        currency="EUR",
        passengers=1,
    )

    await preferences_repo.update(chat_id, updated_preferences)

    loaded = await preferences_repo.load(chat_id)
    assert loaded == updated_preferences
    assert loaded.max_price == Decimal("800.00")
    assert loaded.currency == "EUR"


@pytest.mark.asyncio
async def test_delete_removes_preferences_file(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
    tmp_path: Path,
):
    """
    GIVEN existing preferences for a user
    WHEN deleting the preferences
    THEN the file is removed from storage
    """
    chat_id = 12345
    await preferences_repo.save(chat_id, sample_preferences)

    expected_file = tmp_path / f"{chat_id}.yaml"
    assert expected_file.exists()

    await preferences_repo.delete(chat_id)

    assert not expected_file.exists()


@pytest.mark.asyncio
async def test_delete_raises_not_found_for_nonexistent_user(
    preferences_repo: PreferencesRepository,
):
    """
    GIVEN no preferences saved for a user
    WHEN attempting to delete preferences
    THEN PreferencesNotFoundError is raised
    """
    chat_id = 99999

    with pytest.raises(PreferencesNotFoundError) as exc_info:
        await preferences_repo.delete(chat_id)

    assert str(chat_id) in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_users_returns_all_chat_ids(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
):
    """
    GIVEN multiple users with saved preferences
    WHEN listing all users
    THEN all chat IDs are returned
    """
    chat_ids = [12345, 67890, 11111]

    for chat_id in chat_ids:
        await preferences_repo.save(chat_id, sample_preferences)

    users = await preferences_repo.list_users()

    assert sorted(users) == sorted(chat_ids)


@pytest.mark.asyncio
async def test_list_users_returns_empty_list_when_no_files(
    preferences_repo: PreferencesRepository,
):
    """
    GIVEN no preferences saved
    WHEN listing all users
    THEN an empty list is returned
    """
    users = await preferences_repo.list_users()

    assert users == []


@pytest.mark.asyncio
async def test_exists_returns_true_for_existing_user(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
):
    """
    GIVEN preferences saved for a user
    WHEN checking if preferences exist
    THEN True is returned
    """
    chat_id = 12345
    await preferences_repo.save(chat_id, sample_preferences)

    exists = await preferences_repo.exists(chat_id)

    assert exists is True


@pytest.mark.asyncio
async def test_exists_returns_false_for_nonexistent_user(
    preferences_repo: PreferencesRepository,
):
    """
    GIVEN no preferences saved for a user
    WHEN checking if preferences exist
    THEN False is returned
    """
    chat_id = 99999

    exists = await preferences_repo.exists(chat_id)

    assert exists is False


@pytest.mark.asyncio
async def test_handles_corrupted_yaml_file(
    preferences_repo: PreferencesRepository,
    tmp_path: Path,
):
    """
    GIVEN a corrupted YAML file for a user
    WHEN attempting to load preferences
    THEN PreferencesStorageError is raised
    """
    chat_id = 12345
    corrupted_file = tmp_path / f"{chat_id}.yaml"

    with open(corrupted_file, "w") as f:
        f.write("invalid: yaml: content: [[[")

    with pytest.raises(PreferencesStorageError) as exc_info:
        await preferences_repo.load(chat_id)

    assert "corrupted" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_save_overwrites_existing_file(
    preferences_repo: PreferencesRepository,
    sample_preferences: UserPreferences,
):
    """
    GIVEN existing preferences for a user
    WHEN saving new preferences with the same chat ID
    THEN the file is overwritten with new values
    """
    chat_id = 12345

    await preferences_repo.save(chat_id, sample_preferences)

    new_preferences = UserPreferences(
        routes=[Route(origin="BOS", destination="MIA")],
        date_range=DateRange(
            earliest=date(2026, 5, 1),
            latest=date(2026, 5, 15),
        ),
        max_price=Decimal("300.00"),
        currency="USD",
    )
    await preferences_repo.save(chat_id, new_preferences)

    loaded = await preferences_repo.load(chat_id)
    assert loaded == new_preferences
    assert loaded.max_price == Decimal("300.00")
