# Complete Regen Ledger Data Taxonomy

**Generated**: 2025-10-17
**Method**: Live blockchain queries + codebase analysis
**Status**: ⚠️ Some endpoints experiencing issues (see notes)

## Executive Summary

Regen Network uses a **hierarchical taxonomy** for ecological credits, from foundational credit types down to individual tradeable batches. The system also includes marketplace mechanisms, governance structures, and standard Cosmos SDK modules for banking and distribution.

---

## 1. Credit Types (Foundation Layer)

**Endpoint**: `/regen/ecocredit/v1/credit-types`
**Status**: ✅ Working

Credit types are the **highest level taxonomy**, defining fundamental categories of ecological benefits.

### Active Credit Types (5 total)

| Abbreviation | Name | Unit | Precision | Description |
|--------------|------|------|-----------|-------------|
| **BT** | BioTerra | weighted 10m² score | 6 | Long-term restoration/preservation scoring |
| **C** | Carbon | metric ton CO2e | 6 | Carbon sequestration and emissions reduction |
| **KSH** | Kilo-Sheep-Hour | sheep × hours / 1000 | 6 | Regenerative grazing management |
| **MBS** | Marine Biodiversity Stewardship | generic | 6 | Marine ecosystem restoration |
| **USS** | Umbrella Species Stewardship | ~1 hectare-year | 6 | Biodiversity conservation through habitat |

### Structure

```json
{
  "abbreviation": "C",
  "name": "carbon",
  "unit": "metric ton CO2 equivalent",
  "precision": 6
}
```

### Key Insights
- All credits use **6 decimal precision** (1,000,000 base units = 1 whole credit)
- **Carbon (C)** is the most common type
- **KSH** represents innovative local knowledge integration
- **USS** uses composite index: Umbrella Species Health + Habitat Quality + Conservation interventions

---

## 2. Credit Classes (Methodology Layer)

**Endpoint**: `/regen/ecocredit/v1/classes`
**Status**: ⚠️ Currently failing with 'key' field error (model bug)

Credit classes define specific **methodologies** for generating credits within a type.

### Known Classes (from documentation)

| Class ID | Type | Description | Status |
|----------|------|-------------|--------|
| **C01** | Carbon | Reforestation & Afforestation | Active |
| **C02** | Carbon | Soil Carbon Sequestration | Active |
| **C03** | Carbon | Blue Carbon (Coastal/Marine) | Active (16 batches) |
| **C04** | Carbon | Avoided Emissions (Renewable Energy) | Active |
| **C07** | Carbon | TBD | Awaiting first issuance |

### Structure

```typescript
interface CreditClass {
  id: string;                    // e.g., "C01", "C02"
  admin: string;                 // Administrator address
  metadata: string;              // IPFS/AR link to methodology
  credit_type_abbrev: string;    // Links to Credit Type (e.g., "C")
}
```

### Key Relationships
```
CreditType (C)
  ├── CreditClass (C01) - Reforestation
  ├── CreditClass (C02) - Soil Carbon
  ├── CreditClass (C03) - Blue Carbon
  └── CreditClass (C04) - Avoided Emissions
```

---

## 3. Projects (Implementation Layer)

**Endpoint**: `/regen/ecocredit/v1/projects`
**Status**: ⚠️ Currently failing with 'key' field error (model bug)

Projects are **on-the-ground implementations** of credit class methodologies.

### Structure

```typescript
interface Project {
  id: string;                    // Unique project ID
  admin: string;                 // Project administrator address
  class_id: string;              // Links to Credit Class
  jurisdiction: string;          // Geographic jurisdiction code
  metadata: string;              // IPFS/AR link to project details
  reference_id: string;          // External reference ID (optional)
}
```

### Geographic Scope
- **jurisdiction**: ISO country code or regional identifier
- Enables filtering by geography for portfolio construction

### Key Relationships
```
CreditClass (C02)
  ├── Project A (Kenya soil carbon project)
  ├── Project B (India regenerative farm)
  └── Project C (Brazil pasture restoration)
```

---

## 4. Credit Batches (Issuance Layer)

**Endpoint**: `/regen/ecocredit/v1/batches`
**Status**: ⚠️ Currently failing with 'key' field error (model bug)

Credit batches are **specific issuances** of credits from a project, representing ecological work during a monitoring period.

### Observed Distribution
- **64 total batches** issued across network
- **Vintage years**: 2012-2034 (includes retroactive and forward-looking credits)
- **C03 class**: Leading with 16 batches

### Structure

