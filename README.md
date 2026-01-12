# Raton

An AI-powered Telegram bot that monitors flight prices and notifies you about cheap deals. The name means "mouse" in Spanish - because we're being thrifty!

## The Problem

Tracking flight prices is tedious and time-consuming. Airlines and aggregators don't always notify you when prices drop, and manually checking multiple routes daily isn't practical.

## The Solution

Raton automates flight price monitoring by:

1. **Storing your preferences** - Routes, dates, price limits, cabin class, stop preferences
2. **Periodically checking prices** - Queries the Amadeus API on a configurable schedule
3. **Analyzing deals** - Evaluates flights against your rules (max price, stops, duration)
4. **Notifying you** - Sends Telegram messages with flight details and booking links

## Features

- **Multi-user support** - Each user's preferences are isolated by Telegram chat ID
- **Flexible preferences** - Multiple routes, date ranges, cabin classes, stop preferences
- **Smart deal detection** - Rules engine evaluates price, currency, stops, and duration
- **Rich notifications** - Formatted messages with flight details and Google Flights links
- **File-based storage** - Simple YAML files, no database required
- **Graceful operation** - Continues checking other users if one fails

## Tech Stack

- **Python 3.13** - Modern Python with full type hints
- **pydantic-ai** - AI agent framework (for conversational features)
- **python-telegram-bot** - Async Telegram bot library
- **amadeus** - Official Amadeus Python SDK for flight data
- **pydantic-settings** - Environment configuration
- **APScheduler** - Async job scheduling
- **Logfire** - Structured logging and observability

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- API keys for Telegram, Anthropic, and Amadeus

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/raton.git
cd raton

# Install dependencies
uv sync
```

### Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/botfather) |
| `ANTHROPIC_API_KEY` | API key from [Anthropic Console](https://console.anthropic.com/) |
| `AMADEUS_API_KEY` | API key from [Amadeus Developer Portal](https://developers.amadeus.com/) |
| `AMADEUS_API_SECRET` | API secret from Amadeus Developer Portal |

Optional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AMADEUS_HOSTNAME` | `test` | `test` or `production` |
| `CHECK_INTERVAL_HOURS` | `1` | Hours between price checks |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DATA_DIR` | `./data` | Storage directory for preferences |

### Running

```bash
# Run the bot
uv run python -m raton.main
```

The bot will start checking prices immediately and then repeat at the configured interval.

## Project Structure

```
src/raton/
├── main.py              # Entry point, main loop
├── config.py            # Configuration from .env
├── logging_config.py    # Structured logging setup
├── bot/                 # Telegram command handlers
├── agent/               # PydanticAI agent for conversations
├── models/              # Domain models
│   ├── base.py          # Enums (CabinClass, TripType, etc.)
│   ├── flight.py        # FlightOffer, Itinerary, FlightSegment
│   ├── preferences.py   # UserPreferences, Route, DateRange
│   ├── amadeus.py       # API response models
│   └── mappers.py       # Amadeus → Domain converters
└── services/            # Business logic
    ├── amadeus.py       # Amadeus API client
    ├── preferences.py   # Preferences persistence (YAML)
    ├── rules.py         # Deal detection rules engine
    ├── telegram.py      # Telegram notification service
    ├── orchestrator.py  # Check cycle coordinator
    └── exceptions.py    # Custom exceptions
```

## User Preferences

Preferences are stored as YAML files in `data/preferences/{chat_id}.yaml`:

```yaml
routes:
  - origin: JFK
    destination: CDG
  - origin: EWR
    destination: LHR
departure_date_range:
  start: 2025-06-01
  end: 2025-06-15
return_date_range:
  start: 2025-06-15
  end: 2025-06-30
max_price: 800.00
currency: USD
adults: 2
cabin_class: economy
stop_preference: any
max_duration_hours: 12
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=raton

# Run specific test file
uv run pytest tests/services/test_amadeus.py
```

### Linting and Formatting

```bash
# Run all pre-commit hooks
uv run pre-commit run -a
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- TDD workflow
- Branch naming conventions
- Commit message standards
- Code style requirements

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Project Foundation | Complete | Setup, config, logging, tooling |
| 2. Domain Models | Complete | Flight & preference models |
| 3. Amadeus Integration | Complete | Flight search client |
| 4. Preferences Storage | Complete | YAML persistence |
| 5. Deal Detection | Complete | Rules engine |
| 6. Telegram Notifications | Complete | Rich formatted messages |
| 7. Scheduled Checks | Complete | Main loop with orchestrator |
| 8. Telegram Commands | In Progress | /start, /help, /preferences, /search |
| 9. Long-Running Service | Planned | APScheduler, graceful shutdown |
| 10. AI Agent | Planned | Conversational interface with Claude |

## Limitations

The Amadeus API free tier has some limitations:

- Monthly request quotas
- Does **not** include: American Airlines, Delta, British Airways, most low-cost carriers
- Test environment may have limited/stale data

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
