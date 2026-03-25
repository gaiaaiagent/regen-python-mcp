#!/usr/bin/env python3
"""Slim REST API wrapper for ChatGPT (max 30 endpoints).

Focuses on the most useful Regen Network queries for a Custom GPT.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import httpx

from mcp_server.tools import (
    bank_tools,
    distribution_tools,
    governance_tools,
    marketplace_tools,
    basket_tools,
    credit_tools,
    analytics_tools,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Off-chain Metadata Enrichment Configuration (Session E)
# =============================================================================
KOI_API_ENDPOINT = "https://regen.gaiaai.xyz/api/koi"
KOI_INTERNAL_API_KEY = os.environ.get("KOI_INTERNAL_API_KEY", "")
ENRICHMENT_MAX_ITEMS = 10  # Cap enriched items per response
ENRICHMENT_TIMEOUT_SECONDS = 5.0  # Strict timeout per enrichment
METADATA_IRI_PREFIX = "regen:"  # Only enrich Regen IRIs


async def derive_hectares_for_iri(
    iri: str,
    client: httpx.AsyncClient,
    force_refresh: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Derive hectares from a metadata IRI via the KOI API.
    Enforces "no citation, no metric" policy.

    Returns None if derivation fails (metric should not be reported).
    """
    if not iri or not iri.startswith(METADATA_IRI_PREFIX):
        return None

    if not KOI_INTERNAL_API_KEY:
        logger.warning("KOI_INTERNAL_API_KEY not configured - skipping enrichment")
        return None

    try:
        response = await client.post(
            f"{KOI_API_ENDPOINT}/metadata/hectares",
            json={"iri": iri, "force_refresh": force_refresh},
            headers={"X-Internal-API-Key": KOI_INTERNAL_API_KEY},
            timeout=ENRICHMENT_TIMEOUT_SECONDS
        )

        if response.status_code != 200:
            # Blocked or failed - no metric
            logger.debug(f"Hectares derivation blocked for {iri}: {response.status_code}")
            return None

        data = response.json()
        # Unwrap KOI envelope if present
        if "data" in data and "request_id" in data:
            data = data["data"]

        return {
            "hectares": data.get("hectares"),
            "unit": data.get("unit", "ha"),
            "derivation": data.get("derivation", {}),
            "citation": data.get("citations", [{}])[0] if data.get("citations") else None
        }

    except httpx.TimeoutException:
        logger.warning(f"Timeout deriving hectares for {iri}")
        return None
    except Exception as e:
        logger.warning(f"Error deriving hectares for {iri}: {e}")
        return None


async def enrich_projects_with_offchain_metrics(
    projects: List[Dict[str, Any]],
    force_refresh: bool = False
) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Enrich projects with off-chain hectares metrics.
    Only enriches the first N projects to prevent long loops.

    Returns:
        tuple: (enriched_projects, warnings)
    """
    warnings: List[str] = []
    enriched_count = 0

    async with httpx.AsyncClient() as client:
        for i, project in enumerate(projects):
            # Cap enrichment to prevent long loops
            if enriched_count >= ENRICHMENT_MAX_ITEMS:
                warnings.append(
                    f"ENRICHMENT_CAPPED: Only first {ENRICHMENT_MAX_ITEMS} projects enriched"
                )
                break

            metadata = project.get("metadata", "")
            if not metadata or not metadata.startswith(METADATA_IRI_PREFIX):
                continue

            hectares_data = await derive_hectares_for_iri(
                metadata, client, force_refresh
            )

            if hectares_data:
                # Add offchain_metrics to project
                project["offchain_metrics"] = {
                    "hectares": hectares_data["hectares"],
                    "unit": hectares_data["unit"],
                    "derivation": {
                        "iri": metadata,
                        "rid": hectares_data["derivation"].get("rid"),
                        "resolver_url": hectares_data["derivation"].get("resolver_url"),
                        "content_hash": hectares_data["derivation"].get("content_hash"),
                        "json_pointer": hectares_data["derivation"].get("json_pointer"),
                        "expected_unit": hectares_data["derivation"].get("expected_unit"),
                    }
                }
                if hectares_data["citation"]:
                    project["offchain_citations"] = [hectares_data["citation"]]
                enriched_count += 1
            else:
                # No valid derivation available (blocked)
                # Do NOT add any metric - "no citation, no metric"
                pass

    if enriched_count > 0:
        logger.info(f"Enriched {enriched_count} projects with offchain metrics")

    return projects, warnings

app = FastAPI(
    title="Regen Network API",
    description="""Query Regen Network blockchain for ecological credits, carbon markets, and governance.

