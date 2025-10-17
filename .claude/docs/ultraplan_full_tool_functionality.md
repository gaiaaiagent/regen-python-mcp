# ULTRAPLAN: Achieving Full Functionality for All 44 Regen Network MCP Tools

**Date:** 2025-10-17
**Current Status:** 24/44 tools working (55%)
**Target:** 100% functionality where technically possible

---

## Executive Summary

After comprehensive testing and deep codebase analysis, I've identified the root causes of all 20 failed tools. The issues fall into three categories:

1. **Code-Level Bugs (CAN FIX):** 3-6 tools - Pagination validation errors and potential analytics bugs
2. **Server-Side Limitations (CANNOT FIX):** 14 tools - HTTP 501/500 errors from missing/broken endpoints
3. **Unknown/Investigation Needed (MIGHT FIX):** 0-3 tools - Analytics tools need deeper investigation

**Key Insight:** We can likely restore 3-9 additional tools through code fixes, bringing us to **27-33/44 (61-75%)** working. The remaining 11-17 tools require server-side changes outside our control.

---

## Part 1: Project Understanding

### Vision & Intent
From @docs/regen_mcp_thesis.md:

> "Unlocking Ecological Intelligence: The Regen Network MCP Server as a Gateway to Autonomous Environmental Markets"

**Core Purpose:**
- Enable AI agents to interact directly with environmental markets
- Provide structured programmatic access to Regen Network's ecological credit system
- Bridge gap between on-ground ecological work and global markets
- Support 12 distinct credit classes across 5 credit types (Carbon, Biodiversity, KSH, MBS, USS)

**Strategic Value:**
- **56 active projects** spanning jurisdictions from CD-MN to US states
- **74 credit batches** with vintages from 2012-2034
- **26 active sell orders** in marketplace
- **216.3T uregen** total supply with **22,908 accounts**
- **3.46T uregen** community pool for governance

### Best Parts of Repository

1. **Solid Foundation:**
   - Well-structured client layer with retry logic and endpoint fallback (regen_client.py:63-1328)
   - Comprehensive Pydantic models for type safety (models/)
   - Proper error handling and logging throughout
   - Good test coverage structure (tests/)

2. **Working Functionality:**
   - Governance module (75% working) - Proposal tracking, voting, tallies
   - Ecocredits module (67% working) - Credit types, classes, projects, batches
   - Bank module (64% working) - Account queries, supply info, token metadata

3. **Advanced Features:**
   - Sophisticated analytics tools for portfolio impact analysis (analytics_tools.py)
   - 10 interactive prompts for guided workflows (prompts/)
   - Caching system for performance optimization (cache/)
   - Health monitoring and metrics (monitoring/)

4. **Documentation:**
   - Clear docstrings throughout
   - Comprehensive test results documentation
   - Well-articulated project thesis

### Worst Aspects of Repository

1. **Critical Bugs:**
   - Pagination model rejects `None` for optional boolean fields (regen_client.py:42-43)
   - Potential analytics tool registration/invocation issues
   - Inconsistent error handling in some tools

2. **Incomplete Testing:**
   - No integration tests for failed endpoints
   - Missing validation of API responses against actual server behavior
   - Analytics tools not properly tested with real data

3. **Server Dependency Gaps:**
   - 14 tools depend on non-existent or broken server endpoints
   - No fallback strategies for missing endpoints
   - No documentation of endpoint availability

4. **Architecture Issues:**
   - Tight coupling between tools and specific API endpoints
   - No abstraction layer for server-side limitations
   - Limited error recovery strategies

### Structural Patterns

```
Project Structure:
├── src/mcp_server/                    # Core MCP server implementation
│   ├── client/regen_client.py         # Blockchain API client (1328 lines)
│   ├── models/                        # Pydantic data models
│   │   ├── bank.py                    # Bank module models + pagination bug
│   │   ├── credit.py                  # Credit models
│   │   ├── marketplace.py             # Marketplace models
│   │   └── analytics.py               # Analytics response models
│   ├── tools/                         # MCP tool implementations
│   │   ├── bank_tools.py              # 456 lines, 11 tools, 7 working
│   │   ├── distribution_tools.py      # 9 tools, 5 working
│   │   ├── governance_tools.py        # 8 tools, 6 working
│   │   ├── marketplace_tools.py       # 5 tools, 2 working
│   │   ├── credit_tools.py            # 6 tools, 4 working
│   │   ├── basket_tools.py            # 5 tools, 0 working
│   │   └── analytics_tools.py         # 918 lines, 3 tools, 0 working
│   ├── prompts/                       # 10 interactive guided workflows
│   ├── resources/                     # Dynamic MCP resources
│   ├── cache/                         # Performance caching layer
│   └── server.py                      # FastMCP server registration
├── tests/                             # Test suite
│   ├── tools/                         # Tool-specific tests
│   └── e2e/                           # End-to-end user journey tests
└── docs/                              # Documentation
```

