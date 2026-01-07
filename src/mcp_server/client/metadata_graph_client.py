"""Client helpers for resolving Regen `regen:` metadata IRIs via api.regen.network.

This module provides a small, allowlisted resolver to translate on-chain metadata IRIs
into human-readable fields (e.g., `schema:name`) for use in MCP tool outputs.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any, Dict, Optional, TypedDict
from urllib.parse import quote

import httpx

from .regen_client import get_regen_client

logger = logging.getLogger(__name__)


REGEN_METADATA_GRAPH_BASE_URL = "https://api.regen.network/data/v2/metadata-graph"

# Per regen-data-standards + KOI anchored metadata resolver:
# regen:{base58check}.{ext}
_REGEN_IRI_PATTERN = re.compile(
    r"^regen:[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+\.[a-z]+$"
)

# Simple in-memory caching to avoid repeated resolver calls.
# Credit class metadata changes rarely; an hour is plenty.
_CACHE_TTL_SECONDS = 3600
_FAILURE_TTL_SECONDS = 300

_cache_lock = asyncio.Lock()
_payload_cache: Dict[str, tuple[float, Dict[str, Any]]] = {}
_failure_cache: Dict[str, float] = {}


class MetadataSummary(TypedDict, total=False):
    name: str
    url: str
    description: str
    source_registry: Dict[str, str]


def _is_valid_regen_iri(iri: str) -> bool:
    return bool(iri and _REGEN_IRI_PATTERN.match(iri))


def _build_metadata_graph_url(iri: str) -> str:
    return f"{REGEN_METADATA_GRAPH_BASE_URL}/{quote(iri, safe='')}"


def _extract_string(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _extract_source_registry(payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Extract a minimal source registry descriptor from resolved JSON-LD."""
    raw = payload.get("regen:sourceRegistry")
    if not isinstance(raw, dict):
        return None

    name = _extract_string(raw.get("schema:name") or raw.get("name"))
    url = _extract_string(raw.get("schema:url") or raw.get("url"))
    if not name and not url:
        return None
    out: Dict[str, str] = {}
    if name:
        out["name"] = name
    if url:
        out["url"] = url
    return out


async def fetch_metadata_graph_payload(iri: str, *, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """Fetch JSON-LD payload from the allowlisted metadata graph resolver.

    Returns None on invalid IRI or if resolution fails.
    """
    if not _is_valid_regen_iri(iri):
        return None

    now = time.time()
    async with _cache_lock:
        if not force_refresh:
            cached = _payload_cache.get(iri)
            if cached and (now - cached[0]) < _CACHE_TTL_SECONDS:
                return cached[1]

            last_failure = _failure_cache.get(iri)
            if last_failure and (now - last_failure) < _FAILURE_TTL_SECONDS:
                return None

    url = _build_metadata_graph_url(iri)
    http_client = await get_regen_client()._get_http_client()

    try:
        resp = await http_client.get(
            url,
            headers={"Accept": "application/ld+json, application/json"},
            timeout=10.0,
            follow_redirects=False,
        )
        resp.raise_for_status()

        payload = resp.json()
        if not isinstance(payload, dict):
            raise ValueError("Resolver returned non-object JSON")

        async with _cache_lock:
            _payload_cache[iri] = (now, payload)
            _failure_cache.pop(iri, None)

        return payload

    except Exception as e:
        logger.warning(f"Failed to resolve metadata IRI via {url}: {e}")
        async with _cache_lock:
            _failure_cache[iri] = now
        return None


async def resolve_metadata_summary(iri: str, *, force_refresh: bool = False) -> Optional[MetadataSummary]:
    """Resolve a Regen metadata IRI and extract a small, stable summary."""
    payload = await fetch_metadata_graph_payload(iri, force_refresh=force_refresh)
    if not payload:
        return None

    summary: MetadataSummary = {}

    name = _extract_string(payload.get("schema:name") or payload.get("name"))
    if name:
        summary["name"] = name

    url = _extract_string(payload.get("schema:url") or payload.get("url"))
    if url:
        summary["url"] = url

    description = _extract_string(payload.get("schema:description") or payload.get("description"))
    if description:
        summary["description"] = description

    source_registry = _extract_source_registry(payload)
    if source_registry:
        summary["source_registry"] = source_registry

    return summary if summary else None

