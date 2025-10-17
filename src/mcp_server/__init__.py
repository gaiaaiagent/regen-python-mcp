"""Regen Network MCP Server package."""

__version__ = "0.1.0"
__author__ = "Regen Network Development Foundation"
__description__ = "MCP server for Regen Network ecocredit queries"

from .server import server, create_modular_regen_mcp_server

__all__ = ["server", "create_modular_regen_mcp_server", "__version__"]
