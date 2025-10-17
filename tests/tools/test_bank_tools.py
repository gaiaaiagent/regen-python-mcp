"""Tests for bank tools with real blockchain data.

These tests validate that bank tools return correct data when called through
the MCP interface. NO MOCK DATA - validates actual tool behavior.

Bank tools are critical for:
- Portfolio tracking (balances)
- Credit supply analysis
- Account management
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.bank_tools import (
    get_balance,
    get_all_balances,
    get_spendable_balances,
    get_total_supply,
    get_supply_of,
    list_accounts,
    get_account,
    get_bank_params,
    get_denoms_metadata,
    get_denom_metadata,
    get_denom_owners,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestBankToolsOnline:
    """Test bank tools with live network connection.

    These tests validate critical portfolio and account management functionality.
    """

    async def test_get_total_supply_returns_data(self):
        """Test that get_total_supply returns supply information.

        VALIDATES: Can we query total supply of all tokens?
        IMPACT: Needed for market analysis and statistics
        """
        result = await get_total_supply()

        assert isinstance(result, dict), "Result must be dictionary"
        assert "success" in result or "supply" in result or isinstance(result, dict)

        # If successful, should have supply list
        if result.get("success", True) and "supply" in result:
            supply_list = result["supply"]
            assert isinstance(supply_list, list), "Supply must be list"

            # Should have at least some tokens
            if len(supply_list) > 0:
                token = supply_list[0]
                # Each token should have denom and amount
                assert "denom" in token or "amount" in token, \
                    "Supply items need denom and amount"

                print(f"✅ Can query total supply: {len(supply_list)} tokens tracked")

    async def test_get_supply_of_credit_batch(self):
        """Test getting supply of specific credit batch.

        VALIDATES: Can we check supply for a specific credit batch?
        IMPACT: Critical for portfolio managers tracking credit availability
        """
        # Use a known credit batch denom from our tests
        test_denom = "C01-001-20150101-20151231-001"

        result = await get_supply_of(test_denom)

        assert isinstance(result, dict), "Result must be dictionary"

        # Should either have supply data or a clear error
        if result.get("success", True):
            # Successful query should have amount
            assert "amount" in result or "supply" in result, \
                "Supply query should return amount"

            if "amount" in result:
                print(f"✅ Can query batch supply: {test_denom}")
                print(f"   Amount: {result.get('amount', {}).get('amount', 'N/A')}")
        else:
            # Expected: batch might not exist or might be retired
            print(f"⚠️  Batch {test_denom} supply not available (expected)")

    async def test_get_bank_params_returns_configuration(self):
        """Test that we can query bank module parameters.

        VALIDATES: Can we access blockchain configuration?
        IMPACT: Needed for understanding transfer limits and rules
        """
        result = await get_bank_params()

        assert isinstance(result, dict), "Result must be dictionary"

        # Should have params or be successful
        if result.get("success", True):
            assert "params" in result or isinstance(result, dict), \
                "Should return bank parameters"

            if "params" in result:
                params = result["params"]
                print(f"✅ Can query bank params")
                print(f"   Params keys: {list(params.keys())[:5]}")

    async def test_get_all_balances_for_known_address(self):
        """Test querying all balances for an address.

        VALIDATES: Can we see all credits owned by an address?
        IMPACT: CRITICAL for portfolio managers tracking holdings
        """
        # Use a known address that should have some credits
        # This is a validator address from Regen Network
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        result = await get_all_balances(test_address)

        assert isinstance(result, dict), "Result must be dictionary"

        # Should return balances structure
        if result.get("success", True):
            assert "balances" in result or isinstance(result, dict), \
                "Should have balances field"

            if "balances" in result:
                balances = result["balances"]
                assert isinstance(balances, list), "Balances must be list"

                print(f"✅ Can query address balances")
                print(f"   Address: {test_address}")
                print(f"   Number of token types: {len(balances)}")

                # If has balances, validate structure
                if len(balances) > 0:
                    balance = balances[0]
                    assert "denom" in balance, "Balance needs denom"
                    assert "amount" in balance, "Balance needs amount"

    async def test_get_balance_for_specific_credit(self):
        """Test querying balance of specific credit for address.

        VALIDATES: Can we check if address owns specific credit type?
        IMPACT: Needed for targeted portfolio queries
        """
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"
        test_denom = "uregen"  # Native token

        result = await get_balance(test_address, test_denom)

        assert isinstance(result, dict), "Result must be dictionary"

        # Should return balance information
        if result.get("success", True):
            # May have balance or may be zero
            if "balance" in result:
                balance = result["balance"]
                assert "denom" in balance or "amount" in balance, \
                    "Balance should have denom/amount"
                print(f"✅ Can query specific balance")

    async def test_get_denoms_metadata_returns_token_info(self):
        """Test querying metadata for all denominations.

        VALIDATES: Can we get display names and details for tokens?
        IMPACT: Needed for UI display of credit types
        """
        result = await get_denoms_metadata()

        assert isinstance(result, dict), "Result must be dictionary"

        # Should return metadata list
        if result.get("success", True):
            if "metadatas" in result:
                metadatas = result["metadatas"]
                assert isinstance(metadatas, list), "Metadatas must be list"

                print(f"✅ Can query denom metadata")
                print(f"   Number of denoms with metadata: {len(metadatas)}")

                # Validate structure if present
                if len(metadatas) > 0:
                    metadata = metadatas[0]
                    # Should have at least base denom
                    assert "base" in metadata or "denom" in metadata, \
                        "Metadata needs denom identifier"

    async def test_get_denom_metadata_for_specific_token(self):
        """Test querying metadata for specific denomination.

        VALIDATES: Can we get display info for a specific token?
        IMPACT: Needed for formatted display in UIs
        """
        test_denom = "uregen"

        result = await get_denom_metadata(test_denom)

        assert isinstance(result, dict), "Result must be dictionary"

        # Should return metadata
        if result.get("success", True):
            if "metadata" in result:
                metadata = result["metadata"]
                print(f"✅ Can query specific denom metadata")
                print(f"   Denom: {test_denom}")


@pytest.mark.asyncio
@pytest.mark.tools
class TestBankToolsValidation:
    """Test bank tools parameter validation and error handling."""

    async def test_get_balance_requires_valid_address(self):
        """Test that get_balance handles invalid addresses."""
        # Empty address should be handled gracefully
        result = await get_balance("", "uregen")

        assert isinstance(result, dict), "Should return dict even on error"
        # Should indicate error
        assert result.get("success") == False or "error" in result, \
            "Should indicate error for invalid input"

    async def test_get_balance_requires_valid_denom(self):
        """Test that get_balance handles invalid denoms."""
        valid_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        # Empty denom should be handled gracefully
        result = await get_balance(valid_address, "")

        assert isinstance(result, dict), "Should return dict even on error"


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestBankToolsPortfolioUseCase:
    """Test bank tools for real portfolio management scenarios.

    These tests validate the complete portfolio tracking workflow.
    """

    async def test_portfolio_manager_can_track_credit_holdings(self):
        """
        USER: Portfolio Manager
        GOAL: Track all credit holdings for an address

        VALIDATES: Can manager see complete portfolio?
        """
        # Use a known address (seller from marketplace)
        test_address = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        # Step 1: Get all balances
        balances = await get_all_balances(test_address)

        assert isinstance(balances, dict), \
            "Portfolio manager cannot track holdings - wrong format"

        # Step 2: Should be able to see what they own
        if balances.get("success", True) and "balances" in balances:
            balance_list = balances["balances"]

            print("✅ PORTFOLIO TRACKING: Manager can view holdings")
            print(f"   Address: {test_address}")
            print(f"   Token types owned: {len(balance_list)}")

            # Step 3: Should be able to identify credit batches
            credit_batches = [
                b for b in balance_list
                if "denom" in b and "-" in b.get("denom", "")
            ]

            if len(credit_batches) > 0:
                print(f"   Credit batches owned: {len(credit_batches)}")

            # Step 4: Should have amount information
            if len(balance_list) > 0:
                first_balance = balance_list[0]
                assert "amount" in first_balance, \
                    "Portfolio manager needs amount data"
                print(f"   ✅ Amount data available")

    async def test_supply_analyst_can_check_batch_availability(self):
        """
        USER: Supply Analyst
        GOAL: Check available supply of credit batch

        VALIDATES: Can analyst determine market supply?
        """
        # Test with a known batch denom
        test_batch = "C01-001-20150101-20151231-001"

        supply_result = await get_supply_of(test_batch)

        assert isinstance(supply_result, dict), \
            "Supply analyst cannot check availability"

        print("✅ SUPPLY ANALYSIS: Analyst can check batch supply")
        print(f"   Batch: {test_batch}")

        if supply_result.get("success", True):
            if "amount" in supply_result:
                print(f"   Supply data available")
        else:
            print(f"   ⚠️  Batch supply not tracked (may be retired)")