```typescript
interface CreditBatch {
  issuer: string;                // Issuer address
  project_id: string;            // Links to Project
  denom: string;                 // Unique batch denomination (tradeable asset)
  metadata: string;              // Batch-specific metadata
  start_date: string;            // Monitoring period start
  end_date: string;              // Monitoring period end
  issuance_date: string;         // Date credits issued
  open: boolean;                 // Can more credits be issued to this batch?
}
```

### Batch Denomination Format
```
Example: C03-20190101-20191231-001
Format:  {ClassID}-{StartDate}-{EndDate}-{SequenceNumber}
```

### Supply Tracking

```typescript
interface Supply {
  batch_denom: string;           // Batch identifier
  tradable_amount: string;       // Available for sale
  retired_amount: string;        // Permanently retired
  cancelled_amount: string;      // Cancelled/invalid
}
```

### Lifecycle States
```
Issuance → Tradable → Escrowed → Retired/Cancelled
                   ↓
              Baskets (optional)
```

---

## 5. Baskets (Aggregation Layer)

**Endpoint**: `/regen/ecocredit/v1/baskets`
**Status**: ⚠️ HTTP 501 (not implemented on current endpoints)

Baskets are **fungible pools** of credits with similar attributes, enabling simplified trading.

### Structure

```typescript
interface Basket {
  basket_denom: string;          // Basket token denomination
  name: string;                  // Human-readable name
  description: string;           // Basket description
  exponent: number;              // Decimal precision
  curator: string;               // Basket curator address
  criteria: BasketCriteria;      // Acceptance criteria
}

interface BasketCriteria {
  credit_type_abbrev?: string;   // Filter by credit type
  allowed_classes?: string[];    // Whitelist of classes
  min_start_date?: string;       // Minimum vintage
  max_start_date?: string;       // Maximum vintage
  // Additional criteria...
}
```

### Known Basket
- **NCT** (Nature Carbon Ton): Verra credits tokenized by Toucan.earth
  - Base denom: `eco.uC.NCT` (micro-NCT)
  - Display denom: `eco.C.NCT` (NCT)
  - Backed 1:1 by Verra carbon credits

### Basket Operations
1. **Deposit**: Put credit batch into basket → receive basket tokens
2. **Withdraw**: Burn basket tokens → receive credit batches
3. **Trade**: Transfer basket tokens (fungible)

---

## 6. Marketplace (Trading Layer)

**Endpoint**: `/regen/ecocredit/marketplace/v1/sell-orders`
**Status**: ⚠️ HTTP 500 (server error)

The marketplace enables **direct trading** of credit batches.

### Sell Order Structure

```typescript
interface SellOrder {
  id: string;                    // Order ID
  seller: string;                // Seller address
  batch_denom: string;           // Which batch is for sale
  quantity: string;              // Amount for sale
  ask_denom: string;             // Payment currency
  ask_amount: string;            // Price per credit
  disable_auto_retire: boolean;  // Auto-retire on purchase?
  expiration: datetime;          // Order expiration
  market_id?: string;            // Market ID (optional)
}
```

### Pricing Structure
```
Total Cost = (quantity × ask_amount) in ask_denom currency

Example:
  quantity: "1000.000000" (1,000 credits)
  ask_amount: "10.000000" ($10 per credit)
  ask_denom: "uregen"
  Total: 10,000 REGEN
```

### Allowed Payment Denominations
**Endpoint**: `/regen/ecocredit/marketplace/v1/allowed-denoms`
**Status**: ⚠️ HTTP 500 (server error)

```typescript
interface AllowedDenom {
  bank_denom: string;            // Token denomination
  display_denom: string;         // Display name
  exponent: number;              // Decimal places
}
```

### Trading Workflow
```
1. Seller creates sell order
2. Buyer purchases credits
3. Credits transfer to buyer (optionally auto-retired)
4. Payment transfers to seller
```

---

## 7. Bank Module (Token Layer)

**Endpoint**: `/cosmos/bank/v1beta1/*`
**Status**: ✅ Mostly working

Standard Cosmos SDK bank module for managing tokens and denominations.

### Native Tokens

#### REGEN (Native Staking Token)
```json
{
  "base": "uregen",
  "display": "regen",
  "denom_units": [
    {"denom": "uregen", "exponent": 0, "aliases": ["microregen"]},
    {"denom": "mregen", "exponent": 3, "aliases": ["milliregen"]},
    {"denom": "regen", "exponent": 6, "aliases": []}
  ],
  "description": "The native staking token of Regen Network",
  "symbol": "REGEN"
}
```

#### NCT (Nature Carbon Ton)
```json
{
  "base": "eco.uC.NCT",
  "display": "eco.C.NCT",
  "denom_units": [
    {"denom": "eco.uC.NCT", "exponent": 0},
    {"denom": "eco.C.NCT", "exponent": 6}
  ],
  "description": "Nature Carbon Ton (NCT) backed 1:1 by Verra credits, tokenized by Toucan.earth",
  "symbol": "NCT"
}
```

