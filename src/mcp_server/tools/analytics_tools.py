"""Advanced analytics tools for Regen Network ecological impact analysis.

This module provides sophisticated analytical tools for portfolio impact assessment,
market trend analysis, and credit methodology comparison.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional, Union

from ..client.regen_client import get_regen_client, Pagination

logger = logging.getLogger(__name__)


async def analyze_portfolio_impact(
    address: str, 
    analysis_type: Literal["full", "carbon", "biodiversity", "diversification"] = "full"
) -> Dict[str, Any]:
    """Analyze the ecological impact of a portfolio with advanced metrics.
    
    Args:
        address: Regen Network address to analyze (regen1...)
        analysis_type: Type of impact analysis to perform
            - "full": Complete ecological impact assessment
            - "carbon": Carbon impact analysis only
            - "biodiversity": Biodiversity impact analysis only  
            - "diversification": Portfolio diversification analysis only
    
    Returns:
        Dictionary with comprehensive impact analysis including:
        - Ecological impact scores and metrics
        - Cross-credit impact assessment
        - Optimization recommendations
        - Risk and diversification analysis
    """
    try:
        # Validate address format
        if not address.startswith("regen1"):
            return {
                "error": "Invalid address format",
                "message": "Address must start with 'regen1'",
                "provided_address": address
            }
        
        client = get_regen_client()
        # Get portfolio balances
        pagination = Pagination(limit=1000, offset=0)
        balances_response = await client.query_all_balances(
            address=address, pagination=pagination
        )
        balances = balances_response.get("balances", [])

        # Filter ecocredits
        ecocredit_balances = [
            balance for balance in balances
            if "/C" in balance.get("denom", "") or "/BIO" in balance.get("denom", "") or "eco." in balance.get("denom", "")
        ]

        if not ecocredit_balances:
            return {
                "address": address,
                "impact_analysis": {
                    "total_impact_score": 0,
                    "carbon_impact": 0,
                    "biodiversity_impact": 0,
                    "message": "No ecocredits found in portfolio"
                },
                "recommendations": [{
                    "type": "acquisition",
                    "priority": "high",
                    "message": "Consider acquiring ecocredits to begin building ecological impact"
                }],
                "metadata": {
                    "analysis_type": analysis_type,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }

        # Get supporting data for analysis
        batches_response = await client.query_credit_batches(pagination)
        batches = batches_response.get("batches", [])

        classes_response = await client.query_credit_classes(pagination)
        classes = classes_response.get("classes", [])

        projects_response = await client.query_projects(pagination)
        projects = projects_response.get("projects", [])

        # Analyze impact by credit type
        impact_analysis = {
            "carbon_impact": {
                "total_co2_tons": 0,
                "verified_tons": 0,
                "additionality_score": 0,
                "vintage_quality": 0,
                "geographic_diversity": set(),
                "methodology_diversity": set()
            },
            "biodiversity_impact": {
                "total_bio_units": 0,
                "habitat_types": set(),
                "species_protection": set(),
                "ecosystem_services": set(),
                "conservation_area": 0
            },
            "cross_cutting_impacts": {
                "social_benefits": set(),
                "economic_benefits": set(),
                "sdg_alignment": set(),
                "co_benefits_score": 0
            }
        }
        
        # Portfolio composition analysis
        composition = {
            "credit_types": {},
            "jurisdictions": {},
            "project_types": {},
            "vintage_distribution": {},
            "total_credits": 0
        }
        
        # Diversification metrics
        diversification = {
            "type_diversity": 0,
            "geographic_diversity": 0,
            "temporal_diversity": 0,
            "methodology_diversity": 0,
            "concentration_risk": 0
        }
        
        # Process each holding
        for balance in ecocredit_balances:
            denom = balance.get("denom", "")
            amount = float(balance.get("amount", 0))
            composition["total_credits"] += amount
            
            # Find corresponding batch and metadata
            batch_info = None
            project_info = None
            class_info = None
            
            for batch in batches:
                if batch.get("denom") == denom:
                    batch_info = batch
                    project_id = batch.get("project_id")

                    # Find project
                    for project in projects:
                        if project.get("id") == project_id:
                            project_info = project
                            class_id = project.get("class_id")

                            # Find class
                            for cls in classes:
                                if cls.get("id") == class_id:
                                    class_info = cls
                                    break
                            break
                    break

            if not batch_info or not project_info or not class_info:
                logger.warning(f"Incomplete data for batch {denom}")
                continue

            credit_type = class_info.get("credit_type_abbrev", "Unknown")
            jurisdiction = project_info.get("jurisdiction", "Unknown")
            methodology = class_info.get("metadata", "")[:50]
            
            # Update composition tracking
            composition["credit_types"][credit_type] = composition["credit_types"].get(credit_type, 0) + amount
            composition["jurisdictions"][jurisdiction] = composition["jurisdictions"].get(jurisdiction, 0) + amount
            composition["project_types"][methodology] = composition["project_types"].get(methodology, 0) + amount
            
            # Vintage analysis
            start_year = None
            if batch_info.get("start_date"):
                try:
                    start_year = int(batch_info.get("start_date")[:4])
                    composition["vintage_distribution"][start_year] = composition["vintage_distribution"].get(start_year, 0) + amount
                except (ValueError, TypeError):
                    pass
            
            # Credit type specific impact analysis
            if analysis_type in ["full", "carbon"] and credit_type == "C":
                impact_analysis["carbon_impact"]["total_co2_tons"] += amount
                impact_analysis["carbon_impact"]["geographic_diversity"].add(jurisdiction)
                impact_analysis["carbon_impact"]["methodology_diversity"].add(methodology)
                
                # Vintage quality scoring (newer = higher quality for carbon)
                if start_year and start_year >= 2020:
                    impact_analysis["carbon_impact"]["vintage_quality"] += amount * 1.0
                elif start_year and start_year >= 2015:
                    impact_analysis["carbon_impact"]["vintage_quality"] += amount * 0.8
                else:
                    impact_analysis["carbon_impact"]["vintage_quality"] += amount * 0.6
            
            elif analysis_type in ["full", "biodiversity"] and credit_type == "BIO":
                impact_analysis["biodiversity_impact"]["total_bio_units"] += amount
                impact_analysis["biodiversity_impact"]["habitat_types"].add(jurisdiction)
                
                # Estimate conservation area (placeholder calculation)
                impact_analysis["biodiversity_impact"]["conservation_area"] += amount * 0.1  # 0.1 ha per unit estimate
            
            # Cross-cutting benefits analysis
            if analysis_type == "full":
                # Social benefits (based on project location)
                if jurisdiction in ["US", "CA", "MX", "BR", "AU"]:
                    impact_analysis["cross_cutting_impacts"]["social_benefits"].add("community_employment")
                    impact_analysis["cross_cutting_impacts"]["economic_benefits"].add("rural_development")
                
                # SDG alignment
                if credit_type == "C":
                    impact_analysis["cross_cutting_impacts"]["sdg_alignment"].update(["SDG13_Climate", "SDG15_Land"])
                elif credit_type == "BIO":
                    impact_analysis["cross_cutting_impacts"]["sdg_alignment"].update(["SDG15_Biodiversity", "SDG14_Ocean"])
        
        # Calculate diversification metrics
        if analysis_type in ["full", "diversification"]:
            diversification["type_diversity"] = len(composition["credit_types"])
            diversification["geographic_diversity"] = len(composition["jurisdictions"])
            diversification["temporal_diversity"] = len(composition["vintage_distribution"])
            diversification["methodology_diversity"] = len(composition["project_types"])
            
            # Concentration risk (Herfindahl-Hirschman Index)
            if composition["total_credits"] > 0:
                amounts = list(composition["credit_types"].values())
                shares = [amount / composition["total_credits"] for amount in amounts]
                diversification["concentration_risk"] = sum(share ** 2 for share in shares)
        
        # Calculate composite impact scores
        total_impact_score = 0
        
        if impact_analysis["carbon_impact"]["total_co2_tons"] > 0:
            carbon_score = (
                impact_analysis["carbon_impact"]["total_co2_tons"] * 1.0 +  # Base impact
                len(impact_analysis["carbon_impact"]["geographic_diversity"]) * 10 +  # Geographic bonus
                len(impact_analysis["carbon_impact"]["methodology_diversity"]) * 5 +  # Methodology bonus
                impact_analysis["carbon_impact"]["vintage_quality"] * 0.1  # Vintage quality bonus
            )
            total_impact_score += carbon_score
        
        if impact_analysis["biodiversity_impact"]["total_bio_units"] > 0:
            biodiversity_score = (
                impact_analysis["biodiversity_impact"]["total_bio_units"] * 2.0 +  # Higher weight for biodiversity
                len(impact_analysis["biodiversity_impact"]["habitat_types"]) * 15 +  # Habitat diversity bonus
                impact_analysis["biodiversity_impact"]["conservation_area"] * 5  # Area protection bonus
            )
            total_impact_score += biodiversity_score
        
        # Co-benefits scoring
        co_benefits_score = (
            len(impact_analysis["cross_cutting_impacts"]["social_benefits"]) * 20 +
            len(impact_analysis["cross_cutting_impacts"]["economic_benefits"]) * 15 +
            len(impact_analysis["cross_cutting_impacts"]["sdg_alignment"]) * 10
        )
        impact_analysis["cross_cutting_impacts"]["co_benefits_score"] = co_benefits_score
        total_impact_score += co_benefits_score
        
        # Convert sets to lists for JSON serialization
        for key in impact_analysis["carbon_impact"]:
            if isinstance(impact_analysis["carbon_impact"][key], set):
                impact_analysis["carbon_impact"][key] = list(impact_analysis["carbon_impact"][key])
        
        for key in impact_analysis["biodiversity_impact"]:
            if isinstance(impact_analysis["biodiversity_impact"][key], set):
                impact_analysis["biodiversity_impact"][key] = list(impact_analysis["biodiversity_impact"][key])
        
        for key in impact_analysis["cross_cutting_impacts"]:
            if isinstance(impact_analysis["cross_cutting_impacts"][key], set):
                impact_analysis["cross_cutting_impacts"][key] = list(impact_analysis["cross_cutting_impacts"][key])
        
        # Generate optimization recommendations
        recommendations = []
        
        if diversification["type_diversity"] == 1:
            recommendations.append({
                "type": "diversification",
                "priority": "high", 
                "message": "Portfolio lacks credit type diversity - consider adding other credit types",
                "specific_action": f"Consider adding {'biodiversity' if 'C' in composition['credit_types'] else 'carbon'} credits"
            })
        
        if diversification["concentration_risk"] > 0.5:
            recommendations.append({
                "type": "concentration",
                "priority": "medium",
                "message": "High concentration risk detected",
                "specific_action": "Rebalance portfolio to reduce single-asset concentration"
            })
        
        if diversification["geographic_diversity"] < 3:
            recommendations.append({
                "type": "geographic",
                "priority": "low",
                "message": "Limited geographic diversity",
                "specific_action": "Consider credits from different jurisdictions for risk mitigation"
            })
        
        # Vintage recommendations
        current_year = datetime.now().year
        old_vintages = [year for year in composition["vintage_distribution"] if year < current_year - 5]
        if old_vintages:
            recommendations.append({
                "type": "vintage",
                "priority": "medium",
                "message": f"Portfolio contains older vintages from {min(old_vintages)}",
                "specific_action": "Consider newer vintage credits for improved market liquidity"
            })
        
        return {
            "address": address,
            "impact_analysis": {
                "total_impact_score": round(total_impact_score, 2),
                "carbon_impact": impact_analysis["carbon_impact"],
                "biodiversity_impact": impact_analysis["biodiversity_impact"],
                "cross_cutting_impacts": impact_analysis["cross_cutting_impacts"]
            },
            "portfolio_composition": composition,
            "diversification_metrics": diversification,
            "optimization_recommendations": recommendations,
            "risk_assessment": {
                "concentration_risk": "high" if diversification["concentration_risk"] > 0.4 else ("medium" if diversification["concentration_risk"] > 0.2 else "low"),
                "diversification_score": (diversification["type_diversity"] * 25 + 
                                       diversification["geographic_diversity"] * 15 + 
                                       diversification["temporal_diversity"] * 10),
                "liquidity_risk": "medium",  # Placeholder - would need market data
                "vintage_risk": "low" if max(composition["vintage_distribution"].keys(), default=2024) >= 2020 else "medium"
            },
            "metadata": {
                "analysis_type": analysis_type,
                "generated_at": datetime.utcnow().isoformat(),
                "data_sources": ["balances", "batches", "classes", "projects"],
                "credits_analyzed": len(ecocredit_balances),
                "impact_methodology": "Regen MCP Advanced Analytics v1.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio impact for {address}: {e}")
        return {
            "error": "Failed to analyze portfolio impact",
            "message": str(e),
            "address": address,
            "metadata": {
                "analysis_type": analysis_type,
                "generated_at": datetime.utcnow().isoformat()
            }
        }


async def analyze_market_trends(
    time_period: Literal["7d", "30d", "90d", "1y"] = "30d",
    credit_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Analyze market trends across credit types with historical data analysis.
    
    Args:
        time_period: Time period for trend analysis
            - "7d": Last 7 days
            - "30d": Last 30 days  
            - "90d": Last 90 days
            - "1y": Last year
        credit_types: List of credit types to analyze (e.g., ["C", "BIO"]). 
                     If None, analyzes all available types.
    
    Returns:
        Dictionary with market trend analysis including:
        - Price trends and volatility analysis
        - Volume trends and market activity
        - Market sentiment indicators
        - Projection insights
    """
    try:
        client = get_regen_client()
        pagination = Pagination(limit=1000, offset=0)

        # Get current market data
        sell_orders_response = await client.query_sell_orders(pagination)
        sell_orders = sell_orders_response.get("sell_orders", [])

        # Get credit classes for categorization
        classes_response = await client.query_credit_classes(pagination)
        classes = classes_response.get("classes", [])

        # Get credit batches for supply analysis
        batches_response = await client.query_credit_batches(pagination)
        batches = batches_response.get("batches", [])

        # Get projects for proper credit type lookup
        projects_response = await client.query_projects(pagination)

        # Filter by credit types if specified
        if credit_types:
            credit_types = [ct.upper() for ct in credit_types]
        
        # Analyze current market state
        market_data = {
            "by_credit_type": {},
            "overall_metrics": {
                "total_orders": len(sell_orders),
                "total_volume": 0,
                "total_value": 0,
                "active_credit_types": set(),
                "unique_batches": set(),
                "price_distribution": []
            }
        }
        
        # Build lookup maps for efficient querying
        batch_to_project = {b.get("denom"): b.get("project_id") for b in batches}
        project_to_class = {p.get("id"): p.get("class_id") for p in projects_response.get("projects", [])}
        class_to_type = {c.get("id"): c.get("credit_type_abbrev", "Unknown") for c in classes}

        # Process each sell order
        for order in sell_orders:
            batch_denom = order.get("batch_denom", "")
            quantity = float(order.get("quantity", 0))
            ask_amount = float(order.get("ask_amount", 0))
            price_per_unit = ask_amount / max(1, quantity)

            # Find credit type through proper chain: batch -> project -> class -> type
            credit_type = "Unknown"
            project_id = batch_to_project.get(batch_denom)
            if project_id:
                class_id = project_to_class.get(project_id)
                if class_id:
                    credit_type = class_to_type.get(class_id, "Unknown")
            
            # Apply filter if specified
            if credit_types and credit_type not in credit_types:
                continue
            
            market_data["overall_metrics"]["total_volume"] += quantity
            market_data["overall_metrics"]["total_value"] += ask_amount
            market_data["overall_metrics"]["active_credit_types"].add(credit_type)
            market_data["overall_metrics"]["unique_batches"].add(batch_denom)
            market_data["overall_metrics"]["price_distribution"].append(price_per_unit)
            
            # Credit type breakdown
            if credit_type not in market_data["by_credit_type"]:
                market_data["by_credit_type"][credit_type] = {
                    "orders": 0,
                    "volume": 0,
                    "value": 0,
                    "prices": [],
                    "batches": set(),
                    "avg_order_size": 0
                }
            
            market_data["by_credit_type"][credit_type]["orders"] += 1
            market_data["by_credit_type"][credit_type]["volume"] += quantity
            market_data["by_credit_type"][credit_type]["value"] += ask_amount
            market_data["by_credit_type"][credit_type]["prices"].append(price_per_unit)
            market_data["by_credit_type"][credit_type]["batches"].add(batch_denom)
        
        # Convert sets to lists and calculate averages
        market_data["overall_metrics"]["active_credit_types"] = list(market_data["overall_metrics"]["active_credit_types"])
        market_data["overall_metrics"]["unique_batches"] = len(market_data["overall_metrics"]["unique_batches"])
        
        # Calculate trend insights (simulated historical analysis)
        time_period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[time_period]
        
        trends_analysis = {
            "time_period": time_period,
            "period_days": time_period_days,
            "trend_direction": {},
            "volatility_analysis": {},
            "volume_trends": {},
            "market_sentiment": {}
        }
        
        # Analyze trends by credit type
        for credit_type, data in market_data["by_credit_type"].items():
            prices = data["prices"]
            data["avg_order_size"] = data["volume"] / max(1, data["orders"])
            data["avg_price"] = sum(prices) / len(prices) if prices else 0
            data["price_range"] = {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "spread": (max(prices) - min(prices)) if prices else 0
            }
            data["batches"] = len(data["batches"])
            
            # Simulate trend analysis (in real implementation, would use historical data)
            price_volatility = (data["price_range"]["spread"] / max(1, data["avg_price"])) * 100
            
            trends_analysis["trend_direction"][credit_type] = {
                "price_trend": "stable",  # Placeholder - would calculate from historical data
                "volume_trend": "increasing" if data["volume"] > 1000 else "stable",
                "order_trend": "stable"
            }
            
            trends_analysis["volatility_analysis"][credit_type] = {
                "price_volatility_percent": round(price_volatility, 2),
                "volatility_rating": "high" if price_volatility > 20 else ("medium" if price_volatility > 10 else "low"),
                "price_stability": "stable" if price_volatility < 5 else "volatile"
            }
            
            trends_analysis["volume_trends"][credit_type] = {
                "current_volume": data["volume"],
                "average_order_size": round(data["avg_order_size"], 2),
                "market_depth_rating": "good" if data["orders"] > 10 else "limited",
                "liquidity_indicator": "high" if data["volume"] > 5000 else ("medium" if data["volume"] > 1000 else "low")
            }
        
        # Overall market sentiment analysis
        avg_prices = []
        for data in market_data["by_credit_type"].values():
            if data["prices"]:
                avg_prices.extend(data["prices"])
        
        if avg_prices:
            overall_avg_price = sum(avg_prices) / len(avg_prices)
            price_std = (sum((p - overall_avg_price) ** 2 for p in avg_prices) / len(avg_prices)) ** 0.5
            
            trends_analysis["market_sentiment"] = {
                "overall_sentiment": "neutral",  # Would be calculated from trend data
                "market_activity": "active" if len(sell_orders) > 100 else ("moderate" if len(sell_orders) > 50 else "low"),
                "price_discovery": "healthy" if len(avg_prices) > 20 else "limited",
                "competition_level": "competitive" if len(market_data["by_credit_type"]) > 2 else "limited",
                "market_maturity": "developing"
            }
        
        # Generate projections and insights
        projections = {
            "short_term": f"Based on current {time_period} trends, market shows stable activity with moderate liquidity.",
            "medium_term": "Credit diversification suggests healthy market development potential.",
            "risk_factors": [],
            "opportunities": []
        }
        
        # Risk factor analysis
        if len(market_data["by_credit_type"]) < 2:
            projections["risk_factors"].append("Limited credit type diversity may impact market resilience")
        
        if market_data["overall_metrics"]["total_orders"] < 50:
            projections["risk_factors"].append("Low order count indicates limited market liquidity")
        
        # Opportunity analysis  
        if any(data["avg_price"] < 10 for data in market_data["by_credit_type"].values()):
            projections["opportunities"].append("Some credit types showing attractive entry pricing")
        
        if len(market_data["overall_metrics"]["active_credit_types"]) > 1:
            projections["opportunities"].append("Diverse credit types enable portfolio optimization strategies")
        
        return {
            "analysis_period": {
                "time_period": time_period,
                "period_days": time_period_days,
                "analysis_date": datetime.utcnow().isoformat()
            },
            "current_market_snapshot": market_data,
            "trend_analysis": trends_analysis,
            "projections_and_insights": projections,
            "methodology": {
                "data_sources": ["current_sell_orders", "credit_classes", "credit_batches"],
                "analysis_type": "cross_sectional_with_simulated_trends",
                "limitations": "Historical data simulation - real trends would require time-series data"
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "credit_types_analyzed": list(market_data["by_credit_type"].keys()),
                "orders_analyzed": len(sell_orders),
                "analysis_version": "1.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {e}")
        return {
            "error": "Failed to analyze market trends",
            "message": str(e),
            "metadata": {
                "time_period": time_period,
                "credit_types": credit_types,
                "generated_at": datetime.utcnow().isoformat()
            }
        }


async def compare_credit_methodologies(class_ids: List[str]) -> Dict[str, Any]:
    """Compare different credit class methodologies for impact efficiency analysis.
    
    Args:
        class_ids: List of credit class IDs to compare
    
    Returns:
        Dictionary with methodology comparison including:
        - Methodology descriptions and characteristics
        - Impact efficiency scoring
        - Investment recommendation scoring
        - Comparative analysis matrix
    """
    try:
        if not class_ids or len(class_ids) < 2:
            return {
                "error": "At least 2 credit class IDs required for comparison",
                "provided_class_ids": class_ids
            }
        
        client = get_regen_client()
        pagination = Pagination(limit=1000, offset=0)

        # Get credit classes
        classes_response = await client.query_credit_classes(pagination)
        classes = classes_response.get("classes", [])
        
        # Find requested classes
        comparison_classes = []
        for class_id in class_ids:
            for cls in classes:
                if cls.get("id") == class_id:
                    comparison_classes.append(cls)
                    break
        
        if len(comparison_classes) < len(class_ids):
            found_ids = [cls.get("id") for cls in comparison_classes]
            missing_ids = [cid for cid in class_ids if cid not in found_ids]
            return {
                "error": "Some credit classes not found",
                "requested_class_ids": class_ids,
                "found_class_ids": found_ids,
                "missing_class_ids": missing_ids,
                "available_classes": [cls.get("id") for cls in classes[:20]]
            }
        
        # Get supporting data for analysis
        projects_response = await client.query_projects(pagination)
        projects = projects_response.get("projects", [])

        batches_response = await client.query_credit_batches(pagination)
        batches = batches_response.get("batches", [])

        # Get market data for pricing analysis
        try:
            sell_orders_response = await client.query_sell_orders(pagination)
            sell_orders = sell_orders_response.get("sell_orders", [])
        except Exception as e:
            logger.warning(f"Could not fetch market data: {e}")
            sell_orders = []

        # Analyze each class
        class_analyses = {}

        for cls in comparison_classes:
            class_id = cls.get("id")

            # Find projects for this class
            class_projects = [p for p in projects if p.get("class_id") == class_id]

            # Find batches for this class
            class_project_ids = [p.get("id") for p in class_projects]
            class_batches = [
                b for b in batches
                if b.get("project_id") in class_project_ids
            ]

            # Find market orders for this class batches
            class_batch_denoms = [b.get("denom") for b in class_batches]
            class_orders = [
                order for order in sell_orders
                if order.get("batch_denom") in class_batch_denoms
            ]

            # Calculate supply metrics
            total_issued = sum(float(b.get("total_amount", 0)) for b in class_batches)
            total_tradable = sum(float(b.get("tradable_amount", 0)) for b in class_batches)
            total_retired = sum(float(b.get("retired_amount", 0)) for b in class_batches)

            # Calculate market metrics
            market_volume = sum(float(order.get("quantity", 0)) for order in class_orders)
            market_value = sum(float(order.get("ask_amount", 0)) for order in class_orders)
            avg_price = (market_value / max(1, market_volume)) if market_volume > 0 else 0
            
            # Analyze methodology characteristics
            metadata = cls.get("metadata", "").lower()
            credit_type = cls.get("credit_type_abbrev", "Unknown")
            
            # Methodology scoring (heuristic-based)
            methodology_scores = {
                "additionality": 0,
                "measurability": 0,
                "permanence": 0,
                "co_benefits": 0,
                "scalability": 0
            }
            
            # Additionality scoring based on methodology keywords
            additionality_keywords = ["additionality", "baseline", "business-as-usual", "project"]
            methodology_scores["additionality"] = sum(1 for kw in additionality_keywords if kw in metadata) * 20
            
            # Measurability scoring
            measurability_keywords = ["monitor", "measure", "verify", "quantif", "data"]
            methodology_scores["measurability"] = min(100, sum(1 for kw in measurability_keywords if kw in metadata) * 25)
            
            # Permanence scoring (credit type dependent)
            if credit_type == "C":
                permanence_keywords = ["permanent", "reversal", "buffer", "storage"]
                methodology_scores["permanence"] = min(100, sum(1 for kw in permanence_keywords if kw in metadata) * 30)
            elif credit_type == "BIO":
                permanence_keywords = ["conservation", "protection", "habitat", "long-term"]
                methodology_scores["permanence"] = min(100, sum(1 for kw in permanence_keywords if kw in metadata) * 25)
            
            # Co-benefits scoring
            co_benefit_keywords = ["social", "economic", "community", "development", "biodiversity"]
            methodology_scores["co_benefits"] = min(100, sum(1 for kw in co_benefit_keywords if kw in metadata) * 20)
            
            # Scalability scoring
            methodology_scores["scalability"] = min(100, len(class_projects) * 5 + len(class_batches) * 2)
            
            # Market performance metrics
            market_performance = {
                "liquidity_score": min(100, len(class_orders) * 10),
                "pricing_attractiveness": 100 - min(100, avg_price * 2) if avg_price > 0 else 50,
                "market_adoption": min(100, total_retired / max(1, total_issued) * 100),
                "supply_health": min(100, total_tradable / max(1, total_issued) * 200)
            }
            
            # Investment recommendation scoring
            investment_score = (
                sum(methodology_scores.values()) / len(methodology_scores) * 0.4 +
                sum(market_performance.values()) / len(market_performance) * 0.3 +
                len(class_projects) * 2 +  # Project diversity
                min(100, total_issued / 1000) * 0.2  # Market size
            )
            
            class_analyses[class_id] = {
                "class_info": {
                    "id": class_id,
                    "admin": cls.get("admin"),
                    "credit_type": credit_type,
                    "metadata_length": len(cls.get("metadata", "")),
                    "creation_date": cls.get("created")
                },
                "methodology_scores": methodology_scores,
                "market_performance": market_performance,
                "supply_metrics": {
                    "total_issued": total_issued,
                    "total_tradable": total_tradable,
                    "total_retired": total_retired,
                    "retirement_rate": (total_retired / max(1, total_issued)) * 100
                },
                "adoption_metrics": {
                    "total_projects": len(class_projects),
                    "total_batches": len(class_batches),
                    "active_market_orders": len(class_orders),
                    "geographic_diversity": len(set(p.get("jurisdiction", "Unknown") for p in class_projects))
                },
                "pricing_info": {
                    "average_price": avg_price,
                    "market_volume": market_volume,
                    "market_value": market_value
                },
                "investment_recommendation": {
                    "overall_score": round(investment_score, 2),
                    "rating": (
                        "Strong Buy" if investment_score >= 80 else
                        "Buy" if investment_score >= 65 else
                        "Hold" if investment_score >= 50 else
                        "Weak Hold" if investment_score >= 35 else
                        "Avoid"
                    )
                }
            }
        
        # Generate comparative analysis
        comparative_analysis = {
            "methodology_comparison": {},
            "market_comparison": {},
            "risk_comparison": {},
            "recommendation_ranking": []
        }
        
        # Compare methodology scores
        for score_type in ["additionality", "measurability", "permanence", "co_benefits", "scalability"]:
            comparative_analysis["methodology_comparison"][score_type] = {
                class_id: analysis["methodology_scores"][score_type]
                for class_id, analysis in class_analyses.items()
            }
        
        # Compare market metrics
        for metric in ["liquidity_score", "pricing_attractiveness", "market_adoption", "supply_health"]:
            comparative_analysis["market_comparison"][metric] = {
                class_id: analysis["market_performance"][metric]
                for class_id, analysis in class_analyses.items()
            }
        
        # Risk comparison
        for class_id, analysis in class_analyses.items():
            risk_factors = []
            
            if analysis["supply_metrics"]["retirement_rate"] < 10:
                risk_factors.append("Low retirement rate may indicate limited end-user demand")
            
            if analysis["adoption_metrics"]["total_projects"] < 5:
                risk_factors.append("Limited project diversity increases concentration risk")
            
            if analysis["adoption_metrics"]["active_market_orders"] < 5:
                risk_factors.append("Limited market liquidity")
            
            if analysis["pricing_info"]["average_price"] == 0:
                risk_factors.append("No current market pricing data available")
            
            comparative_analysis["risk_comparison"][class_id] = {
                "risk_level": "high" if len(risk_factors) >= 3 else ("medium" if len(risk_factors) >= 2 else "low"),
                "risk_factors": risk_factors
            }
        
        # Investment recommendation ranking
        ranked_classes = sorted(
            class_analyses.items(),
            key=lambda x: x[1]["investment_recommendation"]["overall_score"],
            reverse=True
        )
        
        for rank, (class_id, analysis) in enumerate(ranked_classes, 1):
            comparative_analysis["recommendation_ranking"].append({
                "rank": rank,
                "class_id": class_id,
                "overall_score": analysis["investment_recommendation"]["overall_score"],
                "rating": analysis["investment_recommendation"]["rating"],
                "key_strengths": _identify_key_strengths(analysis),
                "key_weaknesses": _identify_key_weaknesses(analysis)
            })
        
        return {
            "comparison_summary": {
                "classes_compared": len(class_analyses),
                "credit_types_represented": list(set(
                    analysis["class_info"]["credit_type"] 
                    for analysis in class_analyses.values()
                )),
                "top_recommendation": comparative_analysis["recommendation_ranking"][0]["class_id"] if comparative_analysis["recommendation_ranking"] else None
            },
            "detailed_class_analyses": class_analyses,
            "comparative_analysis": comparative_analysis,
            "methodology": {
                "scoring_approach": "Multi-factor analysis with methodology, market, and adoption metrics",
                "weighting": {
                    "methodology_quality": 40,
                    "market_performance": 30,
                    "project_diversity": 20,
                    "market_size": 10
                },
                "limitations": [
                    "Methodology scoring based on keyword analysis of metadata",
                    "Market data reflects current snapshot, not historical performance",
                    "Investment recommendations are analytical, not financial advice"
                ]
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "class_ids_analyzed": class_ids,
                "analysis_version": "1.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing credit methodologies: {e}")
        return {
            "error": "Failed to compare credit methodologies",
            "message": str(e),
            "class_ids": class_ids,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat()
            }
        }


def _identify_key_strengths(analysis: Dict[str, Any]) -> List[str]:
    """Identify key strengths of a credit class based on analysis."""
    strengths = []
    
    methodology = analysis["methodology_scores"]
    market = analysis["market_performance"]
    adoption = analysis["adoption_metrics"]
    
    if methodology["additionality"] >= 80:
        strengths.append("Strong additionality framework")
    
    if methodology["measurability"] >= 80:
        strengths.append("Robust measurement and verification")
    
    if market["liquidity_score"] >= 70:
        strengths.append("Good market liquidity")
    
    if adoption["total_projects"] >= 10:
        strengths.append("Diverse project portfolio")
    
    if analysis["supply_metrics"]["retirement_rate"] >= 30:
        strengths.append("High end-user adoption")
    
    return strengths[:3]  # Top 3 strengths


def _identify_key_weaknesses(analysis: Dict[str, Any]) -> List[str]:
    """Identify key weaknesses of a credit class based on analysis."""
    weaknesses = []
    
    methodology = analysis["methodology_scores"]
    market = analysis["market_performance"]
    adoption = analysis["adoption_metrics"]
    
    if methodology["permanence"] < 50:
        weaknesses.append("Limited permanence assurance")
    
    if market["liquidity_score"] < 30:
        weaknesses.append("Low market liquidity")
    
    if adoption["total_projects"] < 5:
        weaknesses.append("Limited project diversity")
    
    if analysis["supply_metrics"]["retirement_rate"] < 10:
        weaknesses.append("Low retirement rate")
    
    if methodology["co_benefits"] < 40:
        weaknesses.append("Limited co-benefits documentation")
    
    return weaknesses[:3]  # Top 3 weaknesses