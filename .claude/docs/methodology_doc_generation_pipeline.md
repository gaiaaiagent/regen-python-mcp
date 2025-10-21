# Methodology Document Generation Pipeline

**Version:** 1.0
**Date:** 2025-10-21
**Purpose:** Generate normalized 9-criteria methodology documents from multiple sources

---

## Pipeline Overview

The methodology document generator is a **multi-source, fallback-based pipeline** that:

1. **Attempts multiple data sources** in order of quality/reliability
2. **Normalizes heterogeneous data** into canonical 9-criteria schema
3. **Uses LLM assistance** for intelligent extraction and validation
4. **Caches results** to avoid repeated fetches
5. **Tracks provenance** for transparency and debugging

---

## Data Sources (Priority Order)

### **Tier 1: Regen KOI Knowledge Graph** ⭐ (Preferred)
**Why:** Curated, structured, actively maintained knowledge base

**MCP Tools:**
- `search_knowledge(query, filters)` - Search for methodology documents
- `get_entity(identifier)` - Get specific methodology/credit class details

**Capabilities:**
- Semantic search across methodology docs
- Credit class → methodology mapping
- Structured metadata extraction
- Governance and version tracking

**Example Usage:**
```python
# Search for AEI methodology
results = await mcp_regen_koi.search_knowledge(
    query="AEI Regenerative Soil Organic Carbon Methodology",
    filters={"source_type": "methodology"}
)

# Get detailed credit class info
c02_details = await mcp_regen_koi.get_entity(
    identifier="C02",  # or "orn:credit_class:C02"
    include_related=True
)
```

**Advantages:**
- ✅ Structured, validated data
- ✅ Fast retrieval (<1s)
- ✅ Relationships preserved (credit class ↔ methodology)
- ✅ Version tracking
- ✅ No rate limiting issues

**Limitations:**
- ⚠️ Coverage may be incomplete for new methodologies
- ⚠️ May not have granular 9-criteria breakdowns

### **Tier 2: Web Scraping (Regen Registry)** 🌐
**Why:** Comprehensive, official source of truth

**Tools:**
- `RegistryScraper` (existing in `scrapers/registry_scraper.py`)
- `WebFetch` tool (for Claude Code integration)

**Capabilities:**
- Fetch official methodology documents
- Extract sections (MRV, Additionality, etc.)
- Parse tables and structured content
- Cache raw HTML for audit

**Example URLs:**
- AEI: `https://www.registry.regen.network/crediting-protocols/aei-regenerative-soil-organic-carbon-methodology-for-rangeland-grassland-agricultural-and-conservation-lands`
- EcoMetric: `https://www.registry.regen.network/crediting-protocols/ecometric---ghg-benefits-in-managed-crop-and-grassland-systems-credit-class`

**Advantages:**
- ✅ Official, authoritative source
- ✅ Comprehensive coverage
- ✅ Includes full text for LLM extraction

**Limitations:**
- ⚠️ Unstructured HTML - requires parsing
- ⚠️ Slower (2-5s per methodology)
- ⚠️ Potential for HTML structure changes

### **Tier 3: LLM-Enhanced Web Search** 🔍
**Why:** Fallback for methodologies not in KOI or Registry

**Tools:**
- `WebSearch` - Find methodology documents
- `WebFetch` - Retrieve found documents
- Claude (this conversation) - Extract and normalize

**Workflow:**
1. Search: `"[Methodology Name] carbon credit methodology PDF"`
2. Fetch top results
3. LLM extracts 9-criteria data
4. Human validation required (confidence < 0.8)

**Example:**
```python
# Search for methodology document
search_results = await web_search(
    query="VCS VM0042 methodology additionality leakage permanence"
)

# Fetch and extract
for result in search_results[:3]:
    content = await web_fetch(result.url)
    extracted = await llm_extract_9_criteria(content)
```

**Advantages:**
- ✅ Universal fallback
- ✅ Can find external methodologies (Verra, Gold Standard, etc.)
- ✅ LLM can handle varied formats

**Limitations:**
- ⚠️ Requires validation
- ⚠️ Slower (10-30s)
- ⚠️ May require multiple iterations
- ⚠️ Lower confidence scores

### **Tier 4: Blockchain-Only (Degraded Mode)** ⛓️
**Why:** Last resort when no methodology docs available

**Source:** Regen Ledger MCP + inference

**Approach:**
- Use credit class metadata
- Infer from project patterns
- Use methodology type heuristics
- Lower all confidence scores

**Example:**
```python
# No methodology doc available, use blockchain inference
methodology_data = infer_from_blockchain(
    credit_class_id="C02",
    projects=projects,
    batches=batches
)
# All scores get confidence penalty: confidence *= 0.6
```

