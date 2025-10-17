"""Portfolio analysis resources for Regen Network MCP server.

This module provides dynamic resources for analyzing portfolio impact,
credit holdings, and optimization recommendations for specific addresses.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from ..client.regen_client import get_regen_client

logger = logging.getLogger(__name__)


def register_portfolio_resources(server: FastMCP) -> None:
    """Register all portfolio analysis resources with the MCP server.
    
    Args:
        server: FastMCP server instance to register resources with
    """
    
    @server.resource(
        "portfolio://{address}/analysis",
        description="Comprehensive portfolio analysis for a specific address including holdings, impact metrics, and optimization recommendations"
    )
    async def portfolio_analysis(address: str) -> str:
        """Generate comprehensive portfolio analysis for a given address.
        
        Args:
            address: Regen Network address to analyze (regen1...)
            
        Returns:
            JSON string with portfolio analysis including:
            - Credit holdings breakdown by type and class
            - Environmental impact assessment
            - Diversification metrics
            - Optimization recommendations
        """
        try:
            # Validate address format
            if not address.startswith("regen1"):
                return json.dumps({
                    "error": "Invalid address format",
                    "message": "Address must start with 'regen1'",
                    "provided_address": address
                }, indent=2)
            
            client = get_regen_client()
            # Get account balances
            balances_response = await client.query_all_balances(
                address=address, limit=1000, offset=0
            )
            balances = balances_response.get("balances", [])
            
            # Separate regular tokens from ecocredits
            ecocredit_balances = []
            regular_balances = []
            
            for balance in balances:
                denom = balance.get("denom", "")
                if "/C" in denom or "/BIO" in denom or "eco." in denom:
                    ecocredit_balances.append(balance)
                else:
                    regular_balances.append(balance)
            
            # Get credit batch information for analysis
            batches_response = await client.query_credit_batches(limit=1000, offset=0)
            batches = batches_response.get("batches", [])
            
            # Get credit classes for categorization
            classes_response = await client.query_credit_classes(limit=1000, offset=0)
            classes = classes_response.get("classes", [])
            
            # Get projects for jurisdiction analysis
            projects_response = await client.query_projects(limit=1000, offset=0)
            projects = projects_response.get("projects", [])
            
            # Analyze ecocredit holdings
            holdings_analysis = {
                "by_credit_type": {},
                "by_jurisdiction": {},
                "by_credit_class": {},
                "batch_details": []
            }
            
            total_credits = 0
            unique_batches = set()
            unique_classes = set()
            
            for balance in ecocredit_balances:
                denom = balance.get("denom", "")
                amount = float(balance.get("amount", 0))
                total_credits += amount
                unique_batches.add(denom)
                
                # Find corresponding batch
                batch_info = None
                for batch in batches:
                    if batch.get("denom") == denom:
                        batch_info = batch
                        break
                
                if batch_info:
                    project_id = batch_info.get("projectId")
                    
                    # Find project and class info
                    project_info = None
                    class_info = None
                    
                    for project in projects:
                        if project.get("id") == project_id:
                            project_info = project
                            class_id = project.get("classId")
                            
                            for cls in classes:
                                if cls.get("id") == class_id:
                                    class_info = cls
                                    unique_classes.add(class_id)
                                    break
                            break
                    
                    # Categorize by credit type
                    credit_type = class_info.get("creditTypeAbbrev", "Unknown") if class_info else "Unknown"
                    if credit_type not in holdings_analysis["by_credit_type"]:
                        holdings_analysis["by_credit_type"][credit_type] = {
                            "total_amount": 0,
                            "batches": 0,
                            "classes": set()
                        }
                    
                    holdings_analysis["by_credit_type"][credit_type]["total_amount"] += amount
                    holdings_analysis["by_credit_type"][credit_type]["batches"] += 1
                    holdings_analysis["by_credit_type"][credit_type]["classes"].add(class_info.get("id") if class_info else "Unknown")
                    
                    # Categorize by jurisdiction
                    jurisdiction = project_info.get("jurisdiction", "Unknown") if project_info else "Unknown"
                    if jurisdiction not in holdings_analysis["by_jurisdiction"]:
                        holdings_analysis["by_jurisdiction"][jurisdiction] = {
                            "total_amount": 0,
                            "batches": 0,
                            "credit_types": set()
                        }
                    
                    holdings_analysis["by_jurisdiction"][jurisdiction]["total_amount"] += amount
                    holdings_analysis["by_jurisdiction"][jurisdiction]["batches"] += 1
                    holdings_analysis["by_jurisdiction"][jurisdiction]["credit_types"].add(credit_type)
                    
                    # Categorize by credit class
                    class_id = class_info.get("id", "Unknown") if class_info else "Unknown"
                    if class_id not in holdings_analysis["by_credit_class"]:
                        holdings_analysis["by_credit_class"][class_id] = {
                            "total_amount": 0,
                            "batches": 0,
                            "credit_type": credit_type,
                            "methodology": class_info.get("metadata", "")[:100] if class_info else ""
                        }
                    
                    holdings_analysis["by_credit_class"][class_id]["total_amount"] += amount
                    holdings_analysis["by_credit_class"][class_id]["batches"] += 1
                    
                    # Add batch details
                    holdings_analysis["batch_details"].append({
                        "denom": denom,
                        "amount": amount,
                        "credit_type": credit_type,
                        "jurisdiction": jurisdiction,
                        "class_id": class_id,
                        "project_id": project_id,
                        "start_date": batch_info.get("startDate"),
                        "end_date": batch_info.get("endDate")
                    })
            
            # Convert sets to counts for JSON serialization
            for credit_type in holdings_analysis["by_credit_type"]:
                holdings_analysis["by_credit_type"][credit_type]["unique_classes"] = len(holdings_analysis["by_credit_type"][credit_type]["classes"])
                del holdings_analysis["by_credit_type"][credit_type]["classes"]
            
            for jurisdiction in holdings_analysis["by_jurisdiction"]:
                holdings_analysis["by_jurisdiction"][jurisdiction]["unique_credit_types"] = len(holdings_analysis["by_jurisdiction"][jurisdiction]["credit_types"])
                holdings_analysis["by_jurisdiction"][jurisdiction]["credit_types"] = list(holdings_analysis["by_jurisdiction"][jurisdiction]["credit_types"])
            
            # Calculate diversification metrics
            diversification = {
                "credit_type_diversity": len(holdings_analysis["by_credit_type"]),
                "jurisdictional_diversity": len(holdings_analysis["by_jurisdiction"]),
                "class_diversity": len(unique_classes),
                "concentration_risk": {
                    "largest_holding_percentage": 0,
                    "top_3_holdings_percentage": 0,
                    "herfindahl_index": 0
                }
            }
            
            # Calculate concentration risk
            if total_credits > 0:
                amounts = [balance.get("amount", 0) for balance in ecocredit_balances]
                amounts = [float(amt) for amt in amounts]
                amounts.sort(reverse=True)
                
                if amounts:
                    diversification["concentration_risk"]["largest_holding_percentage"] = (amounts[0] / total_credits) * 100
                    diversification["concentration_risk"]["top_3_holdings_percentage"] = (sum(amounts[:3]) / total_credits) * 100
                    
                    # Herfindahl-Hirschman Index
                    hhi = sum((amt / total_credits) ** 2 for amt in amounts)
                    diversification["concentration_risk"]["herfindahl_index"] = hhi
            
            # Generate optimization recommendations
            recommendations = []
            
            if diversification["credit_type_diversity"] == 1:
                recommendations.append({
                    "type": "diversification",
                    "priority": "high",
                    "message": "Consider diversifying across multiple credit types (Carbon, Biodiversity, etc.)"
                })
            
            if diversification["concentration_risk"]["largest_holding_percentage"] > 50:
                recommendations.append({
                    "type": "concentration",
                    "priority": "medium", 
                    "message": "Largest holding represents over 50% of portfolio - consider rebalancing"
                })
            
            if diversification["jurisdictional_diversity"] < 3:
                recommendations.append({
                    "type": "geographic",
                    "priority": "low",
                    "message": "Consider geographic diversification across different jurisdictions"
                })
            
            if len(ecocredit_balances) < 5:
                recommendations.append({
                    "type": "scale",
                    "priority": "low",
                    "message": "Small portfolio - consider increasing position sizes or batch diversity"
                })
            
            # Compile final analysis
            analysis = {
                "address": address,
                "summary": {
                    "total_ecocredits": total_credits,
                    "unique_batches": len(unique_batches),
                    "unique_credit_classes": len(unique_classes),
                    "unique_credit_types": len(holdings_analysis["by_credit_type"]),
                    "jurisdictions_represented": len(holdings_analysis["by_jurisdiction"]),
                    "regular_token_balances": len(regular_balances)
                },
                "holdings_breakdown": holdings_analysis,
                "diversification_metrics": diversification,
                "optimization_recommendations": recommendations,
                "impact_assessment": {
                    "carbon_credits": holdings_analysis["by_credit_type"].get("C", {}).get("total_amount", 0),
                    "biodiversity_credits": holdings_analysis["by_credit_type"].get("BIO", {}).get("total_amount", 0),
                    "estimated_co2_impact_tons": holdings_analysis["by_credit_type"].get("C", {}).get("total_amount", 0),
                    "jurisdictional_impact": list(holdings_analysis["by_jurisdiction"].keys())
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "analysis_version": "1.0",
                    "data_sources": ["account_balances", "credit_batches", "credit_classes", "projects"]
                }
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating portfolio analysis for {address}: {e}")
            return json.dumps({
                "error": "Failed to generate portfolio analysis",
                "message": str(e),
                "address": address,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat()
                }
            }, indent=2)
    
    
    @server.resource(
        "portfolio://{address}/holdings",
        description="Detailed breakdown of credit holdings for a specific address with current market values"
    )
    async def portfolio_holdings(address: str) -> str:
        """Get detailed breakdown of credit holdings for an address.
        
        Args:
            address: Regen Network address to analyze (regen1...)
            
        Returns:
            JSON string with holdings details including:
            - Individual batch holdings with metadata
            - Current market values and pricing
            - Batch aging and vintage analysis
        """
        try:
            if not address.startswith("regen1"):
                return json.dumps({
                    "error": "Invalid address format",
                    "message": "Address must start with 'regen1'",
                    "provided_address": address
                }, indent=2)
            
            client = get_regen_client()
            # Get account balances
            balances_response = await client.query_all_balances(
                address=address, limit=1000, offset=0
            )
            balances = balances_response.get("balances", [])
            
            # Filter to ecocredits only
            ecocredit_balances = [
                balance for balance in balances
                if "/C" in balance.get("denom", "") or "/BIO" in balance.get("denom", "") or "eco." in balance.get("denom", "")
            ]
            
            # Get market data for pricing
            try:
                sell_orders_response = await client.query_sell_orders(limit=1000, offset=0)
                sell_orders = sell_orders_response.get("sellOrders", [])
            except Exception as e:
                logger.warning(f"Could not fetch market data: {e}")
                sell_orders = []
            
            # Get batch details
            batches_response = await client.query_credit_batches(limit=1000, offset=0)
            batches = batches_response.get("batches", [])
            
            holdings_detail = []
            total_estimated_value = 0
            
            for balance in ecocredit_balances:
                denom = balance.get("denom", "")
                amount = float(balance.get("amount", 0))
                
                # Find batch information
                batch_info = None
                for batch in batches:
                    if batch.get("denom") == denom:
                        batch_info = batch
                        break
                
                # Find market pricing
                market_orders = [
                    order for order in sell_orders
                    if order.get("batchDenom") == denom
                ]
                
                current_market_price = None
                market_depth = 0
                
                if market_orders:
                    prices = [
                        float(order.get("askAmount", 0)) / max(1, float(order.get("quantity", 1)))
                        for order in market_orders
                    ]
                    current_market_price = min(prices) if prices else None
                    market_depth = sum(float(order.get("quantity", 0)) for order in market_orders)
                
                estimated_value = (current_market_price * amount) if current_market_price else 0
                total_estimated_value += estimated_value
                
                holding_detail = {
                    "batch_denom": denom,
                    "amount_held": amount,
                    "batch_info": {
                        "project_id": batch_info.get("projectId") if batch_info else None,
                        "issuer": batch_info.get("issuer") if batch_info else None,
                        "start_date": batch_info.get("startDate") if batch_info else None,
                        "end_date": batch_info.get("endDate") if batch_info else None,
                        "issuance_date": batch_info.get("issuanceDate") if batch_info else None,
                        "total_amount": batch_info.get("totalAmount") if batch_info else None,
                        "tradable_amount": batch_info.get("tradableAmount") if batch_info else None
                    },
                    "market_info": {
                        "current_market_price": current_market_price,
                        "estimated_value": estimated_value,
                        "market_depth": market_depth,
                        "active_orders": len(market_orders),
                        "liquidity_status": "high" if market_depth > amount else ("medium" if market_depth > amount/2 else "low")
                    },
                    "vintage_info": {
                        "start_year": int(batch_info.get("startDate", "0000")[:4]) if batch_info and batch_info.get("startDate") else None,
                        "end_year": int(batch_info.get("endDate", "0000")[:4]) if batch_info and batch_info.get("endDate") else None,
                        "age_years": 2024 - int(batch_info.get("startDate", "2024")[:4]) if batch_info and batch_info.get("startDate") else None
                    }
                }
                
                holdings_detail.append(holding_detail)
            
            # Sort by estimated value (highest first)
            holdings_detail.sort(key=lambda x: x["market_info"]["estimated_value"], reverse=True)
            
            response = {
                "address": address,
                "summary": {
                    "total_holdings": len(holdings_detail),
                    "total_credits": sum(h["amount_held"] for h in holdings_detail),
                    "total_estimated_value": total_estimated_value,
                    "holdings_with_market_data": len([h for h in holdings_detail if h["market_info"]["current_market_price"]]),
                    "average_vintage": sum(
                        h["vintage_info"]["start_year"] or 2024 
                        for h in holdings_detail 
                        if h["vintage_info"]["start_year"]
                    ) / max(1, len([h for h in holdings_detail if h["vintage_info"]["start_year"]]))
                },
                "detailed_holdings": holdings_detail,
                "market_summary": {
                    "tradeable_value": sum(
                        h["market_info"]["estimated_value"] 
                        for h in holdings_detail 
                        if h["market_info"]["current_market_price"]
                    ),
                    "high_liquidity_holdings": len([
                        h for h in holdings_detail 
                        if h["market_info"]["liquidity_status"] == "high"
                    ]),
                    "price_discovery_coverage": len([
                        h for h in holdings_detail 
                        if h["market_info"]["current_market_price"]
                    ]) / max(1, len(holdings_detail)) * 100
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "pricing_data": "current market orders",
                    "coverage": f"{len(ecocredit_balances)} credit holdings analyzed"
                }
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting portfolio holdings for {address}: {e}")
            return json.dumps({
                "error": "Failed to get portfolio holdings",
                "message": str(e),
                "address": address,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat()
                }
            }, indent=2)

    logger.info("Registered portfolio analysis resources")