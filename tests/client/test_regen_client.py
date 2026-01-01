"""Tests for RegenClient with real blockchain data.

These tests use real data from Regen Network, captured and cached via FixtureManager.
NO MOCK DATA - these tests validate actual API behavior.
"""

import pytest
from mcp_server.client.regen_client import (
    RegenClient,
    Pagination,
    get_regen_client,
    RegenClientError,
    NetworkError,
    ValidationError,
    HttpClientError,
    HttpServerError,
)


@pytest.mark.asyncio
@pytest.mark.client
@pytest.mark.offline
class TestRegenClientWithRealData:
    """Test RegenClient using real cached blockchain data."""

    async def test_query_credit_types_structure(self, real_credit_types):
        """Verify credit types response has correct structure.

        Uses real Regen Network data. If this fails, the API has changed!
        """
        # Validate top-level structure
        assert isinstance(real_credit_types, dict), "Response should be a dictionary"
        assert "credit_types" in real_credit_types, "Must have 'credit_types' key"

        credit_types = real_credit_types["credit_types"]
        assert isinstance(credit_types, list), "credit_types should be a list"
        assert len(credit_types) > 0, "Should have at least one credit type"

        # Validate first credit type structure
        credit_type = credit_types[0]
        assert "name" in credit_type, "Credit type must have 'name'"
        assert "abbreviation" in credit_type, "Credit type must have 'abbreviation'"

    async def test_query_credit_types_contains_carbon(self, real_credit_types):
        """Verify carbon credit type exists (known real data validation).

        This test validates against known real-world state: Regen Network
        supports carbon credits. If this fails, either:
        1. API has changed (update fixture)
        2. Real bug in our code
        """
        credit_types = real_credit_types["credit_types"]
        type_abbreviations = [ct["abbreviation"] for ct in credit_types]

        # Known fact: Regen Network has carbon credits (abbreviation "C")
        assert "C" in type_abbreviations, \
            f"Carbon credits (C) should exist. Got: {type_abbreviations}"

    async def test_query_credit_classes_structure(self, real_credit_classes):
        """Verify credit classes response structure with real data."""
        assert isinstance(real_credit_classes, dict)
        assert "classes" in real_credit_classes

        classes = real_credit_classes["classes"]
        assert isinstance(classes, list)

        if len(classes) > 0:
            # Validate first class structure
            credit_class = classes[0]
            assert "id" in credit_class
            assert "admin" in credit_class
            assert "credit_type_abbrev" in credit_class

    async def test_query_credit_classes_contains_real_classes(self, real_credit_classes):
        """Verify response contains known real credit classes.

        Regen Network has classes like C01, C02, C03 etc. This validates
        we're getting real data, not empty/fake responses.
        """
        classes = real_credit_classes["classes"]
        class_ids = [c["id"] for c in classes]

        # Validate we have actual class IDs
        assert len(class_ids) > 0, "Should have at least one credit class"

        # Check that IDs follow expected pattern (C## format)
        carbon_classes = [cid for cid in class_ids if cid.startswith("C")]
        assert len(carbon_classes) > 0, \
            f"Should have carbon classes (C##). Got: {class_ids}"

    async def test_query_projects_structure(self, real_projects):
        """Verify projects response structure with real data."""
        assert isinstance(real_projects, dict)
        assert "projects" in real_projects

        projects = real_projects["projects"]
        assert isinstance(projects, list)

        if len(projects) > 0:
            project = projects[0]
            assert "id" in project
            assert "admin" in project
            assert "class_id" in project
            assert "jurisdiction" in project

    async def test_query_credit_batches_structure(self, real_credit_batches):
        """Verify credit batches response structure with real data."""
        assert isinstance(real_credit_batches, dict)
        assert "batches" in real_credit_batches

        batches = real_credit_batches["batches"]
        assert isinstance(batches, list)

        if len(batches) > 0:
            batch = batches[0]
            assert "issuer" in batch
            assert "project_id" in batch
            assert "denom" in batch

    async def test_query_sell_orders_structure(self, real_sell_orders):
        """Verify sell orders response structure with real data."""
        assert isinstance(real_sell_orders, dict)
        assert "sell_orders" in real_sell_orders

        sell_orders = real_sell_orders["sell_orders"]
        assert isinstance(sell_orders, list)

        # Marketplace may be empty, so we check structure only if orders exist
        if len(sell_orders) > 0:
            order = sell_orders[0]
            assert "id" in order
            assert "seller" in order
            assert "batch_denom" in order
            assert "quantity" in order