---

## Normalized Schema

All methodologies are normalized to this canonical structure:

```json
{
  "methodology_id": "aei",
  "credit_class_id": "C02",
  "official_name": "AEI Regenerative Soil Organic Carbon Methodology...",
  "scraped_at": "2025-10-21T12:00:00Z",
  "data_sources": ["koi", "registry_web"],  // Provenance tracking
  "confidence_score": 0.95,  // Overall data quality

  "mrv": {
    "monitoring_approach": "soil_sampling_laboratory_analysis",
    "monitoring_frequency": "annual",
    "sampling_requirements": "rigorous soil sampling protocols",
    "verification_type": "independent_third_party",
    "reporting_standards": ["ISO", "Verra", "Climate Action Reserve"],
    "evidence_sources": ["Section 4.2: MRV Protocol"],
    "confidence": 0.95
  },

  "additionality": {
    "assessment_required": true,
    "barrier_analysis": "comprehensive",  // Enum: none|described|comprehensive
    "baseline_methodology": "described",  // Enum: not_specified|described|quantified
    "evidence_sources": ["Section 3.1: Additionality"],
    "confidence": 0.90
  },

  "leakage": {
    "assessment_approach": "landscape_level",  // Enum: project|landscape|regional
    "boundary_definition": "clear_project_boundaries",
    "risk_level": "low",  // Enum: low|moderate|high
    "evidence_sources": ["Section 3.3: Leakage Assessment"],
    "confidence": 0.88
  },

  "traceability": {
    "record_keeping": "blockchain_native",
    "tracking_mechanism": "regen_registry",
    "transparency_level": "high",  // Enum: low|moderate|high
    "confidence": 1.0  // Always high for Regen Registry
  },

  "cost_efficiency": {
    "estimated_cost_per_credit": 12.50,  // USD, nullable
    "methodology_complexity": "moderate",  // Enum: simple|moderate|complex
    "implementation_requirements": ["soil_sampling", "lab_analysis"],
    "confidence": 0.70
  },

  "permanence": {
    "monitoring_period_years": 10,
    "buffer_pool_percentage": 10,
    "reversal_risk_management": "described",
    "evidence_sources": ["Section 5: Permanence"],
    "confidence": 0.85
  },

  "co_benefits": {
    "documented_benefits": [
      "soil_health_improvement",
      "biodiversity_enhancement",
      "water_quality_improvement",
      "rural_economic_development"
    ],
    "quantification_approach": "qualitative_with_some_metrics",
    "sdg_alignment": ["SDG13", "SDG15", "SDG2"],
    "evidence_sources": ["Section 6: Co-Benefits"],
    "confidence": 0.80
  },

  "accuracy": {
    "measurement_protocols": ["laboratory_analysis", "field_sampling"],
    "uncertainty_quantification": true,
    "peer_review_status": "published",  // Enum: draft|in_review|published
    "standards_compliance": ["IPCC_2003", "ISO"],
    "confidence": 0.92
  },

  "precision": {
    "consistency_measures": "described",
    "replication_protocols": true,
    "statistical_validation": "required",
    "confidence": 0.88
  },

  "project_requirements": {
    "eligible_land_types": ["rangeland", "grassland", "agricultural"],
    "practices": ["regenerative_agriculture", "rotational_grazing"],
    "geographic_scope": "global_with_us_focus",
    "minimum_project_size_hectares": null
  },

  "metadata": {
    "version": "1.2",
    "last_updated": "2024-09-15",
    "developer": "Applied Ecological Institute",
    "status": "active",  // Enum: draft|active|retired
    "documentation_url": "https://...",
    "peer_review_reports": []
  }
}
```

**Key Features:**
1. **Confidence scores per criterion** - Enables validation prioritization
2. **Evidence sources** - Citations for transparency
3. **Controlled vocabularies** - Enums for consistency
4. **Provenance tracking** - data_sources field
5. **Nullable fields** - Graceful handling of missing data

---

## Pipeline FSM (Updated)

**New States:**

### `GENERATING_METHODOLOGY_DOCS`
Entry point for methodology document generation

**Substates:**
1. `QUERYING_KOI` - Search Regen KOI knowledge graph
2. `WEB_SCRAPING` - Fetch from Regen Registry
3. `WEB_SEARCHING` - Search web for external docs
4. `LLM_EXTRACTING` - Extract 9-criteria with LLM
5. `NORMALIZING` - Convert to canonical schema
6. `VALIDATING` - Validate schema and confidence
7. `CACHING` - Save to data/methodologies/

