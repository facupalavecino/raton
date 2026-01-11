# Task 2.04: Price Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Task 2.01 (Base Types)

## Objective

Model pricing information for a flight offer.

## Deliverables

Add to: `src/raton/models/flight.py`

### Model Definition

```python
from decimal import Decimal
from pydantic import BaseModel, field_validator

class Price(BaseModel):
    currency: str           # 3-letter code (e.g., "USD")
    total: Decimal          # Grand total including all fees
    base: Decimal | None = None   # Base fare before fees
    fees: Decimal | None = None   # Total fees

    @field_validator('total', 'base', 'fees', mode='before')
    @classmethod
    def parse_decimal(cls, v):
        """Parse string prices to Decimal."""
        if v is None:
            return None
        return Decimal(str(v))
```

## Acceptance Criteria

- [ ] Prices parsed correctly from strings (Amadeus returns strings)
- [ ] Decimal precision maintained through serialization
- [ ] Currency stored as-is (3-letter code)
- [ ] Optional fields (base, fees) handle None gracefully

## Tests Required

- `tests/models/test_flight.py`
  - Test Decimal parsing from string
  - Test Decimal parsing from float/int
  - Test zero/null fee handling
  - Test JSON serialization preserves precision
  - Test currency field

## Implementation Notes

- ALWAYS use `Decimal` for money (never float)
- Amadeus returns prices as strings, validator handles conversion
- Keep it simple for MVP - individual fee breakdown not needed
