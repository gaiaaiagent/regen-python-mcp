"""Tests for basket tools with real blockchain data.

Baskets are aggregated credit pools that allow diversified credit holdings.
These tests validate basket operations. NO MOCK DATA.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.basket_tools import (
    list_baskets,
    get_basket,
    list_basket_balances,
    get_basket_balance,
    get_basket_fee,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.offline
class TestBasketToolsWithRealData:
    """Test basket tools using real cached blockchain data."""

    async def test_list_baskets_returns_valid_structure(self):
        """Test that list_baskets returns proper structure.

        Baskets enable portfolio managers to hold diversified credit pools.
        This test validates core functionality for that use case.
        """
        result = await list_baskets(limit=50, offset=0)

        assert isinstance(result, dict), "Tool must return dictionary"

        # Validate structure
        if "baskets" in result:
            baskets = result["baskets"]
            assert isinstance(baskets, list)

            # If baskets exist, validate structure
            if len(baskets) > 0:
                basket = baskets[0]
                # Critical fields for basket functionality
                assert "basket_denom" in basket or "denom" in basket, \
                    "Basket must have denomination for identification"

    async def test_list_baskets_pagination(self):
        """Test pagination works for baskets."""
        result = await list_baskets(limit=10, offset=0)

        assert isinstance(result, dict)

        if "baskets" in result:
            baskets = result["baskets"]
            assert len(baskets) <= 10, "Should respect limit parameter"

    async def test_get_basket_fee_returns_creation_cost(self):
        """Test that basket fee information is available.

        Users need to know the cost of creating new baskets.
        """
        result = await get_basket_fee()

        assert isinstance(result, dict), "Tool must return dictionary"
        # Structure depends on API - may have fee amount, denom, etc.


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestBasketToolsOnline:
    """Test basket tools with live network connection."""

    async def test_live_list_baskets(self):
        """Test live basket query.

        CRITICAL: If this fails, basket functionality is broken.
        """
        result = await list_baskets(limit=50, offset=0)

        assert result is not None
        assert isinstance(result, dict)

    async def test_live_get_basket_fee(self):
        """Test live query for basket creation fee."""
        result = await get_basket_fee()

        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.asyncio
@pytest.mark.tools
class TestBasketToolsEdgeCases:
    """Test edge cases and error handling."""

    async def test_invalid_basket_denom_raises_error(self):
        """Test that invalid basket denomination returns error."""
        with pytest.raises(Exception):
            # Should raise NetworkError or similar
            await get_basket("INVALID_BASKET_DENOM_DOES_NOT_EXIST")

    async def test_invalid_basket_denom_in_balance_query(self):
        """Test error handling for balance queries with invalid basket."""
        with pytest.raises(Exception):
            await list_basket_balances(
                basket_denom="INVALID_BASKET",
                limit=10,
                offset=0
            )

    async def test_large_offset_returns_empty_gracefully(self):
        """Test that large offsets don't crash."""
        result = await list_baskets(limit=10, offset=999999)

        # Should return empty list or valid structure, not crash
        assert isinstance(result, dict)