**Transitions:**
```
GENERATING_METHODOLOGY_DOCS
  → QUERYING_KOI (check cache first)
    → [Found in KOI] → LLM_EXTRACTING
    → [Not in KOI] → WEB_SCRAPING

WEB_SCRAPING
  → [Found on Registry] → LLM_EXTRACTING
  → [Not on Registry] → WEB_SEARCHING

WEB_SEARCHING
  → [Found external docs] → LLM_EXTRACTING
  → [Not found] → BLOCKCHAIN_ONLY (degraded mode)

LLM_EXTRACTING
  → NORMALIZING → VALIDATING

VALIDATING
  → [Confidence ≥ 0.8] → CACHING → COMPLETED
  → [Confidence < 0.8] → MANUAL_REVIEW (human in loop)
```

**State Timing:**
- `QUERYING_KOI`: <1s
- `WEB_SCRAPING`: 2-5s
- `WEB_SEARCHING`: 5-15s
- `LLM_EXTRACTING`: 3-10s (depends on doc length)
- `NORMALIZING`: <100ms
- `VALIDATING`: <50ms
- `CACHING`: <100ms

**Total pipeline time:**
- Best case (KOI): 4-11s
- Typical (Web scraping): 5-15s
- Worst case (Web search): 10-30s

---

## LLM Extraction Prompt

**System Prompt for Criterion Extraction:**

```
You are a carbon credit methodology analyst. Extract 9-criteria data from the provided methodology document.

TASK: Extract structured data for these 9 criteria:
1. MRV (Monitoring, Reporting, Verification)
2. Additionality
3. Leakage
4. Traceability
5. Cost Efficiency
6. Permanence
7. Co-Benefits
8. Accuracy
9. Precision

For EACH criterion:
- Extract relevant information from the document
- Assign confidence score (0-1) based on evidence quality
- Cite section numbers or page numbers as evidence
- Use controlled vocabulary (see schema)

METHODOLOGY DOCUMENT:
{document_text}

OUTPUT FORMAT: JSON matching the normalized schema
```

**Validation Rules:**
1. All 9 criteria must be present
2. Confidence scores must be 0-1
3. Evidence sources should cite specific sections
4. Enums must match allowed values
5. Overall methodology confidence = min(criterion_confidences)

---

## Implementation Architecture

```
src/mcp_server/
  generators/
    __init__.py
    methodology_generator.py         # Main orchestrator
    koi_fetcher.py                   # Tier 1: KOI integration
    web_scraper_enhanced.py          # Tier 2: Enhanced scraper
    web_search_fetcher.py            # Tier 3: Search + fetch
    llm_extractor.py                 # LLM-based extraction
    schema_normalizer.py             # Normalization logic
    validator.py                     # Validation and confidence

  models/
    methodology_schema.py            # Pydantic models for schema
```

**Key Classes:**

### `MethodologyGenerator`
Main orchestrator coordinating the pipeline

```python
class MethodologyGenerator:
    async def generate(
        self,
        methodology_identifier: str,  # Name, slug, or credit class
        sources: List[str] = ["koi", "web_scraping", "web_search"],
        force_refresh: bool = False
    ) -> NormalizedMethodology:
        """Generate normalized methodology document.

        Args:
            methodology_identifier: Methodology to fetch
            sources: Data sources to try (in order)
            force_refresh: Bypass cache

        Returns:
            NormalizedMethodology with 9-criteria data
        """
```

### `KOIFetcher`
```python
class KOIFetcher:
    async def fetch_methodology(
        self,
        identifier: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch methodology from KOI knowledge graph."""

        # Try search first
        search_results = await self.koi_client.search_knowledge(
            query=identifier,
            filters={"source_type": "methodology"}
        )

        # Get entity details
        if search_results:
            entity = await self.koi_client.get_entity(
                identifier=search_results[0]["id"],
                include_related=True
            )
            return entity

        return None
```

### `LLMExtractor`
```python
class LLMExtractor:
    async def extract_9_criteria(
        self,
        document_text: str,
        methodology_name: str
    ) -> Dict[str, Any]:
        """Use LLM to extract 9-criteria data from document.

        Returns normalized dict with confidence scores.
        """

        # Construct extraction prompt
        prompt = self._build_extraction_prompt(document_text)

        # Call LLM (would use Claude API in production)
        response = await self._call_llm(prompt)

        # Parse and validate response
        extracted = json.loads(response)

        # Calculate confidence based on evidence quality
        extracted = self._assign_confidence_scores(extracted)

        return extracted
```