**Key Pattern:** Layered architecture with clear separation:
1. Client layer (API interaction)
2. Model layer (data validation)
3. Tool layer (MCP interface)
4. Server layer (MCP registration)

---

## Part 2: Root Cause Analysis (All 20 Failed Tools)

### Category A: Code-Level Bugs (CAN FIX - 3-6 tools)

#### Issue #1: Pagination Boolean Validation Error (3 tools)
**Location:** `src/mcp_server/client/regen_client.py:37-44`

**Root Cause:**
```python
class Pagination(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    count_total: bool = Field(default=True)  # ❌ Should be Optional[bool]
    reverse: bool = Field(default=False)     # ❌ Should be Optional[bool]
```

**Problem:** When bank_tools.py (lines 100-102, 158-163, 213-218) creates Pagination objects with `count_total=None` and `reverse=None`, Pydantic validation fails because `bool` type doesn't accept `None`.

**Affected Tools:**
1. `get_all_balances` - src/mcp_server/tools/bank_tools.py:58-116
2. `get_spendable_balances` - src/mcp_server/tools/bank_tools.py:119-177
3. `get_total_supply` - src/mcp_server/tools/bank_tools.py:180-232

**Evidence from Test:**
```
"error": "Validation error: 2 validation errors for Pagination\ncount_total\n  Input should be a valid boolean..."
```

**Fix Difficulty:** EASY - Single line change per field
**Impact:** Restores 3 tools immediately

---

#### Issue #2: Advanced Analytics Parameter Bugs (0-3 tools)
**Location:** `src/mcp_server/tools/analytics_tools.py` (multiple functions)

**Root Cause:** UNCLEAR - Test errors suggest parameter mismatch but code analysis shows correct usage

**Test Error Messages:**
```
"message": "RegenClient.query_all_balances() got an unexpected keyword argument 'limit'"
"message": "RegenClient.query_sell_orders() got an unexpected keyword argument 'limit'"
"message": "RegenClient.query_credit_classes() got an unexpected keyword argument 'limit'"
```

**Code Analysis:** Lines 49-52, 378-381, 601-604 show correct Pagination object creation and usage

**Affected Tools:**
1. `analyze_portfolio_impact` - analytics_tools.py:17-351
2. `analyze_market_trends` - analytics_tools.py:354-577
3. `compare_credit_methodologies` - analytics_tools.py:580-866

**Hypotheses:**
1. **Stale code hypothesis:** Old version of client methods cached somewhere
2. **Registration issue:** Analytics tool registration has parameter mapping problem
3. **Misleading error:** Actual error is different, message is confusing
4. **Test artifact:** Error only occurs in specific test conditions

**Investigation Needed:**
- Run analytics tools directly outside of test harness
- Check for multiple Regen client instances
- Verify MCP tool parameter passing
- Review analytics_tool_registration.py:20-112 execution

**Fix Difficulty:** MEDIUM - Requires debugging
**Impact:** Could restore 0-3 tools (30-50% chance of success)

---

### Category B: Server-Side Limitations (CANNOT FIX - 14 tools)

#### Issue #3: Baskets Module - Complete Endpoint Failure (5 tools)
**HTTP Error:** 501 Not Implemented

**Endpoints Missing:**
- `/regen/ecocredit/v1/baskets` (list)
- `/regen/ecocredit/v1/basket/{denom}` (get)
- `/regen/ecocredit/v1/basket/{denom}/balances` (list balances)
- `/regen/ecocredit/v1/basket/{denom}/balance/{batch}` (get balance)
- `/regen/ecocredit/v1/basket-fee` (get fee)

**Affected Tools:**
1. `list_baskets` - basket_tools.py:21-52
2. `get_basket` - basket_tools.py:55-81
3. `list_basket_balances` - basket_tools.py:84-119
4. `get_basket_balance` - basket_tools.py:122-158
5. `get_basket_fee` - basket_tools.py:179-204 (also in credit_tools if duplicated)

