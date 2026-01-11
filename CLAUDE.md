# Claude Code Guidelines for Raton

## Project Overview

**Raton** is an AI-powered Telegram bot that monitors flight prices and notifies users about cheap deals. The name means "mouse" in Spanish - because we're being thrifty!

This project solves a real problem: tracking flight prices is tedious and time-consuming. Raton automates this by periodically querying the Amadeus API for flights matching user preferences, then using an AI agent (powered by PydanticAI and Anthropic Claude) to analyze deals and notify users via Telegram. The bot is conversational - users can chat naturally to set preferences, ask questions about routes, or trigger manual searches.

The architecture is straightforward: a long-running async Python process that combines a Telegram bot handler, an APScheduler for periodic checks, and a PydanticAI agent that orchestrates everything. User data (preferences, chat history) is stored in simple YAML/JSON files - no database needed for the MVP. The system is designed to be multi-user from the start, with each user's data isolated by their Telegram chat ID.

We aim for small, quality contributions and shipping working software. Every feature should be minimal, tested, and verified to work before moving on.

## Contributing

**Note:** For human contributors (including team members), see `CONTRIBUTING.md` for detailed guidelines on branch naming, commit messages, PR workflow, and code quality standards.

You will address me as "Pala"

### TDD Workflow

We follow Test-Driven Development. Every task must follow this workflow:

1. **Understand** - Review project context and the goal of the task
2. **Define scenarios** - Identify acceptance criteria as concrete scenarios (happy path + key edge cases)
3. **Write tests first** - Implement those scenarios as failing tests
4. **Code** - Write the minimum code to make tests pass
5. **Verify** - Ensure all tests pass and linting is clean

Keep test coverage pragmatic: happy path and a few important edge cases. No need for exhaustive coverage.

### Approval Process

Before writing any code:

1. **Consult the software architect** - Discuss the approach and get architect approval
2. **Get Pala's approval** - Present the plan to Pala for final sign-off
3. **Then code** - Only after both approvals, begin implementation

## Technical Stack

- **Python 3.13** - Use modern Python features (type hints, match statements, etc.)
- **uv** - Package manager (already available globally)
- **pydantic-ai** - AI agent framework with Anthropic Claude
- **python-telegram-bot** - Async Telegram bot library
- **amadeus** - Official Amadeus Python SDK for flight data
- **pydantic-settings** - Environment configuration
- **APScheduler** - Async job scheduling
- **pytest** - Testing framework
- **ruff** - Linting and formatting
- **pre-commit** - Git hooks for code quality

## Code Style Guidelines

### Linting and Formatting

- Run `uv run pre-commit run -a` to lint and format all files
- Pre-commit hooks enforce this automatically on commits
- Configuration lives in `pyproject.toml` and `.pre-commit-config.yaml`

### Documentation

- All public methods, functions, and classes must have Google Style docstrings
- Docstrings should describe what the function does, its arguments, and return values
- Keep docstrings concise but informative

### Type Hints

- Use type hints everywhere
- Use `from __future__ import annotations` for forward references
- Prefer `list[str]` over `List[str]` (Python 3.9+ syntax)

### Async

- This is an async-first codebase
- Use `async def` for I/O operations
- Use `asyncio` for concurrency
- The Telegram bot and scheduler run in the same event loop

### Imports

- Use absolute imports: `from raton.services.amadeus import AmadeusClient`
- Group imports: stdlib, third-party, local (ruff handles this)

### Error Handling

- Use custom exceptions where appropriate
- Log errors with context
- Never silently swallow exceptions

## Project Structure

```
src/raton/
├── main.py          # Entry point, wires everything together
├── config.py        # Pydantic settings from .env
├── bot/             # Telegram bot handlers
├── agent/           # PydanticAI agent and tools
├── services/        # Business logic (amadeus, preferences, scheduler)
└── models/          # Pydantic models/schemas
```

## Storage

- User preferences: YAML files in `data/preferences/{chat_id}.yaml`
- Chat history: JSON files in `data/history/{chat_id}.json`

## Testing Guidelines

### Test Structure

- Tests must be functions, not classes
- Use descriptive names that explain what is being tested
- Configuration and shared setup belongs in fixtures under `conftest.py` files

### Test Documentation

Every test function must have a docstring in GIVEN/WHEN/THEN format:

```python
def test_search_flights_returns_empty_list_when_no_matches():
    """
    GIVEN a user preference for flights from NYC to LAX
    WHEN no flights match the criteria
    THEN an empty list is returned
    """
    ...
```

### Test Commands

- Run all tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov=raton`
- Run specific test: `uv run pytest tests/test_amadeus.py::test_name`

### Mocking

- Mock external APIs (Amadeus, Telegram, Anthropic) in tests
- Use `pytest-asyncio` for async tests

## Verification Requirements

Every contribution must be verified to work before considering a task complete. This means:

1. **Code runs without errors** - The feature works as intended
2. **Tests pass** - All existing tests still pass, new tests cover the change
3. **Linting passes** - `uv run pre-commit run -a` exits cleanly
4. **Verification instructions provided** - Document how to verify the change works (in PR description or working session notes)

Do not mark a task as done until you can demonstrate it works.

For commit message and branch naming standards when creating commits or PRs, follow the conventions in `CONTRIBUTING.md`.

## Running the Project

```bash
# Install dependencies
uv sync

# Run locally
uv run python -m raton.main

# Run tests
uv run pytest

# Lint and format
uv run pre-commit run -a
```

## Environment Variables

Required in `.env`:

- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `ANTHROPIC_API_KEY` - From Anthropic Console
- `AMADEUS_API_KEY` - From Amadeus Developer Portal
- `AMADEUS_API_SECRET` - From Amadeus Developer Portal

Optional:

- `AMADEUS_BASE_URL` - Default: `https://test.api.amadeus.com`
- `CHECK_INTERVAL_HOURS` - Default: `1`
- `LOG_LEVEL` - Default: `INFO`
- `DATA_DIR` - Default: `./data`

## Deployment

The bot runs as a systemd service on a Digital Ocean VM. See `deploy/raton.service` for the unit file.

## External API Notes

### Amadeus

- Free tier has monthly quotas
- Does NOT include: American Airlines, Delta, British Airways, low-cost carriers
- OAuth token auto-refreshes (SDK handles this)
- Rate limiting handled by SDK

### Telegram

- Use async handlers from `python-telegram-bot`
- All user messages route through the AI agent
- Commands: `/start`, `/help`, `/preferences`, `/search`

## Implementation Reference

See `docs/PLAN.md` for the detailed implementation plan with all phases.
