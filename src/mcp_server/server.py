"""
Integrated Regen MCP Server
Combines tools from all three implementation trees into a unified server.
"""

from mcp.server import FastMCP
from typing import Dict, Any, List, Optional
import os

# Import all tools
from .prompts import (
    chain_exploration,
    ecocredit_query_workshop,
    marketplace_investigation,
    project_discovery,
    credit_batch_analysis,
    list_regen_capabilities,
    query_builder_assistant,
    chain_config_setup,
    methodology_comparison,
)

from .tools import (
    # Basket tools (Tree 1)
    list_baskets,
    get_basket,
    list_basket_balances,
    get_basket_balance,
    get_basket_fee,
    # Analytics tools (Tree 1)
    analyze_portfolio_impact,
    analyze_market_trends,
    compare_credit_methodologies,
    # Methodology Comparison tools (9-criteria framework)
    compare_methodologies_nine_criteria,
    BUYER_PRESETS,
    # Export tools
    generate_comparison_onepager,
    save_report_to_file,
    # Cache tools (Tree 1)
    clear_cache,
    get_cache_stats,
    invalidate_cache_key,
    # Credit tools (Tree 2)
    list_credit_types,
    list_credit_classes,
    list_projects,
    list_credit_batches,
    # Marketplace tools (Tree 2)
    get_sell_order,
    list_sell_orders,
    list_sell_orders_by_batch,
    list_sell_orders_by_seller,
    list_allowed_denoms,
    # Bank tools (Tree 3)
    get_balance,
    get_all_balances,
    get_spendable_balances,
    get_total_supply,
    get_supply_of
)

# Create the FastMCP server instance
mcp = FastMCP(name="Regen Network Integrated MCP")

# ============================================================================
# BASKET TOOLS (Tree 1) - 5 tools
# ============================================================================

