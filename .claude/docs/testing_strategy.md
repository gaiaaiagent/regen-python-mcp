# Comprehensive Testing Strategy for Regen Python MCP

**Status:** Implementation Required
**Created:** 2025-10-17
**Principle:** No Mock Data - Real Blockchain Data Only

---

## Executive Summary

This document outlines a comprehensive testing strategy for the Regen Network MCP server that ensures **actual behavioral correctness** when the MCP is used in production. We follow the principle of **no mock/fake data** - all tests use real Regen Network blockchain data, captured and versioned for reproducibility.

### Current State

✅ **What Exists:**
- `/tests/test_prompts.py` - Tests for 8 prompts (content validation only)
- `/tests/test_prompts_integration.py` - Basic prompt integration test
- **Coverage:** ~15% (prompts only, no tool tests)

❌ **What's Missing:**
- Tests for 45 blockchain tools
- Real blockchain data fixtures
- Integration tests with MCP protocol
- End-to-end Claude Code interaction tests
- Client-level tests
- Error handling and edge case tests

---

## Testing Philosophy

### Principle: Real Data, Real Behavior

**Why No Mocks:**
1. **Mocks lie** - They test what we think the API returns, not what it actually returns
2. **Schema drift** - Real Regen Network API may change, mocks won't catch this
3. **Edge cases** - Real data contains edge cases mocks might miss
4. **Confidence** - Tests with real data prove actual functionality

**Approach:**
1. **Capture** real data from Regen Network on first run
2. **Version** captured data in repository (`data/test_fixtures/`)
3. **Reuse** captured data for fast, repeatable tests
4. **Update** captured data periodically to catch API changes

### Test Pyramid Structure

```
       /\          E2E Tests (10%)
      /  \         - Full MCP protocol with Claude Code
     /    \        - Real network interaction
    /------\       Integration Tests (30%)
   /        \      - Tool → Client → Network
  /          \     - Multi-component workflows
 /------------\    Unit Tests (60%)
/              \   - Individual functions
\______________/   - Data validation
```

---

## Test Categories & Coverage Goals

### 1. Client Tests (`tests/test_client.py`)

**Purpose:** Verify RegenClient correctly interacts with blockchain

**Coverage:**
- ✓ Connection handling & endpoint fallback
- ✓ All query methods (baskets, credits, marketplace, etc.)
- ✓ Pagination handling
- ✓ Error handling & retries
- ✓ Health checks

**Test Data Strategy:**
- Capture real responses from `/regen/ecocredit/v1/credit-types`
- Capture real responses from `/regen/ecocredit/v1/classes`
- Store in `data/test_fixtures/client/`

**Example:**
```python
@pytest.mark.asyncio
async def test_query_credit_types_real_data():
    """Test credit types query with real Regen Network data."""
    client = RegenClient()

    # First run: captures data
    # Subsequent runs: uses captured data
    result = await client.query_credit_types()

    # Validate real structure
    assert "credit_types" in result
    assert isinstance(result["credit_types"], list)
    assert len(result["credit_types"]) > 0

    # Validate real data content
    credit_type = result["credit_types"][0]
    assert "name" in credit_type
    assert credit_type["name"] in ["carbon", "biodiversity", "C"]
```

**Target Coverage:** 90%

---

### 2. Tool Tests (`tests/tools/`)

**Purpose:** Verify each of 45 tools produces correct output

**Structure:**
```
tests/tools/
├── test_bank_tools.py       # 11 bank module tools
├── test_distribution_tools.py  # 9 distribution tools
├── test_governance_tools.py    # 8 governance tools
├── test_marketplace_tools.py   # 5 marketplace tools
├── test_credit_tools.py        # 4 credit tools
├── test_basket_tools.py        # 5 basket tools
├── test_analytics_tools.py     # 3 analytics tools
└── fixtures/
    ├── bank_responses.json
    ├── distribution_responses.json
    ├── governance_responses.json
    ├── marketplace_responses.json
    ├── credit_responses.json
    ├── basket_responses.json
    └── analytics_responses.json
```

**Test Template for Each Tool:**
```python
@pytest.mark.asyncio
async def test_list_credit_types_tool():
    """Test list_credit_types tool with real data."""

    # Call the actual tool
    result = await list_credit_types()

    # Validate response structure (MCP format)
    assert isinstance(result, dict)
    assert "credit_types" in result or "data" in result

    # Validate data content (real blockchain data)
    # This will fail if API changes - GOOD!
    assert len(result["credit_types"]) >= 5  # Known min count

    # Validate specific known credit types exist
    type_names = [ct["name"] for ct in result["credit_types"]]
    assert "C" in type_names  # Carbon credits exist
```

