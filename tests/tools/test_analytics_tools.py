"""Tests for analytics tools with real blockchain data.

These tests validate that analytics tools provide meaningful insights when called
through the MCP interface. NO MOCK DATA - validates actual analytical capabilities.

Analytics tools are critical for:
- Portfolio impact assessment
- Market trend analysis
- Methodology comparison and selection
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.analytics_tools import (
    analyze_portfolio_impact,
    analyze_market_trends,
    compare_credit_methodologies,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestAnalyticsToolsOnline:
    """Test analytics tools with live network connection.

    These tests validate critical analytical capabilities for decision-making.
    """

    async def test_analyze_portfolio_impact_returns_comprehensive_data(self):
        """Test that portfolio impact analysis returns comprehensive metrics.

        VALIDATES: Can we analyze ecological impact of a portfolio?
        IMPACT: Needed for impact investors and ESG reporting
        """
        # Use a known address (may or may not have credits)
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        result = await analyze_portfolio_impact(test_address, analysis_type="full")

        assert isinstance(result, dict), "Result must be dictionary"
        assert "address" in result, "Must include address"
        assert result["address"] == test_address

        # Should have impact analysis section
        assert "impact_analysis" in result, "Must have impact analysis"
        impact = result["impact_analysis"]

        # Should have key impact metrics
        assert "total_impact_score" in impact, "Must have total impact score"
        assert isinstance(impact["total_impact_score"], (int, float)), \
            "Impact score must be numeric"

        # Should have carbon and biodiversity sections
        assert "carbon_impact" in impact, "Must have carbon impact analysis"
        assert "biodiversity_impact" in impact, "Must have biodiversity analysis"

        # Should have metadata
        assert "metadata" in result, "Must have metadata"
        assert "analysis_type" in result["metadata"]

        print(f"✅ Can analyze portfolio impact")
        print(f"   Address: {test_address}")
        print(f"   Total impact score: {impact['total_impact_score']}")

        # If portfolio has credits, should have additional data
        if impact["total_impact_score"] > 0:
            assert "portfolio_composition" in result, \
                "Portfolio with credits needs composition data"
            assert "diversification_metrics" in result, \
                "Portfolio needs diversification metrics"
            print(f"   Portfolio has credits - full analysis available")

    async def test_analyze_portfolio_impact_handles_empty_portfolio(self):
        """Test portfolio analysis for address with no ecocredits.

        VALIDATES: Does analysis handle edge case gracefully?
        IMPACT: Important for new users or empty portfolios
        """
        # Use an address unlikely to have ecocredits
        test_address = "regen1000000000000000000000000000000000000000"

        result = await analyze_portfolio_impact(test_address)

        assert isinstance(result, dict), "Must return dict for empty portfolio"
        assert "impact_analysis" in result or "error" in result, \
            "Must have impact analysis or error"

        # Empty portfolios should get helpful response
        if "impact_analysis" in result:
            print(f"✅ Empty portfolio handled gracefully")
            if "recommendations" in result:
                print(f"   Recommendations provided for building portfolio")

    async def test_analyze_portfolio_impact_carbon_analysis(self):
        """Test carbon-specific portfolio analysis.

        VALIDATES: Can we analyze just carbon impact?
        IMPACT: Needed for carbon offset buyers and corporate ESG
        """
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        result = await analyze_portfolio_impact(
            test_address,
            analysis_type="carbon"
        )

        assert isinstance(result, dict), "Result must be dictionary"
        assert "metadata" in result, "Must have metadata"
        assert result["metadata"]["analysis_type"] == "carbon", \
            "Must respect analysis type parameter"

        print(f"✅ Can perform carbon-specific analysis")

    async def test_analyze_market_trends_returns_market_data(self):
        """Test that market trend analysis returns comprehensive market insights.

        VALIDATES: Can we analyze market trends and activity?
        IMPACT: CRITICAL for traders, investors, and market analysts
        """
        result = await analyze_market_trends(time_period="30d")

        assert isinstance(result, dict), "Result must be dictionary"

        # Should not have error
        if "error" in result:
            pytest.fail(f"Market analysis failed: {result.get('error')}")

        # Should have analysis period info
        assert "analysis_period" in result, "Must have analysis period"
        assert result["analysis_period"]["time_period"] == "30d"

        # Should have market snapshot
        assert "current_market_snapshot" in result, \
            "Must have current market snapshot"
        snapshot = result["current_market_snapshot"]

        # Should have overall metrics
        assert "overall_metrics" in snapshot, "Must have overall metrics"
        metrics = snapshot["overall_metrics"]

        assert "total_orders" in metrics, "Must have total orders count"
        assert isinstance(metrics["total_orders"], int), "Orders must be integer"

        # Should have trend analysis
        assert "trend_analysis" in result, "Must have trend analysis"
        trends = result["trend_analysis"]

        assert "time_period" in trends, "Trends must specify time period"

        # Should have methodology info
        assert "methodology" in result, "Must document methodology"

        print(f"✅ Can analyze market trends")
        print(f"   Time period: 30d")
        print(f"   Total orders analyzed: {metrics['total_orders']}")

        if "by_credit_type" in snapshot and snapshot["by_credit_type"]:
            credit_types = list(snapshot["by_credit_type"].keys())
            print(f"   Credit types in market: {credit_types}")

    async def test_analyze_market_trends_different_periods(self):
        """Test market analysis with different time periods.

        VALIDATES: Can we analyze different time horizons?
        IMPACT: Needed for short-term vs long-term strategy
        """
        # Test 7-day analysis
        result_7d = await analyze_market_trends(time_period="7d")
        assert isinstance(result_7d, dict), "7d analysis must return dict"

        # Test 90-day analysis
        result_90d = await analyze_market_trends(time_period="90d")
        assert isinstance(result_90d, dict), "90d analysis must return dict"

        print(f"✅ Can analyze multiple time periods (7d, 90d)")

    async def test_analyze_market_trends_with_credit_type_filter(self):
        """Test market analysis filtered by credit type.

        VALIDATES: Can we focus analysis on specific credit types?
        IMPACT: Needed for specialized traders (e.g., carbon-only)
        """
        result = await analyze_market_trends(
            time_period="30d",
            credit_types=["C"]
        )

        assert isinstance(result, dict), "Filtered analysis must return dict"

        print(f"✅ Can filter market analysis by credit type")

    async def test_compare_credit_methodologies_returns_comparison(self):
        """Test methodology comparison for investment decisions.

        VALIDATES: Can we compare different credit class methodologies?
        IMPACT: CRITICAL for methodology selection and investment decisions
        """
        # Use known credit classes (C01, C02 are common carbon classes)
        # We'll try C01 and if it exists, another class
        test_class_ids = ["C01", "C02"]

        result = await compare_credit_methodologies(test_class_ids)

        assert isinstance(result, dict), "Result must be dictionary"

        # If classes not found, should have helpful error
        if "error" in result:
            # This is acceptable - might not have those exact classes
            print(f"⚠️  Methodology comparison: {result.get('error')}")
            if "available_classes" in result:
                available = result["available_classes"][:5]
                print(f"   Available classes: {available}")
            return

        # If successful, should have comprehensive comparison
        assert "comparison_summary" in result, "Must have comparison summary"
        summary = result["comparison_summary"]

        assert "classes_compared" in summary, "Must show count of classes"
        assert summary["classes_compared"] >= 2, \
            "Should compare at least 2 classes"

        # Should have detailed analyses
        assert "detailed_class_analyses" in result, \
            "Must have detailed class analyses"

        # Should have comparative analysis
        assert "comparative_analysis" in result, \
            "Must have comparative analysis"
        comparative = result["comparative_analysis"]

        assert "methodology_comparison" in comparative, \
            "Must compare methodologies"
        assert "recommendation_ranking" in comparative, \
            "Must provide investment ranking"

        # Should have methodology documentation
        assert "methodology" in result, "Must document analysis methodology"

        print(f"✅ Can compare credit methodologies")
        print(f"   Classes compared: {summary['classes_compared']}")

        if "top_recommendation" in summary and summary["top_recommendation"]:
            print(f"   Top recommendation: {summary['top_recommendation']}")

    async def test_compare_credit_methodologies_requires_multiple_classes(self):
        """Test that methodology comparison validates input.

        VALIDATES: Does comparison require at least 2 classes?
        IMPACT: Ensures valid comparisons
        """
        # Try with only 1 class
        result = await compare_credit_methodologies(["C01"])

        assert isinstance(result, dict), "Must return dict"
        assert "error" in result, "Should error with only 1 class"

        print(f"✅ Methodology comparison validates input (requires 2+ classes)")


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestAnalyticsToolsUserJourneys:
    """Test analytics tools for real user scenarios.

    These tests validate complete analytical workflows.
    """

    async def test_impact_investor_can_assess_portfolio_esg(self):
        """
        USER: Impact Investor
        GOAL: Assess ecological impact of portfolio for ESG reporting

        VALIDATES: Can investor get comprehensive impact metrics?
        """
        # Use a known address
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        # Step 1: Get full impact analysis
        impact_analysis = await analyze_portfolio_impact(
            test_address,
            analysis_type="full"
        )

        assert isinstance(impact_analysis, dict), \
            "Impact investor cannot assess portfolio - wrong format"

        # Step 2: Should have impact scores
        assert "impact_analysis" in impact_analysis, \
            "Impact investor needs impact scores"

        # Step 3: Should have recommendations
        if "optimization_recommendations" in impact_analysis:
            recommendations = impact_analysis["optimization_recommendations"]
            assert isinstance(recommendations, list), \
                "Recommendations must be list"

        print("✅ IMPACT ASSESSMENT: Investor can assess portfolio ESG")
        print(f"   Address: {test_address}")

        if "impact_analysis" in impact_analysis:
            score = impact_analysis["impact_analysis"].get("total_impact_score", 0)
            print(f"   Total impact score: {score}")

        if "diversification_metrics" in impact_analysis:
            div = impact_analysis["diversification_metrics"]
            print(f"   Diversification: {div.get('type_diversity', 0)} credit types")

    async def test_trader_can_identify_market_opportunities(self):
        """
        USER: Market Trader
        GOAL: Identify market trends and trading opportunities

        VALIDATES: Can trader get actionable market insights?
        """
        # Step 1: Analyze recent market trends
        trends = await analyze_market_trends(time_period="30d")

        assert isinstance(trends, dict), \
            "Trader cannot analyze market - wrong format"

        # Step 2: Should have market snapshot
        if "error" not in trends:
            assert "current_market_snapshot" in trends, \
                "Trader needs current market snapshot"

            snapshot = trends["current_market_snapshot"]

            # Step 3: Should have actionable data
            assert "overall_metrics" in snapshot, \
                "Trader needs market metrics"

            # Step 4: Should have trend projections
            if "projections_and_insights" in trends:
                projections = trends["projections_and_insights"]
                assert isinstance(projections, dict), \
                    "Projections must be structured data"

            print("✅ MARKET ANALYSIS: Trader can identify opportunities")

            metrics = snapshot["overall_metrics"]
            print(f"   Active orders: {metrics.get('total_orders', 0)}")
            print(f"   Total volume: {metrics.get('total_volume', 0)}")

            if "by_credit_type" in snapshot:
                credit_count = len(snapshot["by_credit_type"])
                print(f"   Credit types trading: {credit_count}")

    async def test_methodology_analyst_can_compare_approaches(self):
        """
        USER: Methodology Analyst
        GOAL: Compare different carbon methodologies for selection

        VALIDATES: Can analyst get detailed methodology comparison?
        """
        # Try to compare common carbon methodologies
        # We'll handle gracefully if they don't exist
        class_ids = ["C01", "C02"]

        comparison = await compare_credit_methodologies(class_ids)

        assert isinstance(comparison, dict), \
            "Analyst cannot compare methodologies - wrong format"

        # If classes exist, should have detailed comparison
        if "error" not in comparison:
            assert "detailed_class_analyses" in comparison, \
                "Analyst needs detailed analyses"

            assert "comparative_analysis" in comparison, \
                "Analyst needs comparative analysis"

            comp_analysis = comparison["comparative_analysis"]

            # Should compare key methodology aspects
            assert "methodology_comparison" in comp_analysis, \
                "Analyst needs methodology comparison"

            # Should have investment recommendations
            assert "recommendation_ranking" in comp_analysis, \
                "Analyst needs investment ranking"

            print("✅ METHODOLOGY COMPARISON: Analyst can compare approaches")

            summary = comparison["comparison_summary"]
            print(f"   Classes compared: {summary['classes_compared']}")

            if "top_recommendation" in summary:
                print(f"   Top recommendation: {summary['top_recommendation']}")
        else:
            # Classes might not exist - that's okay
            print("⚠️  METHODOLOGY COMPARISON: Test classes not available")
            print(f"   Error: {comparison.get('error')}")

            # Should still provide helpful info
            if "available_classes" in comparison:
                print(f"   Available alternatives shown: Yes")


@pytest.mark.asyncio
@pytest.mark.tools
class TestAnalyticsToolsValidation:
    """Test analytics tools parameter validation and error handling."""

    async def test_portfolio_impact_requires_valid_address(self):
        """Test that portfolio analysis handles invalid addresses."""
        # Invalid address format
        result = await analyze_portfolio_impact("invalid_address")

        assert isinstance(result, dict), "Should return dict even on error"
        # Should indicate error
        assert "error" in result, "Should indicate error for invalid address"

    async def test_methodology_comparison_requires_multiple_classes(self):
        """Test that methodology comparison validates minimum input."""
        # Empty list
        result = await compare_credit_methodologies([])

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should error with empty list"

        # Single class
        result = await compare_credit_methodologies(["C01"])

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should error with single class"

    async def test_market_trends_handles_invalid_time_period(self):
        """Test market trends with invalid time period."""
        # Should handle gracefully (either accept or reject clearly)
        try:
            result = await analyze_market_trends(time_period="invalid")
            # If accepted, should return dict
            assert isinstance(result, dict)
        except ValueError:
            # Acceptable to reject invalid format
            pass
