# Task 2.02: Flight Segment Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Task 2.01 (Base Types)

## Objective

Model a single flight segment (one takeoff-to-landing portion).

## Deliverables

Create new file: `src/raton/models/flight.py`

### Model Definition

```python
from datetime import datetime, timedelta
from pydantic import BaseModel

class FlightSegment(BaseModel):
    departure_airport: str      # IATA code (e.g., "JFK")
    arrival_airport: str        # IATA code (e.g., "BCN")
    departure_time: datetime    # Timezone-aware
    arrival_time: datetime      # Timezone-aware
    carrier_code: str           # Marketing carrier (e.g., "IB")
    flight_number: str          # e.g., "6251"
    operating_carrier_code: str | None = None  # If different from marketing
    aircraft_code: str | None = None           # e.g., "359"
    duration: timedelta | None = None          # Segment duration
```

## Acceptance Criteria

- [ ] Model validates IATA codes are 3 characters (optional for MVP)
- [ ] Model handles optional fields gracefully
- [ ] JSON serialization works correctly with datetime/timedelta
- [ ] Can construct from typical Amadeus segment data

## Tests Required

- `tests/models/test_flight.py`
  - Test creation with all fields
  - Test creation with minimal fields (only required)
  - Test JSON round-trip serialization
  - Test datetime parsing with timezone

## Implementation Notes

- Store times as `datetime` with timezone info (Amadeus returns ISO 8601)
- Duration as `timedelta` for easy calculations
- Operating carrier is optional (same as marketing if not specified)
