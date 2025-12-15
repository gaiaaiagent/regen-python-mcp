#!/usr/bin/env python3
"""Consolidated REST API v2 for ChatGPT - Full functionality in 25 endpoints.

This version uses smart query parameters and comprehensive responses to provide
ALL functionality from the original 45+ endpoints while staying under ChatGPT's
30 endpoint limit.

Key consolidations:
- Marketplace orders: 4 endpoints -> 1 (query params for id/batch/seller)
- Bank balances: 3 endpoints -> 1 (query params for denom/spendable)
- Distribution validator: 3 endpoints -> 1 (returns rewards+commission+slashes)
- Distribution delegator: 4 endpoints -> 1 (returns all delegation info)
- Governance params: 3 endpoints -> 1 (query param for type)
- Governance proposal: 5 endpoints -> 1 (comprehensive response)
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, List
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Query, Path as PathParam
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums for query parameters
# ============================================================================

class GovParamsType(str, Enum):
    voting = "voting"
    deposit = "deposit"
    tally = "tally"
    all = "all"


class ProposalStatus(str, Enum):
    unspecified = "PROPOSAL_STATUS_UNSPECIFIED"
    deposit_period = "PROPOSAL_STATUS_DEPOSIT_PERIOD"
    voting_period = "PROPOSAL_STATUS_VOTING_PERIOD"
    passed = "PROPOSAL_STATUS_PASSED"
    rejected = "PROPOSAL_STATUS_REJECTED"
    failed = "PROPOSAL_STATUS_FAILED"


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Regen Network API v2",
    description="""Query Regen Network blockchain for ecological credits, carbon markets, governance, and staking.

## Full Functionality in 25 Endpoints

This API consolidates 45+ queries into 25 smart endpoints using query parameters:

### Modules
- **Ecocredits** (4): Credit types, classes, projects, batches
- **Marketplace** (2): Sell orders (flexible filtering), allowed denoms
- **Baskets** (3): Basket tokens with optional balance inclusion
- **Bank** (5): Accounts, balances, supply, metadata, params
- **Distribution** (4): Staking rewards, validator info, delegator info
- **Governance** (4): Proposals, voting, params, community pool
- **Analytics** (3): Portfolio analysis, market trends, methodology comparison

### Smart Query Parameters
Many endpoints accept optional parameters to filter or expand results:
- `?id=` - Get specific item instead of list
- `?include_X=true` - Include related data in response
- `?denom=` / `?batch=` / `?seller=` - Filter by specific values