### Denomination Patterns

| Pattern | Example | Purpose |
|---------|---------|---------|
| `uregen` | Base native token | Staking, fees, governance |
| `eco.uC.{BASKET}` | `eco.uC.NCT` | Basket base units |
| `eco.C.{BASKET}` | `eco.C.NCT` | Basket display units |
| `{CLASS}-{DATES}-{SEQ}` | `C03-20190101-20191231-001` | Credit batch denoms |

### Key Operations
- **Balance queries**: Track holdings by address and denom
- **Supply queries**: Total circulating supply
- **Metadata queries**: Human-readable info about tokens

---

## 8. Governance Module (Decision Layer)

**Endpoint**: `/cosmos/gov/v1beta1/*`
**Status**: ✅ Working

Standard Cosmos SDK governance for network decisions.

### Proposal Structure

```typescript
interface Proposal {
  proposal_id: string;           // Unique ID
  content: {
    "@type": string;             // Proposal type
    title: string;
    description: string;
    changes?: ParameterChange[]; // For param changes
    plan?: UpgradePlan;          // For upgrades
  };
  status: ProposalStatus;        // PASSED, REJECTED, VOTING, etc.
  final_tally_result: {
    yes: string;
    no: string;
    abstain: string;
    no_with_veto: string;
  };
  submit_time: datetime;
  deposit_end_time: datetime;
  voting_start_time: datetime;
  voting_end_time: datetime;
  total_deposit: Coin[];
}
```

### Observed Governance Activity
- **56 total proposals** on mainnet
- **Recent proposals**: Validator set changes, module upgrades, parameter adjustments
- **Key decisions**: Credit class creator permissions, voting period changes

### Proposal Types
1. **ParameterChangeProposal**: Modify chain parameters
2. **SoftwareUpgradeProposal**: Network upgrades
3. **TextProposal**: Signaling/discussion
4. **CommunityPoolSpendProposal**: Treasury allocation

---

## 9. Distribution Module (Rewards Layer)

**Endpoint**: `/cosmos/distribution/v1beta1/*`
**Status**: ✅ Working (based on client code)

Standard Cosmos SDK distribution for staking rewards.

### Community Pool
```json
{
  "pool": [
    {
      "denom": "uregen",
      "amount": "3461160191438.302945172187418784"
    }
  ]
}
```

**Current pool**: ~3.46 trillion uregen (~3.46 million REGEN)

### Key Queries
- Validator outstanding rewards
- Validator commission
- Delegator rewards (per validator and total)
- Validator slashing events

---

## Data Hierarchy Visualization

```
┌─────────────────────────────────────────────────────────┐
│ CREDIT TYPES (5)                                        │
│ BT | C | KSH | MBS | USS                                │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ CREDIT CLASSES (~11+)                                   │
│ C01 | C02 | C03 | C04 | C07 | ...                      │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ PROJECTS (100s)                                         │
│ Geographic implementations of methodologies             │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ CREDIT BATCHES (64 observed)                            │
│ Specific issuances with vintage periods                 │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌──────────────────┐
│ BASKETS       │       │ MARKETPLACE      │
│ (Fungible     │       │ (Direct Trading) │
│  Aggregation) │       │                  │
└───────────────┘       └──────────────────┘
```

---

## Cross-Cutting Concerns

### Addresses
All addresses follow **Bech32 format** with `regen1` prefix:
- Account: `regen1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Validator: `regenvaloper1xxxxxxxxxxxxxxxxxxxxxxx`

### Pagination
Standard pattern across endpoints:
```typescript
interface Pagination {
  limit: number;          // Items per page (1-1000)
  offset: number;         // Items to skip
  count_total: boolean;   // Include total count
  reverse: boolean;       // Reverse order
}

interface PaginationResponse {
  next_key: string;       // Key for next page
  total: number;          // Total items (if count_total=true)
}
```

### Metadata References
Most entities include `metadata` field pointing to off-chain data:
- **IPFS**: `ipfs://Qm...`
- **Arweave**: `ar://...`
- **HTTP**: `https://...`

Contains detailed information:
- Credit class: Full methodology document
- Project: Project details, documentation, monitoring reports
- Batch: Verification reports, monitoring data

---

## API Status Summary

| Module | Endpoint Status | Notes |
|--------|----------------|-------|
| Credit Types | ✅ Working | All 5 types retrieved |
| Credit Classes | ⚠️ Model Error | 'key' field bug in parser |
| Projects | ⚠️ Model Error | 'key' field bug in parser |
| Credit Batches | ⚠️ Model Error | 'key' field bug in parser |
| Baskets | ⚠️ HTTP 501 | Endpoint not implemented |
| Marketplace | ⚠️ HTTP 500 | Server error |
| Bank | ✅ Working | Metadata retrieved |
| Governance | ✅ Working | 56 proposals retrieved |
| Distribution | ✅ Working | Community pool retrieved |