**Data Capture Process:**
1. Run tests against live network (first time)
2. Tests automatically save responses to `fixtures/`
3. Mark data with capture timestamp and version
4. Future runs use cached data (fast)
5. Optional `--update-fixtures` flag to refresh

**Target Coverage:** 100% (all 45 tools)

---

### 3. Prompt Tests (`tests/test_prompts.py`)

**Status:** Already exists but needs enhancement

**Current Coverage:**
- ✓ Prompt content validation
- ✓ Parameter handling
- ✓ Markdown formatting

**Additional Tests Needed:**
- ❌ Prompt output actually helps user understand concepts
- ❌ Code examples in prompts are executable
- ❌ Prompts reference real credit classes that exist

**Enhancement:**
```python
@pytest.mark.asyncio
async def test_ecocredit_workshop_references_real_classes():
    """Verify prompt references real credit classes from blockchain."""

    # Get real credit classes
    client = RegenClient()
    classes_response = await client.query_credit_classes()
    real_class_ids = [c["id"] for c in classes_response["classes"]]

    # Get prompt content
    prompt_content = await ecocredit_query_workshop()

    # Verify prompt references at least some real classes
    referenced_classes = re.findall(r'C\d{2}', prompt_content)
    assert any(rc in real_class_ids for rc in referenced_classes), \
        f"Prompt references non-existent classes: {referenced_classes}"
```

**Target Coverage:** 100% (all 8 prompts)

---

### 4. Server Integration Tests (`tests/test_server_integration.py`)

**Purpose:** Verify complete server startup and MCP protocol compliance

**Tests:**
- ✓ Server initialization
- ✓ All 45 tools registered
- ✓ All 8 prompts registered
- ✓ Tool execution through MCP
- ✓ Prompt execution through MCP
- ✓ Error handling at server level

**Example:**
```python
@pytest.mark.asyncio
async def test_server_registers_all_tools():
    """Verify server registers all expected tools."""
    from mcp_server.server import create_modular_regen_mcp_server

    server = create_modular_regen_mcp_server()

    # Count registered tools
    # This will vary based on FastMCP introspection API
    tool_count = len(server.list_tools())

    assert tool_count == 45, f"Expected 45 tools, got {tool_count}"

@pytest.mark.asyncio
async def test_tool_execution_through_mcp():
    """Test calling a tool through MCP protocol."""
    server = create_modular_regen_mcp_server()

    # Simulate MCP tool call
    result = await server.call_tool("list_credit_types", {})

    # Validate MCP response format
    assert "content" in result or "result" in result
```

**Target Coverage:** 95%

---

### 5. MCP Protocol Compliance Tests (`tests/test_mcp_compliance.py`)

**Purpose:** Ensure strict adherence to MCP specification

**Tests:**
- ✓ Tool schema validation
- ✓ Prompt schema validation
- ✓ Response format compliance
- ✓ Error format compliance
- ✓ JSON-RPC 2.0 compliance

**Example:**
```python
def test_tool_schemas_valid():
    """Verify all tool schemas match MCP specification."""
    server = create_modular_regen_mcp_server()

    for tool in server.list_tools():
        # Validate schema structure
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

        # Validate JSON Schema compliance
        jsonschema.validate(
            instance=tool["inputSchema"],
            schema=MCP_TOOL_SCHEMA
        )
```

**Target Coverage:** 100%

---

### 6. End-to-End Tests (`tests/test_e2e.py`)

**Purpose:** Test complete user workflows as they would occur in Claude Code

**Scenarios:**

#### Scenario 1: Query Credit Types
```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_e2e_query_credit_types():
    """E2E: User asks Claude to list credit types."""

    # 1. Start server
    server = create_modular_regen_mcp_server()

    # 2. Simulate MCP client connection
    async with MCPClient(server) as client:

        # 3. User prompt: "List credit types on Regen Network"
        tools = await client.list_tools()
        tool = next(t for t in tools if t["name"] == "list_credit_types")

        # 4. Claude calls tool
        result = await client.call_tool("list_credit_types", {})

        # 5. Validate user-visible result
        assert "credit_types" in result
        assert len(result["credit_types"]) > 0

        # 6. Validate response is human-readable
        credit_type = result["credit_types"][0]
        assert "name" in credit_type
        assert "abbreviation" in credit_type
```

