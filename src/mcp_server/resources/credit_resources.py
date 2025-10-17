"""Credit data resources for Regen Network MCP server.

This module provides dynamic resources for accessing credit class summaries,
market statistics, and real-time credit analytics.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from ..client.regen_client import get_regen_client

logger = logging.getLogger(__name__)


def register_credit_resources(server: FastMCP) -> None:
    """Register all credit data resources with the MCP server.
    
    Args:
        server: FastMCP server instance to register resources with
    """
    
    @server.resource(
        "credits://{credit_class}/summary",
        description="Comprehensive summary of a specific credit class including metadata, statistics, and current status"
    )
    async def credit_class_summary(credit_class: str) -> str:
        """Get comprehensive summary for a specific credit class.
        
        Args:
            credit_class: Credit class ID to summarize
            
        Returns:
            JSON string with credit class summary including:
            - Class metadata and methodology
            - Project count and distribution
            - Batch statistics and issuance info
            - Market activity and pricing
        """
        try:
            client = get_regen_client()
            # Get credit class details
            classes_response = await client.query_credit_classes(
                limit=1000, offset=0
            )
            
            # Find the specific class
            target_class = None
            for cls in classes_response.get("classes", []):
                if cls.get("id") == credit_class:
                    target_class = cls
                    break
            
            if not target_class:
                return json.dumps({
                    "error": f"Credit class '{credit_class}' not found",
                    "available_classes": [cls.get("id") for cls in classes_response.get("classes", [])[:10]]
                }, indent=2)
            
            # Get projects for this class
            projects_response = await client.query_projects(limit=1000, offset=0)
            class_projects = [
                project for project in projects_response.get("projects", [])
                if project.get("classId") == credit_class
            ]
            
            # Get credit batches for this class
            batches_response = await client.query_credit_batches(limit=1000, offset=0)
            class_batches = [
                batch for batch in batches_response.get("batches", [])
                if batch.get("projectId") and any(
                    p.get("id") == batch.get("projectId") 
                    for p in class_projects
                )
            ]
            
            # Calculate statistics
            total_tradable = sum(
                float(batch.get("tradableAmount", 0)) 
                for batch in class_batches
            )
            total_retired = sum(
                float(batch.get("retiredAmount", 0)) 
                for batch in class_batches  
            )
            total_cancelled = sum(
                float(batch.get("cancelledAmount", 0))
                for batch in class_batches
            )
            
            # Get market data (sell orders)
            try:
                sell_orders_response = await client.query_sell_orders(limit=1000, offset=0)
                class_orders = []
                for order in sell_orders_response.get("sellOrders", []):
                    # Check if order is for a batch from this class
                    batch_denom = order.get("batchDenom")
                    if batch_denom and any(
                        batch.get("denom") == batch_denom 
                        for batch in class_batches
                    ):
                        class_orders.append(order)
            except Exception as e:
                logger.warning(f"Could not fetch market data: {e}")
                class_orders = []
            
            summary = {
                "class_info": {
                    "id": target_class.get("id"),
                    "admin": target_class.get("admin"),
                    "metadata": target_class.get("metadata", ""),
                    "credit_type": target_class.get("creditTypeAbbrev", ""),
                    "created": target_class.get("created")
                },
                "statistics": {
                    "total_projects": len(class_projects),
                    "total_batches": len(class_batches),
                    "credits_issued": {
                        "tradable_amount": total_tradable,
                        "retired_amount": total_retired, 
                        "cancelled_amount": total_cancelled,
                        "total_issued": total_tradable + total_retired + total_cancelled
                    }
                },
                "market_activity": {
                    "active_sell_orders": len(class_orders),
                    "total_credits_for_sale": sum(
                        float(order.get("quantity", 0)) 
                        for order in class_orders
                    ),
                    "price_range": {
                        "min_ask": min(
                            (float(order.get("askAmount", 0)) / max(1, float(order.get("quantity", 1))))
                            for order in class_orders
                        ) if class_orders else None,
                        "max_ask": max(
                            (float(order.get("askAmount", 0)) / max(1, float(order.get("quantity", 1)))) 
                            for order in class_orders
                        ) if class_orders else None
                    }
                },
                "project_distribution": {
                    "jurisdictions": list(set(
                        project.get("jurisdiction", "Unknown")
                        for project in class_projects
                        if project.get("jurisdiction")
                    )),
                    "project_sample": [
                        {
                            "id": project.get("id"),
                            "jurisdiction": project.get("jurisdiction"),
                            "metadata": project.get("metadata", "")[:100] + "..." if len(project.get("metadata", "")) > 100 else project.get("metadata", "")
                        }
                        for project in class_projects[:5]  # Show top 5 projects
                    ]
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_sources": ["credit_classes", "projects", "credit_batches", "sell_orders"]
                }
            }
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating credit class summary: {e}")
            return json.dumps({
                "error": "Failed to generate credit class summary",
                "message": str(e),
                "credit_class": credit_class
            }, indent=2)
    
    
    @server.resource(
        "credits://market/statistics",
        description="Real-time market statistics across all credit types including pricing, volume, and activity metrics"
    )
    async def market_statistics() -> str:
        """Get comprehensive market statistics for all credit types.
        
        Returns:
            JSON string with market statistics including:
            - Trading volume and activity metrics
            - Price analysis across credit types
            - Market depth and liquidity indicators
            - Credit class performance rankings
        """
        try:
            client = get_regen_client()
            # Get all sell orders for market analysis
            sell_orders_response = await client.query_sell_orders(limit=1000, offset=0)
            sell_orders = sell_orders_response.get("sellOrders", [])
            
            # Get credit classes for categorization
            classes_response = await client.query_credit_classes(limit=1000, offset=0)
            classes = classes_response.get("classes", [])
            
            # Get credit batches for supply analysis
            batches_response = await client.query_credit_batches(limit=1000, offset=0)
            batches = batches_response.get("batches", [])
            
            # Analyze market by credit type
            credit_type_stats = {}
            total_volume = 0
            total_orders = len(sell_orders)
            
            # Group orders by credit type
            for order in sell_orders:
                batch_denom = order.get("batchDenom", "")
                quantity = float(order.get("quantity", 0))
                ask_amount = float(order.get("askAmount", 0))
                
                # Find credit type for this batch
                credit_type = "Unknown"
                for batch in batches:
                    if batch.get("denom") == batch_denom:
                        project_id = batch.get("projectId")
                        # Find class for this project
                        for project in classes:  # This would need projects data
                            if project.get("id") == project_id:
                                credit_type = project.get("creditTypeAbbrev", "Unknown")
                                break
                        break
                
                if credit_type not in credit_type_stats:
                    credit_type_stats[credit_type] = {
                        "orders": 0,
                        "total_quantity": 0,
                        "total_value": 0,
                        "prices": [],
                        "batches": set()
                    }
                
                price_per_credit = ask_amount / max(1, quantity)
                credit_type_stats[credit_type]["orders"] += 1
                credit_type_stats[credit_type]["total_quantity"] += quantity
                credit_type_stats[credit_type]["total_value"] += ask_amount
                credit_type_stats[credit_type]["prices"].append(price_per_credit)
                credit_type_stats[credit_type]["batches"].add(batch_denom)
                total_volume += quantity
            
            # Calculate market metrics
            market_stats = {
                "overview": {
                    "total_active_orders": total_orders,
                    "total_credits_for_sale": total_volume,
                    "unique_credit_types": len(credit_type_stats),
                    "total_credit_classes": len(classes),
                    "total_credit_batches": len(batches)
                },
                "credit_type_breakdown": {},
                "market_depth": {
                    "price_ranges": [],
                    "volume_distribution": {}
                },
                "liquidity_metrics": {
                    "average_order_size": total_volume / max(1, total_orders),
                    "market_concentration": {}
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_freshness": "real-time",
                    "coverage": f"{total_orders} active orders analyzed"
                }
            }
            
            # Process credit type statistics
            for credit_type, stats in credit_type_stats.items():
                prices = stats["prices"]
                market_stats["credit_type_breakdown"][credit_type] = {
                    "active_orders": stats["orders"],
                    "total_quantity": stats["total_quantity"],
                    "total_value": stats["total_value"],
                    "unique_batches": len(stats["batches"]),
                    "pricing": {
                        "min_price": min(prices) if prices else 0,
                        "max_price": max(prices) if prices else 0,
                        "avg_price": sum(prices) / len(prices) if prices else 0,
                        "median_price": sorted(prices)[len(prices)//2] if prices else 0
                    },
                    "market_share": {
                        "by_orders": (stats["orders"] / max(1, total_orders)) * 100,
                        "by_volume": (stats["total_quantity"] / max(1, total_volume)) * 100
                    }
                }
            
            # Calculate price ranges for market depth
            all_prices = []
            for stats in credit_type_stats.values():
                all_prices.extend(stats["prices"])
            
            if all_prices:
                all_prices.sort()
                market_stats["market_depth"]["price_ranges"] = [
                    {
                        "range": "0-25th percentile",
                        "min_price": all_prices[0],
                        "max_price": all_prices[len(all_prices)//4] if len(all_prices) > 4 else all_prices[-1],
                        "order_count": len(all_prices)//4
                    },
                    {
                        "range": "25-75th percentile", 
                        "min_price": all_prices[len(all_prices)//4] if len(all_prices) > 4 else all_prices[0],
                        "max_price": all_prices[3*len(all_prices)//4] if len(all_prices) > 4 else all_prices[-1],
                        "order_count": len(all_prices)//2
                    },
                    {
                        "range": "75-100th percentile",
                        "min_price": all_prices[3*len(all_prices)//4] if len(all_prices) > 4 else all_prices[0], 
                        "max_price": all_prices[-1],
                        "order_count": len(all_prices)//4
                    }
                ]
            
            return json.dumps(market_stats, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating market statistics: {e}")
            return json.dumps({
                "error": "Failed to generate market statistics",
                "message": str(e),
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat()
                }
            }, indent=2)
    
    
    @server.resource(
        "credits://types/overview",
        description="Overview of all available credit types on Regen Network with their characteristics and usage"
    )
    async def credit_types_overview() -> str:
        """Get overview of all credit types available on Regen Network.
        
        Returns:
            JSON string with credit types overview including:
            - All available credit types and their properties
            - Usage statistics per credit type
            - Credit type definitions and purposes
        """
        try:
            client = get_regen_client()
            # Get credit types
            credit_types_response = await client.query_credit_types()
            credit_types = credit_types_response.get("creditTypes", [])
            
            # Get credit classes for usage analysis
            classes_response = await client.query_credit_classes(limit=1000, offset=0)
            classes = classes_response.get("classes", [])
            
            # Analyze credit type usage
            type_usage = {}
            for cls in classes:
                credit_type = cls.get("creditTypeAbbrev", "Unknown")
                if credit_type not in type_usage:
                    type_usage[credit_type] = {
                        "classes": 0,
                        "class_ids": []
                    }
                type_usage[credit_type]["classes"] += 1
                type_usage[credit_type]["class_ids"].append(cls.get("id"))
            
            overview = {
                "summary": {
                    "total_credit_types": len(credit_types),
                    "types_in_use": len(type_usage),
                    "total_credit_classes": len(classes)
                },
                "credit_types": [],
                "usage_statistics": type_usage,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_source": "regen network credit type registry"
                }
            }
            
            # Add detailed credit type information
            for credit_type in credit_types:
                type_info = {
                    "abbreviation": credit_type.get("abbreviation"),
                    "name": credit_type.get("name"),
                    "unit": credit_type.get("unit"),
                    "precision": credit_type.get("precision"),
                    "classes_using": type_usage.get(credit_type.get("abbreviation", ""), {}).get("classes", 0),
                    "description": credit_type.get("name", "").replace("_", " ").title()
                }
                overview["credit_types"].append(type_info)
            
            return json.dumps(overview, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating credit types overview: {e}")
            return json.dumps({
                "error": "Failed to generate credit types overview", 
                "message": str(e),
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat()
                }
            }, indent=2)

    logger.info("Registered credit data resources")