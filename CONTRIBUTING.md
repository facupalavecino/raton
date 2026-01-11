# Contributing to Raton

Thanks for your interest in contributing to Raton! We value quality over quantity and aim to ship working software in small, well-tested increments.

## Getting Started

1. **Fork and clone** the repository
2. **Install dependencies**: `uv sync`
3. **Set up pre-commit hooks**: `uv run pre-commit install`
4. **Copy `.env.example` to `.env`** and fill in your API keys
5. **Run tests** to verify setup: `uv run pytest`

## Development Workflow

We follow Test-Driven Development (TDD):

1. **Understand** - Review project context and task requirements
2. **Define scenarios** - Identify acceptance criteria (happy path + key edge cases)
3. **Write tests first** - Implement scenarios as failing tests
4. **Code** - Write minimum code to make tests pass
5. **Verify** - Ensure tests pass and linting is clean

## Branch Naming

Use this format: `<type>/<ticket>-<description>` or `<type>/<description>`

### Branch Types

- `feat/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code restructuring
- `docs/` - Documentation changes
- `test/` - Adding or updating tests
- `chore/` - Dependencies, tooling, configs
- `perf/` - Performance improvements
- `hotfix/` - Urgent production fixes

### Naming Rules

**DO:**
- Use lowercase only: `feat/add-search` ✅
- Use hyphens: `feat/flight-search` ✅
- Be concise but descriptive: `fix/null-pointer-in-amadeus` ✅
- Include issue ID when available: `feat/42-user-preferences` ✅

**DON'T:**
- Use spaces or underscores: `feat/add search`, `feat/add_search` ❌
- Be vague: `feat/updates` ❌
- Include your name: `feat/john-feature` ❌

**Examples:**
```bash
feat/42-telegram-webhook
fix/amadeus-token-refresh
docs/update-readme
refactor/simplify-preferences
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Structure

**Type:** Same as branch types (`feat`, `fix`, `refactor`, etc.)

**Scope (optional):** Component affected
- Examples: `feat(bot):`, `fix(amadeus):`, `refactor(agent):`

**Subject:**
- Keep under 50 characters
- Use imperative mood: "add feature" not "added feature"
- No period at end
- Complete the sentence: "If applied, this commit will..."

**Body (optional):**
- Wrap at 72 characters
- Explain *why* this change exists, not *what* changed
- Include context that isn't obvious from code

**Footer (optional):**
- Breaking changes: `BREAKING CHANGE: description`
- Issue references: `Closes #123`

### Commit Examples

**Simple:**
```
feat(bot): add /search command handler
```

**With body:**
```
fix(amadeus): handle token refresh race condition

The Amadeus SDK can fail when multiple concurrent requests
trigger token refresh simultaneously. Added a lock to ensure
only one refresh happens at a time.

Fixes #42
```

**Breaking change:**
```
refactor(preferences)!: change YAML structure for multi-city

BREAKING CHANGE: Preference files now use nested structure.
Users must re-configure preferences or migrate manually.
```

### Commit Rules

- **One logical change per commit** - Keep commits atomic
- **All commits should build** - Don't break the build mid-PR
- **All commits should pass tests** - Each commit is potentially deployable
- **Explain non-obvious decisions** - Use commit body when helpful

## Code Quality

### Before Committing

```bash
# Run linting and formatting
uv run pre-commit run -a

# Run tests
uv run pytest

# Check coverage (optional)
uv run pytest --cov=raton
```

Pre-commit hooks will enforce linting automatically, but run manually to catch issues early.

### Code Style

- **Type hints everywhere** - Use modern Python 3.13+ syntax
- **Google-style docstrings** - All public functions/classes
- **Async-first** - Use `async def` for I/O operations
- **Simple over clever** - Avoid over-engineering

See `CLAUDE.md` for detailed style guidelines.

## Testing

### Test Structure

- Tests are **functions**, not classes
- Use descriptive names: `test_search_returns_empty_when_no_matches`
- Every test needs a **GIVEN/WHEN/THEN docstring**:

```python
def test_search_flights_returns_empty_list_when_no_matches():
    """
    GIVEN a user preference for flights from NYC to LAX
    WHEN no flights match the criteria
    THEN an empty list is returned
    """
    ...
```

### Test Coverage

- Happy path + key edge cases
- Mock external APIs (Amadeus, Telegram, Anthropic)
- Use `pytest-asyncio` for async tests

### Running Tests

```bash
# All tests
uv run pytest

# Specific test
uv run pytest tests/test_amadeus.py::test_name

# With coverage
uv run pytest --cov=raton

# Watch mode (requires pytest-watch)
uv run ptw
```

## Pull Requests

### Before Opening a PR

1. ✅ All tests pass
2. ✅ Linting is clean (`uv run pre-commit run -a`)
3. ✅ Code runs without errors
4. ✅ You've verified the feature works

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added X
- Fixed Y
- Refactored Z

## Testing
How to verify this works:
1. Step one
2. Step two
3. Expected result

## Checklist
- [ ] Tests added/updated
- [ ] Linting passes
- [ ] Documentation updated (if needed)
- [ ] Verified working locally
```

### PR Guidelines

- **Keep PRs small** - 1-3 files changed is ideal, <500 lines
- **One concern per PR** - Don't mix features, fixes, and refactors
- **Draft PRs are fine** - Use them to get early feedback
- **Link to issues** - Use `Closes #123` in description
- **Respond to reviews promptly** - Keep the conversation moving

### Merge Strategy

- We **squash and merge** to keep history clean
- Your commits will become one commit on `main`
- Write good PR titles - they become the commit message

## Common Pitfalls

### For Everyone

- ❌ Committing directly to `main`
- ❌ Vague commit messages: "fix bug", "updates"
- ❌ Skipping tests "to save time"
- ❌ Not running linting before committing
- ❌ PRs with >500 lines of changes

### For Juniors Specifically

- ❌ Opening too many branches at once - finish one first
- ❌ Never pushing - push daily, even incomplete work
- ❌ Fear of small PRs - small is fast to review
- ❌ Not asking questions - ask early, ask often

### For Seniors Specifically

- ❌ Over-engineering - build what's needed, not what might be needed
- ❌ Assuming context - explain your reasoning in commits/PRs
- ❌ Skipping the approval process - everyone follows TDD

## Need Help?

- **Questions?** Open a GitHub Discussion
- **Found a bug?** Open an issue
- **Want to propose a feature?** Open an issue first to discuss

## Quick Reference

**Branch:**
```bash
git checkout -b feat/42-short-description
```

**Commit:**
```bash
git commit -m "feat(scope): short description"
```

**Before PR:**
```bash
uv run pre-commit run -a
uv run pytest
```

**Open PR:**
- Small, focused changes
- Good description with testing steps
- Link to issue

---

Thanks for contributing! 🐭
