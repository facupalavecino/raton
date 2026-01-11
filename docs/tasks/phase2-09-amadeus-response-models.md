# Task 2.09: Amadeus Response Models

**Phase:** 2 - Domain Models
**Status:** Pending
**Depends on:** None (can be done in parallel with domain models)

## Objective

Model raw Amadeus API responses for parsing (separate from domain models).

## Deliverables

Create new file: `src/raton/models/amadeus.py`

### Model Definitions

```python
from pydantic import BaseModel, ConfigDict

class AmadeusSegment(BaseModel):
    """Raw segment from Amadeus API."""
    model_config = ConfigDict(populate_by_name=True)

    departure: dict  # {iataCode, terminal, at}
    arrival: dict    # {iataCode, terminal, at}
    carrierCode: str
    number: str
    aircraft: dict | None = None
    operating: dict | None = None
    duration: str | None = None  # ISO 8601 (e.g., "PT2H30M")

class AmadeusItinerary(BaseModel):
    """Raw itinerary from Amadeus API."""
    duration: str | None = None
    segments: list[AmadeusSegment]

class AmadeusPrice(BaseModel):
    """Raw price from Amadeus API."""
    currency: str
    total: str
    base: str | None = None
    fees: list[dict] | None = None
    grandTotal: str

class AmadeusFlightOffer(BaseModel):
    """Raw flight offer from Amadeus API."""
    type: str
    id: str
    source: str
    itineraries: list[AmadeusItinerary]
    price: AmadeusPrice
    validatingAirlineCodes: list[str]
    numberOfBookableSeats: int | None = None
    lastTicketingDate: str | None = None

class AmadeusResponse(BaseModel):
    """Complete Amadeus API response."""
    data: list[AmadeusFlightOffer]
    dictionaries: dict | None = None  # Reference data (carriers, aircraft, etc.)
```

## Acceptance Criteria

- [ ] Can parse actual Amadeus API response JSON
- [ ] Handles optional fields gracefully
- [ ] Clear separation from domain models (these are internal/API layer)
- [ ] camelCase field names match API exactly

## Tests Required

- `tests/models/test_amadeus.py`
  - Test parsing sample Amadeus response (full response)
  - Test handling missing optional fields
  - Test nested structure parsing (segments within itineraries)

## Sample API Response

Store in `tests/fixtures/amadeus_response.json` - see Amadeus Flight Offers Search API documentation for structure.

## Implementation Notes

- These models match the Amadeus API response structure EXACTLY
- Use camelCase field names (matches API, no aliasing needed)
- These are "throw-away" models for parsing only
- NOT exported from `raton.models` (internal use in mappers)
- Will be converted to domain models via mappers (Task 2.10)
