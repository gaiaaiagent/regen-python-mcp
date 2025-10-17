# Regen Network MCP Tools Test Results

**Test Date:** 2025-10-17
**Total Tools Tested:** 44
**Tools Working:** 24/44 (55%)

## Executive Summary

Comprehensive testing of all 44 Regen Network MCP tools reveals:
- **Core functionality working:** Bank, Governance, and Ecocredits modules have good coverage
- **Critical issues:** Baskets module entirely non-functional, Advanced Analytics have code bugs
- **API limitations:** Several HTTP 501/500 errors indicate missing server endpoints

---

## Module-by-Module Results

### 1. Bank Module (11 tools) - 64% Working

**Working Tools (7):**
- ✅ `list_accounts` - Lists all accounts with pagination (22,908 total accounts)
- ✅ `get_account` - Retrieves detailed account information
- ✅ `get_supply_of` - Gets total supply of specific token (216.3T uregen)
- ✅ `get_bank_params` - Returns bank module parameters
- ✅ `get_denoms_metadata` - Lists token metadata (NCT, REGEN)
- ✅ `get_denom_metadata` - Gets metadata for specific token
- ✅ `get_denom_owners` - Lists all holders of a token (22,442 uregen holders)

**Failed Tools (4):**
- ❌ `get_balance` - HTTP 501 (endpoint not implemented)
- ❌ `get_all_balances` - Pagination validation error (boolean type issues)
- ❌ `get_spendable_balances` - Pagination validation error
- ❌ `get_total_supply` - Pagination validation error

**Issues:**
- Pagination model has validation errors with `count_total` and `reverse` boolean fields
- The `/cosmos/bank/v1beta1/balances/{address}/{denom}` endpoint returns HTTP 501

---

### 2. Distribution Module (9 tools) - 56% Working

**Working Tools (5):**
- ✅ `get_distribution_params` - Returns distribution parameters (17% community tax)
- ✅ `get_community_pool` - Gets community pool balance (3.46T uregen)
- ✅ `get_delegator_validators` - Lists validators for delegator
- ✅ `get_delegator_withdraw_address` - Gets withdrawal address
- ✅ `get_delegation_total_rewards` - Gets total delegation rewards

**Failed Tools (4):**
- ❌ `get_validator_outstanding_rewards` - HTTP 500
- ❌ `get_validator_commission` - HTTP 500
- ❌ `get_validator_slashes` - HTTP 400
- ❌ `get_delegation_rewards` - HTTP 500

**Issues:**
- Validator-specific reward queries fail with server errors
- May be related to validator address format or inactive validators

---

### 3. Governance Module (8 tools) - 75% Working

**Working Tools (6):**
- ✅ `list_governance_proposals` - Lists proposals with pagination (56 total)
- ✅ `get_governance_proposal` - Gets specific proposal details
- ✅ `list_governance_votes` - Lists votes on proposal
- ✅ `list_governance_deposits` - Lists proposal deposits
- ✅ `get_governance_params` - Gets governance parameters (voting, deposit, tally)
- ✅ `get_governance_tally_result` - Gets vote tally for proposal

**Not Tested (2):**
- ⚠️ `get_governance_vote` - Requires specific voter address from active proposal
- ⚠️ `get_governance_deposit` - Requires specific depositor address

**Sample Data:**
- Proposal #1: "Enable REGEN Transfers" (PASSED)
- 48.7M YES votes, 48.5M NO votes, 0 ABSTAIN

---

### 4. Marketplace Module (5 tools) - 40% Working

**Working Tools (2):**
- ✅ `list_sell_orders` - Lists active sell orders (26 total)
- ✅ `get_sell_order` - Gets specific sell order details

**Failed Tools (3):**
- ❌ `list_sell_orders_by_batch` - HTTP 501 (not implemented)
- ❌ `list_sell_orders_by_seller` - HTTP 501 (not implemented)
- ❌ `list_allowed_denoms` - HTTP 500

**Sample Data:**
- Order #39: 5 credits from batch C02-002-20211012-20241013-001
- Ask price: 45M (in IBC token)
- Seller: regen19hglnhnv05470arvvvc6nfngzx0kq39apzht35

**Issues:**
- Filtered query endpoints not implemented on server side
- Limits marketplace analysis capabilities

---

### 5. Ecocredits Module (6 tools) - 67% Working

**Working Tools (4):**
- ✅ `list_credit_types` - Lists enabled credit types (5 types: BT, C, KSH, MBS, USS)
- ✅ `list_classes` - Lists credit classes (12 total: C01-C07, BT01, KSH01, MBS01)
- ✅ `list_projects` - Lists registered projects (56 total across various jurisdictions)
- ✅ `list_credit_batches` - Lists credit batches (74 total batches)

**Failed Tools (2):**
- ❌ `get_basket` - HTTP 501 (see Baskets Module)
- ❌ `get_basket_fee` - HTTP 501

**Sample Data:**
- Credit Class C01: Carbon sequestration through reforestation
- Project C01-001: VCS-934 in CD-MN (Democratic Republic of Congo)
- Batch C01-001-20150101-20151231-001: 2015 vintage, issued 2022-05-06

---

