# Testing Quick Start Guide

**Getting Started with Real Data Testing - No Mocks!**

## First Time Setup (5 minutes)

### 1. Install Test Dependencies

```bash
cd /home/ygg/Workspace/sandbox/regen-python-mcp

# Install test packages
pip install pytest pytest-asyncio pytest-cov
```

### 2. Run Your First Test

```bash
# This will capture real data from Regen Network on first run
pytest --online tests/client/test_regen_client.py::TestRegenClientOnline::test_live_credit_types_query -v
```

**Expected Output:**
```
tests/client/test_regen_client.py::TestRegenClientOnline::test_live_credit_types_query
Capturing fresh data for: client/credit_types
Captured and saved: client/credit_types (2847 bytes)
PASSED [100%]

1 passed in 2.43s
```

### 3. Run Again (Now Cached - Fast!)

```bash
pytest tests/client/test_regen_client.py::TestRegenClientOnline::test_live_credit_types_query -v
```

**Expected Output:**
```
tests/client/test_regen_client.py::TestRegenClientOnline::test_live_credit_types_query
Using cached fixture: client/credit_types
PASSED [100%]

1 passed in 0.12s  ← Much faster!
```

## Understanding What Happened

1. **First Run:** Test connected to live Regen Network, captured real data
2. **Data Saved:** Real blockchain response saved to `data/test_fixtures/client/credit_types.json`
3. **Second Run:** Test used cached data (no network call needed)
4. **Result:** Same test, 20x faster, but still validates real data!

## Explore Captured Data

```bash
# See what was captured
cat data/test_fixtures/client/credit_types.json

# See metadata
cat data/test_fixtures/metadata.json
```

## Run More Tests

### Test the Client Layer

```bash
# Run all client tests (will capture more fixtures)
pytest --online tests/client/test_regen_client.py -v

# Now run offline (uses cached data)
pytest tests/client/test_regen_client.py -v
```

### Test Tool Layer

```bash
# Test credit tools
pytest tests/tools/test_credit_tools.py -v
```

### Run Everything

```bash
# All tests with coverage
pytest --cov=src --cov-report=term-missing tests/
```

## What's Tested?

### ✅ Already Implemented

1. **Client Tests** (`tests/client/test_regen_client.py`)
   - Credit types query structure
   - Credit types contains carbon
   - Credit classes structure
   - Credit classes contains real classes
   - Projects structure
   - Credit batches structure
   - Sell orders structure
   - Live health check
   - Pagination
   - Error handling

2. **Tool Tests** (`tests/tools/test_credit_tools.py`)
   - list_credit_types tool
   - list_credit_classes tool with pagination
   - list_projects tool
   - list_credit_batches tool
   - Edge cases (large limits, zero offset, empty results)

3. **Infrastructure**
   - FixtureManager for data capture
   - pytest configuration
   - Test markers (online/offline, unit/integration/e2e)
   - Fixtures for common data (credit_types, classes, projects, batches)

### ❌ Still To Implement

Following the roadmap in `.claude/docs/testing_strategy.md`:

1. **More Tool Tests:**
   - test_basket_tools.py (5 tools)
   - test_marketplace_tools.py (5 tools)
   - test_bank_tools.py (11 tools)
   - test_distribution_tools.py (9 tools)
   - test_governance_tools.py (8 tools)
   - test_analytics_tools.py (3 tools)

2. **Integration Tests:**
   - Server initialization
   - Tool registration
   - MCP protocol compliance

3. **E2E Tests:**
   - Complete user workflows
   - Claude Code interaction scenarios

## Test Development Workflow

### Adding a New Test

1. **Create test file:**
   ```bash
   touch tests/tools/test_basket_tools.py
   ```

2. **Write test using fixtures:**
   ```python
   @pytest.mark.asyncio
   @pytest.mark.tools
   @pytest.mark.offline
   async def test_list_baskets(real_baskets):
       """Test list_baskets tool with real data."""
       from mcp_server.tools.basket_tools import list_baskets

       result = await list_baskets()

       assert isinstance(result, dict)
       assert len(result) > 0
   ```

3. **Add fixture in conftest.py if needed:**
   ```python
   @pytest.fixture
   async def real_baskets(fixture_manager):
       """Fixture for real basket data."""
       async def capture():
           client = get_regen_client()
           return await client.query_baskets()

       return await fixture_manager.get_or_capture(
           "baskets", capture, ttl_days=7, category="client"
       )
   ```

4. **Run test to capture data:**
   ```bash
   pytest --online tests/tools/test_basket_tools.py -v
   ```

5. **Subsequent runs use cached data:**
   ```bash
   pytest tests/tools/test_basket_tools.py -v
   ```

## Common Commands

```bash
# Fast iteration (offline, cached)
pytest tests/

# Update all stale fixtures
pytest --online --update-fixtures tests/

# Run specific test
pytest tests/client/test_regen_client.py::test_credit_types_structure -v

# Only unit tests (fast)
pytest -m unit tests/

# Everything with coverage
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# Verbose with print statements
pytest -v -s tests/client/
```

## Fixture Management

```bash
# See what's cached
ls -lh data/test_fixtures/client/

# Check fixture age
pytest --collect-only tests/  # Shows which fixtures will be used

# Invalidate single fixture
rm data/test_fixtures/client/credit_types.json

# Invalidate all fixtures
rm -rf data/test_fixtures/*

# Fresh capture
pytest --online tests/
```

## Debugging Tests

```bash
# Run with full output
pytest -v -s tests/client/test_regen_client.py

# Drop into debugger on failure
pytest --pdb tests/

# Only failed tests
pytest --lf tests/

# Stop on first failure
pytest -x tests/
```

## Next Steps

1. **Complete Tool Tests**
   - Follow the template in `tests/tools/test_credit_tools.py`
   - Test all 45 tools across 7 modules
   - Target: 100% tool coverage

2. **Add Integration Tests**
   - Server startup
   - MCP protocol compliance
   - Multi-tool workflows

3. **Add E2E Tests**
   - User journey scenarios
   - Claude Code interaction

4. **Setup CI/CD**
   - GitHub Actions workflow
   - Automated fixture updates
   - Coverage tracking

## Resources

- **Full Strategy:** `.claude/docs/testing_strategy.md`
- **Test README:** `tests/README.md`
- **CLAUDE.md:** Project principles (no mock data)
- **pytest docs:** https://docs.pytest.org/

---

**Remember:** All tests use REAL data from Regen Network. When tests fail, they're telling you about real API changes or bugs - that's valuable!

---

## Quick Reference Card

| Task | Command |
|------|---------|
| First run (capture data) | `pytest --online tests/` |
| Fast run (cached data) | `pytest tests/` |
| Update fixtures | `pytest --online --update-fixtures tests/` |
| Run specific test | `pytest tests/path/to/test.py::test_name -v` |
| With coverage | `pytest --cov=src --cov-report=html tests/` |
| Only online tests | `pytest -m online --online tests/` |
| Only offline tests | `pytest -m offline tests/` |
| Debug mode | `pytest --pdb tests/` |
| Stop on first fail | `pytest -x tests/` |
| Verbose output | `pytest -v -s tests/` |

**Status:** Infrastructure complete ✅ | Tool tests in progress 🚧 | Target: 85% coverage