All queries access public blockchain data (read-only).
""",
    version="2.0.0",
    servers=[
        {"url": "https://aa3c102a1a9abf.lhr.life", "description": "API endpoint"}
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
# ROOT (1 endpoint)
# ============================================================================

@app.get("/", summary="API Info", tags=["Info"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "name": "Regen Network API v2",
        "version": "2.0.0",
        "description": "Full Regen Network blockchain access - 45 queries consolidated into 25 endpoints",
        "endpoints": 25,
        "modules": {
            "ecocredits": 4,
            "marketplace": 2,
            "baskets": 3,
            "bank": 5,
            "distribution": 4,
            "governance": 4,
            "analytics": 3,
        }
    }


# ============================================================================
# ECOCREDITS (4 endpoints) - Unchanged
# ============================================================================

@app.get("/ecocredits/types", summary="List credit types", tags=["Ecocredits"])
async def list_credit_types():
    """List all ecological credit types enabled on Regen (Carbon, Biodiversity, etc.)."""
    result = await credit_tools.list_credit_types()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/classes", summary="List credit classes", tags=["Ecocredits"])
async def list_credit_classes(
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List credit classes (methodologies for measuring ecological benefits)."""
    result = await credit_tools.list_credit_classes(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/projects", summary="List projects", tags=["Ecocredits"])
async def list_projects(
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List ecological projects registered on Regen that generate credits."""
    result = await credit_tools.list_projects(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/ecocredits/batches", summary="List credit batches", tags=["Ecocredits"])
async def list_credit_batches(
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List issued credit batches with vintage dates and supply info."""
    result = await credit_tools.list_credit_batches(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# MARKETPLACE (2 endpoints) - Consolidated from 5
# ============================================================================

@app.get("/marketplace/orders", summary="Query sell orders", tags=["Marketplace"])
async def query_marketplace_orders(
    id: Optional[int] = Query(None, description="Get specific order by ID"),
    batch: Optional[str] = Query(None, description="Filter orders by credit batch denom"),
    seller: Optional[str] = Query(None, description="Filter orders by seller address"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query marketplace sell orders. Use query params to filter:
    - No params: List all active orders
    - ?id=123: Get specific order by ID
    - ?batch=C01-001-...: Filter orders for a credit batch
    - ?seller=regen1...: Filter orders by seller address
    """
    if id is not None:
        result = await marketplace_tools.get_sell_order(id)
    elif batch is not None:
        result = await marketplace_tools.list_sell_orders_by_batch(batch, page, limit)
    elif seller is not None:
        result = await marketplace_tools.list_sell_orders_by_seller(seller, page, limit)
    else:
        result = await marketplace_tools.list_sell_orders(page, limit)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/marketplace/denoms", summary="Allowed payment tokens", tags=["Marketplace"])
async def list_allowed_denoms():
    """List token denominations accepted for marketplace payments."""
    result = await marketplace_tools.list_allowed_denoms()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# BASKETS (3 endpoints) - Consolidated from 5
# ============================================================================

@app.get("/baskets", summary="List baskets", tags=["Baskets"])
async def list_baskets(
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List ecocredit baskets (pooled credits represented as fungible tokens)."""
    result = await basket_tools.list_baskets(limit, offset)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/baskets/fee", summary="Basket creation fee", tags=["Baskets"])
async def get_basket_fee():
    """Get the fee required to create a new ecocredit basket."""
    result = await basket_tools.get_basket_fee()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/baskets/{denom}", summary="Get basket details", tags=["Baskets"])
async def get_basket_details(
    denom: str = PathParam(..., description="Basket token denomination"),
    include_balances: bool = Query(False, description="Include credit batches held in basket"),
    batch: Optional[str] = Query(None, description="Get balance for specific batch only"),
    limit: int = Query(100, ge=1, le=500, description="Max balances to return"),
    offset: int = Query(0, ge=0, description="Skip balances"),
):
    """Get basket details. Options:
    - Basic: Just basket info (criteria, credit type, etc.)
    - ?include_balances=true: Also return all credit batches in the basket
    - ?include_balances=true&batch=X: Get balance for a specific batch
    """
    basket_result = await basket_tools.get_basket(denom)
    if "error" in basket_result:
        raise HTTPException(status_code=400, detail=basket_result["error"])

    response = {"basket": basket_result}

    if include_balances:
        if batch:
            balance_result = await basket_tools.get_basket_balance(denom, batch)
            if "error" not in balance_result:
                response["batch_balance"] = balance_result
        else:
            balances_result = await basket_tools.list_basket_balances(denom, limit, offset)
            if "error" not in balances_result:
                response["balances"] = balances_result

    return response


# ============================================================================
# BANK (5 endpoints) - Consolidated from 11
# ============================================================================

@app.get("/bank/accounts", summary="Query accounts", tags=["Bank"])
async def query_bank_accounts(
    address: Optional[str] = Query(None, description="Get specific account by address"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query Regen accounts. Options:
    - No params: List all accounts (paginated)
    - ?address=regen1...: Get specific account details
    """
    if address:
        result = await bank_tools.get_account(address)
    else:
        result = await bank_tools.list_accounts(page, limit)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/balances/{address}", summary="Get account balances", tags=["Bank"])
async def get_account_balances(
    address: str = PathParam(..., description="Regen account address"),
    denom: Optional[str] = Query(None, description="Get balance for specific token only"),
    spendable: bool = Query(False, description="Return only spendable balances"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Get token balances for an account. Options:
    - Basic: All balances for the account
    - ?denom=uregen: Balance for specific token only
    - ?spendable=true: Only spendable balances (excludes vesting/locked)
    """
    if spendable:
        result = await bank_tools.get_spendable_balances(address, page, limit)
    elif denom:
        result = await bank_tools.get_balance(address, denom)
    else:
        result = await bank_tools.get_all_balances(address, page, limit)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/supply", summary="Query token supply", tags=["Bank"])
async def query_token_supply(
    denom: Optional[str] = Query(None, description="Get supply for specific token"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query total token supply. Options:
    - No params: Total supply of all tokens
    - ?denom=uregen: Supply of specific token
    """
    if denom:
        result = await bank_tools.get_supply_of(denom)
    else:
        result = await bank_tools.get_total_supply(page, limit)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/bank/metadata", summary="Query token metadata", tags=["Bank"])
async def query_token_metadata(
    denom: Optional[str] = Query(None, description="Get metadata for specific token"),
    include_owners: bool = Query(False, description="Include list of token holders (requires denom)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query token metadata (name, symbol, decimals). Options:
    - No params: Metadata for all tokens
    - ?denom=uregen: Metadata for specific token
    - ?denom=uregen&include_owners=true: Also include token holders
    """
    if denom:
        metadata_result = await bank_tools.get_denom_metadata(denom)
        if "error" in metadata_result:
            raise HTTPException(status_code=400, detail=metadata_result["error"])

        response = {"metadata": metadata_result}

        if include_owners:
            owners_result = await bank_tools.get_denom_owners(denom, page, limit)
            if "error" not in owners_result:
                response["owners"] = owners_result

        return response
    else:
        result = await bank_tools.get_denoms_metadata(page, limit)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result


@app.get("/bank/params", summary="Bank module params", tags=["Bank"])
async def get_bank_params():
    """Get bank module parameters (send enabled, default settings)."""
    result = await bank_tools.get_bank_params()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# DISTRIBUTION (4 endpoints) - Consolidated from 9
# ============================================================================

@app.get("/distribution/params", summary="Distribution params", tags=["Distribution"])
async def get_distribution_params():
    """Get distribution module parameters (community tax, base proposer reward, etc.)."""
    result = await distribution_tools.get_distribution_params()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/pool", summary="Community pool", tags=["Distribution"])
async def get_community_pool():
    """Get community pool balance (funds available for governance spending)."""
    result = await distribution_tools.get_community_pool()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/distribution/validator/{address}", summary="Validator distribution info", tags=["Distribution"])
async def get_validator_distribution(
    address: str = PathParam(..., description="Validator operator address (regenvaloper1...)"),
    starting_height: Optional[int] = Query(None, ge=0, description="Start block for slashes"),
    ending_height: Optional[int] = Query(None, ge=0, description="End block for slashes"),
    page: int = Query(1, ge=1, description="Page for slashes"),
    limit: int = Query(100, ge=1, le=200, description="Limit for slashes"),
):
    """Get comprehensive validator distribution info in one call:
    - Outstanding rewards
    - Accumulated commission
    - Slashing events (with optional height range filter)
    """
    # Fetch all three in parallel
    rewards_task = distribution_tools.get_validator_outstanding_rewards(address)
    commission_task = distribution_tools.get_validator_commission(address)
    slashes_task = distribution_tools.get_validator_slashes(
        address, starting_height, ending_height, page, limit
    )

    rewards, commission, slashes = await asyncio.gather(
        rewards_task, commission_task, slashes_task
    )

    return {
        "validator_address": address,
        "outstanding_rewards": rewards if "error" not in rewards else None,
        "commission": commission if "error" not in commission else None,
        "slashes": slashes if "error" not in slashes else None,
    }


@app.get("/distribution/delegator/{address}", summary="Delegator distribution info", tags=["Distribution"])
async def get_delegator_distribution(
    address: str = PathParam(..., description="Delegator account address (regen1...)"),
    validator: Optional[str] = Query(None, description="Get rewards for specific validator only"),
):
    """Get delegator staking rewards info. Options:
    - Basic: Total rewards, list of validators, withdraw address
    - ?validator=regenvaloper1...: Rewards from specific validator only
    """
    if validator:
        result = await distribution_tools.get_delegation_rewards(address, validator)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {
            "delegator_address": address,
            "validator_address": validator,
            "rewards": result
        }
    else:
        # Fetch all delegator info in parallel
        total_task = distribution_tools.get_delegation_total_rewards(address)
        validators_task = distribution_tools.get_delegator_validators(address)
        withdraw_task = distribution_tools.get_delegator_withdraw_address(address)

        total, validators, withdraw = await asyncio.gather(
            total_task, validators_task, withdraw_task
        )

        return {
            "delegator_address": address,
            "total_rewards": total if "error" not in total else None,
            "validators": validators if "error" not in validators else None,
            "withdraw_address": withdraw if "error" not in withdraw else None,
        }


# ============================================================================
# GOVERNANCE (4 endpoints) - Consolidated from 8
# ============================================================================

@app.get("/governance/params", summary="Governance params", tags=["Governance"])
async def get_governance_params(
    type: Optional[GovParamsType] = Query(None, description="Param type: voting, deposit, tally, or all"),
):
    """Get governance module parameters. Options:
    - No params or ?type=all: All parameter types
    - ?type=voting: Voting period, quorum, threshold
    - ?type=deposit: Min deposit, max deposit period
    - ?type=tally: Quorum, threshold, veto threshold
    """
    if type and type != GovParamsType.all:
        result = await governance_tools.get_governance_params(type.value)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    else:
        # Get all params in parallel
        voting_task = governance_tools.get_governance_params("voting")
        deposit_task = governance_tools.get_governance_params("deposit")
        tally_task = governance_tools.get_governance_params("tally")

        voting, deposit, tally = await asyncio.gather(
            voting_task, deposit_task, tally_task
        )

        return {
            "voting": voting if "error" not in voting else None,
            "deposit": deposit if "error" not in deposit else None,
            "tally": tally if "error" not in tally else None,
        }


@app.get("/governance/proposals", summary="Query proposals", tags=["Governance"])
async def query_governance_proposals(
    id: Optional[int] = Query(None, description="Get specific proposal by ID"),
    status: Optional[ProposalStatus] = Query(None, description="Filter by status"),
    voter: Optional[str] = Query(None, description="Filter proposals this address voted on"),
    depositor: Optional[str] = Query(None, description="Filter proposals this address deposited to"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query governance proposals. Options:
    - No params: List all proposals
    - ?id=123: Get specific proposal
    - ?status=PROPOSAL_STATUS_VOTING_PERIOD: Filter by status
    - ?voter=regen1...: Proposals the address voted on
    - ?depositor=regen1...: Proposals the address deposited to
    """
    if id is not None:
        result = await governance_tools.get_governance_proposal(id)
    else:
        result = await governance_tools.list_governance_proposals(
            proposal_status=status.value if status else None,
            voter=voter,
            depositor=depositor,
            page=page,
            limit=limit
        )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/governance/proposal/{id}/full", summary="Full proposal details", tags=["Governance"])
async def get_proposal_full_details(
    id: int = PathParam(..., description="Proposal ID"),
    voter: Optional[str] = Query(None, description="Filter votes to specific voter"),
    depositor: Optional[str] = Query(None, description="Filter deposits to specific depositor"),
    page: int = Query(1, ge=1, description="Page for votes/deposits lists"),
    limit: int = Query(100, ge=1, le=200, description="Limit for votes/deposits"),
):
    """Get comprehensive proposal info in one call:
    - Proposal details
    - Votes (all, or filtered to specific voter)
    - Deposits (all, or filtered to specific depositor)
    - Current tally results
    """
    # Fetch proposal first (we need this to succeed)
    proposal = await governance_tools.get_governance_proposal(id)
    if "error" in proposal:
        raise HTTPException(status_code=404, detail=f"Proposal {id} not found")

    # Fetch votes, deposits, tally in parallel
    if voter:
        votes_task = governance_tools.get_governance_vote(id, voter)
    else:
        votes_task = governance_tools.list_governance_votes(id, page, limit)

    if depositor:
        deposits_task = governance_tools.get_governance_deposit(id, depositor)
    else:
        deposits_task = governance_tools.list_governance_deposits(id, page, limit)

    tally_task = governance_tools.get_governance_tally_result(id)

    votes, deposits, tally = await asyncio.gather(
        votes_task, deposits_task, tally_task
    )

    return {
        "proposal": proposal,
        "votes": votes if "error" not in votes else None,
        "deposits": deposits if "error" not in deposits else None,
        "tally": tally if "error" not in tally else None,
    }


@app.get("/governance/pool", summary="Community pool", tags=["Governance"])
async def get_governance_community_pool():
    """Get community pool balance (alias for /distribution/pool)."""
    result = await distribution_tools.get_community_pool()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# ANALYTICS (3 endpoints) - Unchanged
# ============================================================================

@app.get("/analytics/portfolio/{address}", summary="Portfolio impact analysis", tags=["Analytics"])
async def analyze_portfolio_impact(
    address: str = PathParam(..., description="Account address to analyze"),
    analysis_type: str = Query("full", description="Analysis type: full, credits, or summary"),
):
    """Analyze ecological impact of an address's credit holdings."""
    result = await analytics_tools.analyze_portfolio_impact(address, analysis_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/analytics/trends", summary="Market trends", tags=["Analytics"])
async def analyze_market_trends(
    credit_types: Optional[str] = Query(None, description="Comma-separated credit types to analyze"),
    time_period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
):
    """Analyze market trends across credit types."""
    types_list = credit_types.split(",") if credit_types else None
    result = await analytics_tools.analyze_market_trends(types_list, time_period)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


class MethodologyCompareRequest(BaseModel):
    """Request body for methodology comparison."""
    class_ids: List[str] = Field(..., description="Credit class IDs to compare", min_length=2)


@app.post("/analytics/compare", summary="Compare methodologies", tags=["Analytics"])
async def compare_credit_methodologies(request: MethodologyCompareRequest):
    """Compare different credit class methodologies for impact efficiency."""
    result = await analytics_tools.compare_credit_methodologies(request.class_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Regen Network API v2 (25 endpoints - Full functionality)")
    print("=" * 60)
    print("Local:   http://localhost:8006")
    print("Docs:    http://localhost:8006/docs")
    print("Schema:  http://localhost:8006/openapi.json")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8006)
