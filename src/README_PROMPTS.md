# 🌱 Regen Network MCP Prompts System

## Overview

The Regen Network MCP Server includes a comprehensive prompt system designed to guide users through blockchain exploration, ecological credit analysis, and marketplace investigation. These prompts provide interactive, context-aware guidance for working with the Regen Network ecosystem.

## Available Prompts

### 1. **Chain Exploration** (`chain_exploration`)
- **Purpose**: Initial exploration guide for the Regen Network chain
- **Features**: Quick start commands, module overview, data discovery paths
- **Parameters**: Optional `chain_info` for context-aware content

### 2. **Eco Credit Query Workshop** (`ecocredit_query_workshop`)
- **Purpose**: Comprehensive guide for querying eco credit modules
- **Features**: Credit classes, projects, batches, balances, advanced patterns
- **Parameters**: Optional `focus_area` (classes, projects, batches, marketplace)

### 3. **Marketplace Investigation** (`marketplace_investigation`)
- **Purpose**: Market analysis and trading query guidance
- **Features**: Price discovery, seller analysis, arbitrage detection, trading strategies
- **Parameters**: Optional `market_focus` (prices, sellers, arbitrage)

### 4. **Project Discovery** (`project_discovery`)
- **Purpose**: Find and analyze ecological projects
- **Features**: Geographic search, performance metrics, comparison tools
- **Parameters**: Optional `criteria` dict with location or credit_class filters

### 5. **Credit Batch Analysis** (`credit_batch_analysis`)
- **Purpose**: Deep dive into credit batch lifecycle
- **Features**: Supply analysis, retirement trends, market integration
- **Parameters**: Optional `batch_denom` for specific batch analysis

### 6. **List Regen Capabilities** (`list_regen_capabilities`)
- **Purpose**: Complete reference of all MCP server capabilities
- **Features**: All tools, prompts, query patterns, quick start examples
- **Parameters**: None

### 7. **Query Builder Assistant** (`query_builder_assistant`)
- **Purpose**: Help building complex queries step by step
- **Features**: Query templates, optimization tips, error handling patterns
- **Parameters**: Optional `query_type` (aggregation, filtering, analysis)

### 8. **Chain Config Setup** (`chain_config_setup`)
- **Purpose**: Guide for setting up chain configuration
- **Features**: Network options, endpoint testing, troubleshooting
- **Parameters**: None

## Installation

### Python Server

1. Install dependencies:
```bash
cd mcp/src
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

### Testing

Run the test suite:
```bash
python test_prompts.py
```

Or with pytest:
```bash
pytest test_prompts.py -v
```

## Usage Examples

### Using with MCP Client

```python
# Connect to the server
client = MCPClient("regen-network-mcp")

# List available prompts
prompts = await client.list_prompts()

# Get a specific prompt
response = await client.get_prompt(
    name="project_discovery",
    arguments={"criteria": {"location": "US"}}
)

# The response contains guided exploration content
print(response.messages[0].content.text)
```

### Direct Python Usage

```python
from prompts import project_discovery

# Get project discovery guidance
guidance = await project_discovery({"location": "United States"})
print(guidance)
```

## Prompt Design Patterns

### 1. **Context-Aware Content**
Prompts adapt based on provided parameters:
- Default content for general exploration
- Focused content when specific parameters are provided
- Progressive disclosure of advanced features

### 2. **Executable Examples**
All prompts include:
- Ready-to-run Python code snippets
- Real query patterns that work with the blockchain
- Progressive examples from simple to complex

### 3. **Educational Structure**
Each prompt follows a learning progression:
- Conceptual introduction
- Basic operations
- Advanced patterns
- Best practices
- Troubleshooting guides

### 4. **Visual Organization**
Prompts use markdown formatting for clarity:
- Emoji icons for visual navigation
- Clear section headers
- Code blocks with syntax highlighting
- Tables and lists for structured data

## Extending the System

### Adding New Prompts

1. Create a new prompt file in `src/prompts/`:
```python
# src/prompts/my_new_prompt.py
async def my_new_prompt(param: Optional[str] = None) -> str:
    """Your prompt implementation."""
    return """Your prompt content..."""
```

2. Add to `src/prompts/__init__.py`:
```python
from .my_new_prompt import my_new_prompt

# Add to __all__
__all__ = [..., "my_new_prompt"]

# Add to PROMPTS metadata
PROMPTS.append({
    "name": "my_new_prompt",
    "description": "Description of your prompt",
    "arguments": [...]
})
```

3. Update server routing in `src/server.py`:
```python
elif prompt_name == "my_new_prompt":
    param = arguments.get("param")
    return await my_new_prompt(param)
```

## Architecture

```
mcp/src/
├── prompts/                    # Prompt implementations
│   ├── __init__.py            # Package exports and metadata
│   ├── chain_exploration_prompt.py
│   ├── ecocredit_query_workshop_prompt.py
│   ├── marketplace_investigation_prompt.py
│   ├── project_discovery_prompt.py
│   ├── credit_batch_analysis_prompt.py
│   ├── list_regen_capabilities_prompt.py
│   ├── query_builder_assistant_prompt.py
│   └── chain_config_setup_prompt.py
├── server.py                   # MCP server implementation
├── test_prompts.py            # Test suite
├── requirements.txt           # Python dependencies
└── README_PROMPTS.md          # This file
```

## Key Features

### 🎯 **Focused Exploration**
- Start broad with chain exploration
- Dive deep into specific areas
- Progress from learning to doing

### 📚 **Comprehensive Documentation**
- Every tool and query pattern documented
- Real-world examples included
- Best practices and tips

### 🔧 **Practical Tools**
- Query builders for complex operations
- Market analysis utilities
- Project comparison tools

### 🌍 **Ecosystem Coverage**
- Credit classes and methodologies
- Projects and implementations
- Marketplace dynamics
- Supply and retirement tracking

## Support

For questions or issues:
1. Check the `list_regen_capabilities` prompt for complete reference
2. Use `query_builder_assistant` for help with complex queries
3. Refer to `chain_config_setup` for connection issues

## License

Part of the Regen Network MCP Server project.