**Evidence:** All 5 Regen Network REST endpoints tested return HTTP 501

**Server Status:** Basket functionality not implemented in current Regen Network version

**Workaround Potential:** NONE - Fundamental feature missing

---

#### Issue #4: Validator Distribution Queries (4 tools)
**HTTP Errors:** 500 Internal Server Error, 400 Bad Request

**Endpoints Failing:**
- `/cosmos/distribution/v1beta1/validators/{address}/outstanding_rewards` (500)
- `/cosmos/distribution/v1beta1/validators/{address}/commission` (500)
- `/cosmos/distribution/v1beta1/validators/{address}/slashes` (400)
- `/cosmos/distribution/v1beta1/delegators/{delegator}/rewards/{validator}` (500)

**Affected Tools:**
1. `get_validator_outstanding_rewards` - distribution_tools.py
2. `get_validator_commission` - distribution_tools.py
3. `get_validator_slashes` - distribution_tools.py
4. `get_delegation_rewards` - distribution_tools.py

**Root Cause Hypotheses:**
1. Validator address format incorrect (tested `regenvaloper1...` format - should be correct)
2. Validator not active/registered
3. Server-side query optimization disabled
4. Module version mismatch

**Fix Difficulty:** HARD - Requires server-side investigation or validator address validation

**Workaround:** Validate validator addresses before querying, provide better error messages

---

#### Issue #5: Marketplace Filtered Queries (3 tools)
**HTTP Error:** 501 Not Implemented

**Endpoints Missing:**
- `/regen/ecocredit/marketplace/v1/sell-orders-by-batch` (501)
- `/regen/ecocredit/marketplace/v1/sell-orders-by-seller` (501)
- `/regen/ecocredit/marketplace/v1/allowed-denoms` (500)

**Affected Tools:**
1. `list_sell_orders_by_batch` - marketplace_tools.py
2. `list_sell_orders_by_seller` - marketplace_tools.py
3. `list_allowed_denoms` - marketplace_tools.py

**Server Status:** Filtered marketplace queries not implemented

**Workaround:** Use `list_sell_orders` and filter client-side (already works, 26 orders found)

---

#### Issue #6: Single Balance Query (1 tool)
**HTTP Error:** 501 Not Implemented

**Endpoint Missing:**
- `/cosmos/bank/v1beta1/balances/{address}/{denom}` (501)

**Affected Tool:**
1. `get_balance` - bank_tools.py:24-55

**Workaround:** Use `get_all_balances` and filter, or use `get_denom_owners` to find balance

---

#### Issue #7: List Allowed Denoms (1 tool - duplicate from #5)
Already counted in Issue #5

---

### Summary of Fixable Tools

| Issue | Tools | Difficulty | Success Probability | Time Estimate |
|-------|-------|------------|---------------------|---------------|
| Pagination Bug | 3 | EASY | 100% | 15 minutes |
| Analytics Bugs | 3 | MEDIUM | 30-50% | 2-4 hours |
| **Total Fixable** | **6** | **MIXED** | **75-88%** | **2.5-4.5 hours** |

**Best Case:** Restore 6 tools → 30/44 working (68%)
**Likely Case:** Restore 3-4 tools → 27-28/44 working (61-64%)
**Worst Case:** Restore 3 tools → 27/44 working (61%)

---

## Part 3: Comprehensive Fix Strategy

### Phase 1: Quick Wins (15 minutes - Guaranteed Success)

#### Fix #1: Pagination Boolean Fields

**File:** `src/mcp_server/client/regen_client.py`
**Lines:** 42-43

**Change:**
```python
# BEFORE
class Pagination(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    count_total: bool = Field(default=True, description="Whether to return total count")
    reverse: bool = Field(default=False, description="Whether to reverse the order")

# AFTER
class Pagination(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    count_total: Optional[bool] = Field(default=True, description="Whether to return total count")
    reverse: Optional[bool] = Field(default=False, description="Whether to reverse the order")
```

**Import Required:**
```python
from typing import Any, Dict, List, Optional, Union  # Add Optional if not present
```

**Tests to Run:**
```bash
pytest tests/tools/test_bank_tools.py::test_get_all_balances -v
pytest tests/tools/test_bank_tools.py::test_get_spendable_balances -v
pytest tests/tools/test_bank_tools.py::test_get_total_supply -v
```

