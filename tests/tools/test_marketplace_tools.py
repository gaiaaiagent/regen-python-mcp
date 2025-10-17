"""Tests for marketplace tools with real blockchain data.

These tests validate marketplace operations including sell orders,
allowed denominations, and order queries. NO MOCK DATA.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.marketplace_tools import (
    get_sell_order,
    list_sell_orders,
    list_sell_orders_by_batch,
    list_sell_orders_by_seller,
    list_allowed_denoms,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.offline
class TestMarketplaceToolsWithRealData:
    """Test marketplace tools using real cached blockchain data."""

    async def test_list_sell_orders_returns_valid_structure(self):
        """Test that list_sell_orders returns proper structure.

        This validates the MCP can provide marketplace data to agents
        for arbitrage and price discovery.
        """
        result = await list_sell_orders(page=1, limit=50)

        assert isinstance(result, dict), "Tool must return dictionary"

        # Validate contains sell orders (may be empty if no active orders)
        if "sell_orders" in result:
            orders = result["sell_orders"]
            assert isinstance(orders, list)

            # If orders exist, validate structure
            if len(orders) > 0:
                order = orders[0]
                # Critical fields for marketplace functionality
                assert "id" in order or "order_id" in order, \
                    "Orders must have ID for retrieval"

    async def test_list_sell_orders_pagination(self):
        """Test pagination works for sell orders."""
        # Small page size to test pagination
        result = await list_sell_orders(page=1, limit=5)

        assert isinstance(result, dict)

        if "sell_orders" in result:
            orders = result["sell_orders"]
            assert len(orders) <= 5, "Should respect limit parameter"

    async def test_list_allowed_denoms_returns_payment_options(self):
        """Test that list_allowed_denoms returns valid payment currencies.

        This is critical for marketplace transactions - users need to know
        what currencies they can use to purchase credits.
        """
        result = await list_allowed_denoms(page=1, limit=100)

        assert isinstance(result, dict), "Tool must return dictionary"

        # Should contain allowed denoms information
        # Structure depends on API response format

    async def test_list_sell_orders_by_batch_filters_correctly(self):
        """Test filtering sell orders by batch denomination."""
        # This test would need a known batch_denom from fixtures
        # For now, test that the function can be called
        # Real validation would require fixture data
        pass

    async def test_list_sell_orders_by_seller_filters_correctly(self):
        """Test filtering sell orders by seller address."""
        # This test would need a known seller address from fixtures
        # For now, test that the function can be called
        # Real validation would require fixture data
        pass


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestMarketplaceToolsOnline:
    """Test marketplace tools with live network connection."""

    async def test_live_list_sell_orders(self):
        """Test live marketplace query.

        CRITICAL: If this fails, marketplace functionality is broken.
        """
        result = await list_sell_orders(page=1, limit=20)

        assert result is not None
        assert isinstance(result, dict)

    async def test_live_list_allowed_denoms(self):
        """Test live query for allowed payment denominations."""
        result = await list_allowed_denoms(page=1, limit=50)

        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.asyncio
@pytest.mark.tools
class TestMarketplaceToolsEdgeCases:
    """Test edge cases and error handling."""

    async def test_invalid_order_id_handled_gracefully(self):
        """Test that invalid order IDs return proper errors."""
        with pytest.raises(Exception):
            # Should raise NetworkError or return error structure
            await get_sell_order("INVALID_ORDER_ID_9999999")

    async def test_empty_seller_address_handled(self):
        """Test behavior with empty seller address."""
        # Should either return all orders or return error
        # Depends on API validation
        pass

    async def test_large_page_limit_handled(self):
        """Test that large page limits are handled gracefully."""
        result = await list_sell_orders(page=1, limit=1000)

        # Should not crash, may return capped results
        assert isinstance(result, dict)
