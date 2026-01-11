# Task 2.11: Package Exports

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Tasks 2.01-2.10 (All model tasks)

## Objective

Clean up package exports in `__init__.py` for clean public API.

## Deliverables

Modify: `src/raton/models/__init__.py`

### Implementation

```python
"""Pydantic models and schemas for Raton."""

from raton.models.base import CabinClass, StopPreference, TripType
from raton.models.flight import FlightOffer, FlightSegment, Itinerary, Price
from raton.models.preferences import DateRange, Route, UserPreferences

__all__ = [
    # Enums
    "CabinClass",
    "StopPreference",
    "TripType",
    # Flight models
    "FlightOffer",
    "FlightSegment",
    "Itinerary",
    "Price",
    # Preference models
    "DateRange",
    "Route",
    "UserPreferences",
]
```

## Acceptance Criteria

- [ ] All public models exported from `raton.models`
- [ ] API models NOT exported (internal use only)
- [ ] Mappers NOT exported (internal use only)
- [ ] Import from `raton.models` works cleanly
- [ ] `__all__` defines public API

## Tests Required

- `tests/models/test_init.py`
  - Test all exports are importable
  - Test typical import patterns work:
    - `from raton.models import FlightOffer, UserPreferences`
    - `from raton.models import CabinClass, StopPreference`

## Implementation Notes

- Only export PUBLIC domain models
- Internal models (`amadeus.py`) stay internal
- Mappers are used by services, not exported
- This creates a clean public API for the models package