**Expected Outcome:** 3 tools restored immediately

---

### Phase 2: Analytics Investigation & Fix (2-4 hours - 30-50% Success)

#### Step 1: Reproduce Analytics Errors

**Test Script:**
```python
# Create: test_analytics_direct.py
import asyncio
from src.mcp_server.tools.analytics_tools import (
    analyze_portfolio_impact,
    analyze_market_trends,
    compare_credit_methodologies
)

async def test_portfolio_impact():
    result = await analyze_portfolio_impact("regen1qqy8su5mf4tlm9h36fgf2p43gdtnu4ka8gmjmg", "full")
    print("Portfolio Impact Result:", result)

async def test_market_trends():
    result = await analyze_market_trends("30d", None)
    print("Market Trends Result:", result)

async def test_methodology_comparison():
    result = await compare_credit_methodologies(["C01", "C02"])
    print("Methodology Comparison Result:", result)

async def main():
    await test_portfolio_impact()
    await test_market_trends()
    await test_methodology_comparison()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:**
```bash
cd /home/ygg/Workspace/sandbox/regen-python-mcp
python test_analytics_direct.py
```

**Analyze:**
- If errors reproduce: Fix the actual bug
- If no errors: Issue is in MCP tool registration or parameter passing
- If different error: Update understanding and fix accordingly

#### Step 2: Potential Fixes (Based on Investigation)

**Hypothesis A: Client Method Signature Issue**

Check if old client instance cached:
```python
# Add to analytics_tools.py top
from ..client.regen_client import close_regen_client

# Before first use in each function
await close_regen_client()  # Force fresh client
client = get_regen_client()
```

**Hypothesis B: MCP Tool Registration Issue**

Verify parameter passing in server.py:
```python
# Check server registration matches tool signatures exactly
```

**Hypothesis C: Pagination Object Issue**

Add explicit type validation:
```python
# In analytics_tools.py before client calls
if not isinstance(pagination, Pagination):
    pagination = Pagination(limit=pagination.get('limit', 1000), offset=pagination.get('offset', 0))
```

#### Step 3: Incremental Testing

Test each fix:
```bash
pytest tests/tools/test_analytics_tools.py -v -s
```

Document results:
- What was the actual bug?
- Which hypothesis was correct?
- Any side effects?

---

### Phase 3: Server-Side Workarounds & Documentation (30 minutes)

#### Workaround #1: Marketplace Filtering

**File:** `src/mcp_server/tools/marketplace_tools.py`

**Add client-side filtering helper:**
```python
async def list_sell_orders_by_batch_clientside(
    batch_denom: str,
    limit: int = 100,
    page: int = 1
) -> Dict[str, Any]:
    """List sell orders for batch (client-side filtering fallback).

    Since server endpoint not implemented, fetches all orders and filters.
    """
    try:
        # Get all orders
        all_orders = await list_sell_orders(limit=1000, page=1)

        # Filter by batch
        filtered_orders = [
            order for order in all_orders.get("sell_orders", [])
            if order.get("batch_denom") == batch_denom
        ]

        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = filtered_orders[start:end]

        return {
            "sell_orders": paginated,
            "pagination": {
                "total": len(filtered_orders),
                "filtered_total": len(filtered_orders),
                "source_total": all_orders.get("pagination", {}).get("total", 0)
            },
            "success": True,
            "note": "Server endpoint not available - using client-side filtering"
        }
    except Exception as e:
        logger.error(f"Error in client-side filtering: {e}")
        return {
            "error": str(e),
            "success": False,
            "note": "Both server endpoint and client-side filtering failed"
        }
```

#### Workaround #2: Validator Address Validation

**File:** `src/mcp_server/tools/distribution_tools.py`

**Add pre-flight validation:**
```python
async def get_validator_outstanding_rewards(validator_address: str) -> Dict[str, Any]:
    """Get validator outstanding rewards with validation."""
    try:
        # Validate validator address format
        if not validator_address.startswith("regenvaloper1"):
            return {
                "error": "Invalid validator address format",
                "expected": "regenvaloper1...",
                "provided": validator_address,
                "suggestion": "Use list_validators to find valid addresses"
            }

        # Try query with better error handling
        client = get_regen_client()
        response = await client.get_validator_outstanding_rewards(validator_address)
        return response

    except NetworkError as e:
        if "500" in str(e):
            return {
                "error": "Server error querying validator rewards",
                "validator_address": validator_address,
                "note": "Validator may not be active or server query disabled",
                "suggestion": "Verify validator is active using explorer: https://www.mintscan.io/regen/validators",
                "technical_error": str(e)
            }
        raise
