# Regen Network API Navigator

This guide helps you serve users effectively by understanding what data lives where and how to find it.

## Complete Endpoint Reference

### Ledger API (prefix: `/regen-api`)

**Ecocredits**
- `GET /regen-api/ecocredits/types` — Credit type definitions (C, BT, KSH, etc.)
- `GET /regen-api/ecocredits/classes` — All credit classes
- `GET /regen-api/ecocredits/projects` — All registered projects
- `GET /regen-api/ecocredits/batches` — All issued credit batches with quantities

**Marketplace**
- `GET /regen-api/marketplace/orders` — Active sell orders (credits for sale)
- `GET /regen-api/marketplace/denoms` — Accepted payment denominations

**Baskets**
- `GET /regen-api/baskets` — All basket tokens (like NCT)
- `GET /regen-api/baskets/{denom}` — Specific basket details
- `GET /regen-api/baskets/fee` — Basket creation fees

**Governance**
- `GET /regen-api/governance/proposals` — All governance proposals
- `GET /regen-api/governance/proposal/{id}/full` — Full proposal with votes
- `GET /regen-api/governance/params` — Governance parameters

**Bank (Token)**
- `GET /regen-api/bank/supply` — Total token supply
- `GET /regen-api/bank/balances/{address}` — Address balances
- `GET /regen-api/bank/accounts` — Account information
- `GET /regen-api/bank/metadata` — Token metadata
- `GET /regen-api/bank/params` — Bank module params

**Distribution**
- `GET /regen-api/distribution/pool` — Community pool
- `GET /regen-api/distribution/params` — Distribution parameters
- `GET /regen-api/distribution/delegator/{address}` — Delegator rewards
- `GET /regen-api/distribution/validator/{address}` — Validator commission

**Analytics**
- `GET /regen-api/analytics/trends` — Market trends
- `GET /regen-api/analytics/compare` — Compare credits
- `GET /regen-api/analytics/portfolio/{address}` — Portfolio analysis

**Utility**
- `GET /regen-api/summary` — Network overview

### Knowledge API (prefix: `/api/koi`)

- `GET /api/koi/weekly-digest` — Curated weekly activity summary
- `POST /api/koi/query` — Search knowledge base (body: `{"question": "..."}`)
- `GET /api/koi/graph` — Query codebase knowledge graph
- `GET /api/koi/stats` — Knowledge base statistics
- `GET /api/koi/health` — System health check

## Decision Guide

| When someone asks about... | Use this endpoint |
|---------------------------|-------------------|
| Credits for sale / marketplace | `GET /regen-api/marketplace/orders` |
| How many credits exist | `GET /regen-api/ecocredits/batches` |
| What credit types exist | `GET /regen-api/ecocredits/types` |
| List of projects | `GET /regen-api/ecocredits/projects` |
| Governance proposals | `GET /regen-api/governance/proposals` |
| Token supply | `GET /regen-api/bank/supply` |
| What happened this week | `GET /api/koi/weekly-digest` |
| What is [concept] | `POST /api/koi/query` |
| How does [thing] work | `POST /api/koi/query` |

## Understanding the Data

### Credit Lifecycle
1. **Methodology** defines how ecological outcomes are measured
2. **Credit Class** is created under a methodology (e.g., C01 for carbon)
3. **Project** registers land/activity under a class
4. **Batch** is issued when credits are verified (has start/end dates)
5. **Credits** can be held, sold, or retired

### Credit Types
Query `/regen-api/ecocredits/types` for current credit types — this data is live and authoritative.

### Key Concepts
- **dMRV** — Digital Monitoring, Reporting, Verification using technology for transparent tracking
- **Ecological State** — Measurable condition of an ecosystem's health and function
- **Retirement** — Permanently claiming a credit's environmental benefit (removes from circulation)
- **Basket tokens** — Query `/regen-api/baskets` for current basket tokens and their composition

## Common Questions Mapped

**"How many credits exist?"**
→ `/regen-api/ecocredits/batches` shows all issued batches with quantities

**"What's for sale?"**
→ `/regen-api/marketplace/orders` lists active sell orders

**"What projects are there?"**
→ `/regen-api/ecocredits/projects` returns all registered projects

**"What is regenerative agriculture?"**
→ Knowledge base query — this is conceptual, not on-chain

**"Who are the key people?"**
→ Knowledge base query — governance and community info lives in documents

**"What's the token price?"**
→ `/regen-api/bank/supply` for circulating supply; price requires external data

## When Things Go Wrong

**API returns error**
→ Upstream blockchain nodes occasionally have issues. Acknowledge the temporary limitation and offer what you can from other sources.

**Data seems missing**
→ Some information exists in the knowledge base but not on-chain (or vice versa). Be transparent about where you looked.

**Question spans both systems**
→ Combine sources. For "What carbon credits are for sale and what do they represent?" — check marketplace orders AND query knowledge base about the credit class.

## The Ecosystem Context

Regen Network connects:
- **Land stewards** doing regenerative work
- **Methodology developers** defining measurement standards
- **Credit buyers** supporting ecological outcomes
- **Validators** securing the blockchain
- **Community members** participating in governance

Everything flows toward one goal: making regeneration economically viable at scale.
