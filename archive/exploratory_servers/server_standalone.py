#!/usr/bin/env python3
"""Regen Network MCP Server - Integrated Implementation.

This server provides the integrated tools from all three implementation trees
for exploring the Regen Network blockchain and its ecological credit ecosystem.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import the integrated server
from mcp_server.server import mcp, get_server
from mcp.types import (
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    ListToolsRequest,
    ListToolsResult,
    CallToolRequest,
    CallToolResult,
)

# Import all prompts
from prompts import (
    chain_exploration,
    ecocredit_query_workshop,
    marketplace_investigation,
    project_discovery,
    credit_batch_analysis,
    list_regen_capabilities,
    query_builder_assistant,
    chain_config_setup,
    PROMPTS,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegenMCPServer:
    """MCP Server for Regen Network blockchain exploration."""
    
    def __init__(self):
        """Initialize the Regen MCP server."""
        self.server = Server("regen-network-mcp")
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up all server handlers."""
        self.setup_prompt_handlers()
        self.setup_tool_handlers()
        
    def setup_prompt_handlers(self):
        """Register prompt handlers."""
        
        @self.server.list_prompts()
        async def list_prompts(request: ListPromptsRequest) -> ListPromptsResult:
            """List all available prompts."""
            prompts = []
            
            for prompt_info in PROMPTS:
                prompt = Prompt(
                    name=prompt_info["name"],
                    description=prompt_info["description"],
                    arguments=[
                        PromptArgument(
                            name=arg["name"],
                            description=arg["description"],
                            required=arg.get("required", False)
                        )
                        for arg in prompt_info.get("arguments", [])
                    ]
                )
                prompts.append(prompt)
                
            return ListPromptsResult(prompts=prompts)
        
        @self.server.get_prompt()
        async def get_prompt(request: GetPromptRequest) -> GetPromptResult:
            """Get a specific prompt by name."""
            prompt_name = request.name
            arguments = request.arguments or {}
            
            # Route to appropriate prompt function
            prompt_content = await self.route_prompt(prompt_name, arguments)
            
            if prompt_content is None:
                raise ValueError(f"Unknown prompt: {prompt_name}")
            
            messages = [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_content
                    )
                )
            ]
            
            return GetPromptResult(
                description=f"Regen Network {prompt_name.replace('_', ' ').title()} Prompt",
                messages=messages
            )
    
    async def route_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Route prompt requests to appropriate handler."""
        
        if prompt_name == "chain_exploration":
            chain_info = arguments.get("chain_info")
            return await chain_exploration(chain_info)
            
        elif prompt_name == "ecocredit_query_workshop":
            focus_area = arguments.get("focus_area")
            return await ecocredit_query_workshop(focus_area)
            
        elif prompt_name == "marketplace_investigation":
            market_focus = arguments.get("market_focus")
            return await marketplace_investigation(market_focus)
            
        elif prompt_name == "project_discovery":
            criteria = arguments.get("criteria")
            return await project_discovery(criteria)
            
        elif prompt_name == "credit_batch_analysis":
            batch_denom = arguments.get("batch_denom")
            return await credit_batch_analysis(batch_denom)
            
        elif prompt_name == "list_regen_capabilities":
            return await list_regen_capabilities()
            
        elif prompt_name == "query_builder_assistant":
            query_type = arguments.get("query_type")
            return await query_builder_assistant(query_type)
            
        elif prompt_name == "chain_config_setup":
            return await chain_config_setup()
            
        return None
    
    def setup_tool_handlers(self):
        """Register tool handlers."""
        
        @self.server.list_tools()
        async def list_tools(request: ListToolsRequest) -> ListToolsResult:
            """List available tools."""
            # For now, we'll provide a basic set of query tools
            # These would normally interface with the actual blockchain
            tools = [
                Tool(
                    name="get_chain_config",
                    description="Get current chain configuration and endpoints",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_credit_classes",
                    description="List all credit class methodologies",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_all_projects",
                    description="List all ecological projects on chain",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_project_by_id",
                    description="Get detailed project information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID (e.g., C01-001)"
                            }
                        },
                        "required": ["project_id"]
                    }
                ),
                Tool(
                    name="get_sell_orders",
                    description="Get all active marketplace sell orders",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool execution requests."""
            tool_name = request.name
            arguments = request.arguments or {}
            
            # Mock implementations for demonstration
            # In production, these would connect to actual blockchain
            result = await self.execute_tool(tool_name, arguments)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results."""
        
        # Mock implementations - in production these would query the actual blockchain
        if tool_name == "get_chain_config":
            return {
                "chain_id": "regen-1",
                "rest_endpoint": "https://rest.cosmos.directory/regen",
                "rpc_endpoint": "https://rpc.cosmos.directory/regen",
                "status": "connected"
            }
            
        elif tool_name == "get_credit_classes":
            return {
                "classes": [
                    {
                        "id": "C01",
                        "name": "Carbon Sequestration through Reforestation",
                        "admin": "regen1...",
                        "metadata": "Reforestation methodology for carbon credits"
                    },
                    {
                        "id": "C02",
                        "name": "Soil Carbon Sequestration",
                        "admin": "regen1...",
                        "metadata": "Agricultural soil carbon methodology"
                    }
                ]
            }
            
        elif tool_name == "get_all_projects":
            return {
                "projects": [
                    {
                        "id": "C01-001",
                        "name": "Amazon Reforestation Initiative",
                        "class_id": "C01",
                        "jurisdiction": "BR",
                        "admin": "regen1..."
                    },
                    {
                        "id": "C01-002",
                        "name": "California Forest Restoration",
                        "class_id": "C01",
                        "jurisdiction": "US-CA",
                        "admin": "regen1..."
                    }
                ]
            }
            
        elif tool_name == "get_project_by_id":
            project_id = arguments.get("project_id", "C01-001")
            return {
                "id": project_id,
                "name": f"Project {project_id}",
                "class_id": project_id.split("-")[0],
                "jurisdiction": "US",
                "admin": "regen1...",
                "metadata": f"Detailed information about {project_id}",
                "start_date": "2024-01-01",
                "reference_id": f"VCS-{project_id}"
            }
            
        elif tool_name == "get_sell_orders":
            return {
                "orders": [
                    {
                        "id": "1",
                        "seller": "regen1...",
                        "batch_key": {
                            "batch_denom": "C01-001-20240101-20240131-001",
                            "class_id": "C01"
                        },
                        "quantity": "1000",
                        "ask_price": "25.00",
                        "disable_auto_retire": False
                    }
                ]
            }
            
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Regen Network MCP Server started")
            logger.info("Ready to provide prompts and tools for blockchain exploration")
            
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for integrated server."""
    print("=" * 60)
    print("🌱 REGEN NETWORK INTEGRATED MCP SERVER")
    print("=" * 60)
    print("Version: 1.0.0")
    print("RPC URL:", os.getenv("REGEN_RPC_URL", "https://regen-rpc.polkachu.com"))
    print("-" * 60)
    print("Tools Available:")
    print("  • Basket Tools: 5")
    print("  • Analytics Tools: 3")  
    print("  • Cache Tools: 3")
    print("  • Credit Tools: 4")
    print("  • Marketplace Tools: 5")
    print("  • Bank Tools: 5")
    print("-" * 60)
    print("Total Tools: 25")
    print("=" * 60)
    print()
    
    # Check if we should use the integrated server or legacy
    use_integrated = os.getenv("USE_INTEGRATED", "true").lower() == "true"
    
    if use_integrated:
        print("Running INTEGRATED server with all tools...")
        # Run the integrated FastMCP server
        mcp.run()
    else:
        print("Running LEGACY server...")
        # Run the original server
        server = RegenMCPServer()
        await server.run()


if __name__ == "__main__":
    asyncio.run(main())