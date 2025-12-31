"""Response envelope models for standardized API responses.

This module provides a consistent response envelope for all /regen-api/* endpoints,
including request tracing, error handling, and data source labeling.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field


class DataSource(str, Enum):
    """Data source classification for response items."""
    ON_CHAIN = "on-chain"
    KOI_DERIVED = "koi-derived"
    ESTIMATED = "estimated"
    CACHED = "cached"
    METADATA = "metadata"


class OnChainAsOf(BaseModel):
    """On-chain data freshness metadata."""
    chain_id: str = Field(default="regen-1", description="Blockchain chain ID")
    block_height: Optional[int] = Field(default=None, description="Block height when data was queried")
    block_time: Optional[str] = Field(default=None, description="Block timestamp (ISO 8601)")


class KoiAsOf(BaseModel):
    """KOI corpus freshness metadata."""
    corpus_version: Optional[str] = Field(default=None, description="KOI corpus version identifier")
    indexed_at: Optional[str] = Field(default=None, description="When the KOI data was last indexed (ISO 8601)")


class MetadataAsOf(BaseModel):
    """Off-chain metadata resolution freshness."""
    iri: Optional[str] = Field(default=None, description="Metadata IRI that was resolved")
    resolved_at: Optional[str] = Field(default=None, description="When metadata was resolved (ISO 8601)")


class AsOf(BaseModel):
    """Combined freshness metadata split by source."""
    on_chain: Optional[OnChainAsOf] = Field(default=None, description="On-chain data freshness")
    koi: Optional[KoiAsOf] = Field(default=None, description="KOI corpus freshness")
    metadata: Optional[MetadataAsOf] = Field(default=None, description="Off-chain metadata freshness")


class ToolTrace(BaseModel):
    """Trace entry for a tool/operation executed to produce the response.

    Note: params_summary is redacted to be public-safe. Never include
    secrets, internal hostnames, or raw user text.
    """
    tool: str = Field(..., description="Tool or operation name")
    params_summary: str = Field(..., description="Redacted summary of params (allowlisted fields only)")
    timestamp: str = Field(..., description="When the tool was invoked (ISO 8601)")
    data_source: DataSource = Field(..., description="Data source for this operation")
    duration_ms: Optional[float] = Field(default=None, description="Operation duration in milliseconds")


class ApiError(BaseModel):
    """Structured error with retryability information."""
    code: str = Field(..., description="Error code (e.g., 'GOVERNANCE_UNAVAILABLE', 'VALIDATION_ERROR')")
    message: str = Field(..., description="Human-readable error message")
    retryable: bool = Field(default=False, description="Whether the client should retry this request")
    retry_after_ms: Optional[int] = Field(default=None, description="Suggested wait time before retry (ms)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context")


class Citation(BaseModel):
    """Citation for KOI-derived data (public-safe)."""
    rid: str = Field(..., description="KOI record ID")
    url: Optional[str] = Field(default=None, description="Canonical URL to source")
    title: Optional[str] = Field(default=None, description="Source title")
    excerpt: Optional[str] = Field(default=None, description="Relevant excerpt/quote")
    verified: Optional[bool] = Field(default=None, description="Whether the link has been verified")
    checked_at: Optional[str] = Field(default=None, description="When link was last verified (ISO 8601)")


class PaginationMeta(BaseModel):
    """Standardized pagination metadata."""
    offset: int = Field(default=0, description="Current offset")
    limit: int = Field(default=100, description="Page size limit")
    total: Optional[int] = Field(default=None, description="Total number of items (if known)")
    has_more: Optional[bool] = Field(default=None, description="Whether more results exist")
    next_offset: Optional[int] = Field(default=None, description="Offset for next page (if has_more)")


class ResponseEnvelope(BaseModel):
    """Standard response envelope for all /regen-api/* endpoints.

    All responses are wrapped in this envelope to provide:
    - Request tracing (request_id)
    - Data freshness (as_of)
    - Data provenance (data_source, tool_trace)
    - Structured errors (errors[])
    - Warnings for partial failures (warnings[])
    - Pagination metadata (pagination)
    - Citations for KOI-derived data (citations[])
    """
    data: Any = Field(..., description="Response payload")
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request ID for correlation"
    )
    data_source: DataSource = Field(
        default=DataSource.ON_CHAIN,
        description="Primary data source for this response"
    )
    as_of: AsOf = Field(
        default_factory=AsOf,
        description="Data freshness metadata by source"
    )
    tool_trace: List[ToolTrace] = Field(
        default_factory=list,
        description="Trace of operations executed (redacted for public safety)"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal issues (e.g., 'pagination_not_exhausted')"
    )
    errors: List[ApiError] = Field(
        default_factory=list,
        description="Structured errors with retryability info"
    )
    pagination: Optional[PaginationMeta] = Field(
        default=None,
        description="Pagination metadata for list responses"
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Citations for KOI-derived data"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ErrorResponse(BaseModel):
    """Error-only response (HTTP 4xx/5xx)."""
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request ID for correlation"
    )
    errors: List[ApiError] = Field(
        default_factory=list,
        description="Structured errors"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Additional context"
    )


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def create_tool_trace(
    tool: str,
    params: Dict[str, Any],
    data_source: DataSource,
    duration_ms: Optional[float] = None,
    allowlisted_params: Optional[List[str]] = None
) -> ToolTrace:
    """Create a tool trace entry with redacted params.

    Args:
        tool: Tool/operation name
        params: Original parameters (will be redacted)
        data_source: Data source classification
        duration_ms: Operation duration
        allowlisted_params: List of param names safe to include in summary.
                           If None, uses default allowlist.

    Returns:
        ToolTrace with redacted params_summary
    """
    # Default allowlist - safe params to include in traces
    default_allowlist = {
        "limit", "offset", "page", "id", "status", "type",
        "batch", "denom", "address", "proposal_id", "voter",
        "depositor", "validator", "delegator", "include_balances",
        "spendable", "starting_height", "ending_height",
        "analysis_type", "time_period", "credit_types"
    }

    allowlist = set(allowlisted_params) if allowlisted_params else default_allowlist

    # Build redacted summary
    summary_parts = []
    for key, value in params.items():
        if key in allowlist and value is not None:
            # Truncate long values
            str_value = str(value)
            if len(str_value) > 50:
                str_value = str_value[:47] + "..."
            summary_parts.append(f"{key}={str_value}")

    params_summary = ",".join(summary_parts) if summary_parts else "(no params)"

    return ToolTrace(
        tool=tool,
        params_summary=params_summary,
        timestamp=datetime.utcnow().isoformat() + "Z",
        data_source=data_source,
        duration_ms=duration_ms
    )


def create_error_response(
    request_id: str,
    code: str,
    message: str,
    retryable: bool = False,
    retry_after_ms: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None
) -> ErrorResponse:
    """Create a structured error response.

    Args:
        request_id: Request ID for correlation
        code: Error code
        message: Human-readable message
        retryable: Whether client should retry
        retry_after_ms: Suggested retry delay
        details: Additional context
        warnings: Any warnings to include

    Returns:
        ErrorResponse with structured error
    """
    return ErrorResponse(
        request_id=request_id,
        errors=[
            ApiError(
                code=code,
                message=message,
                retryable=retryable,
                retry_after_ms=retry_after_ms,
                details=details
            )
        ],
        warnings=warnings or []
    )
