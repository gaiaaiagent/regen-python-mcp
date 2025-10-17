#!/usr/bin/env python3
"""Test suite for Regen Network MCP Server prompts."""

import asyncio
import pytest
from typing import Dict, Any

# Import all prompts
from prompts import (
    chain_exploration,
    ecocredit_query_workshop,
    marketplace_investigation,
    project_discovery,
    credit_batch_analysis,
    list_regen_capabilities,
    query_builder_assistant,
    chain_config_setup,
)


class TestPrompts:
    """Test all prompt functions."""
    
    @pytest.mark.asyncio
    async def test_chain_exploration_default(self):
        """Test chain exploration prompt with default parameters."""
        result = await chain_exploration()
        assert isinstance(result, str)
        assert "Regen Network Chain Explorer" in result
        assert "Quick Start" in result
        
    @pytest.mark.asyncio
    async def test_chain_exploration_with_info(self):
        """Test chain exploration prompt with chain info."""
        chain_info = {
            "chain_id": "regen-1",
            "status": "connected"
        }
        result = await chain_exploration(chain_info)
        assert isinstance(result, str)
        assert "Connected to regen-1" in result
        
    @pytest.mark.asyncio
    async def test_ecocredit_query_workshop_default(self):
        """Test eco credit workshop prompt with default parameters."""
        result = await ecocredit_query_workshop()
        assert isinstance(result, str)
        assert "Eco Credit Query Workshop" in result
        assert "Credit Classes" in result
        
    @pytest.mark.asyncio
    async def test_ecocredit_query_workshop_classes(self):
        """Test eco credit workshop prompt with classes focus."""
        result = await ecocredit_query_workshop("classes")
        assert isinstance(result, str)
        assert "Credit Class Exploration" in result
        assert "C01" in result
        
    @pytest.mark.asyncio
    async def test_marketplace_investigation_default(self):
        """Test marketplace investigation prompt with default parameters."""
        result = await marketplace_investigation()
        assert isinstance(result, str)
        assert "Marketplace Investigation Suite" in result
        assert "Market Analysis" in result
        
    @pytest.mark.asyncio
    async def test_marketplace_investigation_prices(self):
        """Test marketplace investigation prompt with prices focus."""
        result = await marketplace_investigation("prices")
        assert isinstance(result, str)
        assert "Price Discovery & Analysis" in result
        
    @pytest.mark.asyncio
    async def test_project_discovery_default(self):
        """Test project discovery prompt with default parameters."""
        result = await project_discovery()
        assert isinstance(result, str)
        assert "Regen Project Discovery Session" in result
        assert "Open Project Discovery" in result
        
    @pytest.mark.asyncio
    async def test_project_discovery_with_location(self):
        """Test project discovery prompt with location criteria."""
        criteria = {"location": "United States"}
        result = await project_discovery(criteria)
        assert isinstance(result, str)
        assert "United States" in result
        assert "Projects in United States" in result
        
    @pytest.mark.asyncio
    async def test_credit_batch_analysis_default(self):
        """Test credit batch analysis prompt with default parameters."""
        result = await credit_batch_analysis()
        assert isinstance(result, str)
        assert "Credit Batch Deep Dive" in result
        assert "Credit Batch Analysis" in result
        
    @pytest.mark.asyncio
    async def test_credit_batch_analysis_specific(self):
        """Test credit batch analysis prompt with specific batch."""
        batch = "C01-001-20240101-20240131-001"
        result = await credit_batch_analysis(batch)
        assert isinstance(result, str)
        assert batch in result
        assert "Supply and circulation metrics" in result
        
    @pytest.mark.asyncio
    async def test_list_regen_capabilities(self):
        """Test list capabilities prompt."""
        result = await list_regen_capabilities()
        assert isinstance(result, str)
        assert "Regen MCP Server Capabilities" in result
        assert "Query Tools" in result
        assert "Interactive Prompts" in result
        
    @pytest.mark.asyncio
    async def test_query_builder_assistant_default(self):
        """Test query builder assistant prompt with default parameters."""
        result = await query_builder_assistant()
        assert isinstance(result, str)
        assert "Query Builder Assistant" in result
        assert "General Query Building" in result
        
    @pytest.mark.asyncio
    async def test_query_builder_assistant_aggregation(self):
        """Test query builder assistant prompt with aggregation focus."""
        result = await query_builder_assistant("aggregation")
        assert isinstance(result, str)
        assert "Aggregation Queries" in result
        assert "Summing credits" in result
        
    @pytest.mark.asyncio
    async def test_chain_config_setup(self):
        """Test chain config setup prompt."""
        result = await chain_config_setup()
        assert isinstance(result, str)
        assert "Chain Configuration Setup Guide" in result
        assert "Network Options" in result
        assert "Mainnet" in result
        assert "Testnet" in result