#### Scenario 2: Marketplace Analysis
```python
@pytest.mark.e2e
async def test_e2e_marketplace_analysis():
    """E2E: User analyzes marketplace sell orders."""

    server = create_modular_regen_mcp_server()

    async with MCPClient(server) as client:
        # User: "Show me sell orders for credit batch X"
        result = await client.call_tool(
            "list_sell_orders_by_batch",
            {"batch_denom": "C01-001-20220101-20221231-001"}
        )

        # Validate meaningful data for user
        assert "sell_orders" in result
        if len(result["sell_orders"]) > 0:
            order = result["sell_orders"][0]
            assert "quantity" in order
            assert "ask_price" in order
```

**Target Coverage:** Key user journeys (10-15 scenarios)

---

## Real Data Capture Infrastructure

### Fixture Manager (`tests/fixtures/fixture_manager.py`)

```python
class FixtureManager:
    """Manages real blockchain data fixtures with versioning."""

    def __init__(self, fixtures_dir: Path):
        self.fixtures_dir = fixtures_dir
        self.metadata_file = fixtures_dir / "metadata.json"

    async def get_or_capture(
        self,
        fixture_name: str,
        capture_func: Callable,
        ttl_days: int = 30
    ) -> Any:
        """Get cached fixture or capture fresh data."""

        fixture_path = self.fixtures_dir / f"{fixture_name}.json"

        # Check if cached data exists and is fresh
        if fixture_path.exists():
            metadata = self._load_metadata()
            capture_time = metadata.get(fixture_name, {}).get("captured_at")

            if capture_time and self._is_fresh(capture_time, ttl_days):
                # Use cached data
                with open(fixture_path) as f:
                    return json.load(f)

        # Capture fresh data
        print(f"Capturing fresh data for: {fixture_name}")
        data = await capture_func()

        # Save fixture
        with open(fixture_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Update metadata
        self._update_metadata(fixture_name, {
            "captured_at": datetime.now().isoformat(),
            "source": "real_blockchain",
            "network": "regen-1"
        })

        return data
```

### Fixture Organization

```
data/test_fixtures/
├── metadata.json              # Capture timestamps, versions
├── client/
│   ├── credit_types.json      # /credit-types response
│   ├── credit_classes.json    # /classes response
│   ├── projects.json          # /projects response
│   ├── batches.json           # /batches response
│   └── sell_orders.json       # /sell-orders response
├── tools/
│   ├── bank_responses.json
│   ├── distribution_responses.json
│   ├── governance_responses.json
│   └── ...
└── integration/
    ├── full_workflow_1.json
    └── full_workflow_2.json
```

### Usage in Tests

```python
@pytest.fixture
async def real_credit_types(fixture_manager):
    """Fixture providing real credit types data."""
    return await fixture_manager.get_or_capture(
        "credit_types",
        lambda: RegenClient().query_credit_types(),
        ttl_days=7
    )

@pytest.mark.asyncio
async def test_with_real_data(real_credit_types):
    """Test using real captured data."""
    assert len(real_credit_types["credit_types"]) > 0
```

---

## Test Execution Strategy

### Test Marks

```python
# Speed-based marks
@pytest.mark.unit          # Fast, no network (uses fixtures)
@pytest.mark.integration   # Medium, may use network
@pytest.mark.e2e          # Slow, full workflow
@pytest.mark.slow         # Any slow test

# Network-based marks
@pytest.mark.online       # Requires network connection
@pytest.mark.offline      # Can run without network (uses fixtures)

# Coverage-based marks
@pytest.mark.client       # Tests client layer
@pytest.mark.tools        # Tests tools layer
@pytest.mark.server       # Tests server layer
@pytest.mark.mcp         # Tests MCP protocol
```

### Test Commands

