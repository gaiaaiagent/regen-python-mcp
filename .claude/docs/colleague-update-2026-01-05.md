# Update on regen-python-mcp Changes (2026-01-05)

Hi Shawn,

I've been working on `regen-python-mcp` as part of a broader KOI MCP review and remediation effort. This started from Greg's baseline test of the GPT/MCP system ([Slack thread](https://regen-network.slack.com/archives/C097T48KWHM/p1767165264292389?thread_ts=1767041624.321379&cid=C097T48KWHM)), which I reviewed and created a remediation plan for:

**Full remediation plan:** https://www.notion.so/regennetwork/KOI-MCP-Review-Reflection-and-Remediation-Plan-2da25b77eda180dfb157cbdde677d366

Here's a summary of what changed and why:

## What Changed

### Two-Action GPT Architecture
Split the OpenAPI spec into two Actions to expand beyond the 30-operation limit (30 per Action = 60 total capacity):
- **Ledger Action** (`openapi-gpt-ledger.json`, 25 ops) on `https://regen.gaiaai.xyz`
- **KOI Action** (`openapi-gpt-koi.json`, 4 ops) on `https://registry.regen.gaiaai.xyz`

### API Improvements
- **Batch supply totals**: `/regen-api/ecocredits/batches?summary=true&fetch_all=true` now includes real on-chain supply data (total_issued, total_tradable, total_retired)
- **Off-chain metrics**: `include_offchain_metrics=true` on `/regen-api/ecocredits/projects` for hectares from metadata IRIs
- **Pagination guidance**: Updated all 13 paginated endpoint descriptions to include "check `pagination.has_more` for additional pages"
- **Server-side retry/backoff**: Added retry logic with exponential backoff + jitter for idempotent queries
- **Governance fix**: Migrated to `/cosmos/gov/v1` API (v1beta1 was failing after chain upgrade)
- **Error handling**: REST fallback on `cosmos.directory` "chain not found" errors

### GPT Instructions
- Added mandatory host routing rules (KOI endpoints must use KOI Action, Ledger endpoints must use Ledger Action)
- Added privacy policy for Custom GPT sharing

## Deployment Status

All changes are merged to `main` and deployed to production. The PM2 service `regen-network-api` on port 8008 is running the latest code.

## Files to Know

- `openapi-gpt-ledger.json` / `openapi-gpt-koi.json` - The two GPT Action specs
- `openapi-combined.json` - Source of truth for all schemas
- `scripts/generate_openapi_schemas.py` - Regenerates GPT/full schemas
- `scripts/validate_openapi_gpt.py` - Validates op count, typed schemas, examples

## Re-uploading to GPT

If you need to update the Custom GPT:
1. Upload `openapi-gpt-ledger.json` as the Ledger Action
2. Upload `openapi-gpt-koi.json` as the KOI Action
3. Update instructions from `gpt-instructions.md`
4. Update knowledge from `gpt-knowledge.md`

## Tracking Doc

Full details: https://www.notion.so/regennetwork/KOI-MCP-Review-Reflection-and-Remediation-Plan-2da25b77eda180dfb157cbdde677d366

Let me know if you have questions!
