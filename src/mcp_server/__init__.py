"""Regen Network MCP Server package."""

__version__ = "1.0.0"
__author__ = "Regen Network Development Foundation"
__description__ = "MCP server for Regen Network ecocredit queries"

from .server import mcp, get_server

__all__ = ["mcp", "get_server", "__version__"]
