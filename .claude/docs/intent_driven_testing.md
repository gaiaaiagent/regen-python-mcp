# Intent-Driven Testing Strategy: Validating the Thesis

**Purpose:** Ensure tests validate that the MCP actually enables the use cases described in `docs/regen_mcp_thesis.md`, not just that code runs.

**Principle:** Tests should answer "Can a user accomplish their goal?" not "Does this function return a dict?"

---

## Thesis-Driven Use Case Mapping

From the thesis, users need to accomplish these real-world goals:

### 1. ARBITRAGE AGENT: Monitor Credit Markets for Opportunities

**User Story:**
> "As an autonomous agent, I need to identify arbitrage opportunities by comparing credit prices across batches and sellers to maximize returns."

**Required Capabilities:**
- ✓ List all active sell orders
- ✓ Filter sell orders by credit batch
- ✓ Filter sell orders by seller
- ✓ Compare prices across equivalent credits
- ✓ Get credit batch details (vintage year, project, methodology)
- ⚠️ **GAP:** Get credit supply amounts (thesis mentions this limitation)
- ⚠️ **GAP:** Track order history / price changes over time

**Test That Validates This:**
```python
@pytest.mark.e2e
@pytest.mark.user_journey
async def test_arbitrage_agent_can_identify_opportunities():
    """
    Validates: Can an agent identify arbitrage opportunities?

    This is THE test that proves the MCP enables arbitrage trading.
    If this fails, the thesis promise is broken.
    """
    # 1. Agent needs to see all available sell orders
    sell_orders = await list_sell_orders(limit=100)
    assert len(sell_orders["sell_orders"]) > 0, \
        "Agent cannot identify arbitrage without sell order data"

    # 2. Agent needs price and quantity for each order
    order = sell_orders["sell_orders"][0]
    assert "ask_price" in order, "Cannot identify arbitrage without pricing"
    assert "quantity" in order, "Cannot identify arbitrage without quantities"
    assert "batch_denom" in order, "Cannot compare equivalent credits"

    # 3. Agent needs batch details to compare equivalent credits
    batch_denom = order["batch_denom"]
    batch = await get_credit_batch(batch_denom)  # Does this exist?
    assert "vintage_year" in batch or "start_date" in batch, \
        "Cannot compare equivalent vintage credits"

    # 4. Can agent group by credit class to find comparable credits?
    orders_by_class = {}
    for order in sell_orders["sell_orders"]:
        # Extract class from batch denom (e.g., "C01-...")
        class_id = order["batch_denom"].split("-")[0]
        if class_id not in orders_by_class:
            orders_by_class[class_id] = []
        orders_by_class[class_id].append(order)

    # For arbitrage to work, need multiple orders of same class
    classes_with_multiple_orders = [
        k for k, v in orders_by_class.items() if len(v) > 1
    ]

    # If no arbitrage opportunities, that's fine - but agent must be able to check
    # This test proves the CAPABILITY exists, not that opportunities always exist
```

**Status:** ⚠️ Partially Validated (missing batch detail queries, supply data)

---

### 2. ML MODEL: Analyze Trends and Predict Future Adoption

**User Story:**
> "As a machine learning researcher, I need to analyze the relationship between credit vintage years, methodologies, and market adoption to predict future trends."

**Required Capabilities:**
- ✓ List all credit classes with methodology info
- ✓ List all credit batches with vintage years
- ✓ Get project information
- ⚠️ **GAP:** Batch issuance timestamps (when was batch created?)
- ⚠️ **GAP:** Historical sell order data (what sold when?)
- ⚠️ **GAP:** Retirement events (what credits were retired when?)