```

#### Documentation Update

**File:** `.claude/docs/tool_limitations.md` (new file)

Document all non-fixable limitations:
```markdown
# Regen Network MCP Tool Limitations

## Server-Side Endpoint Limitations

### Baskets Module (5 tools)
**Status:** Not Implemented (HTTP 501)
**Reason:** Basket functionality not available in current Regen Network version
**Workaround:** None available
**Future:** May be implemented in future network upgrade

### Validator Distribution Queries (4 tools)
**Status:** Server Error (HTTP 500)
**Reason:** Unknown - possible validator state or query optimization issue
**Workaround:** Validate addresses, check validator status on explorer
**Future:** Requires server-side investigation

[... document all limitations ...]
```

---

### Phase 4: Comprehensive Testing (30 minutes)

#### Test Plan

**1. Unit Tests:**
```bash
# Test pagination fix
pytest tests/tools/test_bank_tools.py -v

# Test analytics (if fixed)
pytest tests/tools/test_analytics_tools.py -v

# Test all modules
pytest tests/tools/ -v
```

**2. Integration Tests:**
```bash
# Test with real addresses
pytest tests/integration/test_user_journeys.py -v
```

**3. MCP Server Test:**
```bash
# Start server
uv run python main.py

# In another terminal - test with Claude
mcp__regen-network__get_all_balances(
    address="regen1qqy8su5mf4tlm9h36fgf2p43gdtnu4ka8gmjmg",
    limit=20,
    page=1
)
```

**4. Update Test Results:**
```bash
# Re-run comprehensive test
# Update .claude/docs/mcp_tools_test_results.md with new results
```

---

### Phase 5: Code Quality & Future-Proofing (30 minutes)

#### Improvement #1: Robust Error Handling

Add standardized error response format:
```python
# src/mcp_server/models/errors.py (new file)
from pydantic import BaseModel
from typing import Optional, Literal

class ToolError(BaseModel):
    success: bool = False
    error_type: Literal["validation", "network", "server", "not_implemented"]
    error_message: str
    technical_details: Optional[str] = None
    user_suggestion: Optional[str] = None
    workaround_available: bool = False
    workaround_description: Optional[str] = None
```

#### Improvement #2: Endpoint Health Check

Add tool availability checker:
```python
# src/mcp_server/tools/health.py (new file)
async def check_tool_availability() -> Dict[str, Any]:
    """Check which tools are currently functional."""
    results = {
        "bank_module": {},
        "distribution_module": {},
        "governance_module": {},
        "marketplace_module": {},
        "ecocredit_module": {},
        "baskets_module": {},
        "analytics_module": {}
    }

    # Test each module
    # Return availability matrix
    return results
```

#### Improvement #3: Caching for Failed Endpoints

Don't retry known-broken endpoints:
```python
# src/mcp_server/cache/endpoint_cache.py
KNOWN_BROKEN_ENDPOINTS = {
    "/regen/ecocredit/v1/baskets": "HTTP 501 - Not Implemented",
    "/cosmos/bank/v1beta1/balances/{address}/{denom}": "HTTP 501 - Not Implemented",
    # ... etc
}

def should_skip_endpoint(endpoint: str) -> bool:
    return endpoint in KNOWN_BROKEN_ENDPOINTS
```

---

## Part 4: Actionable Implementation Plan

### Timeline & Dependencies

```
Phase 1: Quick Wins (15 min)
├─> Pagination fix
└─> Test 3 bank tools

Phase 2: Analytics (2-4 hours)
├─> Reproduce errors
├─> Identify bug
├─> Implement fix
└─> Test 3 analytics tools

Phase 3: Workarounds (30 min)
├─> Client-side filtering
├─> Better error messages
└─> Documentation

Phase 4: Testing (30 min)
├─> Unit tests
├─> Integration tests
└─> Update results

Phase 5: Quality (30 min)
├─> Error handling
├─> Health checks
└─> Caching

