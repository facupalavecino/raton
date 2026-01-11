# Task 2.07: DateRange Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** None

## Objective

Model flexible date ranges for flight search.

## Deliverables

Add to: `src/raton/models/preferences.py`

### Model Definition

```python
from datetime import date
from typing import Self
from pydantic import BaseModel, computed_field, model_validator

class DateRange(BaseModel):
    earliest: date
    latest: date
    flexible_days: int = 0  # Days of flexibility around dates

    @model_validator(mode='after')
    def validate_date_order(self) -> Self:
        """Earliest must be before or equal to latest."""
        if self.earliest > self.latest:
            raise ValueError("Earliest date must be before or equal to latest date")
        return self

    @computed_field
    @property
    def is_single_day(self) -> bool:
        """True if searching for a specific date."""
        return self.earliest == self.latest
```

## Acceptance Criteria

- [ ] Validates earliest <= latest
- [ ] Supports single-day searches (earliest == latest)
- [ ] Flexible days default to 0
- [ ] Serializable to YAML (human-readable date format)

## Tests Required

- `tests/models/test_preferences.py`
  - Test valid date range (earliest < latest)
  - Test single day (earliest == latest)
  - Test invalid order rejected (earliest > latest)
  - Test flexible days default and custom values
  - Test is_single_day computed field

## Implementation Notes

- Use `datetime.date` not `datetime.datetime` for dates
- Flexible days will be used by Amadeus search (date +/- N days)
- YAML serialization should produce readable dates (2024-03-15 not timestamps)
