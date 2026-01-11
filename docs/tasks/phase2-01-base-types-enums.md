# Task 2.01: Base Types and Enums

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** None

## Objective

Establish foundational types used across multiple models.

## Deliverables

Create new file: `src/raton/models/base.py`

### Types to Define

```python
from enum import Enum

class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

class TripType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"

class StopPreference(str, Enum):
    ANY = "any"
    DIRECT_ONLY = "direct_only"
    MAX_ONE_STOP = "max_one_stop"
```

### Type Aliases (Optional)
- `IATACode`: Constrained string (3 uppercase letters)
- `Currency`: Constrained string (3 uppercase letters)

## Acceptance Criteria

- [ ] All enums are defined with appropriate values
- [ ] Type aliases use proper Python 3.13 syntax
- [ ] Docstrings explain each type
- [ ] Unit tests verify enum values can be serialized/deserialized

## Tests Required

- `tests/models/test_base.py`
  - Test enum JSON serialization
  - Test enum from string conversion
  - Test enum values match expected strings

## Implementation Notes

- Use `str, Enum` mixin for JSON-friendly serialization
- Keep it simple - type aliases are optional for MVP
