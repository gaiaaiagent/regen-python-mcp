# Batch Supply Enrichment Implementation

## Overview

This document describes the implementation of real supply totals in the `/regen-api/ecocredits/batches?summary=true` endpoint.

## On-Chain Source for Per-Batch Supply

**Endpoint:** `/regen/ecocredit/v1/batches/{batch_denom}/supply`

**Response Fields:**
- `tradable_amount` - Credits available for trading
- `retired_amount` - Credits that have been retired
- `cancelled_amount` - Credits that have been cancelled

**Total Issued Calculation:**
```
total_issued = tradable_amount + retired_amount + cancelled_amount
```

This follows the conservation of credits principle: all credits issued must be in one of these three states.

**Example Response:**
```json
{
  "tradable_amount": "0",
  "retired_amount": "3525",
  "cancelled_amount": "0"
}
```

## Enforced Caps

| Cap | Value | Purpose |
|-----|-------|---------|
| `MAX_BATCH_PAGES` | 50 | Max pages to fetch when `fetch_all=true` |
| `MAX_SUPPLY_BATCHES` | 500 | Max batches for supply data fetching |
| `SUPPLY_FETCH_TIMEOUT_SECONDS` | 25s | Time budget for supply fetching |
| `SUPPLY_MAX_CONCURRENT` | 20 | Max concurrent supply requests |

These constants are defined in `chatgpt_rest_api_v2.py` lines 74-81.

## Warning Semantics

The API emits warnings when supply totals are partial or incomplete:

| Warning Code | Meaning |
|--------------|---------|
| `SUPPLY_BATCHES_CAPPED` | Supply data fetched only for first N batches due to `MAX_SUPPLY_BATCHES` cap |
| `SUPPLY_TIMEOUT` | Supply fetching stopped due to time budget exhaustion |
| `SUPPLY_FETCH_FAILURES` | Some batches failed to fetch supply data |
| `PARTIAL_SUPPLY_DATA` | Supply data missing for some batches (not due to caps) |
| `PAGINATION_NOT_EXHAUSTED` | Batch list pagination was capped before exhaustion |
| `PARTIAL_SUMMARY` | Summary computed from first page only (when `fetch_all=false`) |

## Implementation Files

### `src/mcp_server/client/regen_client.py`
- `query_batch_supply(batch_denom: str)` - Single batch supply query (line 680)
- `query_batch_supplies_bulk(batch_denoms, max_concurrent, timeout_seconds)` - Bulk supply fetch with concurrency control (line 709)

### `chatgpt_rest_api_v2.py`
- Supply enrichment constants (lines 74-81)
- Summary mode implementation with supply fetching (lines 615-791)

### `openapi-combined.json`
- Updated examples showing non-zero totals
- Added `summary_partial` example demonstrating warning semantics

## Response Format (Summary Mode)

```json
{
  "data": {
    "summary": [
      {
        "credit_type": "C",
        "batch_count": 150,
        "total_issued": 1523456.5,
        "total_tradable": 498123.0,
        "total_retired": 1025333.5,
        "total_cancelled": 0.0,
        "unique_classes": 12,
        "unique_projects": 45
      }
    ],
    "batches_analyzed": 175,
    "batches_with_supply_data": 175,
    "total_batches": 175,
    "aggregation": {
      "method": "by_credit_type",
      "metrics": ["total_issued", "total_tradable", "total_retired", "total_cancelled"],
      "supply_source": "on-chain per-batch supply query"
    },
    "caps": {
      "max_batch_pages": 50,
      "max_supply_batches": 500,
      "supply_timeout_seconds": 25.0
    }
  },
  "request_id": "...",
  "data_source": "on-chain",
  "warnings": []
}
```

## Verification Commands

```bash
# Test summary mode (first page only)
curl "https://regen.gaiaai.xyz/regen-api/ecocredits/batches?summary=true"

# Test summary mode with all pages
curl "https://regen.gaiaai.xyz/regen-api/ecocredits/batches?summary=true&fetch_all=true"

# Test batch supply endpoint directly
curl "http://public-rpc.regen.vitwit.com:1317/regen/ecocredit/v1/batches/C01-001-20150101-20151231-001/supply"
```

## Performance Characteristics

- Single batch supply query: ~100-200ms
- Bulk supply fetch (100 batches, 20 concurrent): ~2-5 seconds
- Full summary with `fetch_all=true` (200 batches): ~10-20 seconds

The implementation uses async semaphores for concurrency control, preventing upstream API overload while maintaining good throughput.
