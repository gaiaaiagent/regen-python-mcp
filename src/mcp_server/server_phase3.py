"""MCP Server factory for Regen Network with Phase 3 enhancements.

This module provides the main entry point for creating and configuring
the Regen Network MCP server instance with advanced analytics, resources,
and performance optimization features.
"""

import asyncio
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config.settings import get_settings
from .tools import (
    register_basket_tools,
    register_analytics_tools,
    register_cache_tools
)
from .resources import (
    register_chain_resources,
    register_credit_resources,
    register_portfolio_resources
)
from .cache import get_cache_manager

logger = logging.getLogger(__name__)


def create_server(name: Optional[str] = None) -> FastMCP:
    """Create and configure the Regen Network MCP server with Phase 3 features.

    Args:
        name: Optional server name override

    Returns:
        Configured FastMCP server instance with:
        - Advanced analytics tools
        - Dynamic resource handlers
        - Performance optimization and caching
    """
    settings = get_settings()

    server_name = name or settings.server_name

    # Create server instance
    server = FastMCP(
        name=server_name,
    )

    logger.info("Created MCP server: %s v%s", server_name, settings.server_version)

    # Register Phase 2 tools
    register_basket_tools(server)

    # Register Phase 3 advanced analytics tools
    register_analytics_tools(server)
    register_cache_tools(server)

    # Register Phase 3 dynamic resources
    register_chain_resources(server)
    register_credit_resources(server)
    register_portfolio_resources(server)

    # Initialize performance optimization features
    cache_manager = get_cache_manager()
    cache_manager.start_cleanup_task()

    logger.info("Phase 3 MCP server configured with:")
    logger.info("  - Advanced Analytics: portfolio impact, market trends, methodology comparison")
    logger.info("  - Dynamic Resources: chain config, credit data, portfolio analysis")
    logger.info("  - Performance Optimization: TTL-based caching, connection pooling")
    logger.info("  - Cache Management: automatic cleanup, memory optimization")

    return server


async def shutdown_handler():
    """Handle server shutdown gracefully."""
    logger.info("Shutting down Phase 3 MCP server...")
    cache_manager = get_cache_manager()
    await cache_manager.stop_cleanup_task()

    # Get final cache statistics
    final_stats = await cache_manager.get_stats()
    logger.info(
        "Final cache stats - Hit rate: %.1f%%, Size: %.1fMB, Entries: %d",
        final_stats['performance']['hit_rate_percent'],
        final_stats['storage']['size_mb'],
        final_stats['storage']['entry_count']
    )

    logger.info("Phase 3 server shutdown complete")


def main() -> None:
    """Main entry point for running the Phase 3 enhanced server."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level, "INFO").upper() if isinstance(
            settings.log_level, str) else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create and run server
    server = create_server()

    logger.info("=" * 60)
    logger.info("🚀 REGEN NETWORK MCP SERVER - PHASE 3")
    logger.info("=" * 60)
    logger.info("Server: %s", settings.server_name)
    logger.info("Version: %s", settings.server_version)
    logger.info("Features:")
    logger.info("  ✅ Basket Operations (Phase 2)")
    logger.info("  ✅ Advanced Analytics")
    logger.info("  ✅ Dynamic Resources")
    logger.info("  ✅ Performance Caching")
    logger.info("  ✅ Chain Configuration")
    logger.info("  ✅ Market Intelligence")
    logger.info("  ✅ Portfolio Analysis")
    logger.info("=" * 60)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutdown requested")
        # Run cleanup in event loop if available
        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(shutdown_handler())
        except RuntimeError:
            # No running loop, create one
            asyncio.run(shutdown_handler())
    except Exception as e:
        logger.error("❌ Server error: %s", e)
        raise


if __name__ == "__main__":
    main()
