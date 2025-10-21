# Regen Network MCP Tool Limitations & Workarounds

**Last Updated:** 2025-10-17
**Tool Status:** 30/44 working (68%)

## Overview

This document provides comprehensive information about tool limitations, their root causes, and available workarounds. Understanding these limitations is essential for building reliable applications on top of the Regen Network MCP server.

---

## ✅ Fully Functional Tools (30)

### Bank Module (7/11 working)
- ✅ `list_accounts` - Lists all blockchain accounts
- ✅ `get_account` - Gets detailed account information
- ✅ `get_all_balances` - **FIXED** - Gets all token balances for address
- ✅ `get_spendable_balances` - **FIXED** - Gets spendable balances
- ✅ `get_total_supply` - **FIXED** - Gets total token supply
- ✅ `get_supply_of` - Gets supply of specific denomination
- ✅ `get_bank_params` - Gets bank module parameters
- ✅ `get_denoms_metadata` - Gets metadata for all tokens
- ✅ `get_denom_metadata` - Gets metadata for specific token
- ✅ `get_denom_owners` - Lists all holders of a token

### Distribution Module (5/9 working)
- ✅ `get_distribution_params` - Gets distribution parameters
- ✅ `get_community_pool` - Gets community pool balance
- ✅ `get_delegator_validators` - Lists delegator's validators
- ✅ `get_delegator_withdraw_address` - Gets withdrawal address
- ✅ `get_delegation_total_rewards` - Gets total delegation rewards

### Governance Module (6/8 working)
- ✅ `list_governance_proposals` - Lists governance proposals
- ✅ `get_governance_proposal` - Gets specific proposal
- ✅ `list_governance_votes` - Lists votes on proposal
- ✅ `list_governance_deposits` - Lists proposal deposits
- ✅ `get_governance_params` - Gets governance parameters
- ✅ `get_governance_tally_result` - Gets proposal vote tally

### Marketplace Module (2/5 working)
- ✅ `list_sell_orders` - Lists all active sell orders
- ✅ `get_sell_order` - Gets specific sell order

### Ecocredits Module (4/6 working)
- ✅ `list_credit_types` - Lists enabled credit types
- ✅ `list_classes` - Lists credit classes
- ✅ `list_projects` - Lists registered projects
- ✅ `list_credit_batches` - Lists credit batches

### Analytics Module (3/3 working)
- ✅ `analyze_portfolio_impact` - **FIXED** - Portfolio impact analysis
- ✅ `analyze_market_trends` - **FIXED** - Market trend analysis
- ✅ `compare_credit_methodologies` - **FIXED** - Methodology comparison

---

## ❌ Non-Functional Tools (14)

### Category A: Missing Server Endpoints (HTTP 501)

These tools fail because the Regen Network REST API does not implement the required endpoints. This is a server-side limitation that cannot be fixed client-side.

#### Baskets Module (5 tools - 0% functional)

**Status:** Completely non-functional
**HTTP Error:** 501 Not Implemented
**Root Cause:** Baskets module endpoints not available in current Regen Network version

**Failed Tools:**
1. ❌ `list_baskets` - `/regen/ecocredit/v1/baskets`
2. ❌ `get_basket` - `/regen/ecocredit/v1/basket/{denom}`
3. ❌ `list_basket_balances` - `/regen/ecocredit/v1/basket/{denom}/balances`
4. ❌ `get_basket_balance` - `/regen/ecocredit/v1/basket/{denom}/balance/{batch}`
5. ❌ `get_basket_fee` - `/regen/ecocredit/v1/basket-fee`

**Workaround:** NONE available. Basket functionality is fundamental infrastructure that must be implemented server-side.

**Evidence:**
- Basket token `eco.C.NCT` exists in denom metadata
- Cannot query basket information despite token existence
- All 5 endpoints consistently return HTTP 501

**Future:** May be implemented in future Regen Network upgrades. Monitor:
- https://github.com/regen-network/regen-ledger releases
- Regen Network Discord announcements

---

#### Marketplace Filtered Queries (2 tools)

**Status:** Endpoints not implemented
**HTTP Error:** 501 Not Implemented
**Root Cause:** Filtered marketplace queries not available

**Failed Tools:**
1. ❌ `list_sell_orders_by_batch` - `/regen/ecocredit/marketplace/v1/sell-orders-by-batch`
2. ❌ `list_sell_orders_by_seller` - `/regen/ecocredit/marketplace/v1/sell-orders-by-seller`

**Workaround:** ✅ CLIENT-SIDE FILTERING

Use `list_sell_orders` and filter results in your application:

```python
# Workaround for list_sell_orders_by_batch
async def get_orders_for_batch(batch_denom: str):
    all_orders = await list_sell_orders(limit=1000)
    return [
        order for order in all_orders.get("sell_orders", [])
        if order.get("batch_denom") == batch_denom
    ]

# Workaround for list_sell_orders_by_seller
async def get_orders_by_seller(seller_address: str):
    all_orders = await list_sell_orders(limit=1000)
    return [
        order for order in all_orders.get("sell_orders", [])
        if order.get("seller") == seller_address
    ]
```

