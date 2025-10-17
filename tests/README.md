# Regen Python MCP Test Suite

**Principle:** Real Blockchain Data Only - No Mocks

This test suite validates the Regen Network MCP server using **real data** from the Regen Network blockchain. All tests follow the principle established in `CLAUDE.md`: no mock or fake data.

## Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov

# Run all tests (offline, using cached fixtures)
pytest tests/

# Run with live network connection
pytest --online tests/

# Run specific test category
pytest -m unit tests/               # Unit tests only
pytest -m integration tests/        # Integration tests
pytest -m client tests/             # Client tests

# Update fixtures from live network
pytest --update-fixtures tests/

# Generate coverage report
pytest --cov=src --cov-report=html tests/
```

## Directory Structure

```
tests/
├── README.md                      # This file
├── conftest.py                    # Pytest configuration & fixtures
├── fixtures/
│   ├── __init__.py
│   └── fixture_manager.py         # Real data capture & caching
├── client/
│   ├── __init__.py
│   └── test_regen_client.py       # RegenClient tests
├── tools/
│   ├── __init__.py
│   ├── test_credit_tools.py       # Credit module tools
│   ├── test_basket_tools.py       # Basket module tools
│   ├── test_marketplace_tools.py  # Marketplace tools
│   ├── test_bank_tools.py         # Bank module tools
│   ├── test_distribution_tools.py # Distribution tools
│   ├── test_governance_tools.py   # Governance tools
│   └── test_analytics_tools.py    # Analytics tools
├── integration/
│   ├── __init__.py
│   └── test_server_integration.py # Server-level tests
├── e2e/
│   ├── __init__.py
│   └── test_mcp_workflows.py      # End-to-end user scenarios
└── test_prompts.py                # Prompt tests (existing)
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast, offline tests
- Use cached fixtures
- Test individual functions
- **Coverage Goal:** 60% of suite

### Integration Tests (`@pytest.mark.integration`)
- Medium speed
- May use network
- Test multiple components together
- **Coverage Goal:** 30% of suite

### End-to-End Tests (`@pytest.mark.e2e`)
- Slow, full workflows
- Simulate real user scenarios
- Test complete MCP protocol flow
- **Coverage Goal:** 10% of suite

## Test Markers

```python
@pytest.mark.unit          # Fast, offline
@pytest.mark.integration   # Medium, may use network
@pytest.mark.e2e          # Slow, full workflow
@pytest.mark.online       # Requires network connection
@pytest.mark.offline      # Can run without network
@pytest.mark.slow         # Any slow test
@pytest.mark.client       # Client layer
@pytest.mark.tools        # Tools layer
@pytest.mark.server       # Server layer
@pytest.mark.mcp         # MCP protocol
```

## Real Data Strategy

### Fixture Manager

All tests use `FixtureManager` to capture and cache real blockchain data:

```python
# In tests/conftest.py
@pytest.fixture
async def real_credit_types(fixture_manager):
    """Provides real credit types from Regen Network."""
    async def capture():
        client = get_regen_client()
        return await client.query_credit_types()

    return await fixture_manager.get_or_capture(
        fixture_name="credit_types",
        capture_func=capture,
        ttl_days=30,  # Cache for 30 days
        category="client"
    )
```

### Data Flow

```
First Run:           Subsequent Runs:
┌─────────────┐     ┌─────────────┐
│ Test needs  │     │ Test needs  │
│ credit data │     │ credit data │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Check cache  │    │ Check cache  │
│ (empty)      │    │ (found!)     │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ Query live   │    │ Use cached   │
│ Regen Network│    │ data (fast)  │
└──────┬───────┘    └──────────────┘
       │
       ▼
┌──────────────┐
│ Save fixture │
│ to cache     │
└──────────────┘
```

### Cached Data Location

```
data/test_fixtures/
├── metadata.json                    # Capture timestamps & TTLs
├── client/
│   ├── credit_types.json           # Cached 30 days
│   ├── credit_classes.json         # Cached 7 days
│   ├── projects.json               # Cached 7 days
│   ├── batches.json                # Cached 7 days
│   └── sell_orders.json            # Cached 1 day
├── tools/
│   └── ...                         # Tool-specific fixtures
└── integration/
    └── ...                         # Integration test fixtures
```

## Writing Tests

### Example: Client Test

