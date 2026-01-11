# Task 2.05: FlightOffer Model

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Tasks 2.02, 2.03, 2.04 (Segment, Itinerary, Price)

## Objective

Model a complete flight offer - the main domain entity.

## Deliverables

Add to: `src/raton/models/flight.py`

### Model Definition

```python
from datetime import date, timedelta
from pydantic import BaseModel, computed_field
from raton.models.base import CabinClass

class FlightOffer(BaseModel):
    id: str                              # Amadeus offer ID
    source: str                          # GDS source
    itineraries: list[Itinerary]         # 1 for one-way, 2 for round-trip
    price: Price
    validating_airline: str              # Airline issuing ticket
    cabin_class: CabinClass | None = None
    number_of_bookable_seats: int | None = None
    last_ticketing_date: date | None = None

    @computed_field
    @property
    def is_round_trip(self) -> bool:
        """True if offer has outbound and return itineraries."""
        return len(self.itineraries) > 1

    @computed_field
    @property
    def total_duration(self) -> timedelta:
        """Sum of all itinerary durations."""
        total = timedelta()
        for itinerary in self.itineraries:
            if itinerary.duration:
                total += itinerary.duration
        return total

    @computed_field
    @property
    def total_stops(self) -> int:
        """Total stops across all itineraries."""
        return sum(it.stops for it in self.itineraries)
```

## Acceptance Criteria

- [ ] Can represent both one-way and round-trip offers
- [ ] All computed properties work correctly
- [ ] ID is preserved for potential booking reference
- [ ] Model is JSON/YAML serializable
- [ ] Validates at least one itinerary exists

## Tests Required

- `tests/models/test_flight.py`
  - Test one-way flight offer (1 itinerary)
  - Test round-trip flight offer (2 itineraries)
  - Test computed properties (is_round_trip, total_duration, total_stops)
  - Test full JSON round-trip serialization
  - Test with all optional fields
  - Test with minimal fields

## Implementation Notes

- This is the main entity returned from flight searches
- ID maps to Amadeus offer ID for potential future booking integration
- Cabin class may not always be available from API response