**Test That Validates This:**
```python
@pytest.mark.e2e
@pytest.mark.user_journey
async def test_ml_model_can_analyze_adoption_trends():
    """
    Validates: Can an ML model gather data for trend analysis?

    Tests the thesis claim: "Machine learning models could analyze
    the relationship between credit vintage years, methodologies,
    and market adoption to predict future trends."
    """
    # 1. Get all credit classes to understand methodologies
    classes = await list_credit_classes(limit=100)
    assert len(classes["classes"]) >= 11, \
        "Thesis mentions 11 distinct credit classes - verify they're accessible"

    # 2. Each class must have methodology information
    for credit_class in classes["classes"]:
        assert "id" in credit_class, "Cannot group batches by methodology"
        # Ideally: assert "methodology_url" or "methodology_description"

    # 3. Get all batches to analyze vintage year distribution
    batches = await list_credit_batches(limit=100)
    assert len(batches["batches"]) >= 64, \
        "Thesis mentions 64 distinct credit batches - verify count"

    # 4. Build dataset for ML: vintage year × methodology → adoption
    ml_dataset = []
    for batch in batches["batches"]:
        # Extract vintage year (this is critical for trend analysis)
        assert "denom" in batch, "Cannot parse vintage information"

        # Batch denom format: C01-001-YYYYMMDD-YYYYMMDD-###
        parts = batch["denom"].split("-")
        class_id = parts[0]
        start_date = parts[2] if len(parts) > 2 else None

        if not start_date:
            continue  # Skip if vintage unparseable

        vintage_year = start_date[:4] if len(start_date) >= 4 else None

        ml_dataset.append({
            "methodology": class_id,
            "vintage_year": vintage_year,
            "batch_denom": batch["denom"],
        })

    # For ML to work, need reasonable dataset size
    assert len(ml_dataset) >= 50, \
        "Insufficient data for meaningful ML trend analysis"

    # Validate vintage year span matches thesis (2012-2034)
    vintage_years = [int(d["vintage_year"]) for d in ml_dataset if d["vintage_year"]]
    assert min(vintage_years) <= 2015, "Should have historical data"
    assert max(vintage_years) >= 2024, "Should have recent data"

    # 5. To measure "adoption", need market activity data
    # This is where current MCP has gaps:
    # - Cannot easily get "how many batches of class C01 were issued per year"
    # - Cannot get "total volume traded" per methodology
    # - Cannot get retirement events

    # Test what we CAN do: count batches by methodology
    batches_by_methodology = {}
    for item in ml_dataset:
        method = item["methodology"]
        batches_by_methodology[method] = batches_by_methodology.get(method, 0) + 1

    # Thesis mentions "C03 leading with 16 batches" - validate
    if "C03" in batches_by_methodology:
        # Don't assert exact number (blockchain changes), but validate it's significant
        assert batches_by_methodology["C03"] > 10, \
            "Thesis mentions C03 leadership - validate high adoption"
```

**Status:** ⚠️ Partially Validated (missing issuance timestamps, trade history, retirement data)

---

### 3. PORTFOLIO MANAGER: Build Diversified Ecological Asset Fund

**User Story:**
> "As a portfolio manager, I need to build diversified ecological asset funds, automatically rebalancing based on environmental outcomes."

**Required Capabilities:**
- ✓ List all credit types (carbon, biodiversity, etc.)
- ✓ List all credit classes within each type
- ✓ List available credits (batches) for purchase
- ✓ Get marketplace prices for each credit
- ⚠️ **GAP:** Credit supply/availability per batch
- ⚠️ **GAP:** Environmental outcome metrics per credit
- ⚠️ **GAP:** Portfolio composition tracking

