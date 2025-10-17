**Goal**

Enable quick, evidence-backed comparison of soil carbon methodologies and projects, starting with **Applied Ecology Institute (AEI)** and **EcoMetric** methods. This tool supports buyer decision-making, sales enablement, and registry operations.

**Inputs**

- Method docs: [Registry protocols library](https://www.registry.regen.network/crediting-protocols?utm_source=chatgpt.com)
    - AEI: [link](https://www.registry.regen.network/crediting-protocols/aei-regenerative-soil-organic-carbon-methodology-for-rangeland-grassland-agricultural-and-conservation-lands?utm_source=chatgpt.com)
    - EcoMetric: [link](https://www.registry.regen.network/crediting-protocols/ecometric---ghg-benefits-in-managed-crop-and-grassland-systems-credit-class?utm_source=chatgpt.com)
- Project data: Regen Ledger MCP server (≥2 projects per method)
- Buyer presets:
    - **High-Integrity** → MRV + Additionality
    - **EU-risk-sensitive** → Leakage + Traceability
    - **Net-Zero** → Cost + Permanence > Co-Benefits > Accuracy & Precision

**Core Features**

- Parse & normalize methodology + project data into common schema
- Criterion-based comparison (9 fixed dimensions)
- Side-by-side **method view** and **project view**
- Buyer preset filters for weighted scoring
- Markdown one-pager export

**Scoring**

- 0–3 scale: Insufficient / Partial / Adequate / Strong
- Each score includes citations and evidence notes

**Acceptance Criteria**

- [ ]  AEI + EcoMetric methods successfully ingested
- [ ]  Method comparison returns 9 criteria with citations ≤10s
- [ ]  Project comparison works across AEI/EcoMetric projects
- [ ]  Buyer preset alters scoring/ordering as expected
- [ ]  Markdown export generates clean, dated one-pager
