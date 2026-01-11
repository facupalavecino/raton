# Task 2.08: UserPreferences Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Tasks 2.01, 2.06, 2.07 (Base Types, Route, DateRange)

## Objective

Model complete user preferences for flight monitoring.

## Deliverables

Add to: `src/raton/models/preferences.py`

### Model Definition

```python
from decimal import Decimal
from typing import Self
from pydantic import BaseModel, ConfigDict, model_validator, field_validator
from raton.models.base import CabinClass, StopPreference

class UserPreferences(BaseModel):
    chat_id: int                                    # Telegram chat ID
    routes: list[Route]                             # Routes to monitor
    departure_dates: DateRange | None = None        # When to depart
    return_dates: DateRange | None = None           # When to return (None = one-way)
    max_price: Decimal | None = None                # Price threshold
    currency: str = "USD"                           # Preferred currency
    passengers: int = 1                             # Number of adults
    cabin_class: CabinClass = CabinClass.ECONOMY
    stop_preference: StopPreference = StopPreference.ANY
    max_duration_hours: int | None = None           # Max total flight time

    model_config = ConfigDict(
        use_enum_values=True,  # Serialize enums as values for YAML readability
    )

    @model_validator(mode='after')
    def validate_preferences(self) -> Self:
        """Validate preference combinations."""
        if not self.routes:
            raise ValueError("At least one route is required")
        if self.return_dates and not self.departure_dates:
            raise ValueError("Return dates require departure dates to be set")
        if not 1 <= self.passengers <= 9:
            raise ValueError("Passengers must be between 1 and 9")
        return self

    @field_validator('max_price', mode='before')
    @classmethod
    def parse_decimal(cls, v):
        """Parse string prices to Decimal."""
        if v is None:
            return None
        return Decimal(str(v))
```

## Acceptance Criteria

- [ ] At least one route required
- [ ] Return dates require departure dates
- [ ] Passengers between 1-9
- [ ] YAML serialization produces human-readable output
- [ ] Default values work correctly (economy, any stops, USD)
- [ ] chat_id is required and identifies the user

## Tests Required

- `tests/models/test_preferences.py`
  - Test minimal preferences (just chat_id and routes)
  - Test full preferences with all options
  - Test validation failures (no routes, invalid passengers, etc.)
  - Test YAML round-trip serialization
  - Test defaults applied correctly
  - Test return_dates without departure_dates rejected

## Example YAML Output

```yaml
chat_id: 12345678
routes:
  - origin: JFK
    destination: BCN
currency: USD
max_price: 500.00
cabin_class: economy
stop_preference: direct_only
passengers: 2
```

## Implementation Notes

- `chat_id` is the primary identifier (Telegram user)
- Multiple routes allowed (monitor several destinations)
- All constraints optional except routes and chat_id
- Enums serialize as values for YAML readability (`economy` not `CabinClass.ECONOMY`)