### `SchemaValidator`
```python
class SchemaValidator:
    def validate(
        self,
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str], float]:
        """Validate normalized methodology data.

        Returns:
            (is_valid, error_messages, confidence_score)
        """

        # Schema validation
        errors = []

        # Check all 9 criteria present
        required_criteria = [
            "mrv", "additionality", "leakage",
            "traceability", "cost_efficiency",
            "permanence", "co_benefits",
            "accuracy", "precision"
        ]

        for criterion in required_criteria:
            if criterion not in data:
                errors.append(f"Missing criterion: {criterion}")

        # Validate confidence scores
        # Validate enums
        # Calculate overall confidence

        overall_confidence = self._calculate_overall_confidence(data)

        return (len(errors) == 0, errors, overall_confidence)
```

---

## Caching Strategy

**Cache Location:**
```
data/methodologies/
  {methodology_id}_normalized.json     # Normalized data
  {methodology_id}_raw.html            # Raw HTML (if web scraped)
  {methodology_id}_metadata.json       # Cache metadata
```

**Cache Metadata:**
```json
{
  "methodology_id": "aei",
  "cached_at": "2025-10-21T12:00:00Z",
  "data_sources": ["koi", "registry_web"],
  "confidence": 0.95,
  "ttl_hours": 168,  // 1 week
  "validation_status": "validated"
}
```

**Cache Invalidation:**
- Time-based: TTL of 1 week (configurable)
- Version-based: Re-fetch if methodology version changes
- Manual: `force_refresh=True` parameter

---

## Error Handling & Fallbacks

### **Graceful Degradation:**

```python
async def generate_with_fallback(methodology_id: str):
    # Try Tier 1: KOI
    try:
        data = await koi_fetcher.fetch(methodology_id)
        if data and validate(data):
            return data
    except Exception as e:
        logger.warning(f"KOI fetch failed: {e}, trying web scraping")

    # Try Tier 2: Web scraping
    try:
        data = await web_scraper.scrape(methodology_id)
        if data:
            normalized = await llm_extractor.extract_9_criteria(data)
            if validate(normalized):
                return normalized
    except Exception as e:
        logger.warning(f"Web scraping failed: {e}, trying web search")

    # Try Tier 3: Web search
    try:
        search_results = await web_search(f"{methodology_id} carbon methodology")
        for result in search_results[:3]:
            doc = await web_fetch(result.url)
            normalized = await llm_extractor.extract_9_criteria(doc)
            if validate(normalized):
                return normalized
    except Exception as e:
        logger.error(f"All fetching methods failed: {e}")

    # Tier 4: Blockchain-only (degraded)
    logger.warning("Using degraded mode: blockchain-only scoring")
    return generate_from_blockchain_only(methodology_id)
```

### **Confidence Thresholds:**

- **High confidence (≥0.85):** Auto-approve, use in comparisons
- **Medium confidence (0.70-0.84):** Use with warning
- **Low confidence (0.60-0.69):** Require validation before use
- **Very low (<0.60):** Reject, require manual input

---

## Testing & Validation

### **Unit Tests:**
```python
def test_koi_fetcher():
    """Test KOI methodology fetching."""
    fetcher = KOIFetcher()
    result = await fetcher.fetch_methodology("AEI")
    assert result is not None
    assert "mrv" in result

def test_schema_validation():
    """Test schema validation logic."""
    valid_data = load_sample_methodology()
    is_valid, errors, confidence = validator.validate(valid_data)
    assert is_valid
    assert confidence >= 0.8

def test_llm_extraction():
    """Test LLM extraction from sample document."""
    sample_doc = load_sample_registry_html()
    extractor = LLMExtractor()
    result = await extractor.extract_9_criteria(sample_doc, "AEI")
    assert all(k in result for k in ["mrv", "additionality", ...])
```

### **Integration Tests:**
```python
async def test_full_pipeline_aei():
    """Test full generation pipeline for AEI."""
    generator = MethodologyGenerator()
    result = await generator.generate(
        methodology_identifier="aei",
        sources=["koi", "web_scraping"]
    )

    # Validate result
    assert result.methodology_id == "aei"
    assert result.confidence >= 0.85
    assert len(result.mrv.evidence_sources) > 0

async def test_fallback_cascade():
    """Test fallback from KOI → web scraping → web search."""
    generator = MethodologyGenerator()

    # Mock KOI failure
    with mock.patch.object(KOIFetcher, 'fetch', side_effect=Exception):
        result = await generator.generate("unknown_methodology")

        # Should fall back to web scraping
        assert "web_scraping" in result.data_sources or "web_search" in result.data_sources
```

---

## Usage Examples

