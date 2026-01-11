# Task 2.03: Itinerary Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Task 2.02 (Flight Segment)

## Objective

Model a complete itinerary (one direction of travel, may have multiple segments).

## Deliverables

Add to: `src/raton/models/flight.py`

### Model Definition

```python
from pydantic import BaseModel, computed_field

class Itinerary(BaseModel):
    segments: list[FlightSegment]
    duration: timedelta | None = None  # Total duration including layovers

    @computed_field
    @property
    def origin(self) -> str:
        """First departure airport."""
        return self.segments[0].departure_airport

    @computed_field
    @property
    def destination(self) -> str:
        """Last arrival airport."""
        return self.segments[-1].arrival_airport

    @computed_field
    @property
    def stops(self) -> int:
        """Number of stops (segments - 1)."""
        return len(self.segments) - 1

    @computed_field
    @property
    def is_direct(self) -> bool:
        """True if no stops."""
        return self.stops == 0
```

## Acceptance Criteria

- [ ] Computed properties work correctly
- [ ] Duration calculated from segments if not provided (optional)
- [ ] Handles single-segment (direct) flights
- [ ] Handles multi-segment (connecting) flights
- [ ] Validates at least one segment exists

## Tests Required

- `tests/models/test_flight.py`
  - Test direct flight itinerary (1 segment)
  - Test multi-stop itinerary (2+ segments)
  - Test computed fields (origin, destination, stops, is_direct)
  - Test empty segments validation (should fail)

## Implementation Notes

- Computed fields are included in JSON serialization by default
- Consider adding a validator to ensure segments list is not empty