@pytest.mark.asyncio
@pytest.mark.client
@pytest.mark.online
class TestRegenClientOnline:
    """Test RegenClient with live network connection.

    These tests actually hit the Regen Network and are marked as @online.
    Run with: pytest --online tests/client/
    """

    async def test_live_credit_types_query(self):
        """Test querying credit types from live network.

        This test MUST work against live network or deployment is broken.
        """
        client = get_regen_client()

        result = await client.query_credit_types()

        # Validate structure
        assert "credit_types" in result
        assert len(result["credit_types"]) > 0

        # Validate contains carbon
        types = [ct["abbreviation"] for ct in result["credit_types"]]
        assert "C" in types

    async def test_live_health_check(self):
        """Test health check against live endpoints.

        Validates that at least one endpoint is healthy.
        """
        client = get_regen_client()

        health = await client.health_check()

        # Should have results for both RPC and REST
        assert "rpc_endpoints" in health
        assert "rest_endpoints" in health

        # At least one REST endpoint should be healthy
        rest_status = [
            ep["status"]
            for ep in health["rest_endpoints"].values()
            if "status" in ep
        ]
        assert "healthy" in rest_status, \
            "At least one REST endpoint should be healthy"

    async def test_live_pagination(self):
        """Test pagination with live network."""
        client = get_regen_client()

        # Query with small limit to test pagination
        result = await client.query_credit_classes(
            pagination=Pagination(limit=5, offset=0, count_total=True)
        )

        assert "classes" in result
        assert len(result["classes"]) <= 5

        # Check pagination metadata
        if "pagination" in result:
            assert "total" in result["pagination"] or "next_key" in result["pagination"]


@pytest.mark.asyncio
@pytest.mark.client
class TestRegenClientErrorHandling:
    """Test error handling in RegenClient."""

    async def test_invalid_basket_denom_returns_error(self):
        """Test that querying non-existent basket returns proper error."""
        client = get_regen_client()

        with pytest.raises(Exception):  # Should raise NetworkError or similar
            await client.query_basket("INVALID_BASKET_DENOM_THAT_DOES_NOT_EXIST")

    async def test_connection_pooling_reuses_client(self):
        """Test that HTTP client is reused across requests."""
        client = get_regen_client()

        # Make multiple requests
        await client.query_credit_types()
        http_client_1 = client._http_client

        await client.query_credit_types()
        http_client_2 = client._http_client

        # Should reuse same client
        assert http_client_1 is http_client_2

    async def test_client_cleanup(self):
        """Test that client cleanup works properly."""
        client = RegenClient()

        # Use client
        await client.query_credit_types()
        assert client._http_client is not None

        # Close client
        await client.close()
        assert client._http_client is None


@pytest.mark.asyncio
@pytest.mark.client
class TestRegenClientExceptions:
    """Test exception classes have correct retryability attributes."""

    def test_network_error_is_retryable(self):
        """NetworkError should be retryable by default."""
        error = NetworkError("Connection failed")
        assert error.retryable is True
        assert error.retry_after_ms == 5000  # default

    def test_network_error_custom_retry_after(self):
        """NetworkError can have custom retry_after_ms."""
        error = NetworkError("Connection failed", retry_after_ms=10000)
        assert error.retryable is True
        assert error.retry_after_ms == 10000

    def test_validation_error_not_retryable(self):
        """ValidationError should not be retryable."""
        error = ValidationError("Invalid JSON")
        assert error.retryable is False
        assert error.retry_after_ms is None

    def test_http_client_error_not_retryable(self):
        """HTTP 4xx errors (except 429) should not be retryable."""
        for status_code in [400, 401, 403, 404, 405, 422]:
            error = HttpClientError(f"HTTP {status_code}", status_code=status_code)
            assert error.retryable is False, f"Status {status_code} should not be retryable"
            assert error.retry_after_ms is None

    def test_http_429_is_retryable(self):
        """HTTP 429 (Rate Limited) should be retryable."""
        error = HttpClientError("Rate limited", status_code=429, retry_after_ms=30000)
        assert error.retryable is True
        assert error.retry_after_ms == 30000

    def test_http_server_error_is_retryable(self):
        """HTTP 5xx errors should be retryable."""
        for status_code in [500, 502, 503, 504]:
            error = HttpServerError(f"HTTP {status_code}", status_code=status_code)
            assert error.retryable is True, f"Status {status_code} should be retryable"
            assert error.retry_after_ms == 5000  # default