### **Example 1: Generate AEI Methodology**
```python
from mcp_server.generators import MethodologyGenerator

generator = MethodologyGenerator()

# Generate from all available sources
aei_data = await generator.generate(
    methodology_identifier="aei",
    sources=["koi", "web_scraping", "web_search"],
    force_refresh=False
)

print(f"Methodology: {aei_data.official_name}")
print(f"Confidence: {aei_data.confidence}")
print(f"Sources: {aei_data.data_sources}")
print(f"MRV Monitoring: {aei_data.mrv.monitoring_approach}")
```

### **Example 2: Generate from Credit Class**
```python
# Generate methodologies for C02 credit class
c02_methodologies = await generator.generate_from_credit_class("C02")

# Returns list: [aei_data, ecometric_data]
for methodology in c02_methodologies:
    print(f"{methodology.methodology_id}: {methodology.confidence}")
```

### **Example 3: Compare Data Sources**
```python
# Fetch from KOI only
koi_data = await generator.generate("aei", sources=["koi"])

# Fetch from web scraping only
web_data = await generator.generate("aei", sources=["web_scraping"])

# Compare confidence scores
print(f"KOI confidence: {koi_data.confidence}")
print(f"Web confidence: {web_data.confidence}")
```

### **Example 4: Batch Generation**
```python
# Generate all C02 methodologies
methodologies = ["aei", "ecometric", "nori", "soil_capital"]

results = await generator.generate_batch(
    methodology_identifiers=methodologies,
    max_concurrency=3  # Rate limiting
)

# Filter by confidence
high_quality = [r for r in results if r.confidence >= 0.85]
```

---

## Milestone 1a Integration

**Updated Acceptance Criteria:**

- [x] AEI + EcoMetric methods successfully ingested *(Already have normalized JSON)*
- [ ] **Method comparison returns 9 criteria with citations ≤10s** *(Need to test)*
- [ ] **Project comparison works across AEI/EcoMetric projects** *(Need to implement)*
- [ ] **Buyer preset alters scoring/ordering as expected** *(Need to test)*
- [ ] **Markdown export generates clean, dated one-pager** *(Already implemented)*

**Additional Criterion:**
- [ ] **Methodology generator can fetch and normalize new methodologies using KOI + web sources**

**Integration Points:**
1. `compare_methodologies_nine_criteria()` calls `load_methodology_data()`
2. `load_methodology_data()` checks cache, falls back to generator
3. Generator pipeline runs if methodology not cached
4. Normalized data saved to cache for future use

**Modified Flow:**
```
compare_methodologies_nine_criteria(["C02"])
  → resolve_methodology_id("C02") → ["aei", "ecometric"]
  → load_methodology_data("aei")
    → Check cache: data/methodologies/aei_normalized.json
    → [Cache miss] → MethodologyGenerator.generate("aei")
      → QUERYING_KOI → LLM_EXTRACTING → CACHING
  → score_mrv("C02", client) // Uses loaded methodology data
  → ...
```

---

## Future Enhancements

### **Week 2+:**
1. **Methodology versioning** - Track changes over time
2. **Differential updates** - Only update changed sections
3. **Multi-language support** - Parse Spanish, French methodology docs
4. **PDF parsing** - Extract from PDF methodology documents
5. **Automated validation** - Compare against known baselines
6. **Methodology comparison report** - Side-by-side comparison of methodology docs themselves

### **Advanced Features:**
1. **Graph-based extraction** - Use KOI graph queries for relationships
2. **Historical analysis** - Track methodology evolution
3. **Expert review integration** - Submit low-confidence extractions for review
4. **Active learning** - Improve LLM extraction with feedback

---

## Appendices

### **Appendix A: Controlled Vocabularies**

**Monitoring Approach:**
- soil_sampling_laboratory_analysis
- remote_sensing
- field_surveys
- modeling
- hybrid

**Barrier Analysis:**
- none
- described
- comprehensive

**Risk Level:**
- low
- moderate
- high

**Methodology Complexity:**
- simple
- moderate
- complex

**Peer Review Status:**
- draft
- in_review
- published
- retired

### **Appendix B: Confidence Score Calibration**

**Data Source Quality:**
- KOI structured data: Base confidence 0.90
- Web scraping with clear sections: Base confidence 0.85
- Web search + LLM extraction: Base confidence 0.75
- Blockchain-only inference: Base confidence 0.60

**Evidence Quality Adjustments:**
- Strong citations (+0.05)
- Quantitative metrics (+0.05)
- Peer-reviewed (+0.05)
- No evidence found (-0.10)
- Ambiguous language (-0.05)

---

*Document Status: Complete v1.0*
*Next Steps: Implement KOIFetcher and test with real methodologies*
