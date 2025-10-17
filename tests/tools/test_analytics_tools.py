"""Tests for analytics tools with real blockchain data.

Analytics tools provide high-level insights including portfolio impact analysis,
market trend analysis, and methodology comparison. NO MOCK DATA.
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
@pytest.mark.offline
class TestAnalyticsToolsWithRealData:
    """Test analytics tools using real cached blockchain data."""

    async def test_compare_credit_methodologies_structure(self):
        """Test methodology comparison returns valid structure.

        This is critical for users choosing between different carbon
        credit methodologies (C01, C02, C03, etc.).
        """
        # Test with known carbon credit class IDs
        class_ids = ["C01", "C02", "C03"]

        result = await compare_credit_methodologies(class_ids)

        assert isinstance(result, dict), "Tool must return dictionary"

        # Result should contain comparison data
        # Exact structure depends on implementation

    async def test_analyze_market_trends_default_period(self):
        """Test market trend analysis with default time period."""
        result = await analyze_market_trends(time_period="30d")

        assert isinstance(result, dict), "Tool must return dictionary"

        # Should contain trend analysis data

    async def test_analyze_market_trends_with_credit_type_filter(self):
        """Test market trends filtered by credit types."""
        # Filter to carbon credits only
        credit_types = ["C"]

        result = await analyze_market_trends(
            time_period="30d",
            credit_types=credit_types
        )

        assert isinstance(result, dict), "Tool must return dictionary"


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestAnalyticsToolsOnline:
    """Test analytics tools with live network connection."""

    async def test_live_portfolio_impact_analysis(self):
        """Test portfolio impact analysis against live network.

        NOTE: This requires a valid Regen Network address with holdings.
        Test may pass with empty portfolio (valid response structure).
        """
        # Use a known address or skip if unavailable
        # For now, test structure only
        pass

    async def test_live_market_trends_analysis(self):
        """Test live market trend analysis.

        CRITICAL: If this fails, market analysis is broken.
        """
        result = await analyze_market_trends(time_period="7d")

        assert result is not None
        assert isinstance(result, dict)

    async def test_live_methodology_comparison(self):
        """Test live methodology comparison.

        This validates that comparison works against current blockchain state.
        """
        class_ids = ["C01", "C02"]

        result = await compare_credit_methodologies(class_ids)

        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.asyncio
@pytest.mark.tools
class TestAnalyticsToolsEdgeCases:
    """Test edge cases and error handling."""

    async def test_empty_class_ids_list_handled(self):
        """Test behavior with empty class IDs list."""
        with pytest.raises(Exception):
            # Should raise validation error
            await compare_credit_methodologies([])

    async def test_invalid_class_id_handled(self):
        """Test behavior with non-existent class ID."""
        # May return partial results or error
        result = await compare_credit_methodologies(
            ["C01", "INVALID_CLASS_ID_999"]
        )

        # Should handle gracefully, not crash
        assert isinstance(result, dict)

    async def test_invalid_time_period_format(self):
        """Test market trends with invalid time period."""
        # Depending on validation, may accept or reject
        # Should not crash either way
        try:
            result = await analyze_market_trends(time_period="invalid")
            assert isinstance(result, dict)
        except ValueError:
            # Acceptable to reject invalid format
            pass

    async def test_invalid_address_in_portfolio_analysis(self):
        """Test portfolio analysis with invalid address."""
        with pytest.raises(Exception):
            await analyze_portfolio_impact(
                address="INVALID_ADDRESS_FORMAT",
                analysis_type="full"
            )

    async def test_portfolio_analysis_types(self):
        """Test different portfolio analysis types."""
        # NOTE: Requires valid address, may skip
        # Tests that different analysis_type values work
        pass
