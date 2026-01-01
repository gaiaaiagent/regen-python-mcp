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
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import httpx
import os

from mcp_server.tools import (
    bank_tools,
    distribution_tools,
    governance_tools,
    marketplace_tools,
    basket_tools,
    credit_tools,
    analytics_tools,
)
from mcp_server.middleware import (
    RequestIDMiddleware,
    TransientError,
    GovernanceUnavailableError,
    get_request_id,
    add_tool_trace,
    create_envelope,
    create_error_envelope,
    extract_pagination_from_response,
    is_transient_error,
)
from mcp_server.models.response_envelope import (
    DataSource,
    create_tool_trace,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Off-chain Metadata Enrichment Configuration (Session E)
# =============================================================================
KOI_API_ENDPOINT = os.environ.get("KOI_API_ENDPOINT", "https://regen.gaiaai.xyz/api/koi")
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
        {"url": "https://regen.gaiaai.xyz/regen-api", "description": "Production API"}
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Request ID middleware for X-Request-ID header support
app.add_middleware(RequestIDMiddleware)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(TransientError)
async def transient_error_handler(request: Request, exc: TransientError):
    """Handle transient errors with 503 status and retryable flag."""
    request_id = getattr(request.state, "request_id", get_request_id())

    error_response = create_error_envelope(
        request_id=request_id,
        code=exc.code,
        message=exc.message,
        retryable=True,
        retry_after_ms=exc.retry_after_ms,
        details=exc.details,
        warnings=["This is a transient error. Please retry after the suggested delay."]
    )
    # Keep error responses consistent with the standard envelope fields used for metrics.
    error_response["data_source"] = DataSource.ON_CHAIN

    response = JSONResponse(
        status_code=503,
        content=error_response,
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["Retry-After"] = str(exc.retry_after_ms // 1000)  # seconds

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured error response."""
    request_id = getattr(request.state, "request_id", get_request_id())

    # Determine if this might be a transient error based on status code
    retryable = exc.status_code in (502, 503, 504)

    error_response = create_error_envelope(
        request_id=request_id,
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        retryable=retryable,
        retry_after_ms=5000 if retryable else None,
    )
    # Keep error responses consistent with the standard envelope fields used for metrics.
    error_response["data_source"] = DataSource.ON_CHAIN

    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )
    response.headers["X-Request-ID"] = request_id

    return response


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


@app.get("/unified-openapi.json", summary="Combined OpenAPI Schema", tags=["Info"], include_in_schema=False)
async def get_combined_openapi():
    """Get combined OpenAPI schema for both Ledger API and KOI Knowledge API.

    Use this schema when you need a single ChatGPT Action that can access both:
    - Regen Ledger API (/regen-api/*) - blockchain data
    - KOI Knowledge API (/api/koi/*) - semantic search
    """
    schema_path = Path(__file__).parent / "openapi-combined.json"
    if not schema_path.exists():
        raise HTTPException(status_code=404, detail="Combined schema not found")

    with open(schema_path) as f:
        return json.load(f)


@app.get("/summary", summary="API capabilities summary", tags=["Discovery"])
async def get_api_summary():
    """Get a complete summary of all API capabilities.

    CALL THIS FIRST to understand what information is available.
    Returns organized list of all endpoints grouped by function.
    """
    summary = {
        "name": "Regen Network Unified API",
        "description": "Query Regen Network blockchain data AND search 6,500+ documents about regenerative agriculture",
        "tip": "For questions about concepts, history, or 'what is X', use Knowledge Search. For live blockchain data, use Ledger endpoints. For 'this week', 'past week', or 'recent news', use Weekly Digest.",
        "capabilities": {
            "weekly_digest": {
                "description": "Curated weekly summary of Regen Network ecosystem activity",
                "when_to_use": "ALWAYS use for: 'this week', 'past week', 'this past week', 'recent news', 'recent activity', 'what's happening', 'summarize the week', 'weekly update', any time-based summary",
                "endpoints": {
                    "GET /api/koi/weekly-digest": "Weekly summary - USE THIS for any 'week' or 'recent' questions"
                }
            },
            "knowledge_search": {
                "description": "Search 6,500+ documents about Regen Network, regenerative agriculture, carbon credits, and ecological finance",
                "when_to_use": "Questions about concepts, explanations, history, 'what is', 'how does', background information",
                "endpoints": {
                    "POST /api/koi/query": "Semantic search - ask any question in natural language",
                    "POST /api/koi/entity": "Entity queries - resolve entity names, get relationships, find related documents (use query_type: resolve|neighborhood|documents)"
                }
            },
            "ecological_credits": {
                "description": "Query live blockchain data about carbon credits, biodiversity credits, and ecological assets",
                "when_to_use": "Questions about current credit types, classes, projects, batches, prices, supply",
                "endpoints": {
                    "GET /regen-api/ecocredits/types": "List all credit types (Carbon, Biodiversity, etc.)",
                    "GET /regen-api/ecocredits/classes": "List credit classes (methodologies)",
                    "GET /regen-api/ecocredits/projects": "List registered ecological projects",
                    "GET /regen-api/ecocredits/batches": "List issued credit batches with supply info"
                }
            },
            "marketplace": {
                "description": "Query carbon credit marketplace - sell orders, prices, trading",
                "when_to_use": "Questions about buying credits, current prices, sell orders, market activity",
                "endpoints": {
                    "GET /regen-api/marketplace/orders": "Query sell orders (filter by id, batch, seller)",
                    "GET /regen-api/marketplace/denoms": "Accepted payment tokens"
                }
            },
            "baskets": {
                "description": "Query basket tokens - pooled ecological credits",
                "when_to_use": "Questions about NCT, basket tokens, pooled credits",
                "endpoints": {
                    "GET /regen-api/baskets": "List all basket tokens",
                    "GET /regen-api/baskets/{denom}": "Get basket details and contents",
                    "GET /regen-api/baskets/fee": "Basket creation fee"
                }
            },
            "accounts_and_balances": {
                "description": "Query Regen accounts, token balances, and supply",
                "when_to_use": "Questions about specific addresses, holdings, token supply",
                "endpoints": {
                    "GET /regen-api/bank/balances/{address}": "Get account token balances",
                    "GET /regen-api/bank/accounts": "Query accounts",
                    "GET /regen-api/bank/supply": "Total token supply",
                    "GET /regen-api/bank/metadata": "Token metadata"
                }
            },
            "staking_and_rewards": {
                "description": "Query staking rewards, validators, delegations",
                "when_to_use": "Questions about staking, validators, rewards, delegations",
                "endpoints": {
                    "GET /regen-api/distribution/pool": "Community pool balance",
                    "GET /regen-api/distribution/validator/{address}": "Validator rewards and commission",
                    "GET /regen-api/distribution/delegator/{address}": "Delegator staking rewards"
                }
            },
            "governance": {
                "description": "Query governance proposals, voting, community decisions",
                "when_to_use": "Questions about proposals, voting, governance decisions",
                "endpoints": {
                    "GET /regen-api/governance/proposals": "List/filter proposals",
                    "GET /regen-api/governance/proposal/{id}/full": "Full proposal with votes and deposits",
                    "GET /regen-api/governance/params": "Governance parameters"
                }
            },
            "analytics": {
                "description": "Analyze portfolios, market trends, and compare methodologies",
                "when_to_use": "Questions about trends, portfolio analysis, methodology comparison",
                "endpoints": {
                    "GET /regen-api/analytics/trends": "Market trends by credit type",
                    "GET /regen-api/analytics/portfolio/{address}": "Portfolio ecological impact",
                    "POST /regen-api/analytics/compare": "Compare credit methodologies"
                }
            }
        }
    }

    add_tool_trace(create_tool_trace(
        tool="get_api_summary",
        params={},
        data_source=DataSource.CACHED,
        duration_ms=0,
        allowlisted_params=[],
    ))

    return create_envelope(
        data=summary,
        request_id=get_request_id(),
        data_source=DataSource.CACHED,
    )


# ============================================================================
# ECOCREDITS (4 endpoints) - With response envelope
# ============================================================================

@app.get("/ecocredits/types", summary="List credit types", tags=["Ecocredits"])
async def list_credit_types(request: Request):
    """List all ecological credit types enabled on Regen (Carbon, Biodiversity, etc.)."""
    start_time = time.time()
    result = await credit_tools.list_credit_types()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    # Add tool trace
    trace = create_tool_trace(
        tool="list_credit_types",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


@app.get("/ecocredits/classes", summary="List credit classes", tags=["Ecocredits"])
async def list_credit_classes(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List credit classes (methodologies for measuring ecological benefits)."""
    start_time = time.time()
    result = await credit_tools.list_credit_classes(limit, offset)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="list_credit_classes",
        params={"limit": limit, "offset": offset},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/ecocredits/projects", summary="List projects", tags=["Ecocredits"])
async def list_projects(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    include_offchain_metrics: bool = Query(
        False,
        description="Enrich projects with off-chain hectares from metadata IRIs. Enforces 'no citation, no metric' policy."
    ),
):
    """List ecological projects registered on Regen that generate credits.

    When include_offchain_metrics=true, projects with Regen metadata IRIs will be
    enriched with hectares derived from off-chain metadata. Enforces 'no citation,
    no metric' - hectares only appear with full provenance.
    """
    start_time = time.time()
    result = await credit_tools.list_projects(limit, offset)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    # Optional off-chain enrichment
    enrichment_warnings: List[str] = []
    if include_offchain_metrics and result.get("projects"):
        projects = result["projects"]
        enriched_projects, enrichment_warnings = await enrich_projects_with_offchain_metrics(projects)
        result["projects"] = enriched_projects

    trace = create_tool_trace(
        tool="list_projects",
        params={"limit": limit, "offset": offset, "include_offchain_metrics": include_offchain_metrics},
        data_source=DataSource.ON_CHAIN if not include_offchain_metrics else DataSource.METADATA,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit)

    envelope = create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN if not include_offchain_metrics else DataSource.METADATA,
        pagination=pagination,
    )

    # Add enrichment warnings to envelope if any
    if enrichment_warnings:
        envelope["warnings"] = enrichment_warnings

    return envelope


@app.get("/ecocredits/batches", summary="List credit batches", tags=["Ecocredits"])
async def list_credit_batches(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    summary: bool = Query(
        False,
        description="Return aggregate summary by credit type instead of individual batches. "
        "Reduces pagination loops for analytics use cases."
    ),
    fetch_all: bool = Query(
        False,
        description="When summary=true, fetch all pages to compute complete totals. "
        "Without this, summary is computed from first page only. Max 50 pages."
    ),
):
    """List issued credit batches with vintage dates and supply info.

    Options:
    - Default: Returns paginated list of individual batches
    - ?summary=true: Returns aggregate summary by credit type (totals for issued/tradable/retired)
    - ?summary=true&fetch_all=true: Fetches all pages to compute complete summary totals

    The summary mode is designed to reduce agent-side pagination loops for common analytics.
    """
    start_time = time.time()
    warnings: List[str] = []

    if summary:
        # Summary mode: aggregate batches by credit type
        from mcp_server.client.regen_client import get_regen_client

        client = get_regen_client()

        if fetch_all:
            # Fetch all pages using the pagination helper
            fetch_result = await client.fetch_all_pages(
                path="/regen/ecocredit/v1/batches",
                page_size=100,
                max_pages=50,  # Safety cap
                item_key="batches",
            )
            batches = fetch_result["items"]
            warnings.extend(fetch_result.get("warnings", []))
            if not fetch_result["exhausted"]:
                warnings.append(
                    f"PAGINATION_NOT_EXHAUSTED: Summary computed from {fetch_result['pages_fetched']} pages "
                    f"({len(batches)} batches). Total may be higher."
                )
            total_batches = fetch_result.get("total") or len(batches)
        else:
            # Single page only
            result = await credit_tools.list_credit_batches(limit, offset)
            if "error" in result:
                if is_transient_error(result["error"]):
                    raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
                raise HTTPException(status_code=400, detail=result["error"])
            batches = result.get("batches", [])
            total_batches = len(batches)
            warnings.append(
                f"PARTIAL_SUMMARY: Summary computed from first page only ({len(batches)} batches). "
                "Use fetch_all=true for complete totals."
            )

        # Compute summary by credit type
        summary_by_type: Dict[str, Dict[str, Any]] = {}
        for batch in batches:
            # Extract credit type from project_id or denom (e.g., "C01-001" -> "C", "BT01-002" -> "BT")
            # The project_id format is typically "{class_id}-{project_num}" where class_id is like "C01"
            project_id = batch.get("project_id", "") or batch.get("denom", "").split("-")[0] if batch.get("denom") else ""
            # Extract the class_id (first part before the hyphen)
            class_id = project_id.split("-")[0] if project_id else ""
            # Credit type is the alphabetic prefix of the class_id
            credit_type = "".join(c for c in class_id if c.isalpha())
            if not credit_type:
                credit_type = "UNKNOWN"

            if credit_type not in summary_by_type:
                summary_by_type[credit_type] = {
                    "credit_type": credit_type,
                    "batch_count": 0,
                    "total_issued": 0.0,
                    "total_tradable": 0.0,
                    "total_retired": 0.0,
                    "total_cancelled": 0.0,
                    "class_ids": set(),
                    "project_ids": set(),
                }

            summary_by_type[credit_type]["batch_count"] += 1

            # Parse supply amounts (they come as strings)
            def parse_amount(val: Any) -> float:
                if val is None:
                    return 0.0
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0

            # Get supply info from batch
            supply = batch.get("supply", {}) if isinstance(batch.get("supply"), dict) else {}
            summary_by_type[credit_type]["total_issued"] += parse_amount(
                batch.get("total_amount") or supply.get("total_amount")
            )
            summary_by_type[credit_type]["total_tradable"] += parse_amount(
                batch.get("tradable_amount") or supply.get("tradable_amount")
            )
            summary_by_type[credit_type]["total_retired"] += parse_amount(
                batch.get("retired_amount") or supply.get("retired_amount")
            )
            summary_by_type[credit_type]["total_cancelled"] += parse_amount(
                batch.get("cancelled_amount") or supply.get("cancelled_amount")
            )
            if class_id:
                summary_by_type[credit_type]["class_ids"].add(class_id)
            if batch.get("project_id"):
                summary_by_type[credit_type]["project_ids"].add(batch["project_id"])

        # Convert sets to counts for JSON serialization
        summary_list = []
        for type_data in summary_by_type.values():
            type_data["unique_classes"] = len(type_data.pop("class_ids"))
            type_data["unique_projects"] = len(type_data.pop("project_ids"))
            summary_list.append(type_data)

        # Sort by total issued descending
        summary_list.sort(key=lambda x: x["total_issued"], reverse=True)

        response_data = {
            "summary": summary_list,
            "batches_analyzed": len(batches),
            "total_batches": total_batches,
            "aggregation": {
                "method": "by_credit_type",
                "metrics": ["total_issued", "total_tradable", "total_retired", "total_cancelled"],
            },
        }

        trace = create_tool_trace(
            tool="list_credit_batches_summary",
            params={"summary": True, "fetch_all": fetch_all},
            data_source=DataSource.ON_CHAIN,
            duration_ms=(time.time() - start_time) * 1000
        )
        add_tool_trace(trace)

        return create_envelope(
            data=response_data,
            request_id=get_request_id(),
            data_source=DataSource.ON_CHAIN,
            warnings=warnings if warnings else None,
        )

    # Standard mode: return paginated batches
    result = await credit_tools.list_credit_batches(limit, offset)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="list_credit_batches",
        params={"limit": limit, "offset": offset},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


# ============================================================================
# MARKETPLACE (2 endpoints) - Consolidated from 5, with response envelope
# ============================================================================

@app.get("/marketplace/orders", summary="Query sell orders", tags=["Marketplace"])
async def query_marketplace_orders(
    request: Request,
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
    start_time = time.time()
    offset = (page - 1) * limit

    if id is not None:
        result = await marketplace_tools.get_sell_order(id)
        tool_name = "get_sell_order"
        params = {"id": id}
    elif batch is not None:
        result = await marketplace_tools.list_sell_orders_by_batch(batch, limit=limit, offset=offset)
        tool_name = "list_sell_orders_by_batch"
        params = {"batch": batch, "limit": limit, "offset": offset}
    elif seller is not None:
        result = await marketplace_tools.list_sell_orders_by_seller(seller, limit=limit, offset=offset)
        tool_name = "list_sell_orders_by_seller"
        params = {"seller": seller, "limit": limit, "offset": offset}
    else:
        result = await marketplace_tools.list_sell_orders(limit=limit, offset=offset)
        tool_name = "list_sell_orders"
        params = {"limit": limit, "offset": offset}

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit) if id is None else None

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/marketplace/denoms", summary="Allowed payment tokens", tags=["Marketplace"])
async def list_allowed_denoms(request: Request):
    """List token denominations accepted for marketplace payments."""
    start_time = time.time()
    result = await marketplace_tools.list_allowed_denoms()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="list_allowed_denoms",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


# ============================================================================
# BASKETS (3 endpoints) - Consolidated from 5, with response envelope
# ============================================================================

@app.get("/baskets", summary="List baskets", tags=["Baskets"])
async def list_baskets(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List ecocredit baskets (pooled credits represented as fungible tokens)."""
    start_time = time.time()
    result = await basket_tools.list_baskets(limit, offset)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="list_baskets",
        params={"limit": limit, "offset": offset},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/baskets/fee", summary="Basket creation fee", tags=["Baskets"])
async def get_basket_fee(request: Request):
    """Get the fee required to create a new ecocredit basket."""
    start_time = time.time()
    result = await basket_tools.get_basket_fee()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="get_basket_fee",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


@app.get("/baskets/{denom}", summary="Get basket details", tags=["Baskets"])
async def get_basket_details(
    request: Request,
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
    start_time = time.time()
    warnings = []

    basket_result = await basket_tools.get_basket(denom)
    if "error" in basket_result:
        if is_transient_error(basket_result["error"]):
            raise TransientError(message=basket_result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=basket_result["error"])

    response = {"basket": basket_result}

    if include_balances:
        try:
            if batch:
                balance_result = await basket_tools.get_basket_balance(denom, batch)
                if "error" not in balance_result:
                    response["batch_balance"] = balance_result
                else:
                    warnings.append(f"batch_balance_error: {balance_result['error']}")
            else:
                balances_result = await basket_tools.list_basket_balances(denom, limit, offset)
                if "error" not in balances_result:
                    response["balances"] = balances_result
                else:
                    warnings.append(f"balances_error: {balances_result['error']}")
        except Exception as e:
            warnings.append(f"Balance query not supported: {str(e)}")

    trace = create_tool_trace(
        tool="get_basket",
        params={"denom": denom, "include_balances": include_balances, "batch": batch},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=response,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        warnings=warnings if warnings else None,
    )


# ============================================================================
# BANK (5 endpoints) - Consolidated from 11, with response envelope
# ============================================================================

@app.get("/bank/accounts", summary="Query accounts", tags=["Bank"])
async def query_bank_accounts(
    request: Request,
    address: Optional[str] = Query(None, description="Get specific account by address"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query Regen accounts. Options:
    - No params: List all accounts (paginated)
    - ?address=regen1...: Get specific account details
    """
    start_time = time.time()
    offset = (page - 1) * limit

    if address:
        result = await bank_tools.get_account(address)
        tool_name = "get_account"
        params = {"address": address}
    else:
        result = await bank_tools.list_accounts(page, limit)
        tool_name = "list_accounts"
        params = {"page": page, "limit": limit}

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit) if not address else None

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/bank/balances/{address}", summary="Get account balances", tags=["Bank"])
async def get_account_balances(
    request: Request,
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
    start_time = time.time()
    offset = (page - 1) * limit

    if spendable:
        result = await bank_tools.get_spendable_balances(address, page, limit)
        tool_name = "get_spendable_balances"
        params = {"address": address, "page": page, "limit": limit, "spendable": True}
    elif denom:
        result = await bank_tools.get_balance(address, denom)
        tool_name = "get_balance"
        params = {"address": address, "denom": denom}
    else:
        result = await bank_tools.get_all_balances(address, page, limit)
        tool_name = "get_all_balances"
        params = {"address": address, "page": page, "limit": limit}

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit) if not denom else None

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/bank/supply", summary="Query token supply", tags=["Bank"])
async def query_token_supply(
    request: Request,
    denom: Optional[str] = Query(None, description="Get supply for specific token"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
):
    """Query total token supply. Options:
    - No params: Total supply of all tokens
    - ?denom=uregen: Supply of specific token
    """
    start_time = time.time()
    offset = (page - 1) * limit

    if denom:
        result = await bank_tools.get_supply_of(denom)
        tool_name = "get_supply_of"
        params = {"denom": denom}
    else:
        result = await bank_tools.get_total_supply(page, limit)
        tool_name = "get_total_supply"
        params = {"page": page, "limit": limit}

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit) if not denom else None

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/bank/metadata", summary="Query token metadata", tags=["Bank"])
async def query_token_metadata(
    request: Request,
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
    start_time = time.time()
    offset = (page - 1) * limit
    warnings = []

    if denom:
        metadata_result = await bank_tools.get_denom_metadata(denom)
        if "error" in metadata_result:
            if is_transient_error(metadata_result["error"]):
                raise TransientError(message=metadata_result["error"], code="UPSTREAM_ERROR")
            raise HTTPException(status_code=400, detail=metadata_result["error"])

        response = {"metadata": metadata_result}

        if include_owners:
            owners_result = await bank_tools.get_denom_owners(denom, page, limit)
            if "error" not in owners_result:
                response["owners"] = owners_result
            else:
                warnings.append(f"owners_error: {owners_result['error']}")

        trace = create_tool_trace(
            tool="get_denom_metadata",
            params={"denom": denom, "include_owners": include_owners},
            data_source=DataSource.ON_CHAIN,
            duration_ms=(time.time() - start_time) * 1000
        )
        add_tool_trace(trace)

        return create_envelope(
            data=response,
            request_id=get_request_id(),
            data_source=DataSource.ON_CHAIN,
            warnings=warnings if warnings else None,
        )
    else:
        result = await bank_tools.get_denoms_metadata(page, limit)
        if "error" in result:
            if is_transient_error(result["error"]):
                raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
            raise HTTPException(status_code=400, detail=result["error"])

        trace = create_tool_trace(
            tool="get_denoms_metadata",
            params={"page": page, "limit": limit},
            data_source=DataSource.ON_CHAIN,
            duration_ms=(time.time() - start_time) * 1000
        )
        add_tool_trace(trace)

        pagination = extract_pagination_from_response(result, offset, limit)

        return create_envelope(
            data=result,
            request_id=get_request_id(),
            data_source=DataSource.ON_CHAIN,
            pagination=pagination,
        )


@app.get("/bank/params", summary="Bank module params", tags=["Bank"])
async def get_bank_params(request: Request):
    """Get bank module parameters (send enabled, default settings)."""
    start_time = time.time()
    result = await bank_tools.get_bank_params()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="get_bank_params",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


# ============================================================================
# DISTRIBUTION (4 endpoints) - Consolidated from 9, with response envelope
# ============================================================================

@app.get("/distribution/params", summary="Distribution params", tags=["Distribution"])
async def get_distribution_params(request: Request):
    """Get distribution module parameters (community tax, base proposer reward, etc.)."""
    start_time = time.time()
    result = await distribution_tools.get_distribution_params()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="get_distribution_params",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


@app.get("/distribution/pool", summary="Community pool", tags=["Distribution"])
async def get_community_pool(request: Request):
    """Get community pool balance (funds available for governance spending)."""
    start_time = time.time()
    result = await distribution_tools.get_community_pool()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="get_community_pool",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


@app.get("/distribution/validator/{address}", summary="Validator distribution info", tags=["Distribution"])
async def get_validator_distribution(
    request: Request,
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
    start_time = time.time()
    warnings = []

    # Fetch all three in parallel
    rewards_task = distribution_tools.get_validator_outstanding_rewards(address)
    commission_task = distribution_tools.get_validator_commission(address)
    slashes_task = distribution_tools.get_validator_slashes(
        address, starting_height, ending_height, page, limit
    )

    rewards, commission, slashes = await asyncio.gather(
        rewards_task, commission_task, slashes_task
    )

    # Collect warnings for partial failures
    if "error" in rewards:
        warnings.append(f"rewards_error: {rewards['error']}")
    if "error" in commission:
        warnings.append(f"commission_error: {commission['error']}")
    if "error" in slashes:
        warnings.append(f"slashes_error: {slashes['error']}")

    response_data = {
        "validator_address": address,
        "outstanding_rewards": rewards if "error" not in rewards else None,
        "commission": commission if "error" not in commission else None,
        "slashes": slashes if "error" not in slashes else None,
    }

    trace = create_tool_trace(
        tool="get_validator_distribution",
        params={"address": address, "starting_height": starting_height, "ending_height": ending_height},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=response_data,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        warnings=warnings if warnings else None,
    )


@app.get("/distribution/delegator/{address}", summary="Delegator distribution info", tags=["Distribution"])
async def get_delegator_distribution(
    request: Request,
    address: str = PathParam(..., description="Delegator account address (regen1...)"),
    validator: Optional[str] = Query(None, description="Get rewards for specific validator only"),
):
    """Get delegator staking rewards info. Options:
    - Basic: Total rewards, list of validators, withdraw address
    - ?validator=regenvaloper1...: Rewards from specific validator only
    """
    start_time = time.time()
    warnings = []

    if validator:
        result = await distribution_tools.get_delegation_rewards(address, validator)
        if "error" in result:
            if is_transient_error(result["error"]):
                raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
            raise HTTPException(status_code=400, detail=result["error"])

        response_data = {
            "delegator_address": address,
            "validator_address": validator,
            "rewards": result
        }
        tool_name = "get_delegation_rewards"
        params = {"address": address, "validator": validator}
    else:
        # Fetch all delegator info in parallel
        total_task = distribution_tools.get_delegation_total_rewards(address)
        validators_task = distribution_tools.get_delegator_validators(address)
        withdraw_task = distribution_tools.get_delegator_withdraw_address(address)

        total, validators, withdraw = await asyncio.gather(
            total_task, validators_task, withdraw_task
        )

        # Collect warnings for partial failures
        if "error" in total:
            warnings.append(f"total_rewards_error: {total['error']}")
        if "error" in validators:
            warnings.append(f"validators_error: {validators['error']}")
        if "error" in withdraw:
            warnings.append(f"withdraw_address_error: {withdraw['error']}")

        response_data = {
            "delegator_address": address,
            "total_rewards": total if "error" not in total else None,
            "validators": validators if "error" not in validators else None,
            "withdraw_address": withdraw if "error" not in withdraw else None,
        }
        tool_name = "get_delegator_distribution"
        params = {"address": address}

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=response_data,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        warnings=warnings if warnings else None,
    )


# ============================================================================
# GOVERNANCE (4 endpoints) - Consolidated from 8, with response envelope + 503 for transient errors
# ============================================================================

@app.get("/governance/params", summary="Governance params", tags=["Governance"])
async def get_governance_params_endpoint(
    request: Request,
    type: Optional[GovParamsType] = Query(None, description="Param type: voting, deposit, tally, or all"),
):
    """Get governance module parameters. Options:
    - No params or ?type=all: All parameter types
    - ?type=voting: Voting period, quorum, threshold
    - ?type=deposit: Min deposit, max deposit period
    - ?type=tally: Quorum, threshold, veto threshold
    """
    start_time = time.time()
    warnings = []

    if type and type != GovParamsType.all:
        # Note: "tally" endpoint doesn't work on cosmos gov v1beta1, extract from voting
        if type.value == "tally":
            result = await governance_tools.get_governance_params("voting")
            if "error" in result:
                # Governance errors are transient - use 503
                raise GovernanceUnavailableError(
                    message=result["error"],
                    details={"type": "tally", "underlying_query": "voting"}
                )
            response_data = {"tally_params": result.get("tally_params")}
        else:
            result = await governance_tools.get_governance_params(type.value)
            if "error" in result:
                raise GovernanceUnavailableError(
                    message=result["error"],
                    details={"type": type.value}
                )
            response_data = result
    else:
        # Get all params (voting and deposit both include all params)
        async def safe_fetch(query_type: str):
            try:
                return await governance_tools.get_governance_params(query_type)
            except Exception as e:
                return {"error": str(e)}

        voting, deposit = await asyncio.gather(
            safe_fetch("voting"), safe_fetch("deposit")
        )

        # Collect warnings for partial failures
        if voting and "error" in voting:
            warnings.append(f"voting_params_error: {voting['error']}")
            voting = None
        if deposit and "error" in deposit:
            warnings.append(f"deposit_params_error: {deposit['error']}")
            deposit = None

        response_data = {
            "voting": voting,
            "deposit": deposit,
            "tally": {"tally_params": voting.get("tally_params")} if voting else None,
        }

    trace = create_tool_trace(
        tool="get_governance_params",
        params={"type": type.value if type else "all"},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=response_data,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        warnings=warnings if warnings else None,
    )


@app.get("/governance/proposals", summary="Query proposals", tags=["Governance"])
async def query_governance_proposals(
    request: Request,
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
    start_time = time.time()
    offset = (page - 1) * limit

    if id is not None:
        result = await governance_tools.get_governance_proposal(id)
        tool_name = "get_governance_proposal"
        params = {"id": id}
    else:
        result = await governance_tools.list_governance_proposals(
            proposal_status=status.value if status else None,
            voter=voter,
            depositor=depositor,
            page=page,
            limit=limit
        )
        tool_name = "list_governance_proposals"
        params = {"status": status.value if status else None, "voter": voter, "depositor": depositor, "page": page, "limit": limit}

    if "error" in result:
        # Governance errors are transient - use 503 with retryable flag
        raise GovernanceUnavailableError(
            message=result["error"],
            details={"tool": tool_name, "params": {k: v for k, v in params.items() if v is not None}}
        )

    trace = create_tool_trace(
        tool=tool_name,
        params=params,
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    pagination = extract_pagination_from_response(result, offset, limit) if id is None else None

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        pagination=pagination,
    )


@app.get("/governance/proposal/{id}/full", summary="Full proposal details", tags=["Governance"])
async def get_proposal_full_details(
    request: Request,
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
    start_time = time.time()
    warnings = []

    # Fetch proposal first (we need this to succeed)
    proposal = await governance_tools.get_governance_proposal(id)
    if "error" in proposal:
        # Check if this looks like a "not found" vs transient error
        error_lower = proposal["error"].lower()
        if "not found" in error_lower or "does not exist" in error_lower:
            raise HTTPException(status_code=404, detail=f"Proposal {id} not found")
        # Otherwise it's a transient governance error
        raise GovernanceUnavailableError(
            message=proposal["error"],
            details={"proposal_id": id}
        )

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

    # Collect warnings for partial failures
    if "error" in votes:
        warnings.append(f"votes_error: {votes['error']}")
    if "error" in deposits:
        warnings.append(f"deposits_error: {deposits['error']}")
    if "error" in tally:
        warnings.append(f"tally_error: {tally['error']}")

    response_data = {
        "proposal": proposal,
        "votes": votes if "error" not in votes else None,
        "deposits": deposits if "error" not in deposits else None,
        "tally": tally if "error" not in tally else None,
    }

    trace = create_tool_trace(
        tool="get_proposal_full_details",
        params={"id": id, "voter": voter, "depositor": depositor},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=response_data,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
        warnings=warnings if warnings else None,
    )


@app.get("/governance/pool", summary="Community pool", tags=["Governance"])
async def get_governance_community_pool(request: Request):
    """Get community pool balance (alias for /distribution/pool)."""
    start_time = time.time()
    result = await distribution_tools.get_community_pool()

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="get_community_pool",
        params={},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


# ============================================================================
# ANALYTICS (3 endpoints) - With response envelope
# ============================================================================

@app.get("/analytics/portfolio/{address}", summary="Portfolio impact analysis", tags=["Analytics"])
async def analyze_portfolio_impact_endpoint(
    request: Request,
    address: str = PathParam(..., description="Account address to analyze"),
    analysis_type: str = Query("full", description="Analysis type: full, credits, or summary"),
):
    """Analyze ecological impact of an address's credit holdings."""
    start_time = time.time()
    result = await analytics_tools.analyze_portfolio_impact(address, analysis_type)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="analyze_portfolio_impact",
        params={"address": address, "analysis_type": analysis_type},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


@app.get("/analytics/trends", summary="Market trends", tags=["Analytics"])
async def analyze_market_trends_endpoint(
    request: Request,
    credit_types: Optional[str] = Query(None, description="Comma-separated credit type codes: C (Carbon), BT (BioTerra), KSH (Kilo-Sheep-Hour), USS (Umbrella Species), MBS (Marine Biodiversity). Example: C,BT"),
    time_period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
):
    """Analyze market trends across credit types. Call without parameters for all credit types."""
    start_time = time.time()
    types_list = credit_types.split(",") if credit_types else None
    result = await analytics_tools.analyze_market_trends(time_period, types_list)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="analyze_market_trends",
        params={"credit_types": credit_types, "time_period": time_period},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


class MethodologyCompareRequest(BaseModel):
    """Request body for methodology comparison."""
    class_ids: List[str] = Field(..., description="Credit class IDs to compare", min_length=2)


@app.post("/analytics/compare", summary="Compare methodologies", tags=["Analytics"])
async def compare_credit_methodologies_endpoint(
    http_request: Request,
    request: MethodologyCompareRequest,
):
    """Compare different credit class methodologies for impact efficiency."""
    start_time = time.time()
    result = await analytics_tools.compare_credit_methodologies(request.class_ids)

    if "error" in result:
        if is_transient_error(result["error"]):
            raise TransientError(message=result["error"], code="UPSTREAM_ERROR")
        raise HTTPException(status_code=400, detail=result["error"])

    trace = create_tool_trace(
        tool="compare_credit_methodologies",
        params={"class_ids": request.class_ids},
        data_source=DataSource.ON_CHAIN,
        duration_ms=(time.time() - start_time) * 1000
    )
    add_tool_trace(trace)

    return create_envelope(
        data=result,
        request_id=get_request_id(),
        data_source=DataSource.ON_CHAIN,
    )


# ============================================================================
# Main
# ============================================================================

import os

PORT = int(os.getenv("PORT", 8007))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print("=" * 60)
    print("Regen Network API v2 (25 endpoints - Full functionality)")
    print("=" * 60)
    print(f"Local:   http://localhost:{PORT}")
    print(f"Docs:    http://localhost:{PORT}/docs")
    print(f"Schema:  http://localhost:{PORT}/openapi.json")
    print("=" * 60)
    uvicorn.run(app, host=HOST, port=PORT)