class TestPromptContent:
    """Test specific content and examples in prompts."""
    
    @pytest.mark.asyncio
    async def test_code_examples_present(self):
        """Verify that prompts contain executable code examples."""
        prompts_to_check = [
            chain_exploration(),
            ecocredit_query_workshop(),
            marketplace_investigation(),
            project_discovery(),
            credit_batch_analysis(),
            query_builder_assistant(),
        ]
        
        for prompt_coro in prompts_to_check:
            result = await prompt_coro
            # Check for code blocks
            assert "```python" in result or "```" in result
            # Check for function definitions
            assert "def " in result or "get_" in result
            
    @pytest.mark.asyncio
    async def test_markdown_formatting(self):
        """Verify that prompts use proper markdown formatting."""
        result = await list_regen_capabilities()
        
        # Check for headers
        assert "##" in result or "#" in result
        # Check for bullet points
        assert "•" in result or "-" in result or "*" in result
        # Check for emphasis
        assert "**" in result or "*" in result
        
    @pytest.mark.asyncio
    async def test_regen_specific_content(self):
        """Verify Regen Network specific content is present."""
        result = await ecocredit_query_workshop()
        
        # Check for Regen-specific terms
        assert "Regen Network" in result
        assert "ecological" in result.lower() or "eco" in result.lower()
        assert "carbon" in result.lower() or "credit" in result.lower()
        
        # Check for credit class references
        assert "C01" in result or "C02" in result
        
    @pytest.mark.asyncio
    async def test_educational_content(self):
        """Verify educational content is included."""
        result = await chain_config_setup()
        
        # Check for troubleshooting section
        assert "Troubleshooting" in result or "troubleshoot" in result.lower()
        # Check for best practices
        assert "Best Practices" in result or "Tips" in result
        # Check for examples
        assert "Example" in result or "example" in result.lower()


class TestPromptIntegration:
    """Test prompt integration with server."""
    
    def test_prompt_metadata(self):
        """Test that PROMPTS metadata is properly defined."""
        from prompts import PROMPTS
        
        assert isinstance(PROMPTS, list)
        assert len(PROMPTS) == 8  # We have 8 prompts
        
        for prompt_info in PROMPTS:
            assert "name" in prompt_info
            assert "description" in prompt_info
            assert "arguments" in prompt_info
            assert isinstance(prompt_info["arguments"], list)
            
    def test_prompt_names_match_functions(self):
        """Test that prompt names in metadata match function names."""
        from prompts import PROMPTS
        import prompts
        
        for prompt_info in PROMPTS:
            prompt_name = prompt_info["name"]
            # Check that the function exists in the module
            assert hasattr(prompts, prompt_name)
            # Check that it's callable
            assert callable(getattr(prompts, prompt_name))


def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    # For quick testing without pytest
    async def quick_test():
        """Quick test of all prompts."""
        print("Testing all prompts...")
        
        prompts_to_test = [
            ("chain_exploration", chain_exploration()),
            ("ecocredit_query_workshop", ecocredit_query_workshop()),
            ("marketplace_investigation", marketplace_investigation()),
            ("project_discovery", project_discovery()),
            ("credit_batch_analysis", credit_batch_analysis()),
            ("list_regen_capabilities", list_regen_capabilities()),
            ("query_builder_assistant", query_builder_assistant()),
            ("chain_config_setup", chain_config_setup()),
        ]
        
        for name, prompt_coro in prompts_to_test:
            try:
                result = await prompt_coro
                print(f"✅ {name}: {len(result)} characters")
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
        
        print("\nAll prompts tested successfully!")
    
    # Run quick test
    asyncio.run(quick_test())