Total Time: 4-6 hours
```

### Success Criteria

**Minimum Success (Guaranteed):**
- ✅ 3 bank tools fixed (pagination)
- ✅ Documentation updated
- ✅ Tests passing
- **Result:** 27/44 tools (61%)

**Target Success (Likely):**
- ✅ 3 bank tools fixed
- ✅ 1-2 analytics tools fixed
- ✅ Workarounds implemented
- ✅ Comprehensive documentation
- **Result:** 28-29/44 tools (64-66%)

**Maximum Success (Best Case):**
- ✅ 3 bank tools fixed
- ✅ 3 analytics tools fixed
- ✅ All workarounds implemented
- ✅ Health monitoring added
- ✅ Error handling improved
- **Result:** 30/44 tools (68%)

### Risk Mitigation

**Risk #1: Analytics bugs unfixable**
- Mitigation: Document thoroughly, provide alternatives
- Fallback: Mark as "known issues" with investigation notes

**Risk #2: Testing reveals new bugs**
- Mitigation: Comprehensive test suite before and after
- Fallback: Roll back changes, document findings

**Risk #3: MCP server integration issues**
- Mitigation: Test with actual MCP server, not just Python
- Fallback: Provide manual testing scripts

---

## Part 5: Post-Implementation

### Monitoring & Maintenance

**1. Add to CI/CD:**
```yaml
# .github/workflows/test.yml (if using GitHub Actions)
- name: Test MCP Tools
  run: pytest tests/tools/ -v --cov=src/mcp_server/tools
```

**2. Regular Health Checks:**
```bash
# Weekly endpoint health check
./scripts/check_endpoint_health.sh
```

**3. Version Tracking:**
```markdown
## Tool Status by Version

### v0.2.0 (2025-10-17)
- Fixed: Pagination validation (3 tools)
- Fixed: Analytics parameter bugs (2-3 tools)
- Added: Client-side marketplace filtering
- Status: 28-30/44 tools working (64-68%)

### v0.1.0 (Initial)
- Status: 24/44 tools working (55%)
```

### Future Improvements

**When Regen Network Updates Server:**
1. Monitor Regen Network GitHub for releases
2. Test endpoints that currently return 501
3. Update documentation when endpoints become available
4. Potentially restore 10+ additional tools

**Upstream Contributions:**
1. Report endpoint availability issues to Regen Network team
2. Contribute endpoint implementations if possible
3. Share tool usage patterns for their roadmap

---

## Conclusion

This ultraplan provides a comprehensive, actionable strategy to maximize tool functionality within the constraints of the current Regen Network server implementation.

**Guaranteed Outcomes:**
- 3 tools fixed immediately (pagination)
- Clear documentation of all limitations
- Better error handling and user experience
- Workarounds for common use cases

**Potential Outcomes:**
- Up to 6 additional tools working (analytics + pagination)
- 68% tool functionality (30/44)
- Robust health monitoring
- Foundation for future improvements

**Key Success Factor:** Focus on what we CAN fix (code-level bugs) while gracefully handling what we CANNOT fix (server-side limitations).

---

## Appendix: Quick Reference

### Files to Modify

1. **MUST CHANGE:**
   - `src/mcp_server/client/regen_client.py:42-43` (pagination fix)

2. **INVESTIGATE & POSSIBLY CHANGE:**
   - `src/mcp_server/tools/analytics_tools.py` (analytics bugs)
   - `src/mcp_server/tools/analytics_tool_registration.py` (registration)

3. **ENHANCE:**
   - `src/mcp_server/tools/marketplace_tools.py` (workarounds)
   - `src/mcp_server/tools/distribution_tools.py` (validation)

4. **CREATE:**
   - `.claude/docs/tool_limitations.md` (documentation)
   - `src/mcp_server/models/errors.py` (error handling)
   - `src/mcp_server/tools/health.py` (monitoring)

### Commands to Run

```bash
# 1. Fix pagination
# Edit regen_client.py lines 42-43

# 2. Test immediately
pytest tests/tools/test_bank_tools.py::test_get_all_balances -v

# 3. Investigate analytics
python test_analytics_direct.py

# 4. Run full test suite
pytest tests/tools/ -v

# 5. Update documentation
# Edit mcp_tools_test_results.md with new results

# 6. Commit changes
git add -A
git commit -m "fix: resolve pagination validation and restore 3-6 tools"
```

---

**END OF ULTRAPLAN**
