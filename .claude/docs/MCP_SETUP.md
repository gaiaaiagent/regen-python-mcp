# MCP Server Setup for Claude Code

This guide explains how to configure Claude Code to connect to the Regen Network MCP server.

## Quick Setup

The repository includes two configuration files:

1. **`.mcp.json`** - MCP server connection configuration (machine-specific, gitignored)
2. **`.claude/settings.json`** - Claude Code settings to enable MCP servers

These files have been pre-configured for this installation.

## Configuration Files

### 1. `.mcp.json` (Current Configuration)

Located at the project root, this file tells Claude Code how to start the MCP server:

```json
{
  "mcpServers": {
    "regen-network": {
      "command": "/home/ygg/.local/bin/uv",
      "args": [
        "run",
        "--directory",
        "/home/ygg/Workspace/sandbox/regen-python-mcp",
        "python",
        "main.py"
      ],
      "env": {
        "PYTHONPATH": "/home/ygg/Workspace/sandbox/regen-python-mcp/src",
        "REGEN_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. `.claude/settings.json` (Current Configuration)

Located in `.claude/settings.json`, this enables all project MCP servers:

```json
{
  "enableAllProjectMcpServers": true
}
```

## Alternative Configurations

The repository includes `.mcp.json.example` with alternative setups:

### Option A: Direct Python (No uv)

```json
{
  "mcpServers": {
    "regen-network": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/regen-python-mcp/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/regen-python-mcp/src"
      }
    }
  }
}
```

### Option B: Virtual Environment

```json
{
  "mcpServers": {
    "regen-network": {
      "command": "/path/to/regen-python-mcp/venv/bin/python",
      "args": ["/path/to/regen-python-mcp/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/regen-python-mcp/src"
      }
    }
  }
}
```

## Installation Steps

### Prerequisites

1. **Install Dependencies:**
   ```bash
   cd /home/ygg/Workspace/sandbox/regen-python-mcp
   pip install -r requirements.txt
   ```

2. **Verify Installation:**
   ```bash
   python main.py --help
   ```

### Testing the Connection

1. **Restart Claude Code** after configuration changes

2. **Verify MCP Server is Loaded:**
   - Look for "regen-network" in Claude Code's MCP servers list
   - Check logs for connection status

3. **Test Basic Query:**
   ```
   Can you list the Regen Network MCP capabilities?
   ```

## Environment Variables

Optional environment variables you can add to `.mcp.json`:

```json
{
  "env": {
    "PYTHONPATH": "/path/to/regen-python-mcp/src",
    "REGEN_MCP_LOG_LEVEL": "INFO",
    "REGEN_MCP_ENABLE_CACHE": "true",
    "REGEN_MCP_CACHE_TTL_SECONDS": "60",
    "REGEN_RPC_ENDPOINTS": "https://regen-rpc.polkachu.com",
    "REGEN_REST_ENDPOINTS": "https://regen-api.polkachu.com"
  }
}
```

See [`src/mcp_server/config/settings.py`](src/mcp_server/config/settings.py) for all available configuration options.

## Troubleshooting

### Server Won't Start

1. **Check Python Path:**
   ```bash
   which python3
   which uv
   ```

2. **Verify Dependencies:**
   ```bash
   cd /home/ygg/Workspace/sandbox/regen-python-mcp
   pip install -r requirements.txt
   ```

3. **Test Server Manually:**
   ```bash
   cd /home/ygg/Workspace/sandbox/regen-python-mcp
   python main.py
   ```

### Import Errors

If you see import errors, ensure `PYTHONPATH` includes the `src` directory:

```json
{
  "env": {
    "PYTHONPATH": "/home/ygg/Workspace/sandbox/regen-python-mcp/src"
  }
}
```

### Configuration Not Loading

1. **Check File Locations:**
   ```bash
   ls -la /home/ygg/Workspace/sandbox/regen-python-mcp/.mcp.json
   ls -la /home/ygg/Workspace/sandbox/regen-python-mcp/.claude/settings.json
   ```

2. **Validate JSON:**
   ```bash
   cat .mcp.json | python -m json.tool
   ```

3. **Restart Claude Code** completely

### Connection Warnings

If you see warnings about missing config directories:
```
Warning: Config directory not found for buyer presets
```

This is **non-critical** and doesn't affect core functionality. To resolve:
```bash
mkdir -p /home/ygg/Workspace/sandbox/config/buyer_presets
```

## Available Tools

Once connected, you'll have access to **45+ tools**:

- **Bank Module** (11 tools): Account queries, balances, supply
- **Distribution Module** (9 tools): Validator rewards, delegations
- **Governance Module** (8 tools): Proposals, votes, deposits
- **Marketplace Module** (5 tools): Sell orders, pricing
- **Ecocredits Module** (4 tools): Credit types, classes, projects, batches
- **Baskets Module** (5 tools): Basket operations
- **Analytics Module** (3 tools): Portfolio analysis, market trends

Plus **8 interactive prompts** for guided workflows.

## Example Usage

### In Claude Code Chat

```
User: List all ecological credit types on Regen Network

Claude: [Uses list_credit_types tool]

User: Analyze market trends for the last 30 days

Claude: [Uses analyze_market_trends tool]

User: Compare methodologies for credit classes C01, C02, C03

Claude: [Uses compare_credit_methodologies tool]
```

## File Locations

```
/home/ygg/Workspace/sandbox/regen-python-mcp/
├── .mcp.json                    # MCP server config (gitignored)
├── .mcp.json.example            # Example configurations
├── .claude/
│   └── settings.json            # Claude Code settings
├── main.py                      # Server entry point
├── src/mcp_server/
│   └── server.py                # Canonical server implementation
└── requirements.txt             # Python dependencies
```

## Security Notes

- **`.mcp.json` is gitignored** - It contains machine-specific absolute paths
- **`.mcp.json.example`** provides templates for your setup
- **Never commit `.env` files** with sensitive credentials
- **Environment variables** are the recommended way to pass secrets

## Updating Configuration

1. **Edit `.mcp.json`** for server connection changes
2. **Edit `.claude/settings.json`** for Claude Code settings
3. **Restart Claude Code** to apply changes

## Additional Resources

- **[README.md](README.md)** - Full project documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[src/README_PROMPTS.md](src/README_PROMPTS.md)** - Interactive prompts guide
- **[docs/regen_mcp_thesis.md](docs/regen_mcp_thesis.md)** - Project vision

---

**Status:** ✅ Configuration files created and ready

The MCP server is now configured and ready to connect with Claude Code!