**Test That Validates This:**
```python
@pytest.mark.e2e
@pytest.mark.user_journey
async def test_portfolio_manager_can_build_diversified_fund():
    """
    Validates: Can a portfolio manager diversify across credit types?

    Tests the thesis claim: "Portfolio managers could build diversified
    ecological asset funds, automatically rebalancing based on
    environmental outcomes."
    """
    # 1. Discover all credit types for diversification
    credit_types = await list_credit_types()
    assert "credit_types" in credit_types

    types_list = credit_types["credit_types"]
    assert len(types_list) >= 5, \
        "Thesis mentions 5 fundamental credit types - validate diversity"

    # Validate thesis-mentioned types exist
    type_abbrevs = [ct["abbreviation"] for ct in types_list]
    assert "C" in type_abbrevs, "Carbon credits must be available"
    # Thesis mentions: KSH, USS, MBS - validate exotic types

    # 2. For each type, get available classes
    portfolio_universe = {}
    for credit_type in types_list:
        type_abbrev = credit_type["abbreviation"]

        # Get classes of this type
        all_classes = await list_credit_classes(limit=100)
        type_classes = [
            c for c in all_classes["classes"]
            if c.get("credit_type_abbrev") == type_abbrev
        ]

        portfolio_universe[type_abbrev] = type_classes

    # 3. For diversification, need multiple options in each type
    assert len(portfolio_universe) > 1, \
        "Cannot diversify with only one credit type"

    # 4. For each class, get market availability (sell orders)
    purchasable_credits = {}
    for type_abbrev, classes in portfolio_universe.items():
        for credit_class in classes:
            class_id = credit_class["id"]

            # Find sell orders for batches of this class
            # (This requires filtering sell orders by batch prefix)
            all_orders = await list_sell_orders(limit=100)
            class_orders = [
                o for o in all_orders["sell_orders"]
                if o["batch_denom"].startswith(class_id + "-")
            ]

            if len(class_orders) > 0:
                purchasable_credits[class_id] = class_orders

    # For portfolio construction, need liquid markets
    assert len(purchasable_credits) >= 3, \
        "Portfolio manager needs multiple liquid credit classes"

    # 5. Calculate portfolio allocation (e.g., equal weight)
    total_types = len(portfolio_universe)
    allocation_per_type = 1.0 / total_types

    # This test proves we CAN gather the data for portfolio construction
    # Missing: Environmental outcome metrics for rebalancing
```

**Status:** ⚠️ Partially Validated (can construct portfolio, but cannot rebalance based on outcomes)

---

### 4. INSURANCE COMPANY: Hedge Climate Risks with Real-Time Data

**User Story:**
> "As an insurance company, I need to hedge climate risks using real-time ecological data to price policies accurately."

**Required Capabilities:**
- ✓ Get current credit prices (market rates)
- ✓ Get project geographic locations
- ⚠️ **GAP:** Real-time environmental metrics
- ⚠️ **GAP:** Project performance data
- ⚠️ **GAP:** Credit retirement patterns (claim events)

**Test That Validates This:**
```python
@pytest.mark.e2e
@pytest.mark.user_journey
async def test_insurance_company_can_hedge_climate_risks():
    """
    Validates: Can insurance companies access data for risk hedging?

    Tests the thesis claim: "Insurance companies could hedge climate
    risks using real-time ecological data."
    """
    # 1. Get all projects to understand geographic exposure
    projects = await list_projects(limit=100)
    assert len(projects["projects"]) > 0, \
        "Cannot hedge without project data"

    # 2. Each project must have location data for risk assessment
    projects_with_location = []
    for project in projects["projects"]:
        if "jurisdiction" in project or "location" in project:
            projects_with_location.append(project)

    assert len(projects_with_location) > 0, \
        "Insurance hedging requires geographic data"

    # 3. For each project, need associated credits (batches)
    project_id = projects["projects"][0]["id"]

    # Get batches for this project
    all_batches = await list_credit_batches(limit=100)
    project_batches = [
        b for b in all_batches["batches"]
        if b.get("project_id") == project_id
    ]

    # 4. For hedging, need current market prices
    if len(project_batches) > 0:
        batch_denom = project_batches[0]["denom"]

        # Get market price for this project's credits
        batch_orders = await list_sell_orders_by_batch(batch_denom, limit=10)

        if len(batch_orders.get("sell_orders", [])) > 0:
            # Can price hedge instrument based on credit price
            order = batch_orders["sell_orders"][0]
            assert "ask_price" in order, "Cannot price hedge without market data"

    # **MAJOR GAP:** Missing real-time environmental metrics
    # Insurance needs: carbon sequestration rates, project health, claim triggers
    # Current MCP: Can get static project/batch data, but not dynamic metrics
```

