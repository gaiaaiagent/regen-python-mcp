"""Response middleware for standardized API responses.

This module provides middleware and utilities for:
- Adding X-Request-ID headers
- Wrapping responses in the standard envelope
- Handling errors with proper status codes
"""

import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import HTTPException

from ..models.response_envelope import (
    ResponseEnvelope,
    ErrorResponse,
    ApiError,
    AsOf,
    OnChainAsOf,
    DataSource,
    ToolTrace,
    PaginationMeta,
    generate_request_id,
    create_tool_trace,
)


# Context variable to store request ID across async calls
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
request_start_time_var: ContextVar[float] = ContextVar("request_start_time", default=0.0)
tool_traces_var: ContextVar[List[ToolTrace]] = ContextVar("tool_traces", default=[])


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get() or generate_request_id()


def get_tool_traces() -> List[ToolTrace]:
    """Get tool traces for current request."""
    return tool_traces_var.get()


def add_tool_trace(trace: ToolTrace) -> None:
    """Add a tool trace to the current request context."""
    traces = tool_traces_var.get()
    if traces is not None:
        traces.append(trace)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add X-Request-ID header to all responses.

    - Generates a UUID for each request
    - Stores it in context for use by handlers
    - Adds X-Request-ID header to response
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for incoming request ID header (for distributed tracing)
        request_id = request.headers.get("X-Request-ID", "") or generate_request_id()

        # Store in context for handlers
        request_id_var.set(request_id)
        request_start_time_var.set(time.time())
        tool_traces_var.set([])  # Fresh list for each request

        # Store on request for easy access
        request.state.request_id = request_id
        request.state.start_time = time.time()

        # Process request
        response = await call_next(request)

        # Add X-Request-ID header to response
        response.headers["X-Request-ID"] = request_id

        return response


class TransientError(Exception):
    """Exception for transient/retryable errors (e.g., upstream service unavailable)."""

    def __init__(
        self,
        message: str,
        code: str = "TRANSIENT_ERROR",
        retry_after_ms: int = 5000,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retry_after_ms = retry_after_ms
        self.details = details


class GovernanceUnavailableError(TransientError):
    """Governance module is temporarily unavailable."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="GOVERNANCE_UNAVAILABLE",
            retry_after_ms=10000,  # 10 seconds suggested retry
            details=details
        )


class UpstreamTimeoutError(TransientError):
    """Upstream blockchain node timed out."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UPSTREAM_TIMEOUT",
            retry_after_ms=5000,
            details=details
        )


def is_transient_error(error_message: str) -> bool:
    """Detect if an error message indicates a transient failure.

    Args:
        error_message: Error message string

    Returns:
        True if the error appears to be transient/retryable
    """
    transient_patterns = [
        "connection",
        "timeout",
        "temporarily unavailable",
        "service unavailable",
        "503",
        "502",
        "504",
        "upstream",
        "network error",
        "refused",
        "reset by peer",
        "governance",  # Governance failures are often transient
        "all endpoints failed",
    ]

    error_lower = error_message.lower()
    return any(pattern in error_lower for pattern in transient_patterns)


def create_envelope(
    data: Any,
    request_id: Optional[str] = None,
    data_source: DataSource = DataSource.ON_CHAIN,
    chain_id: str = "regen-1",
    block_height: Optional[int] = None,
    block_time: Optional[str] = None,
    warnings: Optional[List[str]] = None,
    errors: Optional[List[ApiError]] = None,
    pagination: Optional[PaginationMeta] = None,
    tool_traces: Optional[List[ToolTrace]] = None,
) -> Dict[str, Any]:
    """Create a response envelope dictionary.

    Args:
        data: Response payload
        request_id: Request ID (auto-generated if not provided)
        data_source: Primary data source
        chain_id: Blockchain chain ID
        block_height: Block height (if available)
        block_time: Block timestamp (if available)
        warnings: Non-fatal warnings
        errors: Structured errors
        pagination: Pagination metadata
        tool_traces: Tool execution traces

    Returns:
        Dict representation of ResponseEnvelope
    """
    rid = request_id or get_request_id()
    traces = tool_traces if tool_traces is not None else get_tool_traces()

    envelope = ResponseEnvelope(
        data=data,
        request_id=rid,
        data_source=data_source,
        as_of=AsOf(
            on_chain=OnChainAsOf(
                chain_id=chain_id,
                block_height=block_height,
                block_time=block_time
            )
        ),
        tool_trace=traces,
        warnings=warnings or [],
        errors=errors or [],
        pagination=pagination,
        citations=[]
    )

    return envelope.dict(exclude_none=True)


def create_error_envelope(
    request_id: str,
    code: str,
    message: str,
    retryable: bool = False,
    retry_after_ms: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create an error response envelope.

    Args:
        request_id: Request ID for correlation
        code: Error code
        message: Error message
        retryable: Whether the error is retryable
        retry_after_ms: Suggested retry delay
        details: Additional error context
        warnings: Non-fatal warnings

    Returns:
        Dict representation of ErrorResponse
    """
    response = ErrorResponse(
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

    return response.dict(exclude_none=True)


T = TypeVar("T")


def extract_pagination_from_response(
    result: Dict[str, Any],
    offset: int = 0,
    limit: int = 100
) -> Optional[PaginationMeta]:
    """Extract pagination metadata from blockchain API response.

    Args:
        result: Raw API response
        offset: Current offset
        limit: Current limit

    Returns:
        PaginationMeta if pagination info available
    """
    pagination_data = result.get("pagination")
    if not pagination_data:
        return None

    total = None
    if pagination_data.get("total"):
        try:
            total = int(pagination_data["total"])
        except (ValueError, TypeError):
            pass

    has_more = pagination_data.get("next_key") is not None
    next_offset = offset + limit if has_more else None

    return PaginationMeta(
        offset=offset,
        limit=limit,
        total=total,
        has_more=has_more,
        next_offset=next_offset
    )


async def handle_tool_error(
    result: Dict[str, Any],
    request_id: str,
    tool_name: str,
    is_governance: bool = False
) -> None:
    """Handle errors from tool execution with proper status codes.

    Args:
        result: Tool result (may contain "error" key)
        request_id: Request ID for correlation
        tool_name: Name of the tool for error context
        is_governance: True if this is a governance tool (use 503 for errors)

    Raises:
        TransientError: For retryable errors (will be converted to 503)
        HTTPException: For non-retryable errors (400)
    """
    if "error" not in result:
        return

    error_message = result["error"]

    # Check if this is a transient/retryable error
    if is_governance or is_transient_error(error_message):
        raise GovernanceUnavailableError(
            message=error_message,
            details={"tool": tool_name}
        ) if is_governance else TransientError(
            message=error_message,
            code="UPSTREAM_ERROR",
            retry_after_ms=5000,
            details={"tool": tool_name}
        )

    # Non-retryable error (validation, not found, etc.)
    raise HTTPException(status_code=400, detail=error_message)
