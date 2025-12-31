"""Middleware for the Regen MCP server."""

from .response_middleware import (
    RequestIDMiddleware,
    TransientError,
    GovernanceUnavailableError,
    UpstreamTimeoutError,
    get_request_id,
    get_tool_traces,
    add_tool_trace,
    create_envelope,
    create_error_envelope,
    extract_pagination_from_response,
    handle_tool_error,
    is_transient_error,
)

__all__ = [
    "RequestIDMiddleware",
    "TransientError",
    "GovernanceUnavailableError",
    "UpstreamTimeoutError",
    "get_request_id",
    "get_tool_traces",
    "add_tool_trace",
    "create_envelope",
    "create_error_envelope",
    "extract_pagination_from_response",
    "handle_tool_error",
    "is_transient_error",
]