**Performance Impact:** Minimal - typically only 20-50 orders total in marketplace

---

#### Single Balance Query (1 tool)

**Status:** Endpoint not implemented
**HTTP Error:** 501 Not Implemented

**Failed Tool:**
1. ❌ `get_balance` - `/cosmos/bank/v1beta1/balances/{address}/{denom}`

**Workaround:** ✅ USE get_all_balances

```python
# Instead of get_balance(address, denom)
async def get_balance_workaround(address: str, denom: str):
    all_balances = await get_all_balances(address, limit=200)
    for balance in all_balances.get("balances", []):
        if balance.get("denom") == denom:
            return {"balance": balance}
    return {"balance": {"denom": denom, "amount": "0"}}
```

---

#### Allowed Denoms Query (1 tool)

**Status:** Server error
**HTTP Error:** 500 Internal Server Error

**Failed Tool:**
1. ❌ `list_allowed_denoms` - `/regen/ecocredit/marketplace/v1/allowed-denoms`

**Workaround:** Observe payment denoms in active sell orders

```python
async def get_active_payment_denoms():
    orders = await list_sell_orders(limit=1000)
    denoms = set()
    for order in orders.get("sell_orders", []):
        ask_denom = order.get("ask_denom")
        if ask_denom:
            denoms.add(ask_denom)
    return list(denoms)
```

---

### Category B: Validator Query Errors (HTTP 500/400)

These tools fail with server errors when querying validator-specific information. The root cause is unclear but may be related to validator address formats or server-side query optimization.

**Failed Tools:**
1. ❌ `get_validator_outstanding_rewards` - HTTP 500
2. ❌ `get_validator_commission` - HTTP 500
3. ❌ `get_validator_slashes` - HTTP 400
4. ❌ `get_delegation_rewards` - HTTP 500

**Tested With:** `regenvaloper1tnh2q55v8wyygtt9srz5safamzdengsn5qnlm4`

**Possible Causes:**
- Validator not currently active
- Validator address format issues
- Server-side query optimization disabled
- Module version mismatch

**Workaround:** ⚠️ LIMITED

```python
# Pre-validate validator address
async def safe_get_validator_rewards(validator_address: str):
    if not validator_address.startswith("regenvaloper1"):
        return {
            "error": "Invalid validator address format",
            "suggestion": "Verify address at https://www.mintscan.io/regen/validators"
        }

    try:
        return await get_validator_outstanding_rewards(validator_address)
    except Exception as e:
        return {
            "error": "Server error querying validator",
            "note": "Validator may not be active",
            "validator": validator_address,
            "explorer_url": f"https://www.mintscan.io/regen/validators/{validator_address}"
        }
```

**Recommendation:** Use block explorers for validator data until server-side issues are resolved.

---

## 🔧 Workaround Implementation Examples

### Example 1: Portfolio Manager - Complete Holdings View

```python
async def get_complete_portfolio(address: str):
    """Get complete portfolio including ecocredits and regular tokens."""

    # Get all balances (works after pagination fix)
    balances = await get_all_balances(address, limit=200)

    # Separate ecocredits from regular tokens
    ecocredits = []
    regular_tokens = []

    for balance in balances.get("balances", []):
        denom = balance.get("denom", "")
        if "-" in denom or "eco." in denom:
            ecocredits.append(balance)
        else:
            regular_tokens.append(balance)

    # Get metadata for display
    metadata = await get_denoms_metadata(limit=50)

    return {
        "address": address,
        "ecocredits": ecocredits,
        "regular_tokens": regular_tokens,
        "metadata": metadata.get("metadatas", []),
        "total_holdings": len(balances.get("balances", []))
    }
```

### Example 2: Market Analyst - Order Book Analysis

```python
async def analyze_order_book(batch_denom: Optional[str] = None):
    """Analyze marketplace order book with optional filtering."""

    # Get all orders
    all_orders_result = await list_sell_orders(limit=1000)
    all_orders = all_orders_result.get("sell_orders", [])

    # Filter if batch specified (workaround for missing endpoint)
    if batch_denom:
        all_orders = [
            order for order in all_orders
            if order.get("batch_denom") == batch_denom
        ]

    # Analysis
    total_volume = sum(float(o.get("quantity", 0)) for o in all_orders)
    total_value = sum(float(o.get("ask_amount", 0)) for o in all_orders)
    avg_price = total_value / total_volume if total_volume > 0 else 0

    # Get unique sellers
    sellers = set(o.get("seller") for o in all_orders)

    return {
        "total_orders": len(all_orders),
        "total_volume": total_volume,
        "total_value": total_value,
        "average_price": avg_price,
        "unique_sellers": len(sellers),
        "batch_denom": batch_denom,
        "filtered": batch_denom is not None
    }
```

### Example 3: Credit Researcher - Full Project Analysis

