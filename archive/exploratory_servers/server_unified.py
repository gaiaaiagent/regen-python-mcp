"""Unified Regen Network MCP Server with all tools consolidated.

This server combines tools from all implementation trees following quick-data-mcp patterns:
- Tree 1: Basket tools, Analytics tools, Cache tools, Resources
- Tree 2: Credit tools, Marketplace tools  
- Tree 3: Production infrastructure
- Quality trees: Enhanced error handling and monitoring
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .config.settings import get_settings

# Tool imports - following quick-data-mcp pattern
from .tools import (
    basket_tools,
    credit_tools, 
    marketplace_tools,
    analytics_tools,
    cache_tools
)

# Resource imports
from .resources import (
    chain_resources,
    credit_resources,
    portfolio_resources
)

# Client import
from .client.regen_client import get_regen_client

logger = logging.getLogger(__name__)

# ============================================================================
# SERVER CREATION - Following quick-data-mcp patterns
# ============================================================================

def create_unified_server() -> FastMCP:
    """Create unified Regen Network MCP server with all tools.
    
    Following quick-data-mcp server patterns with clear tool/resource/prompt sections.
    
    Returns:
        Configured FastMCP server with all tools registered
    """
    settings = get_settings()
    
    # Create the FastMCP server instance - following quick-data-mcp pattern
    mcp = FastMCP(
        name=settings.server_name,
        dependencies=["pydantic>=2.0.0", "httpx>=0.24.0", "structlog>=23.0.0"]
    )
    
    # ============================================================================
    # BASKET TOOLS - From Tree 1 (5 tools)
    # ============================================================================
    
    @mcp.tool()
    async def list_baskets(
        limit: int = 100,
        offset: int = 0,
        count_total: bool = False,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """List all ecocredit baskets on Regen Ledger with pagination support."""
        return await basket_tools.list_baskets(limit, offset, count_total, reverse)
    
    @mcp.tool()
    async def get_basket(basket_denom: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific ecocredit basket."""
        return await basket_tools.get_basket(basket_denom)
    
    @mcp.tool()
    async def list_basket_balances(
        basket_denom: str,
        limit: int = 100,
        offset: int = 0,
        count_total: bool = False,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """List all credit batch balances held in a specific basket."""
        return await basket_tools.list_basket_balances(basket_denom, limit, offset, count_total, reverse)
    
    @mcp.tool()
    async def get_basket_balance(basket_denom: str, batch_denom: str) -> Dict[str, Any]:
        """Get the balance of a specific credit batch held in a basket."""
        return await basket_tools.get_basket_balance(basket_denom, batch_denom)
    
    @mcp.tool()
    async def get_basket_fee() -> Dict[str, Any]:
        """Fetch the current fee required to create a new ecocredit basket."""
        return await basket_tools.get_basket_fee()
    
    # ============================================================================
    # CREDIT TOOLS - From Tree 2 (4 tools)
    # ============================================================================
    
    @mcp.tool()
    async def list_credit_types() -> Dict[str, Any]:
        """List all credit types enabled on Regen via governance."""
        return await credit_tools.list_credit_types()
    
    @mcp.tool()
    async def list_credit_classes(
        limit: int = 100,
        offset: int = 0,
        count_total: bool = False,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Retrieve all active credit classes on Regen mainnet."""
        return await credit_tools.list_credit_classes(limit, offset, count_total, reverse)
    
    @mcp.tool()
    async def list_projects(
        limit: int = 100,
        offset: int = 0,
        count_total: bool = False,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Retrieve all registered projects on Regen mainnet."""
        return await credit_tools.list_projects(limit, offset, count_total, reverse)
    
    @mcp.tool()
    async def list_credit_batches(
        limit: int = 100,
        offset: int = 0,
        count_total: bool = False,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Retrieve all issued credit batches on Regen mainnet."""
        return await credit_tools.list_credit_batches(limit, offset, count_total, reverse)
    
    # ============================================================================
    # MARKETPLACE TOOLS - From Tree 2 (5 tools)
    # ============================================================================
    
    @mcp.tool()
    async def get_sell_order(sell_order_id: str) -> Dict[str, Any]:
        """Retrieve full details of a marketplace sell order by its ID."""
        return await marketplace_tools.get_sell_order(sell_order_id)
    
    @mcp.tool()
    async def list_sell_orders(
        limit: int = 100,
        page: int = 1,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Fetch a paginated list of all active ecocredit sell orders."""
        return await marketplace_tools.list_sell_orders(limit, page, count_total, reverse)
    
    @mcp.tool()
    async def list_sell_orders_by_batch(
        batch_denom: str,
        limit: int = 100,
        page: int = 1,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Retrieve all active sell orders for a specific credit batch."""
        return await marketplace_tools.list_sell_orders_by_batch(batch_denom, limit, page, count_total, reverse)
    
    @mcp.tool()
    async def list_sell_orders_by_seller(
        seller: str,
        limit: int = 100,
        page: int = 1,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """Retrieve all active sell orders created by a given seller."""
        return await marketplace_tools.list_sell_orders_by_seller(seller, limit, page, count_total, reverse)
    
    @mcp.tool()
    async def list_allowed_denoms(
        limit: int = 100,
        page: int = 1,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """List all coin denoms approved for use as ask price in the marketplace."""
        return await marketplace_tools.list_allowed_denoms(limit, page, count_total, reverse)
    
    # ============================================================================
    # ANALYTICS TOOLS - From Tree 1 (3 advanced tools)
    # ============================================================================
    
    @mcp.tool()
    async def analyze_portfolio_impact(
        address: str,
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """Advanced portfolio ecological impact analysis with multi-factor scoring."""
        return await analytics_tools.analyze_portfolio_impact(address, analysis_type)
    
    @mcp.tool()
    async def analyze_market_trends(
        time_period: str = "30d",
        credit_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Market trend analysis with historical projections and investment intelligence."""
        return await analytics_tools.analyze_market_trends(time_period, credit_types)
    
    @mcp.tool()
    async def compare_credit_methodologies(class_ids: List[str]) -> Dict[str, Any]:
        """Comparative analysis of credit class methodologies with decision frameworks."""
        return await analytics_tools.compare_credit_methodologies(class_ids)
    
    # ============================================================================
    # CACHE MANAGEMENT TOOLS - From Tree 1 (3 tools)
    # ============================================================================
    
    @mcp.tool()
    async def get_cache_stats() -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        return await cache_tools.get_cache_stats()
    
    @mcp.tool()
    async def clear_cache() -> Dict[str, Any]:
        """Clear the entire cache for testing/debugging."""
        return await cache_tools.clear_cache()
    
    @mcp.tool()
    async def cleanup_expired_cache() -> Dict[str, Any]:
        """Remove expired cache entries and optimize memory usage."""
        return await cache_tools.cleanup_expired_cache()
    
    # ============================================================================
    # DYNAMIC RESOURCES - From Tree 1 (6 resources)
    # ============================================================================
    
    @mcp.resource("chain://config")
    async def get_chain_config_resource() -> Dict[str, Any]:
        """Complete Regen Network chain configuration and endpoints."""
        return await chain_resources.get_chain_config()
    
    @mcp.resource("chain://status")
    async def get_chain_status_resource() -> Dict[str, Any]:
        """Current chain status and block height information."""
        return await chain_resources.get_chain_status()
    
    @mcp.resource("chain://endpoints")
    async def get_chain_endpoints_resource() -> Dict[str, Any]:
        """Live endpoint health and availability status."""
        return await chain_resources.get_chain_endpoints()
    
    @mcp.resource("credits://{credit_class}/summary")
    async def get_credit_class_summary(credit_class: str) -> Dict[str, Any]:
        """Comprehensive credit class summary with dynamic class ID parameters."""
        return await credit_resources.get_credit_class_summary(credit_class)
    
    @mcp.resource("credits://market/statistics")
    async def get_market_statistics_resource() -> Dict[str, Any]:
        """Real-time market statistics across all credit types."""
        return await credit_resources.get_market_statistics()
    
    @mcp.resource("credits://types/overview")
    async def get_credit_types_overview_resource() -> Dict[str, Any]:
        """Complete overview of all available credit types."""
        return await credit_resources.get_credit_types_overview()
    
    @mcp.resource("portfolio://{address}/analysis")
    async def get_portfolio_analysis_resource(address: str) -> Dict[str, Any]:
        """Comprehensive portfolio analysis for any Regen Network address."""
        return await portfolio_resources.get_portfolio_analysis(address)
    
    @mcp.resource("portfolio://{address}/holdings")
    async def get_portfolio_holdings_resource(address: str) -> Dict[str, Any]:
        """Detailed breakdown of individual credit holdings."""
        return await portfolio_resources.get_portfolio_holdings(address)
    
    # ============================================================================
    # HEALTH AND MONITORING - From Quality Trees
    # ============================================================================
    
    @mcp.resource("health://status")
    async def get_health_status() -> Dict[str, Any]:
        """Server health status and diagnostics."""
        try:
            client = await get_regen_client()
            health_result = await client.health_check()
            
            return {
                "status": "healthy" if health_result.get("healthy", False) else "degraded",
                "timestamp": health_result.get("timestamp"),
                "endpoints": health_result.get("endpoints", {}),
                "server": {
                    "name": settings.server_name,
                    "version": "1.0.0"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Health check failed: {str(e)}",
                "server": {
                    "name": settings.server_name,
                    "version": "1.0.0"
                }
            }
    
    # Add startup logging
    logger.info("Unified Regen MCP Server created with %d tools registered", 18)
    logger.info("Tools: 5 basket + 4 credit + 5 marketplace + 3 analytics + 3 cache")
    logger.info("Resources: 8 dynamic resources + health monitoring")
    
    return mcp


# ============================================================================
# SERVER INSTANCE MANAGEMENT - Following quick-data-mcp patterns
# ============================================================================

_server_instance: Optional[FastMCP] = None


def get_server() -> FastMCP:
    """Get the MCP server instance (singleton pattern).
    
    Following quick-data-mcp pattern for server instance management.
    
    Returns:
        The unified Regen Network MCP server instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = create_unified_server()
    return _server_instance


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Following quick-data-mcp main pattern
    server = get_server()
    server.run()