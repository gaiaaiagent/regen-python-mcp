"""Regen Network MCP Server Prompts.

This module provides interactive prompts and guides for exploring
the Regen Network blockchain and its ecological credit ecosystem.
"""

from .chain_exploration_prompt import chain_exploration
from .ecocredit_query_workshop_prompt import ecocredit_query_workshop
from .marketplace_investigation_prompt import marketplace_investigation
from .project_discovery_prompt import project_discovery
from .credit_batch_analysis_prompt import credit_batch_analysis
from .list_regen_capabilities_prompt import list_regen_capabilities
from .query_builder_assistant_prompt import query_builder_assistant
from .chain_config_setup_prompt import chain_config_setup
from .methodology_comparison_prompt import methodology_comparison

__all__ = [
    "chain_exploration",
    "ecocredit_query_workshop",
    "marketplace_investigation",
    "project_discovery",
    "credit_batch_analysis",
    "list_regen_capabilities",
    "query_builder_assistant",
    "chain_config_setup",
    "methodology_comparison",
]

# Prompt metadata for server registration
PROMPTS = [
    {
        "name": "chain_exploration",
        "description": "Initial exploration guide for Regen Network chain",
        "arguments": [
            {
                "name": "chain_info",
                "description": "Optional chain configuration information",
                "required": False
            }
        ]
    },
    {
        "name": "ecocredit_query_workshop",
        "description": "Comprehensive eco credit module query guide",
        "arguments": [
            {
                "name": "focus_area",
                "description": "Specific area to focus on (classes, projects, batches, marketplace)",
                "required": False
            }
        ]
    },
    {
        "name": "marketplace_investigation",
        "description": "Market analysis and trading query guidance",
        "arguments": [
            {
                "name": "market_focus",
                "description": "Market aspect to investigate (prices, sellers, arbitrage)",
                "required": False
            }
        ]
    },
    {
        "name": "project_discovery",
        "description": "Project discovery and analysis workflows",
        "arguments": [
            {
                "name": "criteria",
                "description": "Search criteria (location, credit_class, etc.)",
                "required": False
            }
        ]
    },
    {
        "name": "credit_batch_analysis",
        "description": "Deep dive analysis into credit batches",
        "arguments": [
            {
                "name": "batch_denom",
                "description": "Specific batch denomination to analyze",
                "required": False
            }
        ]
    },
    {
        "name": "list_regen_capabilities",
        "description": "Complete reference of all Regen MCP server capabilities",
        "arguments": []
    },
    {
        "name": "query_builder_assistant",
        "description": "Help building complex queries step by step",
        "arguments": [
            {
                "name": "query_type",
                "description": "Type of query to build (aggregation, filtering, analysis)",
                "required": False
            }
        ]
    },
    {
        "name": "chain_config_setup",
        "description": "Guide for setting up chain configuration",
        "arguments": []
    },
    {
        "name": "methodology_comparison",
        "description": "9-criteria methodology comparison and buyer decision support",
        "arguments": [
            {
                "name": "methodology_ids",
                "description": "List of methodology IDs to compare (e.g., ['C02', 'C01'])",
                "required": False
            },
            {
                "name": "buyer_preset",
                "description": "Buyer profile (high_integrity, eu_risk_sensitive, net_zero)",
                "required": False
            }
        ]
    }
]