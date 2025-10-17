"""Registration module for advanced analytics tools.

This module provides MCP tool registration for the advanced analytics functions.
"""

import logging
from typing import List, Literal, Optional

from mcp.server.fastmcp import FastMCP

from .analytics_tools import (
    analyze_portfolio_impact,
    analyze_market_trends,
    compare_credit_methodologies,
)

logger = logging.getLogger(__name__)


def register_analytics_tools(server: FastMCP) -> None:
    """Register all advanced analytics tools with the MCP server.

    Args:
        server: FastMCP server instance to register tools with
    """

    @server.tool()
    async def analyze_portfolio_impact_tool(
        address: str,
        analysis_type: Literal["full", "carbon", "biodiversity", "diversification"] = "full"
    ) -> dict:
        """Analyze the ecological impact of a portfolio with advanced metrics.

        Provides sophisticated analytical assessment of portfolio ecological impact,
        including cross-credit impact scoring, diversification analysis, and
        optimization recommendations.

        Args:
            address: Regen Network address to analyze (must start with 'regen1')
            analysis_type: Type of analysis to perform:
                - "full": Complete ecological impact assessment
                - "carbon": Carbon impact analysis only
                - "biodiversity": Biodiversity impact analysis only
                - "diversification": Portfolio diversification analysis only

        Returns:
            Dictionary containing:
            - Comprehensive impact analysis with scoring
            - Portfolio composition breakdown
            - Diversification and risk metrics
            - Optimization recommendations
            - Risk assessment with actionable insights
        """
        return await analyze_portfolio_impact(address, analysis_type)


    @server.tool()
    async def analyze_market_trends_tool(
        time_period: Literal["7d", "30d", "90d", "1y"] = "30d",
        credit_types: Optional[List[str]] = None
    ) -> dict:
        """Analyze market trends across credit types with historical data analysis.

        Performs comprehensive market trend analysis including price movements,
        volume patterns, market sentiment, and forward-looking projections.

        Args:
            time_period: Time period for trend analysis:
                - "7d": Last 7 days (short-term trends)
                - "30d": Last 30 days (medium-term trends)
                - "90d": Last 90 days (quarterly trends)
                - "1y": Last year (long-term trends)
            credit_types: List of credit type abbreviations to analyze (e.g., ["C", "BIO"]).
                         If None, analyzes all available credit types.

        Returns:
            Dictionary containing:
            - Current market snapshot with volume and pricing
            - Trend analysis across selected time period
            - Market sentiment indicators
            - Volatility and liquidity analysis
            - Forward-looking projections and insights
        """
        return await analyze_market_trends(time_period, credit_types)


    @server.tool()
    async def compare_credit_methodologies_tool(
        class_ids: List[str]
    ) -> dict:
        """Compare different credit class methodologies for impact efficiency analysis.

        Provides detailed comparative analysis of credit class methodologies,
        including impact efficiency scoring, market performance evaluation,
        and investment recommendations.

        Args:
            class_ids: List of credit class IDs to compare (minimum 2 required).
                      Use list_credit_classes tool to find available class IDs.

        Returns:
            Dictionary containing:
            - Detailed methodology analysis for each class
            - Comparative scoring across multiple dimensions
            - Market performance and adoption metrics
            - Investment recommendation rankings
            - Risk analysis and key strengths/weaknesses
        """
        return await compare_credit_methodologies(class_ids)

    logger.info("Registered advanced analytics tools")
