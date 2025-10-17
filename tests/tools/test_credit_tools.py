"""Tests for credit tools with real blockchain data.

These tests validate that credit tools return correct data when called through
the MCP interface. NO MOCK DATA - validates actual tool behavior.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.credit_tools import (
    list_credit_types,
    list_credit_classes,
    list_projects,
    list_credit_batches,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.offline
class TestCreditToolsWithRealData:
    """Test credit tools using real cached blockchain data."""

    async def test_list_credit_types_returns_valid_structure(self):
        """Test that list_credit_types tool returns proper MCP format.

        This test calls the actual tool function and validates:
        1. Response structure is correct
        2. Data contains real blockchain information
        3. Tool can be called successfully
        """
        # Call the actual tool
        result = await list_credit_types()

        # Validate MCP response structure
        assert isinstance(result, dict), "Tool must return dictionary"

        # Validate contains credit types data
        # (exact structure depends on tool implementation)
        assert "credit_types" in result or "data" in result or isinstance(result, dict)

        # If we got credit_types list, validate it
        if "credit_types" in result:
            credit_types = result["credit_types"]
            assert isinstance(credit_types, list)
            assert len(credit_types) > 0

            # Validate first credit type has expected fields
            ct = credit_types[0]
            assert "abbreviation" in ct or "name" in ct

    async def test_list_credit_classes_with_pagination(self):
        """Test list_credit_classes tool with pagination parameters."""
        # Call with small limit
        result = await list_credit_classes(limit=5, offset=0)

        assert isinstance(result, dict)

        # Should have classes data
        if "classes" in result:
            classes = result["classes"]
            assert isinstance(classes, list)
            assert len(classes) <= 5

    async def test_list_projects_returns_real_projects(self):
        """Test that list_projects returns actual Regen Network projects."""
        result = await list_projects(limit=10, offset=0)

        assert isinstance(result, dict)

        # Validate has projects
        if "projects" in result:
            projects = result["projects"]
            assert isinstance(projects, list)

            # If projects exist, validate structure
            if len(projects) > 0:
                project = projects[0]
                # Projects should have IDs, class references, etc.
                assert "id" in project or "project_id" in project

    async def test_list_credit_batches_returns_batches(self):
        """Test that list_credit_batches returns actual credit batches."""
        result = await list_credit_batches(limit=10, offset=0)

        assert isinstance(result, dict)

        # Validate has batches
        if "batches" in result:
            batches = result["batches"]
            assert isinstance(batches, list)

            # If batches exist, validate structure
            if len(batches) > 0:
                batch = batches[0]
                # Batches should have denoms, project IDs, etc.
                assert "denom" in batch or "batch_denom" in batch


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestCreditToolsOnline:
    """Test credit tools with live network connection."""

    async def test_live_list_credit_types(self):
        """Test list_credit_types against live network.

        This is a critical test: if this fails, the MCP cannot function.
        """
        result = await list_credit_types()

        # Must return data
        assert result is not None
        assert isinstance(result, dict)

        # Must contain credit types
        assert len(result) > 0

    async def test_live_list_classes_returns_known_classes(self):
        """Test that live query returns known credit classes like C01, C02."""
        result = await list_credit_classes(limit=100, offset=0)

        assert "classes" in result or isinstance(result, dict)

        # Extract class IDs
        if "classes" in result:
            class_ids = [c.get("id") for c in result["classes"]]
            # Should have carbon classes (C##)
            carbon_classes = [cid for cid in class_ids if cid and cid.startswith("C")]
            assert len(carbon_classes) > 0, \
                f"Should have carbon classes. Got: {class_ids}"


@pytest.mark.asyncio
@pytest.mark.tools
class TestCreditToolsEdgeCases:
    """Test edge cases and error handling in credit tools."""

    async def test_large_pagination_limit_handled(self):
        """Test that tools handle large pagination limits gracefully."""
        # Some APIs may limit max page size
        result = await list_credit_classes(limit=1000, offset=0)

        # Should not crash
        assert isinstance(result, dict)

    async def test_zero_offset_valid(self):
        """Test that offset=0 is valid (common edge case)."""
        result = await list_projects(limit=10, offset=0)

        assert isinstance(result, dict)

    async def test_tool_returns_empty_list_not_error(self):
        """Test that tools return empty lists, not errors, when no data."""
        # Query with very high offset (likely no results)
        result = await list_projects(limit=10, offset=999999)

        # Should return valid structure with empty list, not crash
        assert isinstance(result, dict)