@pytest.mark.asyncio
@pytest.mark.client
@pytest.mark.online
class TestFetchAllPages:
    """Test fetch_all_pages() helper with live network."""

    async def test_fetch_all_pages_basic(self):
        """Test basic fetch_all_pages functionality."""
        client = get_regen_client()

        result = await client.fetch_all_pages(
            path="/regen/ecocredit/v1/credit-types",
            page_size=100,
            max_pages=1,  # Just one page for this test
            item_key="credit_types",
        )

        # Validate structure
        assert "items" in result
        assert "pages_fetched" in result
        assert "exhausted" in result
        assert "warnings" in result

        # Should have fetched at least one page
        assert result["pages_fetched"] >= 1

        # Should have credit types
        assert len(result["items"]) > 0

    async def test_fetch_all_pages_with_pagination(self):
        """Test fetch_all_pages handles pagination correctly."""
        client = get_regen_client()

        result = await client.fetch_all_pages(
            path="/regen/ecocredit/v1/batches",
            page_size=5,  # Small page size to force pagination
            max_pages=2,  # Limit to 2 pages
            item_key="batches",
        )

        # Should have fetched up to 2 pages
        assert result["pages_fetched"] <= 2

        # If not exhausted, should have warning
        if not result["exhausted"]:
            assert any("MAX_PAGES" in w for w in result["warnings"])

    async def test_fetch_all_pages_max_items_cap(self):
        """Test fetch_all_pages respects max_items cap."""
        client = get_regen_client()

        result = await client.fetch_all_pages(
            path="/regen/ecocredit/v1/batches",
            page_size=100,
            max_pages=10,
            max_items=5,  # Cap at 5 items
            item_key="batches",
        )

        # Should have at most 5 items
        assert len(result["items"]) <= 5

        # Should have warning about cap
        if len(result["items"]) == 5:
            assert any("MAX_ITEMS" in w for w in result["warnings"])

    async def test_fetch_all_pages_auto_detect_item_key(self):
        """Test fetch_all_pages auto-detects item key."""
        client = get_regen_client()

        result = await client.fetch_all_pages(
            path="/regen/ecocredit/v1/credit-types",
            page_size=100,
            max_pages=1,
            # No item_key specified - should auto-detect "credit_types"
        )

        # Should still find items
        assert len(result["items"]) > 0


@pytest.mark.asyncio
@pytest.mark.client
class TestRetryableStatusDetection:
    """Test _is_retryable_status method."""

    async def test_4xx_not_retryable_except_429(self):
        """Test that 4xx errors are not retryable (except 429)."""
        client = get_regen_client()

        # 4xx should not be retryable
        assert client._is_retryable_status(400) is False
        assert client._is_retryable_status(401) is False
        assert client._is_retryable_status(403) is False
        assert client._is_retryable_status(404) is False
        assert client._is_retryable_status(422) is False

        # 429 should be retryable
        assert client._is_retryable_status(429) is True

    async def test_5xx_is_retryable(self):
        """Test that 5xx errors are retryable."""
        client = get_regen_client()

        assert client._is_retryable_status(500) is True
        assert client._is_retryable_status(502) is True
        assert client._is_retryable_status(503) is True
        assert client._is_retryable_status(504) is True

    async def test_2xx_and_3xx_not_retryable(self):
        """Test that success codes are not retryable (they don't need retry)."""
        client = get_regen_client()

        assert client._is_retryable_status(200) is False
        assert client._is_retryable_status(201) is False
        assert client._is_retryable_status(301) is False
        assert client._is_retryable_status(304) is False