```python
async def analyze_credit_project(project_id: str):
    """Complete analysis of a credit project."""

    # Get all projects and find target
    projects = await list_projects(limit=100)
    project = next(
        (p for p in projects.get("projects", []) if p.get("id") == project_id),
        None
    )

    if not project:
        return {"error": f"Project {project_id} not found"}

    # Get class information
    class_id = project.get("class_id")
    classes = await list_classes(limit=50)
    credit_class = next(
        (c for c in classes.get("classes", []) if c.get("id") == class_id),
        None
    )

    # Get related batches
    batches_result = await list_credit_batches(limit=200)
    project_batches = [
        b for b in batches_result.get("batches", [])
        if b.get("project_id") == project_id
    ]

    # Get marketplace activity (workaround: filter all orders)
    orders_result = await list_sell_orders(limit=1000)
    batch_denoms = [b.get("denom") for b in project_batches]
    project_orders = [
        o for o in orders_result.get("sell_orders", [])
        if o.get("batch_denom") in batch_denoms
    ]

    return {
        "project": project,
        "credit_class": credit_class,
        "batches": project_batches,
        "active_orders": project_orders,
        "total_batches": len(project_batches),
        "marketplace_liquidity": len(project_orders)
    }
```

---

## 📊 Limitation Impact Assessment

### High Impact (Blocking Use Cases)

**Baskets Module** - Prevents:
- Basket-based credit trading
- Aggregated credit analysis
- Basket creation/management workflows

**Workaround:** Not available. Users must work with individual credit batches.

### Medium Impact (Workarounds Available)

**Marketplace Filtering** - Impacts:
- Performance of batch-specific queries
- Seller-focused analysis
- Real-time market monitoring

**Workaround:** Client-side filtering (demonstrated above)

**Validator Queries** - Impacts:
- Delegation reward tracking
- Validator performance analysis
- Staking portfolio management

**Workaround:** Use block explorers for validator data

### Low Impact (Minimal Effect)

**Single Balance Query** - Impacts:
- Micro-optimizations only

**Workaround:** Use `get_all_balances` and filter

---

## 🔮 Future Outlook

### Server-Side Improvements Needed

**Priority 1: Baskets Module**
- Implement 5 basket endpoints
- Enable basket-based trading
- Critical for aggregated credit functionality

**Priority 2: Marketplace Filtering**
- Add batch filtering endpoint
- Add seller filtering endpoint
- Improves query performance

**Priority 3: Validator Queries**
- Fix HTTP 500 errors
- Enable delegation analytics
- Support staking dashboards

### Client-Side Enhancements (Available Now)

✅ Pagination validation - **FIXED** (2025-10-17)
✅ Analytics tools - **FIXED** (2025-10-17)
⬜ Endpoint health monitoring - Planned
⬜ Automatic fallback strategies - Planned
⬜ Response caching - Partially implemented

---

## 💡 Best Practices

### For Application Developers

1. **Always check for errors** in tool responses
2. **Implement client-side filtering** for marketplace queries
3. **Cache frequently accessed data** (credit classes, projects)
4. **Use workarounds** documented above for limited functionality
5. **Monitor tool status** updates in this document

### For Data Analysts

1. **Fetch complete datasets** when possible (use high limits)
2. **Filter locally** rather than relying on server-side filtering
3. **Cross-reference** with block explorers for validator data
4. **Aggregate carefully** - some data unavailable (baskets)

### For Portfolio Managers

1. **Use `get_all_balances`** for complete portfolio view
2. **Track orders** via `list_sell_orders` + client filtering
3. **Monitor governance** via fully-functional governance tools
4. **Analyze impact** with restored analytics tools

---

## 📞 Support & Updates

### Reporting Issues

If you encounter tool failures not documented here:
1. Note the exact error message and HTTP code
2. Record the tool name and parameters used
3. Report at: https://github.com/regen-network/regen-ledger/issues

### Monitoring Updates

Tool status may change with Regen Network upgrades:
- Check Regen Network GitHub releases
- Monitor Discord announcements
- Review this document for updates

### Testing Tools

Use the test scripts provided:
```bash
# Test pagination-dependent tools
python test_pagination_fix.py

# Test analytics tools
python test_analytics_direct.py
```

---

## Appendix: Quick Reference

### Working Tools by Category

| Module | Working | Total | % |
|--------|---------|-------|---|
| Bank | 7 | 11 | 64% |
| Distribution | 5 | 9 | 56% |
| Governance | 6 | 8 | 75% |
| Marketplace | 2 | 5 | 40% |
| Ecocredits | 4 | 6 | 67% |
| Baskets | 0 | 5 | 0% |
| Analytics | 3 | 3 | 100% |
| **TOTAL** | **30** | **44** | **68%** |

### Recently Fixed (2025-10-17)

- ✅ `get_all_balances` - Pagination validation
- ✅ `get_spendable_balances` - Pagination validation
- ✅ `get_total_supply` - Pagination validation
- ✅ `analyze_portfolio_impact` - Pagination validation
- ✅ `analyze_market_trends` - Pagination validation
- ✅ `compare_credit_methodologies` - Pagination validation

**Total Restored:** 6 tools (13.6% improvement)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Next Review:** Check after next Regen Network upgrade