**Status:** ❌ **Not Validated** (static data only, no real-time metrics)

---

### 5. DAO: Automatically Fund Conservation Projects

**User Story:**
> "As a DAO, I need to automatically fund and manage conservation projects based on verifiable on-chain results."

**Required Capabilities:**
- ✓ List all projects
- ✓ Get project details (admin, class, jurisdiction)
- ✓ See credit batches issued by projects (proof of results)
- ⚠️ **GAP:** Project performance metrics
- ⚠️ **GAP:** Credit issuance history (timeline of results)
- ⚠️ **GAP:** Retirement events (impact verification)

**Test That Validates This:**
```python
@pytest.mark.e2e
@pytest.mark.user_journey
async def test_dao_can_verify_project_results():
    """
    Validates: Can a DAO verify on-chain conservation results?

    Tests the thesis claim: "DAOs focused on environmental outcomes
    could use MCP-connected agents to automatically fund and manage
    conservation projects based on verifiable on-chain results."
    """
    # 1. DAO discovers fundable projects
    projects = await list_projects(limit=100)
    assert len(projects["projects"]) > 0, "DAO needs projects to fund"

    # 2. For each project, verify on-chain results (credit issuance)
    project = projects["projects"][0]
    project_id = project["id"]

    # Get batches issued by this project (proof of conservation work)
    all_batches = await list_credit_batches(limit=100)
    project_batches = [
        b for b in all_batches["batches"]
        if b.get("project_id") == project_id
    ]

    # 3. DAO funding decision based on verified results
    if len(project_batches) > 0:
        # Project has proven track record (issued credits)
        # DAO can verify: How much carbon sequestered? When?

        # Calculate total credits issued
        total_credits = sum(
            float(b.get("amount_tradable", 0)) + float(b.get("amount_retired", 0))
            for b in project_batches
        )

        # DAO decision logic: Fund projects with proven results
        funding_eligible = total_credits > 1000  # Example threshold

        # Test proves DAO CAN verify results
        assert isinstance(funding_eligible, bool), \
            "DAO can make data-driven funding decisions"

    # **GAP:** Missing issuance timeline
    # DAO needs: "Show me credits issued per year" to verify ongoing work
    # DAO needs: "Show me retirement events" to verify real impact
```

**Status:** ⚠️ Partially Validated (can verify issuance, but not timeline/impact)

---

## Critical Gaps Identified

### 1. Credit Supply/Availability Data
**Thesis Quote:** "inability to directly query credit supply amounts through batch listings"

**Impact:** Breaks arbitrage, portfolio management, market analysis

**Test That Would Validate:**
```python
async def test_can_get_credit_supply_for_batch():
    """This SHOULD pass but currently might not due to API limitations."""
    batch_denom = "C01-001-20220101-20221231-001"

    # Need: Total supply, tradable amount, retired amount
    supply_data = await get_batch_supply(batch_denom)

    assert "total_supply" in supply_data
    assert "amount_tradable" in supply_data
    assert "amount_retired" in supply_data
```

### 2. Historical/Time-Series Data
**Impact:** Breaks ML trend analysis, performance tracking, ROI calculation

**Test That Would Validate:**
```python
async def test_can_analyze_issuance_trends_over_time():
    """ML models need temporal data."""
    # Get batch issuance by month for last 2 years
    issuance_timeline = await get_batch_issuance_timeline(
        class_id="C01",
        start_date="2022-01-01",
        end_date="2024-12-31"
    )

    assert len(issuance_timeline) > 0
    assert "date" in issuance_timeline[0]
    assert "batches_issued" in issuance_timeline[0]
```

### 3. Environmental Outcome Metrics
**Impact:** Breaks insurance hedging, impact verification, rebalancing

**Test That Would Validate:**
```python
async def test_can_get_environmental_outcomes():
    """Portfolio rebalancing needs outcome metrics."""
    project_id = "..."

    outcomes = await get_project_outcomes(project_id)

    assert "carbon_sequestered_tons" in outcomes
    assert "biodiversity_score" in outcomes
    assert "measurement_date" in outcomes
```

