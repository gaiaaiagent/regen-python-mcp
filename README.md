# Regen Network MCP Server

> A Model Context Protocol (MCP) server providing programmatic access to the Regen Network blockchain - enabling AI agents and developers to interact with ecological credit markets.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This MCP server enables seamless interaction with [Regen Network](https://www.regen.network/), a blockchain platform designed for ecological asset verification and trading. Through a standardized interface, you can:

- 🌍 Query ecological credit types, classes, and batches
- 💰 Analyze marketplace dynamics and sell orders
- 📊 Perform portfolio impact analysis
- 🔍 Compare methodology frameworks
- ⛓️ Access blockchain data (bank, governance, distribution modules)
- 🤖 Enable AI agents to participate in environmental markets

### What is Regen Network?

Regen Network is a specialized blockchain infrastructure for ecological credits, supporting diverse asset types:
- **Carbon Credits** (CO2e sequestration and reduction)
- **Biodiversity Credits** (habitat preservation and restoration)
- **Regenerative Agriculture Metrics** (soil health, grazing management)

The network provides transparent, verifiable tracking of ecological projects with on-chain provenance.

### What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is a standardized interface for connecting AI systems to external data sources and tools. This server implements MCP to make Regen Network accessible to AI agents like Claude, ChatGPT, and custom applications.

## Features

### 🛠️ **45+ Blockchain Tools**

- **Bank Module** (11 tools): Account balances, token supplies, denomination metadata
- **Distribution Module** (9 tools): Validator rewards, delegator information, community pool
- **Governance Module** (8 tools): Proposals, votes, deposits, tally results
- **Marketplace Module** (5 tools): Sell orders, pricing, allowed denominations
- **Ecocredits Module** (4 tools): Credit types, classes, projects, batches
- **Baskets Module** (5 tools): Basket operations, balances, fees
- **Analytics Module** (3 tools): Portfolio impact, market trends, methodology comparison

### 📖 **8 Interactive Prompts**

Guided workflows for common tasks:
- Chain exploration and getting started
- Ecocredit query workshop
- Marketplace investigation
- Project discovery
- Credit batch analysis
- Query builder assistance
- Configuration setup
- Full capabilities reference

### 🔧 **Enterprise Features**

- Multiple endpoint failover for reliability
- Configurable caching layer
- Type-safe Pydantic models
- Async/await for performance
- Comprehensive error handling
- Health monitoring and metrics

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/your-org/regen-python-mcp.git
cd regen-python-mcp

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Configuration

The server uses environment variables for configuration. Create a `.env` file:

```bash
# Optional: Override default RPC endpoints
REGEN_RPC_ENDPOINTS=https://regen-rpc.polkachu.com,https://rpc.cosmos.directory/regen

# Optional: Override default REST endpoints
REGEN_REST_ENDPOINTS=https://regen-api.polkachu.com,https://rest.cosmos.directory/regen

# Optional: Configure caching
REGEN_MCP_ENABLE_CACHE=true
REGEN_MCP_CACHE_TTL_SECONDS=60

# Optional: Logging level
REGEN_MCP_LOG_LEVEL=INFO
```

See [`src/mcp_server/config/settings.py`](src/mcp_server/config/settings.py) for all configuration options.

## Quick Start

### Using with Claude Code / Claude Desktop

The repository includes pre-configured MCP setup files. See **[MCP_SETUP.md](MCP_SETUP.md)** for complete instructions.

**Quick Start:**
1. Files are already configured:
   - `.mcp.json` - Server connection config
   - `.claude/settings.json` - Enable MCP servers
2. Install dependencies: `pip install -r requirements.txt`
3. Restart Claude Code

**Manual Configuration:**

Add to your Claude Desktop or Claude Code configuration:

```json
{
  "mcpServers": {
    "regen-network": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/regen-python-mcp", "python", "main.py"],
      "env": {
        "PYTHONPATH": "/path/to/regen-python-mcp/src"
      }
    }
  }
}
```

### Using with Python

```python
from mcp.client import ClientSession, StdioServerParameters
import asyncio

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["main.py"]
    )

    async with ClientSession(server_params) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {len(tools)}")

        # List credit types
        result = await session.call_tool("list_credit_types", {})
        print(result)

asyncio.run(main())
```

### Example Queries

```python
# Get all ecological credit types
await client.call_tool("list_credit_types", {})

# List credit classes with pagination
await client.call_tool("list_classes", {"limit": 10, "offset": 0})

# Get marketplace sell orders
await client.call_tool("list_sell_orders", {"page": 1, "limit": 20})

# Analyze portfolio impact
await client.call_tool("analyze_portfolio_impact", {
    "address": "regen1...",
    "analysis_type": "full"
})

# Compare methodologies
await client.call_tool("compare_credit_methodologies", {
    "class_ids": ["C01", "C02", "C03"]
})
```

## Using With ChatGPT Custom GPT Actions (OpenAPI)

OpenAI Custom GPT Actions enforce a **maximum of 30 operations per OpenAPI spec**, and Action sets cannot include duplicate domains. This repo supports a **two-Action** setup:

- **Ledger Action** (on-chain): upload `openapi-gpt-ledger.json` with server `https://regen.gaiaai.xyz` (25 ops, `/regen-api/*` only)
- **KOI Action** (knowledge): upload `openapi-gpt-koi.json` with server `https://registry.regen.gaiaai.xyz` (4 ops, `/api/koi/*` only)

To regenerate the GPT/Full + split Action specs deterministically:

```bash
python3 scripts/generate_openapi_schemas.py
python3 scripts/validate_openapi_gpt.py --strict
```

Recommended instruction text for the GPT lives in:
- `gpt-instructions.md`
- `gpt-knowledge.md`

## Architecture

```
regen-python-mcp/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── docs/                        # Documentation
│   ├── regen_mcp_thesis.md     # Vision and use cases
│   └── regen_network_exploration_report.md
├── tests/                       # Test suite
├── archive/                     # Archived exploratory code
└── src/
    └── mcp_server/
        ├── server.py            # Main MCP server (45 tools, 8 prompts)
        ├── client/              # Regen Network API client
        ├── config/              # Configuration management
        ├── models/              # Pydantic data models
        ├── tools/               # Tool implementations by module
        ├── prompts/             # Interactive prompt guides
        ├── resources/           # Dynamic resource handlers
        ├── cache/               # Caching layer
        ├── monitoring/          # Health and metrics
        └── scrapers/            # Data collection utilities
```

### Design Principles

- **Modular Organization**: Tools grouped by blockchain module for maintainability
- **Type Safety**: Pydantic models throughout for runtime validation
- **Async-First**: All I/O operations use async/await patterns
- **Graceful Degradation**: Optional modules with fallback behavior
- **Configuration-Driven**: Environment variables for deployment flexibility

## Tool Reference

### Bank Module (11 tools)
- `list_accounts`, `get_account`, `get_balance`, `get_all_balances`
- `get_spendable_balances`, `get_total_supply`, `get_supply_of`
- `get_bank_params`, `get_denoms_metadata`, `get_denom_metadata`, `get_denom_owners`

### Distribution Module (9 tools)
- `get_distribution_params`, `get_validator_outstanding_rewards`
- `get_validator_commission`, `get_validator_slashes`
- `get_delegation_rewards`, `get_delegation_total_rewards`
- `get_delegator_validators`, `get_delegator_withdraw_address`, `get_community_pool`

### Governance Module (8 tools)
- `get_governance_proposal`, `list_governance_proposals`
- `get_governance_vote`, `list_governance_votes`
- `list_governance_deposits`, `get_governance_params`
- `get_governance_deposit`, `get_governance_tally_result`

### Marketplace Module (5 tools)
- `get_sell_order`, `list_sell_orders`
- `list_sell_orders_by_batch`, `list_sell_orders_by_seller`, `list_allowed_denoms`

### Ecocredits Module (4 tools)
- `list_credit_types`, `list_classes`, `list_projects`, `list_credit_batches`

### Baskets Module (5 tools)
- `list_baskets`, `get_basket`, `list_basket_balances`
- `get_basket_balance`, `get_basket_fee`

### Analytics Module (3 tools)
- `analyze_portfolio_impact`, `analyze_market_trends`, `compare_credit_methodologies`

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest black mypy ruff
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src/mcp_server tests/

# Run specific test file
pytest tests/test_prompts.py -v
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Documentation

- **[Prompts Guide](src/README_PROMPTS.md)**: Complete guide to interactive prompts
- **[Thesis Document](docs/regen_mcp_thesis.md)**: Vision, use cases, and impact potential
- **[Exploration Report](docs/regen_network_exploration_report.md)**: Technical deep-dive
- **[Configuration](src/mcp_server/config/settings.py)**: All configuration options

## Use Cases

### For AI Agents
- Autonomous environmental market analysis
- Automated portfolio optimization
- Real-time credit price discovery
- Methodology comparison and selection

### For Developers
- Building eco-finance applications
- Integrating Regen data into dashboards
- Creating custom analytics tools
- Prototyping new market mechanisms

### For Researchers
- Environmental credit market analysis
- Methodology effectiveness studies
- Market liquidity and pricing research
- Impact verification and tracking

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Regen Network](https://www.regen.network/) - For building the ecological credit infrastructure
- [Anthropic](https://www.anthropic.com/) - For the Model Context Protocol specification
- The open source community

## Links

- [Regen Network Documentation](https://docs.regen.network/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Report Issues](https://github.com/your-org/regen-python-mcp/issues)

---

**Built with 🌱 for a regenerative future**
