# ChatGPT REST API Implementation Plan for Regen Python MCP

## Executive Summary

This document outlines the pathway to serving a ChatGPT REST API for the Regen Python MCP server. The implementation follows the proven pattern from `regen-registry-review-mcp/chatgpt_rest_api.py`.

## Current State Analysis

### Architecture Overview

The Regen Python MCP is a **pure MCP server** using stdio-based communication:

- **Entry Point**: `main.py` → `server.run()`
- **Server**: FastMCP from `mcp.server.fastmcp`
- **Transport**: stdio (not HTTP)
- **No existing REST API**

### Tool Inventory (45 Tools)

| Module | Tools | Description |
|--------|-------|-------------|
| **Bank** | 11 | Account/balance queries (`get_balance`, `list_accounts`, etc.) |
| **Distribution** | 9 | Validator rewards, delegation info |
| **Governance** | 8 | Proposals, votes, deposits |
| **Marketplace** | 5 | Sell orders, allowed denoms |
| **Ecocredits** | 4 | Credit types, classes, projects, batches |
| **Baskets** | 5 | Ecocredit baskets and balances |
| **Analytics** | 3 | Portfolio analysis, market trends |

### Key Observations

1. **Tool implementations are modular** - Each module (`bank_tools.py`, `credit_tools.py`, etc.) contains independent async functions
2. **All tools return `Dict[str, Any]`** - JSON-serializable responses
3. **Pagination is page-based** - `page` (1-indexed) and `limit` parameters
4. **No authentication required** - Blockchain queries are public
5. **Error handling via dict** - `{"error": "message"}` pattern, not exceptions

## Implementation Strategy

### Option Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Direct FastAPI Wrapper** | Simple, low latency, full control | Bypasses MCP protocol |
| **MCP-to-HTTP Adapter** | Uses official MCP | Extra complexity, higher latency |
| **Hybrid (chosen)** | Best of both, matches reference pattern | None significant |

**Recommendation**: Use **Direct FastAPI Wrapper** pattern (matching registry-review-mcp approach) - import tool modules directly and call them from FastAPI endpoints.

### Implementation Plan

#### 1. Dependencies Addition

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
rest = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "python-multipart>=0.0.6",
]
```

#### 2. REST API Structure

```
chatgpt_rest_api.py
├── FastAPI app with CORS
├── OpenAPI schema generation
├── Endpoints organized by module:
│   ├── /                     # API info
│   ├── /bank/*               # 11 bank endpoints
│   ├── /distribution/*       # 9 distribution endpoints
│   ├── /governance/*         # 8 governance endpoints
│   ├── /marketplace/*        # 5 marketplace endpoints
│   ├── /ecocredits/*         # 4 ecocredit endpoints
│   ├── /baskets/*            # 5 basket endpoints
│   └── /analytics/*          # 3 analytics endpoints
└── Server startup
```

#### 3. Endpoint Mapping

Each MCP tool becomes an HTTP endpoint:

| MCP Tool | HTTP Method | Endpoint |
|----------|-------------|----------|
| `get_balance(address, denom)` | GET | `/bank/balance?address=...&denom=...` |
| `get_account(address)` | GET | `/bank/accounts/{address}` |
| `list_governance_proposals(...)` | GET | `/governance/proposals` |
| `get_sell_order(sell_order_id)` | GET | `/marketplace/orders/{sell_order_id}` |
| ... | ... | ... |

#### 4. ChatGPT OpenAPI Schema

FastAPI auto-generates OpenAPI 3.1 schema at `/openapi.json`. Key requirements:

- **Title**: "Regen Network API"
- **Description**: Clear tool descriptions for ChatGPT
- **Servers**: Production URL (`https://regen.gaiaai.xyz/ledger`)
- **Response models**: Pydantic schemas for type hints

### Endpoint Design Patterns

#### Query Parameters for Pagination
```python
@app.get("/governance/proposals")
async def list_proposals(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=200, description="Results per page"),
    proposal_status: str | None = Query(None, description="Filter by status")
):
    return await governance_tools.list_governance_proposals(page, limit, proposal_status)
```

#### Path Parameters for IDs
```python
@app.get("/governance/proposals/{proposal_id}")
async def get_proposal(proposal_id: int):
    return await governance_tools.get_governance_proposal(proposal_id)
```

#### Consistent Error Handling
```python
@app.get("/bank/accounts/{address}")
async def get_account(address: str):
    result = await bank_tools.get_account(address)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
```

### File Structure

```
regen-python-mcp/
├── chatgpt_rest_api.py      # NEW: FastAPI wrapper
├── main.py                   # Existing MCP entry point
├── pyproject.toml            # Updated with FastAPI deps
└── src/mcp_server/
    └── tools/                # Existing tool implementations (unchanged)
```

## Deployment Considerations

### Development
```bash
# Install dependencies
pip install ".[rest]"

# Run locally
python chatgpt_rest_api.py
# Serves at http://localhost:8004
```

### Production (similar to registry-review-mcp)
```bash
# Create tunnel for ChatGPT access
ssh -R 80:localhost:8004 nokey@localhost.run

# Or use nginx reverse proxy to regen.gaiaai.xyz/ledger
```

### ChatGPT Custom GPT Configuration
1. Create Custom GPT in ChatGPT
2. Add Action using OpenAPI schema from `https://regen.gaiaai.xyz/ledger/openapi.json`
3. Configure authentication (none required for public queries)

## Security Considerations

- All endpoints are read-only (blockchain queries)
- No authentication required (public data)
- CORS enabled for ChatGPT domains
- Rate limiting should be added for production

## Testing Strategy

1. **Unit tests**: Verify each endpoint calls correct tool function
2. **Integration tests**: Test against live blockchain endpoints
3. **OpenAPI validation**: Verify schema is valid for ChatGPT import

## Comparison with Registry Review MCP

| Aspect | Registry Review MCP | Regen Python MCP |
|--------|---------------------|------------------|
| Tools | Session/document workflow | Blockchain queries |
| State | Stateful sessions | Stateless queries |
| Auth | Session tokens | None |
| Endpoints | ~30 | 45 |
| Pattern | POST-heavy | GET-heavy |

## Conclusion

The implementation follows a proven pattern and should take approximately 2-3 hours to complete:

1. Create `chatgpt_rest_api.py` with 45 endpoints
2. Add FastAPI dependencies to `pyproject.toml`
3. Test endpoints
4. Deploy and configure ChatGPT Custom GPT

The clean separation of tool modules makes this straightforward - each FastAPI endpoint simply calls the corresponding tool function and returns its result.
