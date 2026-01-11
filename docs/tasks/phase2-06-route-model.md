# Task 2.06: Route Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Task 2.01 (Base Types)

## Objective

Model a user's desired route (origin-destination pair).

## Deliverables

Create new file: `src/raton/models/preferences.py`

### Model Definition

```python
from typing import Self
from pydantic import BaseModel, model_validator

class Route(BaseModel):
    origin: str       # IATA code or city code (e.g., "JFK" or "NYC")
    destination: str  # IATA code or city code (e.g., "BCN")

    @model_validator(mode='after')
    def validate_different_airports(self) -> Self:
        """Origin and destination must be different."""
        if self.origin == self.destination:
            raise ValueError("Origin and destination must be different")
        return self
```

## Acceptance Criteria

- [ ] Validates origin != destination
- [ ] Accepts valid IATA/city codes
- [ ] Serializable to YAML (human-readable)
- [ ] Case handling: decide if codes should be uppercase

## Tests Required

- `tests/models/test_preferences.py`
  - Test valid route creation
  - Test same origin/destination rejected
  - Test YAML serialization
  - Test case sensitivity (if enforced)

## Implementation Notes

- Keep route simple - just origin/destination
- Dates belong in preferences, not route
- Allow city codes (NYC) not just airport codes (JFK)
- Consider converting to uppercase on validation