```bash
# Fast: Unit tests only (offline, uses fixtures)
pytest -m "unit and offline" tests/

# Medium: Add integration tests
pytest -m "not e2e" tests/

# Full: Everything including E2E
pytest tests/

# Update fixtures from live network
pytest --update-fixtures tests/

# Coverage report
pytest --cov=src --cov-report=html tests/

# Specific module
pytest tests/tools/test_credit_tools.py -v
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

1. ✅ **Create test directory structure**
   ```bash
   mkdir -p tests/{tools,client,integration,e2e,fixtures}
   mkdir -p data/test_fixtures/{client,tools,integration}
   ```

2. ✅ **Implement FixtureManager**
   - Create `tests/fixtures/fixture_manager.py`
   - Handle data capture, caching, versioning
   - Add metadata tracking

3. ✅ **Setup pytest configuration**
   - Add test marks
   - Configure fixtures
   - Setup coverage

### Phase 2: Client Tests (Week 1-2)

4. ✅ **Test all client query methods**
   - Start with `/credit-types`
   - Capture real responses
   - Test pagination
   - Test error handling

### Phase 3: Tool Tests (Week 2-3)

5. ✅ **Test credit tools** (4 tools)
6. ✅ **Test basket tools** (5 tools)
7. ✅ **Test marketplace tools** (5 tools)
8. ✅ **Test bank tools** (11 tools)
9. ✅ **Test distribution tools** (9 tools)
10. ✅ **Test governance tools** (8 tools)
11. ✅ **Test analytics tools** (3 tools)

### Phase 4: Integration & E2E (Week 3-4)

12. ✅ **Server integration tests**
13. ✅ **MCP protocol compliance**
14. ✅ **End-to-end scenarios**

### Phase 5: CI/CD (Week 4)

15. ✅ **GitHub Actions workflow**
16. ✅ **Coverage reporting**
17. ✅ **Automated fixture updates**

---

## Success Criteria

### Coverage Metrics

- **Overall Coverage:** ≥ 85%
- **Client Coverage:** ≥ 90%
- **Tools Coverage:** 100% (all 45 tools)
- **Prompts Coverage:** 100% (all 8 prompts)
- **Server Coverage:** ≥ 95%

### Quality Metrics

- **All tests use real data** (no mocks except for errors)
- **Tests fail when API changes** (proves they're meaningful)
- **E2E scenarios cover** ≥80% of expected user journeys
- **Test suite runs** <5 minutes (offline mode)
- **Documentation:** Every test has clear docstring

### Behavioral Validation

- ✅ Server starts successfully
- ✅ All tools callable via MCP
- ✅ Real blockchain data fetched correctly
- ✅ Error handling works as expected
- ✅ Pagination works across all tools
- ✅ Claude Code can connect and use tools

---

## Data Staleness Handling

### Problem
Real blockchain data changes over time. How do we handle this?

### Solution: Version + TTL Strategy

```python
# metadata.json
{
  "credit_types": {
    "captured_at": "2025-10-17T10:30:00Z",
    "ttl_days": 7,
    "network": "regen-1",
    "api_version": "v1",
    "checksum": "abc123...",
    "notes": "Captured during stable period"
  }
}
```

**TTL Guidelines:**
- Static data (credit types): 30 days
- Slowly changing (classes, projects): 7 days
- Frequently changing (sell orders, balances): 1 day
- Always fresh (health checks): 0 days (always capture)

**Update Process:**
```bash
# Weekly automated job
pytest --update-fixtures --max-age-days=7 tests/

# Manual refresh
pytest --force-refresh tests/
```

---

## Handling Test Failures

### Expected Failures (GOOD)

1. **API Schema Changes**
   - Fixture doesn't match current API
   - **Action:** Update fixture, validate change intentional

2. **New Credit Classes Added**
   - Test expects 11 classes, now 12 exist
   - **Action:** Update test, capture new data

3. **Endpoint Down**
   - Health check fails
   - **Action:** Switch to backup endpoint, report issue

### Unexpected Failures (BAD)

1. **Logic Errors**
   - Tool returns wrong data format
   - **Action:** Fix tool implementation

2. **Missing Error Handling**
   - Uncaught exception in edge case
   - **Action:** Add error handling, add test

---

## Maintenance

### Weekly
- Review fixture freshness
- Update stale fixtures (>7 days)
- Check for API changes

### Monthly
- Full fixture refresh
- Review coverage metrics
- Update test scenarios

### Quarterly
- Major fixture overhaul
- Performance optimization
- Documentation updates

---

## Tools & Dependencies

```toml
# pyproject.toml [project.optional-dependencies.test]
test = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",  # Only for network errors
    "httpx>=0.24.0",
    "jsonschema>=4.19.0",
]
```

---

## Conclusion

This testing strategy ensures:

1. **Real Behavior:** Tests validate actual MCP functionality
2. **Confidence:** Real blockchain data proves correctness
3. **Maintainability:** Fixtures version and track data sources
4. **Speed:** Cached fixtures enable fast iteration
5. **Reliability:** Comprehensive coverage catches regressions

**Next Steps:**
1. Review and approve this strategy
2. Implement FixtureManager
3. Start with Phase 1 (Foundation)
4. Iterate through phases 2-5

---

**Questions for Discussion:**
1. Is 7-day TTL reasonable for most data?
2. Should we test against testnet in addition to mainnet?
3. How should we handle breaking API changes?
4. Should we include performance benchmarks in tests?