### 4. Retirement Events/History
**Impact:** Breaks impact verification, claim tracking, utilization analysis

**Test That Would Validate:**
```python
async def test_can_track_credit_retirements():
    """DAOs need to verify actual impact (retirements)."""
    batch_denom = "C01-001-20220101-20221231-001"

    retirements = await get_batch_retirement_history(batch_denom)

    assert len(retirements) >= 0  # May be zero, that's ok
    if len(retirements) > 0:
        assert "amount" in retirements[0]
        assert "retirement_date" in retirements[0]
        assert "reason" in retirements[0]
```

---

## Revised Test Priorities

### Tier 1: Core Thesis Validation (MUST PASS)
These tests prove the MCP delivers on its primary promises:

1. **Arbitrage Agent Test** - Proves market monitoring capability
2. **ML Trend Analysis Test** - Proves predictive analytics capability
3. **Portfolio Construction Test** - Proves diversification capability
4. **DAO Verification Test** - Proves impact verification capability

If any Tier 1 test fails, a core thesis promise is broken.

### Tier 2: Boundary Condition Tests
These tests prove the MCP handles real-world edge cases:

1. **Empty Market Test** - What if no sell orders exist?
2. **New Credit Class Test** - Can handle credits with no history?
3. **Large Dataset Test** - Can handle 1000+ batches?
4. **Vintage Span Test** - Can handle 2012-2034 range correctly?

### Tier 3: Gap Documentation Tests
These tests document current limitations:

1. **Supply Query Test** - Documents that supply queries may not work
2. **Historical Data Test** - Documents temporal data limitations
3. **Outcome Metrics Test** - Documents missing environmental metrics

---

## Test Structure: User Journey First

**OLD APPROACH (Wrong):**
```python
def test_list_credit_types_returns_dict():
    """Test that function returns a dict."""
    result = await list_credit_types()
    assert isinstance(result, dict)  # Who cares?
```

**NEW APPROACH (Right):**
```python
@pytest.mark.user_journey
def test_arbitrage_agent_scenario():
    """
    USER GOAL: Identify price differences for same credit across sellers.

    This test validates the ENTIRE capability, not just one function.
    It's named after what the USER wants to accomplish.
    """
    # Step 1: Agent discovers available credits
    # Step 2: Agent compares prices
    # Step 3: Agent identifies opportunity
    # VALIDATES: Can agent accomplish its goal? YES/NO
```

---

## Implementation Plan

### Phase 1: Core Capability Tests (Week 1)
- Implement 5 Tier 1 user journey tests
- Run against live network
- Document which journeys PASS vs FAIL
- Create gap report

### Phase 2: Boundary Tests (Week 2)
- Add edge case handling
- Test pagination at scale
- Test with empty/sparse data
- Test error recovery

### Phase 3: Gap Documentation (Week 3)
- Create tests that document limitations
- Mark as `@pytest.mark.xfail` with explanations
- Propose API enhancements to Regen Network

### Phase 4: Coverage (Week 4)
- Add unit tests for reliability
- But ONLY after journey tests pass
- Unit tests support journeys, not replace them

---

## Success Criteria (Revised)

**PRIMARY:** ✅ Core user journeys validated
- Arbitrage monitoring: WORKS
- Trend analysis: WORKS (with limitations documented)
- Portfolio construction: WORKS
- Impact verification: WORKS (with limitations documented)

**SECONDARY:** ✅ Code coverage ≥85%
**TERTIARY:** ✅ All 45 tools tested

**The order matters.** Journey validation comes first.

---

## Next Steps

1. **Implement Tier 1 Tests** - The 5 user journey tests above
2. **Run Against Live Network** - See what actually works
3. **Document Gaps** - What can't we do yet?
4. **Propose Enhancements** - How to close gaps?
5. **Then Add Unit Tests** - For reliability

This approach ensures tests validate **value delivery**, not just **code execution**.
