#!/usr/bin/env python3
"""
Modular Regen Network MCP Server.

Properly organized server that imports tools and prompts from their respective modules.
Follows Python best practices and maintains clean separation of concerns.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List, Union

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from mcp.server.fastmcp import FastMCP

# Import all tool modules
from mcp_server.tools import (
    bank_tools,
    distribution_tools, 
    governance_tools,
    marketplace_tools,
    basket_tools,
    credit_tools,
    analytics_tools,
    cache_tools
)

# Import all prompt functions with aliases to avoid name collisions
from mcp_server.prompts import (
    list_regen_capabilities as list_capabilities_impl,
    chain_exploration as chain_exploration_impl,
    ecocredit_query_workshop as ecocredit_workshop_impl,
    credit_batch_analysis as batch_analysis_impl,
    marketplace_investigation as marketplace_impl,
    project_discovery as project_discovery_impl,
    query_builder_assistant as query_builder_impl,
    chain_config_setup as config_setup_impl
)

logger = logging.getLogger(__name__)


def create_modular_regen_mcp_server() -> FastMCP:
    """Create modular Regen Network MCP server with proper organization."""
    
    server = FastMCP(
        name="regen-network-mcp-modular",
        dependencies=["pydantic>=2.0.0", "httpx>=0.24.0", "structlog>=23.0.0"]
    )
    
    # ==============================================
    # BANK MODULE TOOLS (11 TOOLS)
    # ==============================================
    
    @server.tool()
    async def list_accounts(page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List all accounts on Regen Network."""
        return await bank_tools.list_accounts(page, limit)
    
    @server.tool()
    async def get_account(address: str) -> Dict[str, Any]:
        """Get detailed account information."""
        return await bank_tools.get_account(address)
    
    @server.tool()
    async def get_balance(address: str, denom: str) -> Dict[str, Any]:
        """Get specific token balance for account."""
        return await bank_tools.get_balance(address, denom)
    
    @server.tool()
    async def get_all_balances(address: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get all token balances for account."""
        return await bank_tools.get_all_balances(address, page, limit)
    
    @server.tool()
    async def get_spendable_balances(address: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get spendable balances for account."""
        return await bank_tools.get_spendable_balances(address, page, limit)
    
    @server.tool()
    async def get_total_supply(page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get total supply of all tokens."""
        return await bank_tools.get_total_supply(page, limit)
    
    @server.tool()
    async def get_supply_of(denom: str) -> Dict[str, Any]:
        """Get total supply of specific token."""
        return await bank_tools.get_supply_of(denom)
    
    @server.tool()
    async def get_bank_params() -> Dict[str, Any]:
        """Get bank module parameters."""
        return await bank_tools.get_bank_params()
    
    @server.tool()
    async def get_denoms_metadata(page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get metadata for all tokens."""
        return await bank_tools.get_denoms_metadata(page, limit)
    
    @server.tool()
    async def get_denom_metadata(denom: str) -> Dict[str, Any]:
        """Get metadata for specific token."""
        return await bank_tools.get_denom_metadata(denom)
    
    @server.tool()
    async def get_denom_owners(denom: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get all holders of a token."""
        return await bank_tools.get_denom_owners(denom, page, limit)
    
    # ==============================================
    # DISTRIBUTION MODULE TOOLS (9 TOOLS)
    # ==============================================
    
    @server.tool()
    async def get_distribution_params() -> Dict[str, Any]:
        """Get distribution module parameters."""
        return await distribution_tools.get_distribution_params()
    
    @server.tool()
    async def get_validator_outstanding_rewards(validator_address: str) -> Dict[str, Any]:
        """Get outstanding rewards for a validator."""
        return await distribution_tools.get_validator_outstanding_rewards(validator_address)
    
    @server.tool()
    async def get_validator_commission(validator_address: str) -> Dict[str, Any]:
        """Get commission for a validator."""
        return await distribution_tools.get_validator_commission(validator_address)
    
    @server.tool()
    async def get_validator_slashes(
        validator_address: str,
        starting_height: Optional[int] = None,
        ending_height: Optional[int] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get slashing events for a validator."""
        return await distribution_tools.get_validator_slashes(
            validator_address, starting_height, ending_height, page, limit
        )
    
    @server.tool()
    async def get_delegation_rewards(delegator_address: str, validator_address: str) -> Dict[str, Any]:
        """Get delegation rewards for specific delegator-validator pair."""
        return await distribution_tools.get_delegation_rewards(delegator_address, validator_address)
    
    @server.tool()
    async def get_delegation_total_rewards(delegator_address: str) -> Dict[str, Any]:
        """Get total delegation rewards for a delegator."""
        return await distribution_tools.get_delegation_total_rewards(delegator_address)
    
    @server.tool()
    async def get_delegator_validators(delegator_address: str) -> Dict[str, Any]:
        """Get validators that a delegator is bonded to."""
        return await distribution_tools.get_delegator_validators(delegator_address)
    
    @server.tool()
    async def get_delegator_withdraw_address(delegator_address: str) -> Dict[str, Any]:
        """Get withdraw address for a delegator."""
        return await distribution_tools.get_delegator_withdraw_address(delegator_address)
    
    @server.tool()
    async def get_community_pool() -> Dict[str, Any]:
        """Get community pool balance."""
        return await distribution_tools.get_community_pool()
    
    # ==============================================
    # GOVERNANCE MODULE TOOLS (8 TOOLS)
    # ==============================================
    
    @server.tool()
    async def get_governance_proposal(proposal_id: Union[str, int]) -> Dict[str, Any]:
        """Get specific governance proposal."""
        return await governance_tools.get_governance_proposal(proposal_id)
    
    @server.tool()
    async def list_governance_proposals(
        page: int = 1,
        limit: int = 100,
        proposal_status: Optional[str] = None,
        voter: Optional[str] = None,
        depositor: Optional[str] = None
    ) -> Dict[str, Any]:
        """List governance proposals with optional filters."""
        return await governance_tools.list_governance_proposals(page, limit, proposal_status, voter, depositor)
    
    @server.tool()
    async def get_governance_vote(proposal_id: Union[str, int], voter: str) -> Dict[str, Any]:
        """Get specific vote on a proposal."""
        return await governance_tools.get_governance_vote(proposal_id, voter)
    
    @server.tool()
    async def list_governance_votes(proposal_id: Union[str, int], page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List votes for a specific proposal."""
        return await governance_tools.list_governance_votes(proposal_id, page, limit)
    
    @server.tool()
    async def list_governance_deposits(proposal_id: Union[str, int], page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List deposits for a specific proposal."""
        return await governance_tools.list_governance_deposits(proposal_id, page, limit)
    
    @server.tool()
    async def get_governance_params(params_type: str) -> Dict[str, Any]:
        """Get governance parameters."""
        return await governance_tools.get_governance_params(params_type)
    
    @server.tool()
    async def get_governance_deposit(proposal_id: Union[str, int], depositor: str) -> Dict[str, Any]:
        """Get specific deposit for a proposal."""
        return await governance_tools.get_governance_deposit(proposal_id, depositor)
    
    @server.tool()
    async def get_governance_tally_result(proposal_id: Union[str, int]) -> Dict[str, Any]:
        """Get vote tally for a proposal."""
        return await governance_tools.get_governance_tally_result(proposal_id)
    
    # ==============================================
    # MARKETPLACE MODULE TOOLS (5 TOOLS)
    # ==============================================
    
    @server.tool()
    async def get_sell_order(sell_order_id: Union[str, int]) -> Dict[str, Any]:
        """Get specific marketplace sell order."""
        return await marketplace_tools.get_sell_order(sell_order_id)
    
    @server.tool()
    async def list_sell_orders(page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List all active sell orders."""
        return await marketplace_tools.list_sell_orders(page, limit)
    
    @server.tool()
    async def list_sell_orders_by_batch(batch_denom: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List sell orders for specific batch."""
        return await marketplace_tools.list_sell_orders_by_batch(batch_denom, page, limit)
    
    @server.tool()
    async def list_sell_orders_by_seller(seller: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List sell orders by seller."""
        return await marketplace_tools.list_sell_orders_by_seller(seller, page, limit)
    
    @server.tool()
    async def list_allowed_denoms(page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """List allowed payment tokens."""
        return await marketplace_tools.list_allowed_denoms(page, limit)
    
    # ==============================================
    # ECOCREDITS MODULE TOOLS (4 TOOLS)
    # ==============================================
    
    @server.tool()
    async def list_credit_types() -> Dict[str, Any]:
        """List all enabled credit types."""
        return await credit_tools.list_credit_types()
    
    @server.tool()
    async def list_classes(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all credit classes."""
        return await credit_tools.list_credit_classes(limit, offset)
    
    @server.tool()
    async def list_projects(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all registered projects."""
        return await credit_tools.list_projects(limit, offset, count_total=True, reverse=False)
    
    @server.tool()
    async def list_credit_batches(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all credit batches."""
        return await credit_tools.list_credit_batches(limit, offset, count_total=True, reverse=False)
    
    # ==============================================
    # BASKETS MODULE TOOLS (5 TOOLS)
    # ==============================================
    
    @server.tool()
    async def list_baskets(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List all ecocredit baskets."""
        return await basket_tools.list_baskets(limit, offset)
    
    @server.tool()
    async def get_basket(basket_denom: str) -> Dict[str, Any]:
        """Get specific basket information."""
        return await basket_tools.get_basket(basket_denom)
    
    @server.tool()
    async def list_basket_balances(basket_denom: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List credit batches in basket."""
        return await basket_tools.list_basket_balances(basket_denom, limit, offset)
    
    @server.tool()
    async def get_basket_balance(basket_denom: str, batch_denom: str) -> Dict[str, Any]:
        """Get specific batch balance in basket."""
        return await basket_tools.get_basket_balance(basket_denom, batch_denom)
    
    @server.tool()
    async def get_basket_fee() -> Dict[str, Any]:
        """Get basket creation fee."""
        return await basket_tools.get_basket_fee()
    
    # ==============================================
    # ANALYTICS TOOLS (3 TOOLS)
    # ==============================================

    @server.tool()
    async def analyze_portfolio_impact(
        address: str,
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """Advanced portfolio ecological impact analysis."""
        return await analytics_tools.analyze_portfolio_impact(address, analysis_type)

    @server.tool()
    async def analyze_market_trends(
        time_period: str = "30d",
        credit_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze market trends across credit types with historical data analysis."""
        return await analytics_tools.analyze_market_trends(time_period, credit_types)

    @server.tool()
    async def compare_credit_methodologies(class_ids: List[str]) -> Dict[str, Any]:
        """Compare different credit class methodologies for impact efficiency analysis."""
        return await analytics_tools.compare_credit_methodologies(class_ids)
    
    # ==============================================
    # INTERACTIVE PROMPTS (8 PROMPTS)
    # ==============================================
    
    @server.prompt()
    async def list_regen_capabilities() -> str:
        """Comprehensive list of all Regen MCP capabilities."""
        return await list_capabilities_impl()
    
    @server.prompt()
    async def chain_exploration(chain_info: Optional[str] = None) -> str:
        """Interactive Regen Network exploration guide."""
        return await chain_exploration_impl(chain_info)
    
    @server.prompt()
    async def ecocredit_query_workshop(focus_area: Optional[str] = None) -> str:
        """Comprehensive ecocredit analysis workshop."""
        return await ecocredit_workshop_impl(focus_area)
    
    @server.prompt()
    async def credit_batch_analysis(batch_denom: Optional[str] = None) -> str:
        """Credit batch lifecycle analysis."""
        return await batch_analysis_impl(batch_denom)
    
    @server.prompt()
    async def marketplace_investigation(market_focus: Optional[str] = None) -> str:
        """Carbon market analytics and investigation."""
        return await marketplace_impl(market_focus)
    
    @server.prompt()
    async def project_discovery(criteria: Optional[str] = None) -> str:
        """Find and analyze ecological projects."""
        return await project_discovery_impl(criteria)
    
    @server.prompt()
    async def query_builder_assistant(query_type: Optional[str] = None) -> str:
        """Build complex queries step-by-step."""
        return await query_builder_impl(query_type)
    
    @server.prompt()
    async def chain_config_setup() -> str:
        """Chain connection configuration guide."""
        return await config_setup_impl()
    
    return server


# Create the server instance
server = create_modular_regen_mcp_server()

if __name__ == "__main__":
    server.run()