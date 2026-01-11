# Task 2.10: Mapper Functions

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** Tasks 2.05, 2.09 (FlightOffer, Amadeus Response Models)

## Objective

Convert Amadeus API models to domain models.

## Deliverables

Create new file: `src/raton/models/mappers.py`

### Function Definitions

```python
from datetime import timedelta
from raton.models.amadeus import (
    AmadeusSegment,
    AmadeusItinerary,
    AmadeusFlightOffer,
    AmadeusResponse,
)
from raton.models.flight import FlightSegment, Itinerary, FlightOffer, Price

def parse_iso8601_duration(iso_duration: str | None) -> timedelta | None:
    """
    Parse ISO 8601 duration string to timedelta.

    Examples:
        "PT2H30M" -> timedelta(hours=2, minutes=30)
        "PT14H5M" -> timedelta(hours=14, minutes=5)
        "PT1H" -> timedelta(hours=1)
        "PT45M" -> timedelta(minutes=45)
    """

def amadeus_segment_to_domain(segment: AmadeusSegment) -> FlightSegment:
    """Convert Amadeus segment to domain segment."""

def amadeus_itinerary_to_domain(itinerary: AmadeusItinerary) -> Itinerary:
    """Convert Amadeus itinerary to domain itinerary."""

def amadeus_price_to_domain(price: AmadeusPrice) -> Price:
    """Convert Amadeus price to domain price."""

def amadeus_offer_to_domain(offer: AmadeusFlightOffer) -> FlightOffer:
    """Convert Amadeus offer to domain flight offer."""

def amadeus_response_to_offers(response: AmadeusResponse) -> list[FlightOffer]:
    """Convert complete API response to list of domain offers."""
```

## Acceptance Criteria

- [ ] All mappers produce valid domain models
- [ ] ISO 8601 duration parsing handles PT format correctly
- [ ] Handles timezone-aware datetimes correctly
- [ ] Handles missing optional data gracefully
- [ ] Pure functions with no side effects

## Tests Required

- `tests/models/test_mappers.py`
  - Test `parse_iso8601_duration` with various formats
  - Test each mapper function individually
  - Test full response mapping end-to-end
  - Test edge cases (missing data, empty lists)

## Duration Parsing Examples

```python
# ISO 8601 duration format: PT[n]H[n]M[n]S
parse_iso8601_duration("PT2H30M")  # -> timedelta(hours=2, minutes=30)
parse_iso8601_duration("PT14H5M")  # -> timedelta(hours=14, minutes=5)
parse_iso8601_duration("PT1H")     # -> timedelta(hours=1)
parse_iso8601_duration("PT45M")    # -> timedelta(minutes=45)
parse_iso8601_duration(None)       # -> None
```

## Implementation Notes

- Pure functions, no side effects
- Consider using regex for ISO 8601 parsing (simple approach for MVP)
- Alternative: `isodate` library (adds dependency)
- Handle all edge cases (missing optional fields)
- Amadeus returns ISO 8601 timestamps with timezone for departure/arrival