```python
@pytest.mark.asyncio
@pytest.mark.client
@pytest.mark.offline
async def test_credit_types_structure(real_credit_types):
    """Test credit types with real data."""
    # real_credit_types is actual blockchain data
    assert "credit_types" in real_credit_types
    assert len(real_credit_types["credit_types"]) > 0

    # Validate against known real-world facts
    types = [ct["abbreviation"] for ct in real_credit_types["credit_types"]]
    assert "C" in types  # Carbon credits exist on Regen Network
```

### Example: Tool Test

```python
@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.offline
async def test_list_credit_types_tool():
    """Test list_credit_types tool."""
    from mcp_server.tools.credit_tools import list_credit_types

    result = await list_credit_types()

    assert isinstance(result, dict)
    assert len(result) > 0
```

### Example: Online Test

```python
@pytest.mark.asyncio
@pytest.mark.online  # Marked as requiring network
async def test_live_query():
    """Test against live network."""
    client = get_regen_client()
    result = await client.query_credit_types()

    assert len(result["credit_types"]) > 0
```

## Test Commands Reference

### Basic Commands

```bash
# Run all offline tests (fast, default)
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific file
pytest tests/client/test_regen_client.py

# Run specific test
pytest tests/client/test_regen_client.py::test_credit_types_structure
```

### Filter by Markers

```bash
# Only unit tests (fast)
pytest -m unit tests/

# Only tests that require network
pytest -m online --online tests/

# Client tests only
pytest -m client tests/

# Tools tests only
pytest -m tools tests/
```

### Coverage

```bash
# Basic coverage
pytest --cov=src tests/

# HTML coverage report
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# Coverage with missing lines
pytest --cov=src --cov-report=term-missing tests/
```

### Fixture Management

```bash
# Force refresh all fixtures
pytest --update-fixtures tests/

# Run online tests (captures fresh data)
pytest --online tests/

# See which fixtures are cached
ls -lh data/test_fixtures/client/
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests (offline)
        run: pytest tests/
      - name: Run online tests (weekly)
        if: github.event.schedule == 'weekly'
        run: pytest --online --update-fixtures tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Data Freshness

### TTL Guidelines

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Credit types | 30 days | Rarely change |
| Credit classes | 7 days | New classes added periodically |
| Projects | 7 days | New projects added |
| Batches | 7 days | New batches issued |
| Sell orders | 1 day | Market changes frequently |
| Health checks | 0 days | Always fresh |

### Updating Stale Data

```bash
# Update all fixtures older than 7 days
pytest --update-fixtures --max-age-days=7 tests/

# Force refresh specific fixture
pytest --online tests/client/test_regen_client.py::test_live_credit_types_query
```

## Troubleshooting

### Tests Fail After API Change

**Expected behavior!** This is good - it means tests caught a real change.

1. Review the API change
2. Update test expectations if change is intentional
3. Refresh fixtures: `pytest --update-fixtures tests/`
4. Verify tests pass with new data

### Network Timeout

```bash
# Use longer timeout
pytest --timeout=60 tests/

# Skip online tests
pytest -m "not online" tests/
```

### Fixture Not Found

```bash
# Clear cache and recapture
rm -rf data/test_fixtures/client/credit_types.json
pytest --online tests/client/test_regen_client.py
```

## Best Practices

### ✅ DO

- Use real blockchain data via fixtures
- Write tests that validate known real-world facts
- Mark online tests with `@pytest.mark.online`
- Use descriptive test names
- Add docstrings explaining what real behavior is tested
- Acknowledge when data may be out of date in comments

### ❌ DON'T

- Use mock data (violates CLAUDE.md principle)
- Assume specific numeric values (blockchain changes)
- Skip validation of response structure
- Write tests that always pass regardless of data
- Commit sensitive data to fixtures

## Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| Overall | TBD% | ≥85% |
| Client | TBD% | ≥90% |
| Tools | TBD% | 100% |
| Prompts | ~15% | 100% |
| Server | TBD% | ≥95% |

## Contributing

When adding tests:

1. Use `FixtureManager` for blockchain data
2. Add appropriate test markers
3. Write clear docstrings
4. Test both success and error cases
5. Validate against known real-world facts
6. Run full test suite before committing

## Resources

- **Testing Strategy:** `.claude/docs/testing_strategy.md`
- **CLAUDE.md:** Project principles including "no mock data"
- **pytest docs:** https://docs.pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/

---

**Remember:** These tests validate REAL MCP functionality against REAL blockchain data. When tests fail, it's usually because:
1. API changed (update fixtures)
2. Network issue (retry)
3. Real bug (fix it!)

All three outcomes are valuable!
