# Raton - Flight Deals Bot

## Vision

A Telegram bot that monitors flight prices and notifies users about cheap deals. Users define their preferences (routes, dates, price thresholds), and Raton periodically checks for matching flights and sends notifications when good deals are found.

## Guiding Principles

1. **Ship working software** - Each phase delivers something usable
2. **Simple first** - Rules before AI, cron before service, files before database
3. **Clean separation** - Each module has one responsibility
4. **Testable** - Every component can be tested in isolation

## Architecture Overview

```
Phase 1-6 (V1 - Cron-based):

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   Cron   │────▶│ Amadeus  │────▶│  Rules   │────▶│ Telegram │
│   Job    │     │  Client  │     │  Engine  │     │ Notifier │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                                  │
                       ▼                                  │
                ┌──────────┐                              │
                │Preferences│◀─────────────────────────────┘
                │  (YAML)  │
                └──────────┘

Phase 7-8 (V2 - Service with Telegram commands):

┌──────────────────────────────────────────────────────────┐
│                    Long-running Service                   │
│  ┌──────────────┐              ┌──────────────────────┐  │
│  │   Telegram   │              │     Scheduler        │  │
│  │   Handlers   │              │   (periodic check)   │  │
│  └──────────────┘              └──────────────────────┘  │
│         │                               │                │
│         ▼                               ▼                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Core Services                          │ │
│  │   Amadeus | Preferences | Rules | Notifier          │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

Phase 9+ (V3 - AI-powered):

┌──────────────────────────────────────────────────────────┐
│                         Service                          │
│  ┌──────────────┐              ┌──────────────────────┐  │
│  │   Telegram   │              │     Scheduler        │  │
│  │   Handlers   │              │                      │  │
│  └──────────────┘              └──────────────────────┘  │
│         │                               │                │
│         ▼                               ▼                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              PydanticAI Agent                       │ │
│  │   - Conversational preference management            │ │
│  │   - Natural language flight queries                 │ │
│  │   - Smart deal analysis and explanations            │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Core Services (as tools)               │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Python 3.13** with `uv` package manager
- **amadeus** - Official Amadeus Python SDK for flight data
- **python-telegram-bot** - Telegram integration
- **pydantic** / **pydantic-settings** - Data validation and configuration
- **APScheduler** - Periodic job scheduling (Phase 7+)
- **pydantic-ai** - AI agent framework (Phase 9+)
- **pytest** - Testing
- **ruff** + **pre-commit** - Code quality

---

## Phases

### Phase 1: Project Foundation

**Objective:** Establish project structure, tooling, and configuration management.

**Delivers:**
- Runnable Python project with dependency management
- Code quality tooling (linting, formatting, pre-commit hooks)
- Configuration system that reads from environment variables
- CI-ready test infrastructure

**Acceptance Criteria:**
- [ ] `uv sync` installs all dependencies without errors
- [ ] `uv run pytest` runs (even if no tests yet) without errors
- [ ] `uv run pre-commit run -a` passes
- [ ] Configuration class loads values from `.env` file
- [ ] `.env.example` documents all required/optional variables

---

### Phase 2: Domain Models

**Objective:** Define the core data structures that represent flights and user preferences.

**Delivers:**
- Pydantic models for flight offers (price, route, times, airline, stops)
- Pydantic models for user preferences (origins, destinations, date ranges, price thresholds, constraints)
- Clear separation between API response models and domain models

**Acceptance Criteria:**
- [ ] Flight offer model can represent a flight with all relevant attributes
- [ ] User preferences model captures: routes, date flexibility, max price, passenger count, stop preferences
- [ ] Models are serializable to/from JSON and YAML
- [ ] Unit tests validate model constraints and serialization

---

### Phase 3: Amadeus Integration

**Objective:** Fetch flight offers from the Amadeus API.

**Delivers:**
- Amadeus client that searches for flight offers
- Transformation from Amadeus API response to domain models
- Error handling for API failures, rate limits, and invalid responses

**Acceptance Criteria:**
- [ ] Client can search flights given origin, destination, dates, and passenger count
- [ ] API responses are transformed into domain Flight models
- [ ] Client handles authentication automatically
- [ ] Client handles and surfaces errors gracefully (network, auth, rate limit)
- [ ] Unit tests with mocked API responses
- [ ] At least one integration test against Amadeus test environment (can be skipped in CI)

---

### Phase 4: Preferences Storage

**Objective:** Persist and retrieve user preferences.

**Delivers:**
- Storage system for user preferences (YAML files, one per user)
- CRUD operations: create, read, update, delete preferences
- User isolation by Telegram chat ID

**Acceptance Criteria:**
- [ ] Can save preferences for a user (by chat_id)
- [ ] Can load preferences for a user
- [ ] Can update existing preferences
- [ ] Can delete a user's preferences
- [ ] Can list all users with preferences
- [ ] File storage location is configurable
- [ ] Unit tests cover all operations

---

### Phase 5: Deal Detection

**Objective:** Determine if a flight offer matches user preferences and qualifies as a "good deal."

**Delivers:**
- Rules engine that evaluates flights against user preferences
- Configurable rules: max price, direct flights only, max duration, preferred airlines
- Clear pass/fail result with reason

**Acceptance Criteria:**
- [ ] Given a flight and user preferences, returns whether it's a match
- [ ] Price threshold is enforced
- [ ] Stop/connection preferences are enforced
- [ ] Duration limits are enforced (if specified)
- [ ] Returns structured result (match: bool, reasons: list)
- [ ] Unit tests cover all rule combinations

---

### Phase 6: Telegram Notifications

**Objective:** Send flight deal notifications to users via Telegram.

**Delivers:**
- Telegram client that sends messages to a chat ID
- Message formatting for flight deals (markdown)
- Error handling for delivery failures

**Acceptance Criteria:**
- [ ] Can send a text message to a Telegram chat ID
- [ ] Flight deals are formatted readably (route, price, times, airline, link)
- [ ] Handles Telegram API errors gracefully
- [ ] Unit tests with mocked Telegram API
- [ ] Manual verification: send a test message to a real chat

---

### Phase 7: Scheduled Flight Checks (V1 Complete)

**Objective:** Periodically check for flight deals and notify users. This is the first fully functional version.

**Delivers:**
- Entry point script that can be run via cron
- Orchestration: load preferences → fetch flights → apply rules → send notifications
- Logging for observability
- Basic deployment documentation

**Acceptance Criteria:**
- [ ] Single command runs a complete check cycle for all users
- [ ] Logs show: users checked, flights found, deals matched, notifications sent
- [ ] Can be scheduled via system cron
- [ ] No crashes on empty preferences or API failures (graceful degradation)
- [ ] End-to-end test: create preferences, run check, receive Telegram notification
- [ ] README documents how to set up and run

**Milestone:** V1 - Usable flight deal notifications via cron job

---

### Phase 8: Telegram Command Handlers

**Objective:** Allow users to manage preferences via Telegram commands.

**Delivers:**
- Telegram bot that listens for messages
- Command handlers: `/start`, `/help`, `/preferences`, `/search`
- Preference management via structured commands
- Manual flight search triggered by user

**Acceptance Criteria:**
- [ ] Bot responds to `/start` with welcome message
- [ ] Bot responds to `/help` with available commands
- [ ] Users can view their current preferences via `/preferences`
- [ ] Users can update preferences via commands (exact UX to be designed)
- [ ] Users can trigger an immediate flight search via `/search`
- [ ] Bot handles unknown commands gracefully
- [ ] Unit tests for command parsing and responses

---

### Phase 9: Long-Running Service

**Objective:** Replace cron with a persistent service that handles both scheduled checks and real-time Telegram interaction.

**Delivers:**
- Async service that runs continuously
- Integrated scheduler for periodic flight checks
- Telegram bot polling in the same process
- Graceful shutdown handling
- Systemd service file for deployment

**Acceptance Criteria:**
- [ ] Service starts and runs indefinitely
- [ ] Scheduled checks execute at configured intervals
- [ ] Telegram commands are processed in real-time
- [ ] Service shuts down cleanly on SIGTERM/SIGINT
- [ ] Systemd unit file provided
- [ ] Deployment documentation updated

**Milestone:** V2 - Interactive Telegram bot with automated checks

---

### Phase 10: AI Agent Integration

**Objective:** Add conversational AI for natural language interaction and smarter deal analysis.

**Delivers:**
- PydanticAI agent with Anthropic Claude
- Natural language preference management ("I want to fly to Barcelona in March for under $300")
- Conversational flight queries ("Find me the cheapest flight to anywhere warm")
- AI-powered deal explanations ("This is a great deal because...")
- Chat history persistence for context

**Acceptance Criteria:**
- [ ] Users can set preferences via natural conversation
- [ ] Users can ask questions about flights in natural language
- [ ] Agent uses existing services (Amadeus, preferences, rules) as tools
- [ ] Agent provides explanations for why a deal is good/bad
- [ ] Conversation history is preserved across sessions
- [ ] Graceful fallback if AI service is unavailable
- [ ] Cost monitoring/limits for API usage

**Milestone:** V3 - AI-powered conversational flight assistant

---

## Future Considerations (Post-MVP)

These are explicitly out of scope for the phases above but worth noting for future direction:

- **Price tracking:** Historical price data to detect actual deals vs normal prices
- **Multi-destination search:** "Anywhere in Europe under $400"
- **Calendar integration:** Sync with user's calendar for date availability
- **Web dashboard:** Visual preference management
- **Group trips:** Coordinate searches for multiple travelers
- **Alerts customization:** Quiet hours, frequency preferences

---

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | YAML files | Simple, human-readable, sufficient for MVP scale |
| Flight data source | Amadeus SDK | Official SDK handles auth/retry, good free tier |
| AI framework | PydanticAI | Native Pydantic integration, async support |
| Scheduler | APScheduler | Async support, in-process, well-maintained |
| Initial runtime | Cron | Simplest path to working software |

---

## External API Notes

### Amadeus

- Free tier has monthly quotas (~2000 calls/month in test)
- Does NOT include: American Airlines, Delta, British Airways, most low-cost carriers
- Test environment uses real (but cached) data
- SDK handles OAuth token refresh automatically

### Telegram

- Bot token from @BotFather
- Long polling is simpler than webhooks for single-instance deployment
- Markdown formatting supported in messages
- Rate limits are generous for notification use case
