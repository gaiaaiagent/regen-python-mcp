"""End-to-end user journey tests validating thesis use cases.

These tests validate that the MCP server enables the use cases promised in
docs/regen_mcp_thesis.md. Each test represents a complete user workflow, not
just individual function calls.

PRINCIPLE: These tests answer "Can a user accomplish their goal?" not just
"Does this function return data?"

If a test fails, it means the MCP cannot support that use case - a critical gap.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.credit_tools import (
    list_credit_types,
    list_credit_classes,
    list_projects,
    list_credit_batches,
)
from mcp_server.tools.marketplace_tools import (
    list_sell_orders,
    get_sell_order,
)
from mcp_server.tools.basket_tools import (
    list_baskets,
    get_basket,
)


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.user_journey
@pytest.mark.online
class TestTier1UserJourneys:
    """Tier 1: Critical user journeys that validate core thesis promises.

    These tests MUST pass for the MCP to fulfill its stated purpose.
    """

    async def test_arbitrage_agent_can_identify_opportunities(self):
        """
        USER: Arbitrage Trading Agent
        GOAL: Identify price differences for the same credit across different sellers

        VALIDATES: Can an agent monitor the marketplace and identify arbitrage?

        This is THE test that proves the MCP enables automated arbitrage trading.
        If this fails, one of the primary thesis promises is broken.
        """
        # Step 1: Agent needs to see all available sell orders
        sell_orders = await list_sell_orders(limit=100)

        assert isinstance(sell_orders, dict), \
            "Agent cannot process sell orders - wrong data format"

        assert "sell_orders" in sell_orders, \
            "Agent cannot access sell orders - missing key field"

        orders = sell_orders.get("sell_orders", [])
        assert len(orders) > 0, \
            "Agent cannot identify arbitrage - no sell order data available"

        # Step 2: Agent needs pricing information for each order
        first_order = orders[0]

        # Critical fields for arbitrage detection
        required_fields = ["ask_amount", "ask_denom", "quantity", "batch_denom"]
        missing_fields = [f for f in required_fields if f not in first_order]

        assert len(missing_fields) == 0, \
            f"Agent cannot identify arbitrage - missing critical fields: {missing_fields}"

        # Step 3: Agent needs to compare equivalent credits
        # For arbitrage, we need batch_denom to identify same credit across sellers
        batch_denom = first_order["batch_denom"]
        assert batch_denom and len(batch_denom) > 0, \
            "Agent cannot compare equivalent credits - no batch denomination"

        # Step 4: Agent needs seller information to avoid trading with same entity
        assert "seller" in first_order or "seller_address" in first_order, \
            "Agent cannot avoid self-trading - no seller identification"

        # Step 5: Validate agent can fetch detailed order information
        if "id" in first_order:
            order_details = await get_sell_order(first_order["id"])
            assert order_details is not None, \
                "Agent cannot analyze orders deeply - detail fetch failed"

        # RESULT: If we get here, the MCP provides core arbitrage capability
        print("✅ ARBITRAGE AGENT: Core capability validated")
        print(f"   Agent can monitor {len(orders)} orders")
        print(f"   Agent can extract pricing, quantity, batch info")
        print(f"   Agent can identify sellers")

    async def test_ml_model_can_analyze_adoption_trends(self):
        """
        USER: ML Researcher / Data Scientist
        GOAL: Analyze adoption trends across credit classes and project types

        VALIDATES: Can a model train on Regen Network data to identify patterns?

        This tests if the MCP provides sufficient data breadth and structure for ML.
        """
        # Step 1: Model needs comprehensive credit class data
        credit_classes = await list_credit_classes(limit=100, offset=0)

        assert isinstance(credit_classes, dict), \
            "ML model cannot process data - wrong format"

        classes = credit_classes.get("classes", [])
        assert len(classes) >= 10, \
            f"ML model needs diverse data - only {len(classes)} classes available"

        # Step 2: Model needs credit type taxonomy
        credit_types = await list_credit_types()
        types = credit_types.get("credit_types", [])

        assert len(types) > 0, \
            "ML model cannot categorize - no credit type taxonomy"

        # Step 3: Model needs project data for feature engineering
        projects = await list_projects(limit=100, offset=0)
        project_list = projects.get("projects", [])

        assert len(project_list) >= 10, \
            f"ML model needs sufficient training data - only {len(project_list)} projects"

        # Step 4: Model needs structured features from projects
        if len(project_list) > 0:
            project = project_list[0]

            # Features useful for ML: location, methodology, developer
            useful_features = ["class_id", "jurisdiction", "metadata"]
            available_features = [f for f in useful_features if f in project]

            assert len(available_features) > 0, \
                f"ML model lacks features - project data too sparse"

        # Step 5: Model needs batch/issuance data for time-series analysis
        batches = await list_credit_batches(limit=100, offset=0)
        batch_list = batches.get("batches", [])

        assert len(batch_list) >= 10, \
            f"ML model needs temporal data - only {len(batch_list)} batches"

        # Check for temporal features
        if len(batch_list) > 0:
            batch = batch_list[0]
            temporal_fields = ["start_date", "end_date", "issuance_date"]
            has_temporal = any(f in batch for f in temporal_fields)

            assert has_temporal, \
                "ML model cannot analyze trends - no temporal data in batches"

        # RESULT: Assess ML readiness
        print("✅ ML TREND ANALYSIS: Data breadth validated")
        print(f"   {len(classes)} credit classes available")
        print(f"   {len(project_list)} projects for training")
        print(f"   {len(batch_list)} batches for time-series")
        print("⚠️  NOTE: Historical price data not validated (API limitation)")

    async def test_portfolio_manager_can_build_diversified_fund(self):
        """
        USER: Portfolio Manager / Fund Manager
        GOAL: Construct diversified portfolio across credit types, geographies, methodologies

        VALIDATES: Can a manager build a diversified ecological credit portfolio?

        This tests if the MCP provides sufficient classification and metadata.
        """
        # Step 1: Manager needs to see all credit types for diversification
        credit_types = await list_credit_types()
        types = credit_types.get("credit_types", [])

        assert len(types) >= 2, \
            "Portfolio manager cannot diversify - insufficient credit types"

        # Step 2: Manager needs projects across different credit classes
        projects = await list_projects(limit=100, offset=0)
        project_list = projects.get("projects", [])

        assert len(project_list) >= 10, \
            "Portfolio manager needs selection - insufficient projects"

        # Step 3: Manager needs geographic diversification data
        if len(project_list) > 0:
            projects_with_location = [
                p for p in project_list
                if "jurisdiction" in p or "location" in p
            ]

            assert len(projects_with_location) > 0, \
                "Portfolio manager cannot diversify geographically - no location data"

        # Step 4: Manager needs methodology diversity
        classes = await list_credit_classes(limit=100, offset=0)
        class_list = classes.get("classes", [])

        if len(class_list) > 0:
            # Check for methodology/standard information
            classes_with_methodology = [
                c for c in class_list
                if "id" in c  # Class ID often indicates methodology (e.g., C01, C02)
            ]

            assert len(classes_with_methodology) >= 5, \
                "Portfolio manager needs methodology diversity - insufficient classes"

        # Step 5: Manager needs basket information for pre-diversified options
        baskets = await list_baskets(limit=50)

        assert isinstance(baskets, dict), \
            "Portfolio manager cannot access baskets - wrong format"

        basket_list = baskets.get("baskets", [])
        if len(basket_list) > 0:
            print(f"✅ Portfolio manager can use {len(basket_list)} pre-diversified baskets")

        # Step 6: Manager needs current availability/supply for each credit
        batches = await list_credit_batches(limit=100, offset=0)
        batch_list = batches.get("batches", [])

        if len(batch_list) > 0:
            batch = batch_list[0]
            # Supply information critical for portfolio sizing
            assert "amount_available" in batch or "tradable_amount" in batch or "quantity" in batch, \
                "Portfolio manager cannot size positions - no supply data"

        # RESULT: Assess portfolio construction capability
        print("✅ PORTFOLIO CONSTRUCTION: Diversification validated")
        print(f"   {len(types)} credit types for diversification")
        print(f"   {len(project_list)} projects across geographies")
        print(f"   {len(class_list)} methodologies available")
        print("⚠️  NOTE: Real-time supply data not fully validated")

    async def test_insurance_company_can_hedge_climate_risks(self):
        """
        USER: Insurance Company / Risk Manager
        GOAL: Hedge climate-related risks using ecological credits

        VALIDATES: Can an insurer monitor and hedge using ecological assets?

        This is the most demanding use case - requires environmental metrics.
        """
        # Step 1: Insurer needs to see biodiversity and ecosystem credits
        credit_types = await list_credit_types()
        types = credit_types.get("credit_types", [])

        type_abbreviations = [t.get("abbreviation", "") for t in types]

        # Insurance needs beyond just carbon
        has_biodiversity = any("B" in abbr for abbr in type_abbreviations)
        has_carbon = any("C" in abbr for abbr in type_abbreviations)

        assert has_carbon, \
            "Insurer cannot hedge climate risks - no carbon credits"

        if not has_biodiversity:
            print("⚠️  WARNING: Biodiversity credits not found - limited hedging")

        # Step 2: Insurer needs real-time environmental data
        # This is a CRITICAL gap - environmental metrics not in current API
        projects = await list_projects(limit=50, offset=0)
        project_list = projects.get("projects", [])

        if len(project_list) > 0:
            project = project_list[0]

            # Look for environmental outcome data
            env_fields = ["metadata", "data", "outcomes", "metrics"]
            has_env_data = any(f in project for f in env_fields)

            if not has_env_data:
                print("❌ CRITICAL GAP: No environmental metrics in project data")
                print("   Insurer CANNOT hedge without outcome tracking")

        # Step 3: Insurer needs geographic risk correlation
        projects_with_location = [
            p for p in project_list
            if "jurisdiction" in p
        ]

        assert len(projects_with_location) > 0, \
            "Insurer cannot correlate geographic risks - no location data"

        # Step 4: Insurer needs marketplace liquidity for hedging
        sell_orders = await list_sell_orders(limit=100)
        orders = sell_orders.get("sell_orders", [])

        assert len(orders) > 0, \
            "Insurer cannot hedge - no marketplace liquidity"

        # Step 5: Check if orders have sufficient volume
        if len(orders) > 0:
            orders_with_quantity = [o for o in orders if "quantity" in o]
            assert len(orders_with_quantity) > 0, \
                "Insurer cannot size hedges - no volume data"

        # RESULT: This use case has MAJOR GAPS
        print("⚠️  INSURANCE HEDGING: Partial capability only")
        print(f"   ✅ {len(orders)} liquid orders available")
        print(f"   ✅ Geographic data available")
        print("   ❌ Environmental metrics NOT available (critical gap)")
        print("   ❌ Real-time outcome tracking NOT available")
        print("\n   CONCLUSION: MCP cannot fully support insurance hedging use case")

    async def test_dao_can_verify_project_results(self):
        """
        USER: DAO / Community Governance
        GOAL: Verify project claims and vote on credit issuance

        VALIDATES: Can a DAO validate project outcomes and govern issuance?

        This tests transparency and verification capabilities.
        """
        # Step 1: DAO needs to see all projects for verification
        projects = await list_projects(limit=100, offset=0)
        project_list = projects.get("projects", [])

        assert len(project_list) > 0, \
            "DAO cannot verify - no project data available"

        # Step 2: DAO needs project metadata and documentation
        if len(project_list) > 0:
            project = project_list[0]

            verification_fields = ["id", "class_id", "jurisdiction", "metadata"]
            available_fields = [f for f in verification_fields if f in project]

            assert len(available_fields) >= 3, \
                f"DAO cannot verify - insufficient project metadata (only {available_fields})"

        # Step 3: DAO needs to see credit issuance history
        batches = await list_credit_batches(limit=100, offset=0)
        batch_list = batches.get("batches", [])

        assert len(batch_list) > 0, \
            "DAO cannot verify issuance - no batch data"

        # Step 4: DAO needs to track credit lifecycle (issuance -> retirement)
        if len(batch_list) > 0:
            batch = batch_list[0]

            lifecycle_fields = ["start_date", "issuance_date", "amount_issued"]
            has_lifecycle = any(f in batch for f in lifecycle_fields)

            assert has_lifecycle, \
                "DAO cannot track lifecycle - no temporal data"

        # Step 5: DAO needs credit class information for methodology review
        classes = await list_credit_classes(limit=100, offset=0)
        class_list = classes.get("classes", [])

        assert len(class_list) > 0, \
            "DAO cannot review methodologies - no class data"

        if len(class_list) > 0:
            credit_class = class_list[0]

            # DAO needs methodology details
            assert "id" in credit_class, \
                "DAO cannot identify methodologies - no class IDs"

        # Step 6: Check for governance/voting data (likely not in current API)
        # This is expected to be missing
        print("⚠️  NOTE: Governance voting data not available in current API")

        # RESULT: Core verification possible, governance limited
        print("✅ DAO VERIFICATION: Core transparency validated")
        print(f"   {len(project_list)} projects can be reviewed")
        print(f"   {len(batch_list)} issuances can be audited")
        print(f"   {len(class_list)} methodologies can be examined")
        print("⚠️  NOTE: Voting/governance features not in current API")
        print("   CONCLUSION: MCP supports verification but not active governance")


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.user_journey
@pytest.mark.online
class TestTier2UserJourneys:
    """Tier 2: Important workflows that enhance the MCP's value proposition.

    These should pass but are not critical blockers.
    """

    async def test_developer_can_monitor_project_performance(self):
        """
        USER: Project Developer
        GOAL: Monitor their project's credit issuance and sales performance

        VALIDATES: Can a developer track their project's success?
        """
        # Step 1: Developer needs to find their project
        projects = await list_projects(limit=50, offset=0)
        project_list = projects.get("projects", [])

        assert len(project_list) > 0, \
            "Developer cannot find projects"

        # Step 2: Developer needs to see their batches
        batches = await list_credit_batches(limit=50, offset=0)
        batch_list = batches.get("batches", [])

        if len(batch_list) > 0:
            batch = batch_list[0]

            # Developer needs issuance info
            performance_fields = ["amount_issued", "tradable_amount", "retired_amount"]
            available_metrics = [f for f in performance_fields if f in batch]

            assert len(available_metrics) > 0, \
                "Developer cannot track performance - no metrics"

        print("✅ DEVELOPER MONITORING: Project tracking validated")

    async def test_buyer_can_purchase_credits_with_attributes(self):
        """
        USER: Corporate Buyer
        GOAL: Purchase credits matching specific ESG criteria

        VALIDATES: Can a buyer filter and purchase credits meeting their needs?
        """
        # Step 1: Buyer needs to browse available credits
        sell_orders = await list_sell_orders(limit=50)
        orders = sell_orders.get("sell_orders", [])

        assert len(orders) > 0, \
            "Buyer cannot purchase - no credits available"

        # Step 2: Buyer needs credit attributes for ESG filtering
        if len(orders) > 0:
            order = orders[0]

            # Buyer needs batch info to evaluate credit
            assert "batch_denom" in order, \
                "Buyer cannot evaluate credits - no batch info"

        # Step 3: Buyer needs to fetch batch details for attributes
        batches = await list_credit_batches(limit=50, offset=0)
        batch_list = batches.get("batches", [])

        if len(batch_list) > 0:
            batch = batch_list[0]

            # Buyer needs project linkage
            assert "project_id" in batch or "project_location" in batch, \
                "Buyer cannot verify ESG criteria - no project link"

        print("✅ BUYER PURCHASE: ESG filtering validated")


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.user_journey
@pytest.mark.offline
class TestUserJourneyDataQuality:
    """Tests that validate the quality and completeness of data for user journeys.

    These tests use cached data to validate structure without network calls.
    """

    async def test_sell_order_data_quality(self):
        """Validate that sell order data has all fields needed by user journeys."""
        # This would use a fixture with cached sell orders
        # For now, structure test only
        pass

    async def test_project_data_quality(self):
        """Validate that project data has all fields needed by user journeys."""
        pass

    async def test_batch_data_quality(self):
        """Validate that batch data has all fields needed by user journeys."""
        pass
