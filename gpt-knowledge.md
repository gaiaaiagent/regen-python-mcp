# Regen Network API Navigator

This guide helps you serve users effectively by understanding what data lives where and how to find it.

## Two Actions (Two Domains)

This GPT has two API Actions, each with its own domain constraint:

- **Ledger Action** (on-chain): `https://regen.gaiaai.xyz` (all `/regen-api/*` endpoints)
- **KOI Action** (knowledge): `https://registry.regen.gaiaai.xyz` (all `/api/koi/*` endpoints)

If a call fails without a `request_id`, assume the Action was not actually invoked and try again.

## Complete Endpoint Reference

### Ledger API (prefix: `/regen-api`)

**Ecocredits**
- `GET /regen-api/ecocredits/types` — Credit type definitions (C, BT, KSH, etc.)
- `GET /regen-api/ecocredits/classes` — All credit classes
- `GET /regen-api/ecocredits/projects` — All registered projects
- `GET /regen-api/ecocredits/batches` — All issued credit batches with quantities
- `GET /regen-api/ecocredits/classes/{class_id}/supply` — Retirement & supply stats for a credit class (total_issued, total_retired, retirement_rate_pct, per-batch breakdown)

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
- `POST /regen-api/analytics/compare` — Compare credits
- `GET /regen-api/analytics/portfolio/{address}` — Portfolio analysis

**Utility**
- `GET /regen-api/summary` — Network overview

### Knowledge API (prefix: `/api/koi`)

- `GET /api/koi/weekly-digest` — Curated weekly activity summary
- `POST /api/koi/query` — Search knowledge base (body: `{"question":"...","limit":3,"intent":"general|person_activity|...","source_policy":"public|internal_ok"}`)
- `POST /api/koi/graph` — Query codebase knowledge graph
- `POST /api/koi/entity` — Entity queries (body includes `query_type`: `resolve|neighborhood|documents`)

Notes:
- `/api/koi/stats` and `/api/koi/health` are intentionally not exposed to the GPT Action surface.

## Decision Guide

| When someone asks about... | Use this endpoint |
|---------------------------|-------------------|
| Credits for sale / marketplace | `GET /regen-api/marketplace/orders` |
| How many credits exist | `GET /regen-api/ecocredits/batches` |
| How many [X] credits have been retired? | `GET /regen-api/ecocredits/classes/{class_id}/supply` |
| Retirement rate for [credit class]? | `GET /regen-api/ecocredits/classes/{class_id}/supply` |
| What credit types exist | `GET /regen-api/ecocredits/types` |
| List of projects | `GET /regen-api/ecocredits/projects` |
| Governance proposals | `GET /regen-api/governance/proposals` |
| Token supply | `GET /regen-api/bank/supply` |
| What happened this week | `GET /api/koi/weekly-digest` |
| What is [concept] | `POST /api/koi/query` |
| How does [thing] work | `POST /api/koi/query` |
| What is [person] working on | `POST /api/koi/query` with `intent="person_activity"` |
| **[Specific name] credit class/project** | **FIRST** resolve via `POST /api/koi/entity`, then use resolved ID |

## Entity Resolution (CRITICAL)

When a user asks about a **specific credit class, project, or organization by NAME** (not by ID), you MUST:

1. **First**, call `/api/koi/entity` with `query_type: "resolve"` to get the canonical ID
2. **Then**, use that ID to query the ledger API

### Why This Matters

Names in the ecosystem can be ambiguous:
- "City Forest Credits" → C05 (the credit class ID)
- "Wilmot Woods" → C05-001 (a project ID)
- "Terrasos" → Organization that administers C04

Without resolution, you'll search the knowledge base by name and likely get wrong results (e.g., returning documents about different projects that happen to mention similar words).

### Example: "What is City Forest Credits?"

**WRONG approach** (leads to hallucinations):
```
POST /api/koi/query {"question": "City Forest Credits"}
→ Returns documents about many different things, possibly wrong projects
```

**CORRECT approach**:
```
Step 1: POST /api/koi/entity {"query_type": "resolve", "label": "City Forest Credits"}
→ Returns: {"winner": {"entity_text": "C05", "entity_type": "CREDIT_CLASS", ...}}

Step 2: GET /regen-api/ecocredits/classes (find C05 in results)
→ Returns authoritative on-chain data for C05
```

### When to Use Entity Resolution

| Query pattern | Action |
|---------------|--------|
| "What is [NAME]?" where NAME could be a credit/project/org | Resolve first |
| "Tell me about [NAME]" | Resolve first |
| "Show credits from [NAME]" | Resolve first |
| "What is regenerative agriculture?" | Skip - this is a concept, not an entity |
| "List all projects" | Skip - no specific entity to resolve |
| "What is C05?" | Skip - already an ID, no resolution needed |

### Entity Resolution Endpoint

```
POST /api/koi/entity
Body: {
  "query_type": "resolve",
  "label": "City Forest Credits",
  "type_hint": "CREDIT_CLASS"  // optional: helps disambiguate
}
```

Returns:
- `winner.entity_text` - The canonical ID (e.g., "C05")
- `winner.entity_type` - CREDIT_CLASS, PROJECT, or ORGANIZATION
- `winner.name` - Human-readable name from metadata
- `candidates` - Other possible matches if ambiguous

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

**"How many [X] credits have been retired?"**
→ `/regen-api/ecocredits/classes/{class_id}/supply` — returns total_retired, total_tradable, retirement_rate_pct for the class

**"What is the retirement rate for [credit class]?"**
→ `/regen-api/ecocredits/classes/{class_id}/supply` — retirement_rate_pct field in supply object

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
→ Check the `errors` array in the response:
- If `retryable: true`, wait for `retry_after_ms` and try again (max 2-3 retries)
- If `retryable: false`, the error is permanent (bad input, resource not found)
- Acknowledge the limitation and offer what you can from other sources

**Model didn’t actually call the Action**
→ If you do not see a real response envelope with `request_id`, do not invent results. Call the Action again and return the raw JSON.

**Data seems missing**
→ Some information exists in the knowledge base but not on-chain (or vice versa). Be transparent about where you looked.

**Question spans both systems**
→ Combine sources. For "What carbon credits are for sale and what do they represent?" — check marketplace orders AND query knowledge base about the credit class.

## Source Hygiene (Important)

- **Cite ALL sources you used**: If a source informed any part of your response, include it. Don't cherry-pick 1-2 when you used 5.
- Prefer primary, human-facing sources for citations: forum threads/posts, GitHub markdown docs, Notion pages, official web pages.
- Avoid citing derived crawl dumps or internal storage artifacts (e.g., GitHub paths like `koi-sensors/.../storage/*_crawl_*.json`) unless the user explicitly asks about that file.

## Critical Distinction: Credit Quantities vs. Impact Claims

**On-Chain Data (Authoritative)**
- Credit batch quantities, tradable/retired amounts
- Account balances, token supplies
- Governance proposal status, vote tallies
- These come from `/regen-api/*` endpoints

**Off-Chain Data (Requires Citation)**
- Impact claims: tCO₂e sequestered, hectares restored, species protected
- Project narratives, methodology descriptions
- Historical context, organizational information
- These come from `/api/koi/*` endpoints

**Rule**: Never present off-chain impact metrics as if they were on-chain verified quantities. Always cite the source document when presenting impact claims.

## The Ecosystem Context

Regen Network connects:
- **Land stewards** doing regenerative work
- **Methodology developers** defining measurement standards
- **Credit buyers** supporting ecological outcomes
- **Validators** securing the blockchain
- **Community members** participating in governance

Everything flows toward one goal: making regeneration economically viable at scale.
