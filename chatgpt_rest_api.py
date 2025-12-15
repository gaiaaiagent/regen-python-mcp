#!/usr/bin/env python3
"""REST API wrapper for ChatGPT Custom GPT integration.

This provides HTTP endpoints that wrap the MCP server's functionality,
allowing ChatGPT to interact with Regen Network blockchain data via Custom GPT Actions.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional, Union

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from mcp_server.tools import (
    bank_tools,
    distribution_tools,
    governance_tools,
    marketplace_tools,
    basket_tools,
    credit_tools,
    analytics_tools,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Regen Network API",
    description="""Query the Regen Network blockchain for ecological credits, governance, and marketplace data.

This API provides access to:
- **Bank**: Account balances and token information
- **Distribution**: Validator rewards and delegation info
- **Governance**: Proposals, votes, and deposits
- **Marketplace**: Credit sell orders and allowed tokens
- **Ecocredits**: Credit types, classes, projects, and batches
- **Baskets**: Ecocredit basket operations
- **Analytics**: Portfolio impact analysis and market trends

All queries are read-only and access public blockchain data.
""",
    version="1.0.0",
    servers=[
        {"url": "https://regen.gaiaai.xyz/ledger", "description": "Production endpoint"}
    ],
)

# Enable CORS for ChatGPT and browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================


class MethodologyComparisonRequest(BaseModel):
    class_ids: List[str] = Field(
        ...,
        description="List of credit class IDs to compare (at least 2)",
        min_items=2
    )


# ============================================================================
# API Root
# ============================================================================


@app.get("/", summary="API information")
async def root():
    """Get API information and available endpoints."""
    return {
        "name": "Regen Network API",
        "version": "1.0.0",
        "description": "Query Regen Network blockchain for ecological credits, governance, and marketplace data",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "modules": {
            "bank": "/bank - Account balances and token info (11 endpoints)",
            "distribution": "/distribution - Validator rewards and delegation (9 endpoints)",
            "governance": "/governance - Proposals, votes, deposits (8 endpoints)",
            "marketplace": "/marketplace - Sell orders and allowed tokens (5 endpoints)",
            "ecocredits": "/ecocredits - Credit types, classes, projects, batches (4 endpoints)",
            "baskets": "/baskets - Ecocredit basket operations (5 endpoints)",
            "analytics": "/analytics - Portfolio analysis and market trends (3 endpoints)",
        },
        "total_endpoints": 45,
    }


# ============================================================================
# Bank Module Endpoints (11)
# ============================================================================


@app.get("/bank/accounts", summary="List all accounts", tags=["Bank"])
async def list_accounts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all accounts on Regen Network with pagination."""
    result = await bank_tools.list_accounts(page, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/accounts/{address}", summary="Get account details", tags=["Bank"])
async def get_account(address: str):
    """Get detailed information for a specific account.

    Args:
        address: Cosmos bech32 address (e.g., regen1abc...)
    """
    result = await bank_tools.get_account(address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/balance", summary="Get token balance", tags=["Bank"])
async def get_balance(
    address: str = Query(..., description="Account address (e.g., regen1abc...)"),
    denom: str = Query(..., description="Token denomination (e.g., uregen)"),
):
    """Get balance of a specific token for an account."""
    result = await bank_tools.get_balance(address, denom)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/balances/{address}", summary="Get all balances", tags=["Bank"])
async def get_all_balances(
    address: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get all token balances for an account."""
    result = await bank_tools.get_all_balances(address, limit, page)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/spendable/{address}", summary="Get spendable balances", tags=["Bank"])
async def get_spendable_balances(
    address: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get spendable (unlocked) balances for an account."""
    result = await bank_tools.get_spendable_balances(address, limit, page)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/supply", summary="Get total supply", tags=["Bank"])
async def get_total_supply(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get total supply of all tokens on the network."""
    result = await bank_tools.get_total_supply(limit, page)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/supply/{denom}", summary="Get supply of token", tags=["Bank"])
async def get_supply_of(denom: str):
    """Get total supply of a specific token denomination."""
    result = await bank_tools.get_supply_of(denom)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/params", summary="Get bank parameters", tags=["Bank"])
async def get_bank_params():
    """Get bank module parameters."""
    result = await bank_tools.get_bank_params()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/denoms/metadata", summary="List token metadata", tags=["Bank"])
async def get_denoms_metadata(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get metadata for all registered token denominations."""
    result = await bank_tools.get_denoms_metadata(page, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/denoms/{denom}/metadata", summary="Get token metadata", tags=["Bank"])
async def get_denom_metadata(denom: str):
    """Get metadata for a specific token denomination."""
    result = await bank_tools.get_denom_metadata(denom)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/denoms/{denom}/owners", summary="Get token holders", tags=["Bank"])
async def get_denom_owners(
    denom: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get all holders of a specific token denomination."""
    result = await bank_tools.get_denom_owners(denom, page, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Distribution Module Endpoints (9)
# ============================================================================


@app.get("/distribution/params", summary="Get distribution parameters", tags=["Distribution"])
async def get_distribution_params():
    """Get distribution module parameters."""
    result = await distribution_tools.get_distribution_params()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/validators/{validator_address}/rewards", summary="Get validator rewards", tags=["Distribution"])
async def get_validator_outstanding_rewards(validator_address: str):
    """Get outstanding rewards for a validator.

    Args:
        validator_address: Validator operator address (e.g., regenvaloper1...)
    """
    result = await distribution_tools.get_validator_outstanding_rewards(validator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/validators/{validator_address}/commission", summary="Get validator commission", tags=["Distribution"])
async def get_validator_commission(validator_address: str):
    """Get commission information for a validator."""
    result = await distribution_tools.get_validator_commission(validator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/validators/{validator_address}/slashes", summary="Get validator slashes", tags=["Distribution"])
async def get_validator_slashes(
    validator_address: str,
    starting_height: Optional[int] = Query(None, description="Starting block height"),
    ending_height: Optional[int] = Query(None, description="Ending block height"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get slashing events for a validator within an optional block range."""
    result = await distribution_tools.get_validator_slashes(
        validator_address, starting_height, ending_height, page, limit
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/delegators/{delegator_address}/rewards/{validator_address}", summary="Get delegation rewards", tags=["Distribution"])
async def get_delegation_rewards(delegator_address: str, validator_address: str):
    """Get rewards for a specific delegator-validator pair."""
    result = await distribution_tools.get_delegation_rewards(delegator_address, validator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/delegators/{delegator_address}/rewards", summary="Get total delegation rewards", tags=["Distribution"])
async def get_delegation_total_rewards(delegator_address: str):
    """Get total delegation rewards for a delegator across all validators."""
    result = await distribution_tools.get_delegation_total_rewards(delegator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/delegators/{delegator_address}/validators", summary="Get delegator validators", tags=["Distribution"])
async def get_delegator_validators(delegator_address: str):
    """Get list of validators a delegator is bonded to."""
    result = await distribution_tools.get_delegator_validators(delegator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/delegators/{delegator_address}/withdraw-address", summary="Get withdraw address", tags=["Distribution"])
async def get_delegator_withdraw_address(delegator_address: str):
    """Get the withdraw address for a delegator."""
    result = await distribution_tools.get_delegator_withdraw_address(delegator_address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/community-pool", summary="Get community pool", tags=["Distribution"])
async def get_community_pool():
    """Get the community pool balance."""
    result = await distribution_tools.get_community_pool()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Governance Module Endpoints (8)
# ============================================================================


@app.get("/governance/proposals", summary="List proposals", tags=["Governance"])
async def list_governance_proposals(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
    proposal_status: Optional[str] = Query(None, description="Filter by status (e.g., PROPOSAL_STATUS_PASSED)"),
    voter: Optional[str] = Query(None, description="Filter by voter address"),
    depositor: Optional[str] = Query(None, description="Filter by depositor address"),
):
    """List governance proposals with optional filters."""
    result = await governance_tools.list_governance_proposals(page, limit, proposal_status, voter, depositor)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}", summary="Get proposal", tags=["Governance"])
async def get_governance_proposal(proposal_id: int):
    """Get details of a specific governance proposal."""
    result = await governance_tools.get_governance_proposal(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/votes", summary="List proposal votes", tags=["Governance"])
async def list_governance_votes(
    proposal_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all votes for a specific proposal."""
    result = await governance_tools.list_governance_votes(proposal_id, page, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/votes/{voter}", summary="Get specific vote", tags=["Governance"])
async def get_governance_vote(proposal_id: int, voter: str):
    """Get a specific vote on a proposal."""
    result = await governance_tools.get_governance_vote(proposal_id, voter)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/deposits", summary="List proposal deposits", tags=["Governance"])
async def list_governance_deposits(
    proposal_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all deposits for a specific proposal."""
    result = await governance_tools.list_governance_deposits(proposal_id, page, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/deposits/{depositor}", summary="Get specific deposit", tags=["Governance"])
async def get_governance_deposit(proposal_id: int, depositor: str):
    """Get a specific deposit on a proposal."""
    result = await governance_tools.get_governance_deposit(proposal_id, depositor)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposals/{proposal_id}/tally", summary="Get proposal tally", tags=["Governance"])
async def get_governance_tally_result(proposal_id: int):
    """Get the current vote tally for a proposal."""
    result = await governance_tools.get_governance_tally_result(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/params/{params_type}", summary="Get governance parameters", tags=["Governance"])
async def get_governance_params(params_type: str):
    """Get governance parameters by type (voting, deposit, or tally)."""
    if params_type not in ["voting", "deposit", "tally"]:
        raise HTTPException(
            status_code=400,
            detail="params_type must be one of: voting, deposit, tally"
        )
    result = await governance_tools.get_governance_params(params_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Marketplace Module Endpoints (5)
# ============================================================================


@app.get("/marketplace/orders", summary="List sell orders", tags=["Marketplace"])
async def list_sell_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all active sell orders on the ecocredit marketplace."""
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


@app.get("/marketplace/orders/by-batch/{batch_denom}", summary="List orders by batch", tags=["Marketplace"])
async def list_sell_orders_by_batch(
    batch_denom: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all sell orders for a specific credit batch."""
    result = await marketplace_tools.list_sell_orders_by_batch(batch_denom, limit, (page - 1) * limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/orders/by-seller/{seller}", summary="List orders by seller", tags=["Marketplace"])
async def list_sell_orders_by_seller(
    seller: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all sell orders created by a specific seller."""
    result = await marketplace_tools.list_sell_orders_by_seller(seller, limit, (page - 1) * limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/allowed-denoms", summary="List allowed payment tokens", tags=["Marketplace"])
async def list_allowed_denoms(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """List all token denominations allowed for marketplace payments."""
    result = await marketplace_tools.list_allowed_denoms(limit, (page - 1) * limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Ecocredits Module Endpoints (4)
# ============================================================================


@app.get("/ecocredits/types", summary="List credit types", tags=["Ecocredits"])
async def list_credit_types():
    """List all enabled credit types (e.g., Carbon, Biodiversity).

    Credit types represent fundamental categories of ecological benefits
    that can be measured and tokenized.
    """
    result = await credit_tools.list_credit_types()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/classes", summary="List credit classes", tags=["Ecocredits"])
async def list_credit_classes(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all credit classes (methodologies).

    Credit classes define specific methodologies for measuring and verifying
    ecological benefits within a credit type.
    """
    result = await credit_tools.list_credit_classes(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/projects", summary="List projects", tags=["Ecocredits"])
async def list_projects(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all registered ecological projects.

    Projects represent specific ecological initiatives that generate credits
    under approved methodologies.
    """
    result = await credit_tools.list_projects(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/batches", summary="List credit batches", tags=["Ecocredits"])
async def list_credit_batches(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all issued credit batches.

    Credit batches represent specific issuances of credits from projects,
    each with a unique denomination and vintage period.
    """
    result = await credit_tools.list_credit_batches(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Baskets Module Endpoints (5)
# ============================================================================


@app.get("/baskets", summary="List baskets", tags=["Baskets"])
async def list_baskets(
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all active ecocredit baskets.

    Baskets are pools of credits that can be traded as fungible tokens.
    """
    try:
        result = await basket_tools.list_baskets(limit, offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/{basket_denom}", summary="Get basket", tags=["Baskets"])
async def get_basket(basket_denom: str):
    """Get detailed information about a specific basket."""
    try:
        result = await basket_tools.get_basket(basket_denom)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/{basket_denom}/balances", summary="List basket balances", tags=["Baskets"])
async def list_basket_balances(
    basket_denom: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all credit batches held in a specific basket."""
    try:
        result = await basket_tools.list_basket_balances(basket_denom, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/{basket_denom}/balances/{batch_denom}", summary="Get basket balance", tags=["Baskets"])
async def get_basket_balance(basket_denom: str, batch_denom: str):
    """Get the balance of a specific credit batch in a basket."""
    try:
        result = await basket_tools.get_basket_balance(basket_denom, batch_denom)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/baskets/fee", summary="Get basket fee", tags=["Baskets"])
async def get_basket_fee():
    """Get the current fee required to create a new basket."""
    try:
        result = await basket_tools.get_basket_fee()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Analytics Module Endpoints (3)
# ============================================================================


@app.get("/analytics/portfolio/{address}", summary="Analyze portfolio impact", tags=["Analytics"])
async def analyze_portfolio_impact(
    address: str,
    analysis_type: str = Query(
        "full",
        description="Analysis type: full, carbon, biodiversity, or diversification"
    ),
):
    """Analyze the ecological impact of a portfolio.

    Provides comprehensive portfolio analysis including:
    - Ecological impact scores
    - Carbon and biodiversity metrics
    - Portfolio diversification analysis
    - Optimization recommendations

    Args:
        address: Regen Network address (e.g., regen1...)
        analysis_type: Type of analysis to perform
    """
    if analysis_type not in ["full", "carbon", "biodiversity", "diversification"]:
        raise HTTPException(
            status_code=400,
            detail="analysis_type must be one of: full, carbon, biodiversity, diversification"
        )
    result = await analytics_tools.analyze_portfolio_impact(address, analysis_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/analytics/market-trends", summary="Analyze market trends", tags=["Analytics"])
async def analyze_market_trends(
    time_period: str = Query(
        "30d",
        description="Time period: 7d, 30d, 90d, or 1y"
    ),
    credit_types: Optional[str] = Query(
        None,
        description="Comma-separated list of credit types to analyze (e.g., 'C,BIO')"
    ),
):
    """Analyze market trends across credit types.

    Provides market analysis including:
    - Price trends and volatility
    - Volume and liquidity analysis
    - Market sentiment indicators
    - Trend projections

    Args:
        time_period: Time period for analysis
        credit_types: Optional filter for specific credit types
    """
    if time_period not in ["7d", "30d", "90d", "1y"]:
        raise HTTPException(
            status_code=400,
            detail="time_period must be one of: 7d, 30d, 90d, 1y"
        )

    credit_types_list = None
    if credit_types:
        credit_types_list = [ct.strip().upper() for ct in credit_types.split(",")]

    result = await analytics_tools.analyze_market_trends(time_period, credit_types_list)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/analytics/compare-methodologies", summary="Compare credit methodologies", tags=["Analytics"])
async def compare_credit_methodologies(request: MethodologyComparisonRequest):
    """Compare different credit class methodologies.

    Provides methodology comparison including:
    - Methodology quality scores
    - Market performance metrics
    - Investment recommendations
    - Risk analysis

    Args:
        class_ids: List of at least 2 credit class IDs to compare
    """
    result = await analytics_tools.compare_credit_methodologies(request.class_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Server Entry Point
# ============================================================================


def main():
    """Run the REST API server."""
    print("=" * 70)
    print("Regen Network REST API for ChatGPT")
    print("=" * 70)
    print("Host:     localhost")
    print("Port:     8004")
    print("Endpoint: http://localhost:8004")
    print("Docs:     http://localhost:8004/docs")
    print("OpenAPI:  http://localhost:8004/openapi.json")
    print("=" * 70)
    print("")
    print("Next Steps for ChatGPT Integration:")
    print("1. Create tunnel: ssh -R 80:localhost:8004 nokey@localhost.run")
    print("2. Create Custom GPT in ChatGPT")
    print("3. Add Action using OpenAPI schema from /openapi.json")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")


if __name__ == "__main__":
    main()
