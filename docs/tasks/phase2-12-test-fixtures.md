# Task 2.12: Test Fixtures

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Tasks 2.01-2.10 (All model tasks)

## Objective

Create reusable test fixtures for models.

## Deliverables

### 1. Modify: `tests/conftest.py`

```python
import pytest
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal

from raton.models import (
    FlightSegment,
    Itinerary,
    Price,
    FlightOffer,
    Route,
    DateRange,
    UserPreferences,
    CabinClass,
    StopPreference,
)

@pytest.fixture
def sample_flight_segment() -> FlightSegment:
    """Create a sample flight segment for testing."""
    return FlightSegment(
        departure_airport="JFK",
        arrival_airport="BCN",
        departure_time=datetime(2024, 6, 15, 10, 30, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 6, 15, 23, 45, tzinfo=timezone.utc),
        carrier_code="IB",
        flight_number="6251",
        duration=timedelta(hours=8, minutes=15),
    )

@pytest.fixture
def sample_connecting_segment() -> FlightSegment:
    """Create a connecting flight segment for testing."""
    return FlightSegment(
        departure_airport="MAD",
        arrival_airport="BCN",
        departure_time=datetime(2024, 6, 16, 1, 30, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 6, 16, 2, 45, tzinfo=timezone.utc),
        carrier_code="IB",
        flight_number="3214",
        duration=timedelta(hours=1, minutes=15),
    )

@pytest.fixture
def sample_direct_itinerary(sample_flight_segment) -> Itinerary:
    """Create a sample direct itinerary for testing."""
    return Itinerary(
        segments=[sample_flight_segment],
        duration=timedelta(hours=8, minutes=15),
    )

@pytest.fixture
def sample_connecting_itinerary(sample_flight_segment, sample_connecting_segment) -> Itinerary:
    """Create a sample connecting itinerary for testing."""
    return Itinerary(
        segments=[sample_flight_segment, sample_connecting_segment],
        duration=timedelta(hours=10, minutes=30),
    )

@pytest.fixture
def sample_price() -> Price:
    """Create a sample price for testing."""
    return Price(
        currency="USD",
        total=Decimal("450.00"),
        base=Decimal("380.00"),
        fees=Decimal("70.00"),
    )

@pytest.fixture
def sample_flight_offer(sample_direct_itinerary, sample_price) -> FlightOffer:
    """Create a sample flight offer for testing."""
    return FlightOffer(
        id="1",
        source="GDS",
        itineraries=[sample_direct_itinerary],
        price=sample_price,
        validating_airline="IB",
        cabin_class=CabinClass.ECONOMY,
        number_of_bookable_seats=9,
    )

@pytest.fixture
def sample_route() -> Route:
    """Create a sample route for testing."""
    return Route(origin="JFK", destination="BCN")

@pytest.fixture
def sample_date_range() -> DateRange:
    """Create a sample date range for testing."""
    return DateRange(
        earliest=date(2024, 6, 1),
        latest=date(2024, 6, 30),
    )

@pytest.fixture
def sample_user_preferences(sample_route, sample_date_range) -> UserPreferences:
    """Create sample user preferences for testing."""
    return UserPreferences(
        chat_id=12345678,
        routes=[sample_route],
        departure_dates=sample_date_range,
        max_price=Decimal("500.00"),
        currency="USD",
        passengers=1,
        cabin_class=CabinClass.ECONOMY,
        stop_preference=StopPreference.DIRECT_ONLY,
    )
```

### 2. Create: `tests/fixtures/amadeus_response.json`

Sample Amadeus API response for testing mappers. Should include:
- At least 2 flight offers
- One direct flight, one connecting flight
- All fields populated for comprehensive testing

## Acceptance Criteria

- [ ] Fixtures provide realistic test data
- [ ] Sample Amadeus response matches real API structure
- [ ] Fixtures are composable (can build on each other)
- [ ] All fixtures have descriptive docstrings

## Tests Required

- N/A (fixtures are tested by their usage in other tests)

## Implementation Notes

- Fixtures should cover common scenarios (direct, connecting, round-trip)
- Use realistic but fake data
- Sample Amadeus response should be based on actual API docs/responses
- Create `tests/fixtures/` directory if it doesn't exist
