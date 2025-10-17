"""Pytest configuration and shared fixtures.

This module provides pytest fixtures and configuration for all tests.
Fixtures provide real Regen Network blockchain data.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.fixtures.fixture_manager import get_fixture_manager
from mcp_server.client.regen_client import RegenClient, get_regen_client


@pytest.fixture(scope="session")
def fixture_manager():
    """Session-wide fixture manager for real blockchain data."""
    return get_fixture_manager()


@pytest.fixture
async def regen_client():
    """Fixture providing RegenClient for tests."""
    client = get_regen_client()
    yield client
    # Cleanup after test
    await client.close()


@pytest.fixture
async def real_credit_types(fixture_manager):
    """Fixture providing real credit types from Regen Network.

    Data is cached for 30 days since credit types rarely change.
    First run will capture from network, subsequent runs use cache.
    """
    async def capture():
        client = get_regen_client()
        return await client.query_credit_types()

    return await fixture_manager.get_or_capture(
        fixture_name="credit_types",
        capture_func=capture,
        ttl_days=30,
        category="client"
    )


@pytest.fixture
async def real_credit_classes(fixture_manager):
    """Fixture providing real credit classes from Regen Network.

    Data is cached for 7 days as new classes are added periodically.
    """
    async def capture():
        client = get_regen_client()
        from mcp_server.client.regen_client import Pagination
        return await client.query_credit_classes(
            pagination=Pagination(limit=100, offset=0)
        )

    return await fixture_manager.get_or_capture(
        fixture_name="credit_classes",
        capture_func=capture,
        ttl_days=7,
        category="client"
    )


@pytest.fixture
async def real_projects(fixture_manager):
    """Fixture providing real projects from Regen Network.

    Data is cached for 7 days.
    """
    async def capture():
        client = get_regen_client()
        from mcp_server.client.regen_client import Pagination
        return await client.query_projects(
            pagination=Pagination(limit=100, offset=0)
        )

    return await fixture_manager.get_or_capture(
        fixture_name="projects",
        capture_func=capture,
        ttl_days=7,
        category="client"
    )


@pytest.fixture
async def real_credit_batches(fixture_manager):
    """Fixture providing real credit batches from Regen Network.

    Data is cached for 7 days.
    """
    async def capture():
        client = get_regen_client()
        from mcp_server.client.regen_client import Pagination
        return await client.query_credit_batches(
            pagination=Pagination(limit=100, offset=0)
        )

    return await fixture_manager.get_or_capture(
        fixture_name="credit_batches",
        capture_func=capture,
        ttl_days=7,
        category="client"
    )


@pytest.fixture
async def real_sell_orders(fixture_manager):
    """Fixture providing real marketplace sell orders from Regen Network.

    Data is cached for 1 day as marketplace changes frequently.
    """
    async def capture():
        client = get_regen_client()
        from mcp_server.client.regen_client import Pagination
        return await client.query_sell_orders(
            pagination=Pagination(limit=50, offset=0)
        )

    return await fixture_manager.get_or_capture(
        fixture_name="sell_orders",
        capture_func=capture,
        ttl_days=1,
        category="client"
    )


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--update-fixtures",
        action="store_true",
        default=False,
        help="Force update all cached fixtures from live network"
    )
    parser.addoption(
        "--online",
        action="store_true",
        default=False,
        help="Run online tests that require network connection"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, offline)")
    config.addinivalue_line("markers", "integration: Integration tests (medium speed)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (slow)")
    config.addinivalue_line("markers", "online: Tests requiring network connection")
    config.addinivalue_line("markers", "offline: Tests that can run without network")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "client: Client layer tests")
    config.addinivalue_line("markers", "tools: Tools layer tests")
    config.addinivalue_line("markers", "server: Server layer tests")
    config.addinivalue_line("markers", "mcp: MCP protocol tests")
    config.addinivalue_line("markers", "user_journey: User journey tests validating thesis use cases")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command-line options."""
    skip_online = pytest.mark.skip(reason="need --online option to run")

    for item in items:
        if "online" in item.keywords and not config.getoption("--online"):
            item.add_marker(skip_online)