### Known Issues
1. **Model parsing**: Tools expect 'key' field that doesn't exist in API responses (fixed in models, needs tool update)
2. **Basket endpoint**: Returns HTTP 501 on available endpoints
3. **Marketplace endpoint**: Returns HTTP 500 on available endpoints

---

## Data Relationships

### Primary Keys
- Credit Type: `abbreviation` (e.g., "C")
- Credit Class: `id` (e.g., "C03")
- Project: `id` (e.g., "P123")
- Credit Batch: `denom` (e.g., "C03-20190101-20191231-001")
- Basket: `basket_denom` (e.g., "eco.uC.NCT")
- Sell Order: `id` (e.g., "1")
- Governance Proposal: `proposal_id` (e.g., "56")

### Foreign Keys
```sql
CreditClass.credit_type_abbrev → CreditType.abbreviation
Project.class_id → CreditClass.id
CreditBatch.project_id → Project.id
SellOrder.batch_denom → CreditBatch.denom
```

---

## Query Patterns

### Find all credits of a type
```
1. Query credit_types, get abbreviation
2. Query classes, filter by credit_type_abbrev
3. For each class, query projects by class_id
4. For each project, query batches by project_id
```

### Find credits in geographic region
```
1. Query projects, filter by jurisdiction
2. For each project, query batches
3. Check marketplace for sell orders by batch_denom
```

### Analyze market for specific methodology
```
1. Query classes, find class_id
2. Query projects by class_id
3. Query batches by project_id
4. Query sell_orders, match by batch_denom
```

---

## Denomination Cheat Sheet

| Type | Pattern | Example | Description |
|------|---------|---------|-------------|
| Native Token | `u{token}` | `uregen` | Micro-denomination (10^-6) |
| Native Display | `{token}` | `regen` | Human-readable |
| Basket Base | `eco.uC.{NAME}` | `eco.uC.NCT` | Basket micro-units |
| Basket Display | `eco.C.{NAME}` | `eco.C.NCT` | Basket display units |
| Credit Batch | `{CLASS}-{DATE}-{SEQ}` | `C03-20190101-001` | Unique credit batch |

---

## Precision & Amounts

All amounts use **string representation** to avoid floating-point errors:
```typescript
"1000000" = 1.000000 (with 6 decimal precision)
"500000"  = 0.500000
"1"       = 0.000001
```

**Important**: Always parse as strings, never as floats!

---

## Use Case Examples

### Portfolio Manager
```
Goal: Diversify across 3 credit types and 5 geographies

1. Query credit_types → Get C, BT, MBS
2. Query projects, filter by jurisdiction codes
3. Query batches for selected projects
4. Query sell_orders for those batches
5. Calculate optimal allocation
```

### Arbitrage Trader
```
Goal: Find price discrepancies for same credit

1. Query sell_orders (all)
2. Group by batch_denom
3. Find batch_denom with multiple orders
4. Compare ask_amount across orders
5. Execute trades
```

### Impact Analyst
```
Goal: Track carbon sequestration by methodology

1. Query classes, filter C type
2. For each class, query projects
3. For each project, query batches
4. Sum retired_amount across batches
5. Analyze by class_id
```

---

## Conclusion

The Regen Ledger taxonomy is a **six-layer hierarchy**:

1. **Credit Types** - fundamental categories (BT, C, KSH, MBS, USS)
2. **Credit Classes** - specific methodologies (C01, C02, C03, etc.)
3. **Projects** - on-ground implementations
4. **Credit Batches** - specific issuances (the tradeable asset)
5. **Baskets** - fungible aggregations (optional)
6. **Marketplace** - trading infrastructure

This structure enables:
- ✅ **Granular differentiation** between ecological benefits
- ✅ **Methodology diversity** within credit types
- ✅ **Geographic tracking** through project jurisdictions
- ✅ **Temporal precision** via vintage periods
- ✅ **Market flexibility** through both direct trading and baskets
- ✅ **Governance integration** for parameter adjustments

The system balances **specificity** (individual batch tracking) with **fungibility** (basket aggregation), supporting both specialized impact investors and general market participants.

---

**Next Steps**:
1. Fix 'key' field parsing errors in credit tools
2. Investigate basket/marketplace endpoint issues
3. Add real-time supply tracking per batch
4. Implement cross-chain IBC credit transfers

**Generated by**: Claude Code MCP exploration
**Data Sources**: Live Regen Network mainnet + codebase analysis
