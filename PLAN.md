# Raton - AI-Powered Flight Deals Bot

## Overview
A Telegram bot that monitors flight prices and notifies users about cheap deals. Powered by PydanticAI with Anthropic models for full conversational capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Raton Bot                                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   Telegram   │  │   Scheduler  │  │    PydanticAI Agent    │ │
│  │   Handler    │──│  (APScheduler)│──│  (Anthropic Claude)   │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│         │                 │                      │               │
│         ▼                 ▼                      ▼               │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                    Agent Tools                                ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐  ││
│  │  │  Amadeus   │  │Preferences │  │   Telegram Notifier    │  ││
│  │  │   Client   │  │  Manager   │  │                        │  ││
│  │  └────────────┘  └────────────┘  └────────────────────────┘  ││
│  └──────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                     Storage                                   ││
│  │              YAML files (per user)                            ││
│  └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack
- **Python 3.13** with `uv` package manager
- **python-telegram-bot** - Telegram integration
- **pydantic-ai** - AI agent framework (Anthropic Claude)
- **pydantic-settings** - Environment configuration
- **APScheduler** - Periodic flight checks
- **amadeus** - Official Amadeus Python SDK
- **pytest** - Testing
- **ruff** - Linting/formatting
- **pre-commit** - Git hooks

## Project Structure

```
raton/
├── pyproject.toml
├── .env.example
├── .pre-commit-config.yaml
├── README.md
├── src/
│   └── raton/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── config.py            # Pydantic settings
│       ├── bot/
│       │   ├── __init__.py
│       │   └── handlers.py      # Telegram handlers
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── agent.py         # PydanticAI agent definition
│       │   └── tools.py         # Agent tools
│       ├── services/
│       │   ├── __init__.py
│       │   ├── amadeus.py       # Amadeus SDK wrapper
│       │   ├── preferences.py   # User preferences manager
│       │   ├── history.py       # Chat history persistence
│       │   └── scheduler.py     # Flight check scheduler
│       └── models/
│           ├── __init__.py
│           └── schemas.py       # Pydantic models
├── data/
│   ├── preferences/             # User preference YAML files
│   └── history/                 # Chat history per user (JSON)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── ...
└── deploy/
    └── raton.service            # Systemd unit file
```

## Implementation Plan

### Phase 1: Project Setup
1. Initialize project with `uv init`
2. Configure `pyproject.toml` with dependencies
3. Set up `ruff` configuration
4. Create `.pre-commit-config.yaml` with ruff hooks
5. Create `.env.example` with required variables
6. Set up `pydantic-settings` configuration class

### Phase 2: Core Models
1. Create Pydantic models for:
   - Flight offers (from Amadeus)
   - User preferences (origin, destinations, dates, passengers, price thresholds)
   - Notifications

### Phase 3: Amadeus Integration
1. Create wrapper around official `amadeus` SDK
2. Configure with credentials from settings
3. Implement flight offers search method
4. Handle errors gracefully

### Phase 4: Preferences Manager
1. YAML-based storage for user preferences
2. One file per Telegram user (keyed by chat_id)
3. CRUD operations for preferences

### Phase 5: Chat History Manager
1. JSON-based storage for conversation history
2. One file per Telegram user
3. Load/save operations with message limit (last N messages)
4. Integration with PydanticAI for context

### Phase 6: PydanticAI Agent
1. Define agent with Anthropic Claude model
2. Implement tools:
   - `search_flights` - Query Amadeus for flights
   - `get_preferences` - Read user preferences
   - `set_preferences` - Update user preferences
   - `analyze_deal` - Evaluate if a flight is a good deal
3. System prompt for flight assistant personality

### Phase 7: Telegram Bot
1. Set up `python-telegram-bot` with async handlers
2. Route all messages through the AI agent
3. Handle commands: `/start`, `/help`, `/preferences`, `/search`
4. Implement notification sending

### Phase 8: Scheduler
1. Set up APScheduler with async support
2. Create job that:
   - Loads all user preferences
   - Queries Amadeus for matching flights
   - Passes results to AI agent for analysis
   - Sends notifications for good deals
3. Configure interval (hourly or per Amadeus limits)

### Phase 9: Main Entry Point
1. Wire everything together in `main.py`
2. Async application with graceful shutdown
3. Logging configuration

### Phase 10: Deployment
1. Create systemd service file
2. Document deployment steps
3. Environment setup on Digital Ocean VM

## Key Files to Create

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config, dependencies |
| `src/raton/config.py` | Pydantic settings |
| `src/raton/models/schemas.py` | Data models |
| `src/raton/services/amadeus.py` | Amadeus SDK wrapper |
| `src/raton/services/preferences.py` | User prefs YAML manager |
| `src/raton/services/history.py` | Chat history persistence |
| `src/raton/agent/agent.py` | PydanticAI agent |
| `src/raton/agent/tools.py` | Agent tools |
| `src/raton/bot/handlers.py` | Telegram handlers |
| `src/raton/services/scheduler.py` | APScheduler setup |
| `src/raton/main.py` | Entry point |

## Configuration (.env)

```
# Telegram
TELEGRAM_BOT_TOKEN=xxx

# Anthropic
ANTHROPIC_API_KEY=xxx

# Amadeus
AMADEUS_API_KEY=xxx
AMADEUS_API_SECRET=xxx
AMADEUS_BASE_URL=https://test.api.amadeus.com  # or production

# App
CHECK_INTERVAL_HOURS=1
LOG_LEVEL=INFO
DATA_DIR=./data
```

## Amadeus API Details

**SDK**: Official `amadeus` Python package (install via `pip install amadeus`)

**Authentication**: OAuth 2.0 (handled automatically by SDK)

**Key Endpoint - Flight Offers Search**:
```python
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='API_KEY',
    client_secret='API_SECRET'
)

response = amadeus.shopping.flight_offers_search.get(
    originLocationCode='MAD',  # IATA code
    destinationLocationCode='ATH',
    departureDate='2024-11-01',  # YYYY-MM-DD
    adults=1
)
```

**Parameters**: originLocationCode, destinationLocationCode, departureDate, returnDate (optional), adults, children, infants, travelClass, currencyCode, max (results limit)

**Limitations**:
- No American Airlines, Delta, British Airways, or low-cost carriers
- Free tier has monthly quota, then pay-as-you-go (€0.001-€0.025 per call)
- Token valid for 30 minutes (SDK handles refresh)

**Decision**: Use the official `amadeus` SDK instead of raw HTTP client - it handles auth, rate limiting, and retries.

## Verification Plan

1. **Unit tests**: Run `pytest` for all components
2. **Manual testing**:
   - Start bot locally
   - Send `/start` command via Telegram
   - Add flight preferences via conversation
   - Trigger manual flight search
   - Verify notifications are sent
3. **Integration test**:
   - Deploy to VM
   - Verify systemd service starts
   - Check logs for scheduled job execution
   - Confirm Telegram notifications arrive

## Decisions Made

1. **Chat History**: Full persistence - store conversation history per user for long-term context
2. **Price Tracking**: Deferred to post-MVP
3. **Amadeus SDK**: Use official `amadeus` Python package instead of raw HTTP client