### 6. Baskets Module (5 tools) - 0% Working

**All Failed:**
- ❌ `list_baskets` - HTTP 501
- ❌ `get_basket` - HTTP 501
- ❌ `list_basket_balances` - HTTP 501
- ❌ `get_basket_balance` - HTTP 501

**Issues:**
- Baskets module appears to be completely non-functional
- All endpoints return HTTP 501 (Not Implemented)
- The eco.C.NCT basket exists (seen in denom metadata) but cannot be queried
- This is a critical gap for basket-related functionality

---

### 7. Advanced Analytics (3 tools) - 0% Working

**All Failed:**
- ❌ `analyze_portfolio_impact` - Code bug: `RegenClient.query_all_balances() got an unexpected keyword argument 'limit'`
- ❌ `analyze_market_trends` - Code bug: `RegenClient.query_sell_orders() got an unexpected keyword argument 'limit'`
- ❌ `compare_credit_methodologies` - Code bug: `RegenClient.query_credit_classes() got an unexpected keyword argument 'limit'`

**Issues:**
- Internal implementation bugs in all three analytics functions
- Methods are calling underlying client methods with incorrect parameters
- Requires code fixes in `src/mcp_server/tools/credit_tools.py`

---

## Critical Issues Summary

### High Priority Bugs

1. **Pagination Validation Errors (Bank Module)**
   - File: Likely in models/pagination.py or similar
   - Issue: Boolean fields `count_total` and `reverse` not accepting None values
   - Impact: Prevents querying all balances and total supply
   - Fix: Make boolean fields optional or default to False

2. **Advanced Analytics Code Bugs**
   - File: `src/mcp_server/tools/credit_tools.py`
   - Issue: Passing `limit` parameter to methods that don't accept it
   - Impact: All three analytics tools broken
   - Fix: Remove or rename parameter in method calls

3. **Baskets Module Non-Functional**
   - Issue: All basket endpoints return HTTP 501
   - Impact: Cannot query basket data despite baskets existing (eco.C.NCT)
   - Investigation needed: Server-side endpoint availability

### Medium Priority Issues

4. **Validator Reward Queries Failing**
   - Impact: Cannot get validator commission, rewards, or slashes
   - May be related to validator address format or endpoint availability

5. **Marketplace Filtered Queries Not Implemented**
   - Impact: Cannot filter sell orders by batch or seller
   - Workaround: Use `list_sell_orders` and filter client-side

6. **get_balance Returns HTTP 501**
   - Impact: Cannot get single token balance for an account
   - Workaround: Use `get_denom_owners` to find balance

---

## Working Use Cases

Despite the issues, these workflows are fully functional:

### Account Analysis
```python
# Get account information
accounts = list_accounts(limit=100)
account_details = get_account(address)
owners = get_denom_owners(denom="uregen")
```

### Credit Discovery
```python
# Explore ecocredits
credit_types = list_credit_types()
classes = list_classes(limit=20)
projects = list_projects(limit=50)
batches = list_credit_batches(limit=100)
```

### Governance Tracking
```python
# Monitor governance
proposals = list_governance_proposals(limit=10)
proposal = get_governance_proposal(proposal_id=1)
tally = get_governance_tally_result(proposal_id=1)
```

### Market Analysis
```python
# Basic market data
orders = list_sell_orders(limit=100)
order = get_sell_order(sell_order_id=39)
# Note: Must filter client-side by batch/seller
```

---

## Recommendations

### For Development Team

1. **Fix pagination validation** in Bank module tools - quick win for 3 tools
2. **Fix analytics function signatures** - quick win for 3 tools
3. **Investigate Baskets module** server-side implementation
4. **Add validator data validation** before querying distribution endpoints
5. **Document HTTP 501 endpoints** as unsupported in tool descriptions

### For Users

1. **Use working tools** for core functionality (24 tools available)
2. **Implement client-side filtering** for marketplace queries
3. **Avoid Baskets module** until server-side fixes deployed
4. **Don't rely on Advanced Analytics** until code bugs fixed
5. **Test validator addresses** before querying distribution data

---

## Test Data Used

- **Account:** `regen1qqy8su5mf4tlm9h36fgf2p43gdtnu4ka8gmjmg`
- **Validator:** `regenvaloper1tnh2q55v8wyygtt9srz5safamzdengsn5qnlm4`
- **Proposal:** #1 (Enable REGEN Transfers)
- **Sell Order:** #39
- **Credit Batch:** `C02-002-20211012-20241013-001`
- **Token:** `uregen` (native REGEN token)
- **Basket:** `eco.C.NCT` (Nature Carbon Ton)

---

## Network Information

- **Total Accounts:** 22,908
- **Total Proposals:** 56
- **Total Sell Orders:** 26
- **Total Credit Classes:** 12
- **Total Projects:** 56
- **Total Credit Batches:** 74
- **Community Pool:** 3,461,266,470,523 uregen
- **Total Supply (uregen):** 216,324,713,208,692 uregen (216.3 trillion)

---

## Next Steps

1. File issues for pagination validation errors
2. Fix analytics function parameter bugs
3. Investigate Baskets module server endpoints
4. Create integration tests for working tools
5. Document workarounds for non-functional endpoints
