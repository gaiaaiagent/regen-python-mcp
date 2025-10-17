"""Chain configuration resources for Regen Network MCP server.

This module provides dynamic resources for accessing chain configuration,
status, and metadata information from Regen Network.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from ..client.regen_client import get_regen_client
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


def register_chain_resources(server: FastMCP) -> None:
    """Register all chain configuration resources with the MCP server.
    
    Args:
        server: FastMCP server instance to register resources with
    """
    
    @server.resource(
        "chain://config",
        description="Complete Regen Network chain configuration including endpoints, parameters, and network info"
    )
    async def chain_config() -> str:
        """Get comprehensive chain configuration for Regen Network.
        
        Returns:
            JSON string with chain configuration including:
            - Network endpoints (RPC, REST, fallbacks)
            - Chain parameters and settings
            - Client configuration
            - Network metadata
        """
        try:
            settings = get_settings()
            
            config = {
                "chain": {
                    "name": "regen",
                    "display_name": "Regen Network",
                    "chain_id": "regen-1",
                    "bech32_prefix": "regen",
                    "slip44": 118,
                    "network": "mainnet"
                },
                "endpoints": {
                    "rpc": {
                        "primary": settings.rpc_endpoints,
                        "fallback": [
                            "https://rpc.cosmos.directory/regen",
                            "https://rpc.regen.network"
                        ]
                    },
                    "rest": {
                        "primary": settings.rest_endpoints,
                        "fallback": [
                            "https://rest.cosmos.directory/regen", 
                            "https://api.regen.network"
                        ]
                    }
                },
                "client_config": {
                    "timeout": settings.client_timeout,
                    "max_retries": settings.max_retries,
                    "retry_delay": settings.retry_delay,
                    "max_connections": 100,
                    "keepalive_connections": 20
                },
                "modules": {
                    "ecocredit": {
                        "module": "regen.ecocredit.v1",
                        "features": ["baskets", "credit_classes", "projects", "batches", "marketplace"]
                    },
                    "cosmos_sdk": {
                        "version": "v0.47.x", 
                        "modules": ["bank", "gov", "distribution", "staking"]
                    }
                },
                "pagination": {
                    "default_limit": settings.default_limit,
                    "max_limit": settings.max_limit
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "server_version": settings.server_version,
                    "description": "Regen Network is a blockchain-based ecological credit platform"
                }
            }
            
            return json.dumps(config, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating chain config: {e}")
            return json.dumps({
                "error": "Failed to generate chain configuration",
                "message": str(e)
            }, indent=2)
    
    
    @server.resource(
        "chain://status",
        description="Current chain status including block height, validator info, and network health"
    )
    async def chain_status() -> str:
        """Get current Regen Network chain status and health information.
        
        Returns:
            JSON string with current chain status including:
            - Current block height and timestamp
            - Network health status
            - Endpoint availability
            - Node synchronization status
        """
        try:
            client = get_regen_client()
            # Perform health check to get endpoint status
            health_result = await client.health_check()

            # Get current chain info
            status_info = {
                "network": {
                    "chain_id": "regen-1",
                    "network_name": "Regen Network Mainnet"
                },
                "endpoints": {
                    "rpc_healthy": health_result.get("rpc_healthy", 0),
                    "rest_healthy": health_result.get("rest_healthy", 0),
                    "total_rpc": len(health_result.get("rpc_results", [])),
                    "total_rest": len(health_result.get("rest_results", []))
                },
                "health": {
                    "status": "healthy" if (
                        health_result.get("rpc_healthy", 0) > 0 and
                        health_result.get("rest_healthy", 0) > 0
                    ) else "degraded",
                    "rpc_availability": health_result.get("rpc_healthy", 0) / max(1, len(health_result.get("rpc_results", []))),
                    "rest_availability": health_result.get("rest_healthy", 0) / max(1, len(health_result.get("rest_results", [])))
                },
                "metadata": {
                    "checked_at": datetime.utcnow().isoformat(),
                    "response_time_ms": health_result.get("total_time_ms", 0)
                }
            }

            return json.dumps(status_info, indent=2)
                
        except Exception as e:
            logger.error(f"Error getting chain status: {e}")
            return json.dumps({
                "network": {
                    "chain_id": "regen-1",
                    "network_name": "Regen Network Mainnet"
                },
                "health": {
                    "status": "error",
                    "error": str(e)
                },
                "metadata": {
                    "checked_at": datetime.utcnow().isoformat()
                }
            }, indent=2)
    
    
    @server.resource(
        "chain://endpoints",
        description="Live endpoint health and availability status for all configured RPC and REST endpoints"
    )
    async def chain_endpoints() -> str:
        """Get detailed endpoint health information for all configured endpoints.
        
        Returns:
            JSON string with detailed endpoint status including:
            - Individual endpoint health status
            - Response times and availability
            - Endpoint configurations
            - Failover information
        """
        try:
            client = get_regen_client()
            health_result = await client.health_check()

            endpoints_info = {
                "rpc_endpoints": [],
                "rest_endpoints": [],
                "summary": {
                    "total_endpoints": 0,
                    "healthy_endpoints": 0,
                    "average_response_time_ms": 0
                },
                "metadata": {
                    "checked_at": datetime.utcnow().isoformat(),
                    "check_duration_ms": health_result.get("total_time_ms", 0)
                }
            }

            # Process RPC endpoint results
            for rpc_result in health_result.get("rpc_results", []):
                endpoints_info["rpc_endpoints"].append({
                    "url": rpc_result.get("endpoint", "unknown"),
                    "type": "rpc",
                    "healthy": rpc_result.get("success", False),
                    "response_time_ms": rpc_result.get("response_time", 0),
                    "error": rpc_result.get("error") if not rpc_result.get("success") else None
                })

            # Process REST endpoint results
            for rest_result in health_result.get("rest_results", []):
                endpoints_info["rest_endpoints"].append({
                    "url": rest_result.get("endpoint", "unknown"),
                    "type": "rest",
                    "healthy": rest_result.get("success", False),
                    "response_time_ms": rest_result.get("response_time", 0),
                    "error": rest_result.get("error") if not rest_result.get("success") else None
                })

            # Calculate summary statistics
            all_endpoints = endpoints_info["rpc_endpoints"] + endpoints_info["rest_endpoints"]
            healthy_endpoints = [ep for ep in all_endpoints if ep["healthy"]]

            endpoints_info["summary"] = {
                "total_endpoints": len(all_endpoints),
                "healthy_endpoints": len(healthy_endpoints),
                "availability_percentage": len(healthy_endpoints) / max(1, len(all_endpoints)) * 100,
                "average_response_time_ms": sum(ep["response_time_ms"] for ep in healthy_endpoints) / max(1, len(healthy_endpoints))
            }

            return json.dumps(endpoints_info, indent=2)
                
        except Exception as e:
            logger.error(f"Error getting endpoint status: {e}")
            return json.dumps({
                "error": "Failed to check endpoint status",
                "message": str(e),
                "metadata": {
                    "checked_at": datetime.utcnow().isoformat()
                }
            }, indent=2)

    logger.info("Registered chain configuration resources")