## Available Modules
- **Ecocredits**: Credit types, classes, projects, and batches
- **Marketplace**: Active sell orders and pricing
- **Baskets**: Pooled credit tokens
- **Bank**: Account balances
- **Governance**: Proposals and voting
- **Analytics**: Portfolio impact analysis

All queries access public blockchain data (read-only).
""",
    version="1.0.0",
    servers=[
        {"url": "https://edbc13dacfe222.lhr.life", "description": "API endpoint"}
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ECOCREDITS (4 endpoints) - Core functionality
# ============================================================================

@app.get("/ecocredits/types", summary="List credit types", tags=["Ecocredits"])
async def list_credit_types():
    """List all ecological credit types (Carbon, Biodiversity, etc.)."""
    result = await credit_tools.list_credit_types()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/classes", summary="List credit classes", tags=["Ecocredits"])
async def list_credit_classes(
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
):
    """List credit classes (methodologies for measuring ecological benefits)."""
    result = await credit_tools.list_credit_classes(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/projects", summary="List projects", tags=["Ecocredits"])
async def list_projects(
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
    include_offchain_metrics: bool = Query(
        False,
        description="If true, enrich projects with off-chain hectares from metadata IRIs. "
                    "Only enriches projects with valid Regen metadata IRIs. "
                    "Max 10 projects enriched per request. "
                    "Enforces 'no citation, no metric' - hectares only returned with full provenance."
    ),
):
    """List ecological projects that generate credits.

    When include_offchain_metrics=true, projects with Regen metadata IRIs will be
    enriched with hectares derived from the off-chain metadata resolver.
    """
    result = await credit_tools.list_projects(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Opt-in enrichment (Part B)
    if include_offchain_metrics and result.get("projects"):
        projects = result["projects"]
        enriched_projects, warnings = await enrich_projects_with_offchain_metrics(projects)
        result["projects"] = enriched_projects
        if warnings:
            result["warnings"] = warnings

    return result


@app.get("/ecocredits/batches", summary="List credit batches", tags=["Ecocredits"])
async def list_credit_batches(
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
):
    """List issued credit batches with vintage and issuance info."""
    result = await credit_tools.list_credit_batches(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# MARKETPLACE (4 endpoints) - Trading info
# ============================================================================

@app.get("/marketplace/orders", summary="List sell orders", tags=["Marketplace"])
async def list_sell_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List active sell orders on the ecocredit marketplace."""
    result = await marketplace_tools.list_sell_orders(limit, (page - 1) * limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/orders/{sell_order_id}", summary="Get sell order", tags=["Marketplace"])
async def get_sell_order(sell_order_id: int):
    """Get details of a specific sell order."""
    result = await marketplace_tools.get_sell_order(sell_order_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/orders/by-batch/{batch_denom}", summary="Orders by batch", tags=["Marketplace"])
async def list_sell_orders_by_batch(
    batch_denom: str,
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List sell orders for a specific credit batch."""
    result = await marketplace_tools.list_sell_orders_by_batch(batch_denom, limit, 0)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/allowed-denoms", summary="Allowed payment tokens", tags=["Marketplace"])
async def list_allowed_denoms():
    """List tokens accepted for marketplace payments."""
    result = await marketplace_tools.list_allowed_denoms(100, 0)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# BASKETS (4 endpoints) - Pooled credits
# ============================================================================

@app.get("/baskets", summary="List baskets", tags=["Baskets"])
async def list_baskets(
    limit: int = Query(100, ge=1, le=500, description="Max results"),
):
    """List ecocredit baskets (pooled credits as fungible tokens)."""
    try:
        result = await basket_tools.list_baskets(limit, 0)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/{basket_denom}", summary="Get basket", tags=["Baskets"])
async def get_basket(basket_denom: str):
    """Get basket details including criteria and credit type."""
    try:
        result = await basket_tools.get_basket(basket_denom)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/{basket_denom}/balances", summary="Basket contents", tags=["Baskets"])
async def list_basket_balances(basket_denom: str, limit: int = Query(100, ge=1, le=500)):
    """List credit batches held in a basket."""
    try:
        result = await basket_tools.list_basket_balances(basket_denom, limit, 0)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/fee", summary="Basket creation fee", tags=["Baskets"])
async def get_basket_fee():
    """Get fee required to create a new basket."""
    try:
        result = await basket_tools.get_basket_fee()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# BANK (5 endpoints) - Account info
# ============================================================================

@app.get("/bank/accounts/{address}", summary="Get account", tags=["Bank"])
async def get_account(address: str):
    """Get account details for a Regen address."""
    result = await bank_tools.get_account(address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/balances/{address}", summary="Get balances", tags=["Bank"])
async def get_all_balances(address: str, limit: int = Query(100, ge=1, le=200)):
    """Get all token balances for an account."""
    result = await bank_tools.get_all_balances(address, limit, 1)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/supply", summary="Total supply", tags=["Bank"])
async def get_total_supply(limit: int = Query(100, ge=1, le=200)):
    """Get total supply of all tokens."""
    result = await bank_tools.get_total_supply(limit, 1)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/supply/{denom}", summary="Token supply", tags=["Bank"])
async def get_supply_of(denom: str):
    """Get total supply of a specific token."""
    result = await bank_tools.get_supply_of(denom)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/denoms/{denom}/metadata", summary="Token metadata", tags=["Bank"])
async def get_denom_metadata(denom: str):
    """Get metadata for a token denomination."""
    result = await bank_tools.get_denom_metadata(denom)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# GOVERNANCE (5 endpoints) - Proposals and voting
# ============================================================================

@app.get("/governance/proposals", summary="List proposals", tags=["Governance"])
async def list_governance_proposals(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    proposal_status: Optional[str] = Query(None, description="Filter by status"),
):
    """List governance proposals."""
    result = await governance_tools.list_governance_proposals(page, limit, proposal_status, None, None)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}", summary="Get proposal", tags=["Governance"])
async def get_governance_proposal(proposal_id: int):
    """Get details of a governance proposal."""
    result = await governance_tools.get_governance_proposal(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/votes", summary="Proposal votes", tags=["Governance"])
async def list_governance_votes(proposal_id: int, limit: int = Query(100, ge=1, le=200)):
    """List votes on a proposal."""
    result = await governance_tools.list_governance_votes(proposal_id, 1, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/tally", summary="Vote tally", tags=["Governance"])
async def get_governance_tally_result(proposal_id: int):
    """Get current vote tally for a proposal."""
    result = await governance_tools.get_governance_tally_result(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/community-pool", summary="Community pool", tags=["Governance"])
async def get_community_pool():
    """Get community pool balance."""
    result = await distribution_tools.get_community_pool()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# ANALYTICS (3 endpoints) - Advanced analysis
# ============================================================================

@app.get("/analytics/portfolio/{address}", summary="Portfolio impact", tags=["Analytics"])
async def analyze_portfolio_impact(
    address: str,
    analysis_type: str = Query("full", description="full, carbon, biodiversity, or diversification"),
):
    """Analyze ecological impact of a portfolio with recommendations."""
    if analysis_type not in ["full", "carbon", "biodiversity", "diversification"]:
        raise HTTPException(status_code=400, detail="Invalid analysis_type")
    result = await analytics_tools.analyze_portfolio_impact(address, analysis_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/analytics/market-trends", summary="Market trends", tags=["Analytics"])
async def analyze_market_trends(
    time_period: str = Query("30d", description="7d, 30d, 90d, or 1y"),
    credit_types: Optional[str] = Query(None, description="Comma-separated: C,BIO"),
):
    """Analyze market trends with price and volume analysis."""
    if time_period not in ["7d", "30d", "90d", "1y"]:
        raise HTTPException(status_code=400, detail="Invalid time_period")
    credit_types_list = [ct.strip().upper() for ct in credit_types.split(",")] if credit_types else None
    result = await analytics_tools.analyze_market_trends(time_period, credit_types_list)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


class MethodologyComparisonRequest(BaseModel):
    class_ids: List[str] = Field(..., min_length=2, description="Credit class IDs to compare")


@app.post("/analytics/compare-methodologies", summary="Compare methodologies", tags=["Analytics"])
async def compare_credit_methodologies(request: MethodologyComparisonRequest):
    """Compare credit class methodologies with investment recommendations."""
    result = await analytics_tools.compare_credit_methodologies(request.class_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# INFO (1 endpoint)
# ============================================================================

@app.get("/", summary="API info", tags=["Info"])
async def root():
    """Get API information and available endpoints."""
    return {
        "name": "Regen Network API",
        "version": "1.0.0",
        "description": "Query Regen Network for ecological credits, carbon markets, and governance",
        "endpoints": 26,
        "modules": ["Ecocredits", "Marketplace", "Baskets", "Bank", "Governance", "Analytics"],
    }


def main():
    print("=" * 60)
    print("Regen Network API (Slim - 26 endpoints)")
    print("=" * 60)
    print("Local:   http://localhost:8005")
    print("Docs:    http://localhost:8005/docs")
    print("Schema:  http://localhost:8005/openapi.json")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")


if __name__ == "__main__":
    main()