@mcp.tool()
async def list_baskets_tool(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all active ecocredit baskets on Regen Network."""
    return await list_baskets(limit, offset)

@mcp.tool()
async def get_basket_tool(basket_denom: str) -> Dict[str, Any]:
    """Get detailed information about a specific basket."""
    return await get_basket(basket_denom)

@mcp.tool()
async def list_basket_balances_tool(basket_denom: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all credit batch balances held in a basket."""
    return await list_basket_balances(basket_denom, limit, offset)

@mcp.tool()
async def get_basket_balance_tool(basket_denom: str, batch_denom: str) -> Dict[str, Any]:
    """Get the balance of a specific credit batch in a basket."""
    return await get_basket_balance(basket_denom, batch_denom)

@mcp.tool()
async def get_basket_fee_tool() -> Dict[str, Any]:
    """Get the current fee required to create a new basket."""
    return await get_basket_fee()

# ============================================================================
# ANALYTICS TOOLS (Tree 1) - 3 tools
# ============================================================================

@mcp.tool()
async def analyze_portfolio_impact_tool(
    portfolio_addresses: List[str],
    include_retired: bool = True,
    calculate_metrics: bool = True
) -> Dict[str, Any]:
    """Analyze the environmental impact of a portfolio of credit holdings."""
    return await analyze_portfolio_impact(portfolio_addresses, include_retired, calculate_metrics)

@mcp.tool()
async def analyze_market_trends_tool(
    time_period_days: int = 30,
    credit_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze market trends for ecological credits."""
    return await analyze_market_trends(time_period_days, credit_types)

@mcp.tool()
async def compare_credit_methodologies_tool(
    methodology_ids: List[str],
    comparison_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Compare different credit methodologies and their effectiveness."""
    return await compare_credit_methodologies(methodology_ids, comparison_metrics)

# ============================================================================
# METHODOLOGY COMPARISON TOOLS (9-criteria framework) - 1 tool
# ============================================================================

@mcp.tool()
async def compare_methodologies_nine_criteria_tool(
    methodology_ids: List[str],
    buyer_preset: str = "high_integrity"
) -> List[Dict[str, Any]]:
    """Compare methodologies using 9-criteria framework with buyer-specific weighting.

    Assesses methodologies across 9 criteria: MRV, Additionality, Leakage, Traceability,
    Cost Efficiency, Permanence, Co-Benefits, Accuracy, and Precision.

    Args:
        methodology_ids: List of credit class IDs to compare (e.g., ["C02", "C01"])
        buyer_preset: Buyer profile ("high_integrity", "eu_risk_sensitive", or "net_zero")

    Returns:
        List of methodology comparison results with scores, evidence, and recommendations
    """
    results = await compare_methodologies_nine_criteria(methodology_ids, buyer_preset)
    # Convert Pydantic models to dicts for MCP response
    return [result.model_dump() for result in results]

# ============================================================================
# EXPORT TOOLS - 1 tool
# ============================================================================

@mcp.tool()
async def export_methodology_comparison_tool(
    methodology_ids: List[str],
    buyer_preset: str = "high_integrity",
    output_format: str = "markdown",
    save_to_file: bool = False
) -> Dict[str, Any]:
    """Export methodology comparison as a one-pager report.

    Generates a professional one-pager report for methodology comparisons,
    suitable for buyer decision-making and stakeholder presentations.

    Args:
        methodology_ids: List of credit class IDs to compare (e.g., ["C02", "C01"])
        buyer_preset: Buyer profile ("high_integrity", "eu_risk_sensitive", or "net_zero")
        output_format: Output format ("markdown" or "html")
        save_to_file: Whether to save the report to a file

    Returns:
        Report content and metadata
    """
    # Run comparison
    comparison_results = await compare_methodologies_nine_criteria(methodology_ids, buyer_preset)

    # Generate report
    report_content = generate_comparison_onepager(comparison_results, buyer_preset, output_format)

    # Optionally save to file
    file_path = None
    if save_to_file:
        from pathlib import Path
        file_path = save_report_to_file(report_content, format=output_format)
        file_path = str(file_path)

    return {
        "report_content": report_content,
        "format": output_format,
        "buyer_preset": buyer_preset,
        "methodology_ids": methodology_ids,
        "length_chars": len(report_content),
        "length_lines": len(report_content.split("\n")),
        "file_path": file_path
    }

# ============================================================================
# CACHE TOOLS (Tree 1) - 3 tools
# ============================================================================

@mcp.tool()
async def clear_cache_tool() -> Dict[str, Any]:
    """Clear all cached data."""
    return await clear_cache()

@mcp.tool()
async def get_cache_stats_tool() -> Dict[str, Any]:
    """Get statistics about the current cache usage."""
    return await get_cache_stats()

@mcp.tool()
async def invalidate_cache_key_tool(key: str) -> Dict[str, Any]:
    """Invalidate a specific cache key."""
    return await invalidate_cache_key(key)

# ============================================================================
# CREDIT TOOLS (Tree 2) - 4 tools
# ============================================================================

@mcp.tool()
async def list_credit_types_tool() -> Dict[str, Any]:
    """List all enabled credit types on Regen Network."""
    return await list_credit_types()

@mcp.tool()
async def list_credit_classes_tool(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all credit classes with pagination."""
    return await list_credit_classes(limit, offset)

@mcp.tool()
async def list_projects_tool(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all registered projects on Regen Network."""
    return await list_projects(limit, offset)

@mcp.tool()
async def list_credit_batches_tool(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List all issued credit batches."""
    return await list_credit_batches(limit, offset)

# ============================================================================
# MARKETPLACE TOOLS (Tree 2) - 5 tools
# ============================================================================

@mcp.tool()
async def get_sell_order_tool(sell_order_id: str) -> Dict[str, Any]:
    """Get details of a specific sell order."""
    return await get_sell_order(sell_order_id)

@mcp.tool()
async def list_sell_orders_tool(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """List all active sell orders on the marketplace."""
    return await list_sell_orders(page, limit)

@mcp.tool()
async def list_sell_orders_by_batch_tool(batch_denom: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """List sell orders for a specific credit batch."""
    return await list_sell_orders_by_batch(batch_denom, page, limit)

@mcp.tool()
async def list_sell_orders_by_seller_tool(seller: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """List sell orders created by a specific seller."""
    return await list_sell_orders_by_seller(seller, page, limit)

@mcp.tool()
async def list_allowed_denoms_tool(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """List all coin denominations approved for marketplace use."""
    return await list_allowed_denoms(page, limit)

# ============================================================================
# BANK TOOLS (Tree 3) - 5 tools
# ============================================================================

@mcp.tool()
async def get_balance_tool(address: str, denom: str) -> Dict[str, Any]:
    """Get the balance of a specific token for an account."""
    return await get_balance(address, denom)

@mcp.tool()
async def get_all_balances_tool(address: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
    """Get all token balances for an account."""
    return await get_all_balances(address, page, limit)

@mcp.tool()
async def get_spendable_balances_tool(address: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
    """Get spendable balances for an account."""
    return await get_spendable_balances(address, page, limit)

@mcp.tool()
async def get_total_supply_tool(page: int = 1, limit: int = 100) -> Dict[str, Any]:
    """Get the total supply of all denominations."""
    return await get_total_supply(page, limit)

@mcp.tool()
async def get_supply_of_tool(denom: str) -> Dict[str, Any]:
    """Get the total supply of a specific denomination."""
    return await get_supply_of(denom)

# ============================================================================
# RESOURCES (optional - from Tree 1)
# ============================================================================

@mcp.resource("regen://chain/config")
async def get_chain_config() -> Dict[str, Any]:
    """Get the current chain configuration."""
    return {
        "chain_id": "regen-1",
        "rpc_url": os.getenv("REGEN_RPC_URL", "https://regen-rpc.polkachu.com"),
        "version": "v5.0.0",
        "modules": ["ecocredit", "bank", "marketplace", "basket"]
    }

@mcp.resource("regen://tools/summary")
async def get_tools_summary() -> Dict[str, Any]:
    """Get a summary of all available tools."""
    from .tools import get_tool_summary
    return get_tool_summary()

# ============================================================================
# PROMPTS - Interactive guides and workflows
# ============================================================================

@mcp.prompt()
async def chain_exploration_prompt(chain_info: str = None) -> str:
    """Interactive chain exploration guide for Regen Network."""
    return await chain_exploration(chain_info)

@mcp.prompt()
async def ecocredit_query_workshop_prompt(focus_area: str = None) -> str:
    """Comprehensive ecocredit module query guide."""
    return await ecocredit_query_workshop(focus_area)

@mcp.prompt()
async def marketplace_investigation_prompt(market_focus: str = None) -> str:
    """Market analysis and trading query guidance."""
    return await marketplace_investigation(market_focus)

@mcp.prompt()
async def project_discovery_prompt(criteria: str = None) -> str:
    """Project discovery and analysis workflows."""
    return await project_discovery(criteria)

@mcp.prompt()
async def credit_batch_analysis_prompt(batch_denom: str = None) -> str:
    """Deep dive analysis into credit batches."""
    return await credit_batch_analysis(batch_denom)

@mcp.prompt()
async def list_regen_capabilities_prompt() -> str:
    """Complete reference of all Regen MCP server capabilities."""
    return await list_regen_capabilities()

@mcp.prompt()
async def query_builder_assistant_prompt(query_type: str = None) -> str:
    """Help building complex queries step by step."""
    return await query_builder_assistant(query_type)

@mcp.prompt()
async def chain_config_setup_prompt() -> str:
    """Guide for setting up chain configuration."""
    return await chain_config_setup()

@mcp.prompt()
async def methodology_comparison_prompt(
    methodology_ids: Optional[List[str]] = None,
    buyer_preset: Optional[str] = None
) -> str:
    """9-criteria methodology comparison and buyer decision support."""
    return await methodology_comparison(methodology_ids, buyer_preset)

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

def get_server():
    """Get the MCP server instance."""
    return mcp

if __name__ == "__main__":
    # Run the server
    import asyncio

    print("Starting Regen Network Integrated MCP Server...")
    print("Version: 1.0.0")
    print("Tools available: 27")
    print("Prompts available: 9")
    print("-" * 50)

    mcp.run()