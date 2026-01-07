"""Methodology comparison tools for 9-criteria framework.

This module provides tools for comparing carbon credit methodologies using
the 9-criteria assessment framework with buyer-specific weighting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..client.regen_client import get_regen_client
from ..client.metadata_graph_client import resolve_metadata_summary
from ..models.methodology import (
    BuyerPreset,
    CriterionScore,
    MethodologyMetadata,
    NineCriteriaScores,
    MethodologyComparisonResult,
    ComparisonExportFormat,
)
from .config_loaders import get_buyer_preset_loader

logger = logging.getLogger(__name__)


# ============================================================================
# BUYER PRESETS CONFIGURATION
# ============================================================================

# Load buyer presets from YAML configuration files
# Presets are now externalized to config/buyer_presets/*.yaml
# This allows users to create custom presets without modifying code
try:
    _preset_loader = get_buyer_preset_loader()
    BUYER_PRESETS: Dict[str, BuyerPreset] = _preset_loader.get_all_presets()
    logger.info(f"Loaded {len(BUYER_PRESETS)} buyer presets from configuration files")
except Exception as e:
    logger.error(f"Error loading buyer presets from config files: {e}")
    logger.warning("Falling back to empty buyer presets - please check config/buyer_presets/ directory")
    BUYER_PRESETS = {}


# ============================================================================
# METHODOLOGY METADATA EXTRACTION
# ============================================================================

async def get_methodology_metadata(credit_class_id: str) -> MethodologyMetadata:
    """Extract methodology metadata from Regen blockchain.

    Args:
        credit_class_id: Credit class ID (e.g., "C02")

    Returns:
        MethodologyMetadata with identification and context

    Raises:
        ValueError: If credit class not found
    """
    client = get_regen_client()

    # Query credit class
    response = await client.query_credit_classes()
    classes = response.get('classes', [])
    credit_class = next((c for c in classes if c.get("id") == credit_class_id), None)

    if not credit_class:
        raise ValueError(f"Credit class {credit_class_id} not found")

    # Resolve human-readable name from the on-chain metadata IRI (schema:name)
    resolved_name: Optional[str] = None
    metadata_iri = credit_class.get("metadata")
    if isinstance(metadata_iri, str) and metadata_iri:
        summary = await resolve_metadata_summary(metadata_iri)
        if summary and isinstance(summary.get("name"), str):
            resolved_name = summary["name"]

    # Query projects for this class
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    # Query batches for project count
    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [b for b in batches if any(b.get("project_id") == p.get("id") for p in class_projects)]

    # Extract geographic scope
    geographic_scope = list(set(p.get("jurisdiction", "Unknown") for p in class_projects))

    return MethodologyMetadata(
        methodology_id=credit_class_id,
        credit_class_id=credit_class_id,
        methodology_name=resolved_name or f"Credit Class {credit_class_id}",
        developer=credit_class.get("admin", "Unknown"),
        methodology_type=_infer_methodology_type(credit_class_id),
        status="active",
        geographic_scope=geographic_scope,
        project_count=len(class_projects),
        batch_count=len(class_batches)
    )


def _infer_methodology_type(credit_class_id: str) -> str:
    """Infer methodology type from credit class ID."""
    if credit_class_id.startswith("C01"):
        return "reforestation"
    elif credit_class_id.startswith("C02"):
        return "soil_carbon"
    elif credit_class_id.startswith("C03"):
        return "blue_carbon"
    elif credit_class_id.startswith("BIO"):
        return "biodiversity"
    else:
        return "unknown"


# ============================================================================
# METHODOLOGY DATA LOADER
# ============================================================================

def load_methodology_data(methodology_id: str) -> Optional[Dict[str, Any]]:
    """Load normalized methodology data from JSON file.

    Loads structured methodology data that was scraped and normalized from
    Regen Registry methodology documents. Includes all 9 criteria data.

    Args:
        methodology_id: Methodology identifier (e.g., "aei", "ecometric")

    Returns:
        Dictionary with normalized methodology data, or None if not found

    Example:
        >>> data = load_methodology_data("aei")
        >>> mrv = data["mrv"]
        >>> print(mrv["monitoring_approach"])
        'soil_sampling_laboratory_analysis'
    """
    import json
    from pathlib import Path

    # Path to normalized methodology data
    data_dir = Path(__file__).parent.parent / "data" / "methodologies"
    file_path = data_dir / f"{methodology_id}_normalized.json"

    if not file_path.exists():
        logger.warning(f"Methodology data not found: {methodology_id}")
        return None

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded methodology data: {methodology_id}")
        return data
    except Exception as e:
        logger.error(f"Error loading methodology data for {methodology_id}: {e}")
        return None


def resolve_methodology_id(credit_class_id: str) -> List[str]:
    """Resolve credit class ID to methodology IDs.

    Maps blockchain credit class IDs to corresponding methodology document IDs.
    Some credit classes may map to multiple methodologies (e.g., C02 corresponds
    to both AEI and EcoMetric soil carbon methodologies).

    Args:
        credit_class_id: Credit class ID from blockchain (e.g., "C02")

    Returns:
        List of methodology IDs, or empty list if no mapping exists

    Example:
        >>> resolve_methodology_id("C02")
        ['aei', 'ecometric']

        >>> resolve_methodology_id("C01")
        []  # No normalized data available yet
    """
    import json
    from pathlib import Path

    # Load validation mapping file
    data_dir = Path(__file__).parent.parent / "data" / "methodologies"
    mapping_file = data_dir / "c02_mapping_validation.json"

    # Known mappings from validation
    credit_class_mappings = {}

    # Try to load from validation file
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r') as f:
                validation_data = json.load(f)

            # Build mapping from validation results
            if validation_data.get("credit_class") == "C02":
                methodology_ids = []

                # Check AEI mapping
                aei_mapping = validation_data.get("aei_mapping", {})
                if aei_mapping.get("recommendation") == "CONFIRMED":
                    methodology_ids.append("aei")

                # Check EcoMetric mapping
                ecometric_mapping = validation_data.get("ecometric_mapping", {})
                if ecometric_mapping.get("recommendation") == "CONFIRMED":
                    methodology_ids.append("ecometric")

                credit_class_mappings["C02"] = methodology_ids

        except Exception as e:
            logger.warning(f"Could not load mapping validation file: {e}")

    # Fallback: Static mappings for known credit classes
    if not credit_class_mappings:
        credit_class_mappings = {
            "C02": ["aei", "ecometric"],  # Soil carbon - dual mapping confirmed
        }

    # Return mapping or empty list
    methodology_ids = credit_class_mappings.get(credit_class_id, [])

    if methodology_ids:
        logger.info(f"Resolved {credit_class_id} → {methodology_ids}")
    else:
        logger.info(f"No methodology mapping found for {credit_class_id}")

    return methodology_ids


def select_methodology_for_scoring(
    credit_class_id: str,
    methodology_ids: List[str]
) -> Optional[str]:
    """Select the most appropriate methodology for scoring from multiple options.

    When a credit class maps to multiple methodologies (e.g., C02 → AEI + EcoMetric),
    this function selects the most relevant one for scoring purposes.

    Current strategy: Prefer the first methodology (alphabetically) for consistency.
    Future enhancement: Could select based on project characteristics.

    Args:
        credit_class_id: Credit class ID
        methodology_ids: List of candidate methodology IDs

    Returns:
        Selected methodology ID, or None if list is empty
    """
    if not methodology_ids:
        return None

    # Simple strategy: Use first methodology (alphabetically sorted)
    # This ensures consistent behavior across comparisons
    selected = sorted(methodology_ids)[0]

    if len(methodology_ids) > 1:
        logger.info(
            f"Multiple methodologies for {credit_class_id}: {methodology_ids}. "
            f"Selected {selected} for scoring."
        )

    return selected


# ============================================================================
# NINE CRITERIA SCORING FUNCTIONS
# ============================================================================

async def score_mrv(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Monitoring, Reporting, Verification criterion.

    Assesses the quality and frequency of monitoring, transparency of reporting,
    and rigor of verification processes.

    Scoring factors:
    - Methodology document MRV protocols
    - Batch issuance frequency (monitoring regularity)
    - Blockchain transparency (Regen Registry infrastructure)
    - Project count and consistency

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for MRV criterion
    """
    evidence = []
    data_sources = ["Regen Blockchain", "Batch Analysis", "Project Metadata"]

    # Try to load methodology data for enhanced scoring
    methodology_ids = resolve_methodology_id(credit_class_id)
    methodology_id = select_methodology_for_scoring(credit_class_id, methodology_ids)
    methodology_data = load_methodology_data(methodology_id) if methodology_id else None

    # Query projects for this class
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    # Query batches
    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    # Enhanced MRV evidence from methodology document
    if methodology_data:
        data_sources.append(f"Methodology Document: {methodology_id.upper()}")
        mrv_data = methodology_data.get("mrv", {})

        # Monitoring approach
        monitoring_approach = mrv_data.get("monitoring_approach", "")
        if monitoring_approach:
            evidence.append(
                f"Methodology specifies {monitoring_approach.replace('_', ' ')} monitoring approach"
            )

        # Monitoring frequency
        monitoring_freq = mrv_data.get("monitoring_frequency", "")
        if monitoring_freq:
            evidence.append(
                f"Required monitoring frequency: {monitoring_freq}"
            )

        # Verification type
        verification_type = mrv_data.get("verification_type", "")
        if verification_type:
            evidence.append(
                f"Verification: {verification_type.replace('_', ' ')}"
            )

        # Reporting standards
        reporting_standards = mrv_data.get("reporting_standards", [])
        if reporting_standards:
            standards_str = ", ".join(reporting_standards)
            evidence.append(
                f"Complies with standards: {standards_str}"
            )

    # Calculate monitoring frequency from blockchain
    if class_projects:
        batches_per_project = len(class_batches) / len(class_projects)
        evidence.append(
            f"Average {batches_per_project:.1f} batches per project indicating systematic monitoring"
        )
    else:
        batches_per_project = 0

    # Regen Registry infrastructure
    evidence.append(
        "Regen Registry blockchain infrastructure provides transparent, immutable reporting"
    )

    # Verification evidence
    if len(class_batches) > 0:
        evidence.append(
            f"Evidence of verification through {len(class_batches)} issued batches"
        )

    # Calculate score - enhanced with methodology data
    base_score = 0.0

    # Blockchain-based scoring
    if batches_per_project >= 8:
        base_score = 3.0
        evidence.append("High monitoring frequency exceeds best practice standards")
    elif batches_per_project >= 4:
        base_score = 2.5
        evidence.append("Regular monitoring frequency aligns with best practices")
    elif batches_per_project >= 1:
        base_score = 2.0
        evidence.append("Annual monitoring patterns detected")
    else:
        base_score = 1.5
        evidence.append("Limited blockchain monitoring evidence available")

    # Boost score if methodology data confirms rigorous MRV
    if methodology_data:
        mrv_data = methodology_data.get("mrv", {})

        # Check for rigorous monitoring protocols
        monitoring_approach = mrv_data.get("monitoring_approach", "")
        if "laboratory_analysis" in monitoring_approach or "sampling" in monitoring_approach:
            base_score = min(3.0, base_score + 0.2)
            evidence.append("Laboratory-based monitoring enhances MRV rigor")

        # Check for third-party verification
        verification_type = mrv_data.get("verification_type", "")
        if "third_party" in verification_type or "independent" in verification_type:
            base_score = min(3.0, base_score + 0.1)
            evidence.append("Independent third-party verification confirmed")

        # Check for standards compliance
        reporting_standards = mrv_data.get("reporting_standards", [])
        if len(reporting_standards) >= 2:
            base_score = min(3.0, base_score + 0.1)

    score = round(base_score, 1)

    # Enhanced confidence when methodology data available
    if methodology_data:
        confidence = min(0.95, 0.85 + (len(class_batches) / 100) * 0.10)
    else:
        confidence = min(0.95, 0.70 + (len(class_batches) / 100) * 0.25)

    return CriterionScore(
        criterion_name="MRV",
        score=score,
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[f"Blockchain data: {len(class_projects)} projects, {len(class_batches)} batches"],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_additionality(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Additionality criterion.

    Assesses whether credits represent genuine additional environmental benefits
    beyond business-as-usual scenarios.

    Scoring factors:
    - Methodology document additionality requirements
    - Geographic targeting (indicates barrier analysis)
    - Methodology type characteristics
    - Project distribution patterns

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Additionality criterion
    """
    evidence = []
    data_sources = ["Regen Blockchain", "Project Geographic Analysis", "Methodology Research"]

    # Try to load methodology data
    methodology_ids = resolve_methodology_id(credit_class_id)
    methodology_id = select_methodology_for_scoring(credit_class_id, methodology_ids)
    methodology_data = load_methodology_data(methodology_id) if methodology_id else None

    # Query projects for geographic and distribution analysis
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    # Analyze geographic distribution
    jurisdictions = [p.get("jurisdiction", "Unknown") for p in class_projects]
    unique_jurisdictions = set(jurisdictions)

    evidence.append(
        f"Geographic concentration in {len(unique_jurisdictions)} jurisdictions suggests targeted additionality approach"
    )

    # Enhanced additionality evidence from methodology document
    base_score = 2.0  # Default adequate score

    if methodology_data:
        data_sources.append(f"Methodology Document: {methodology_id.upper()}")
        additionality_data = methodology_data.get("additionality", {})

        # Assessment requirement
        assessment_required = additionality_data.get("assessment_required", False)
        if assessment_required:
            evidence.append(
                "Methodology requires formal additionality assessment"
            )
            base_score = 2.2

        # Barrier analysis
        barrier_analysis = additionality_data.get("barrier_analysis", "")
        if barrier_analysis == "comprehensive":
            evidence.append(
                "Comprehensive barrier analysis framework specified in methodology"
            )
            base_score = min(3.0, base_score + 0.3)
        elif barrier_analysis == "described":
            evidence.append(
                "Barrier analysis approach described in methodology"
            )
            base_score = min(3.0, base_score + 0.2)

        # Baseline methodology
        baseline = additionality_data.get("baseline_methodology", "")
        if baseline and baseline != "not_specified":
            evidence.append(
                f"Baseline methodology: {baseline.replace('_', ' ')}"
            )
            base_score = min(3.0, base_score + 0.1)

    # Fallback to methodology type inference if no data
    if not methodology_data:
        methodology_type = _infer_methodology_type(credit_class_id)

        if methodology_type == "soil_carbon":
            evidence.append(
                "Soil carbon methodology: Agricultural practice changes indicate baseline development"
            )
            evidence.append(
                "Regenerative agriculture practices suggest barrier analysis for adoption"
            )
            base_score = 2.0
        elif methodology_type == "reforestation":
            evidence.append(
                "Reforestation methodology: Land use change indicates additionality framework"
            )
            base_score = 2.2
        elif methodology_type == "blue_carbon":
            evidence.append(
                "Blue carbon methodology: Coastal restoration indicates strong additionality"
            )
            base_score = 2.3
        else:
            evidence.append(
                f"Methodology type {methodology_type}: Additionality assessment pending detailed review"
            )
            base_score = 1.5

    # Adjust for project scale (more projects = more validation)
    if len(class_projects) > 10:
        evidence.append(
            f"Widespread adoption ({len(class_projects)} projects) validates additionality framework"
        )
        score = min(3.0, base_score + 0.2)
    elif len(class_projects) > 5:
        score = base_score + 0.1
    else:
        evidence.append(
            "Limited project implementation - additionality requires additional validation"
        )
        score = base_score

    # Enhanced confidence when methodology data available
    if methodology_data:
        confidence = 0.85 if len(class_projects) >= 5 else 0.80
    else:
        confidence = 0.70 if len(class_projects) >= 5 else 0.60

    return CriterionScore(
        criterion_name="Additionality",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Project analysis: {len(class_projects)} projects across {len(unique_jurisdictions)} jurisdictions"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_leakage(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Leakage criterion.

    Assesses the risk of emissions displacement or activity shifting outside
    the project boundary.

    Scoring factors:
    - Methodology document leakage assessment
    - Methodology type inherent leakage risk
    - Geographic boundary definition
    - Project scale and distribution

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Leakage criterion
    """
    evidence = []
    data_sources = ["Methodology Type Analysis", "Geographic Data", "Leakage Risk Literature"]

    # Try to load methodology data
    methodology_ids = resolve_methodology_id(credit_class_id)
    methodology_id = select_methodology_for_scoring(credit_class_id, methodology_ids)
    methodology_data = load_methodology_data(methodology_id) if methodology_id else None

    # Query projects for geographic analysis
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    # Enhanced leakage evidence from methodology document
    base_score = 2.0
    confidence = 0.75

    if methodology_data:
        data_sources.append(f"Methodology Document: {methodology_id.upper()}")
        leakage_data = methodology_data.get("leakage", {})

        # Assessment approach
        assessment_approach = leakage_data.get("assessment_approach", "")
        if assessment_approach:
            evidence.append(
                f"Leakage assessment: {assessment_approach.replace('_', ' ')}"
            )
            if "landscape" in assessment_approach:
                base_score = 2.7
                evidence.append("Landscape-level assessment addresses systemic leakage risks")

        # Boundary definition
        boundary_def = leakage_data.get("boundary_definition", "")
        if "clear" in boundary_def:
            evidence.append("Clear project boundaries defined to prevent leakage")
            base_score = min(3.0, base_score + 0.1)

        # Risk level
        risk_level = leakage_data.get("risk_level", "")
        if risk_level == "low":
            evidence.append("Methodology assessment indicates low leakage risk")
            base_score = min(3.0, base_score + 0.1)
            confidence = 0.90
        elif risk_level == "moderate":
            evidence.append("Methodology indicates moderate leakage risk with management")
            confidence = 0.85

    # Fallback to methodology type inference if no data
    if not methodology_data:
        methodology_type = _infer_methodology_type(credit_class_id)

        if methodology_type == "soil_carbon":
            evidence.append(
                "Soil carbon methodology: Inherently low leakage risk due to in-situ carbon storage"
            )
            evidence.append(
                "Agricultural practice changes contained within project boundaries"
            )
            evidence.append(
                "Limited activity displacement potential for soil carbon sequestration"
            )
            base_score = 2.8
            confidence = 0.90
        elif methodology_type == "reforestation":
            evidence.append(
                "Reforestation methodology: Low-moderate leakage risk with proper boundary definition"
            )
            evidence.append(
                "Land use change monitoring reduces displacement risk"
            )
            base_score = 2.5
            confidence = 0.85
        elif methodology_type == "blue_carbon":
            evidence.append(
                "Blue carbon methodology: Low leakage risk due to geographic constraints"
            )
            base_score = 2.7
            confidence = 0.88
        else:
            evidence.append(
                f"Methodology type {methodology_type}: Leakage assessment pending detailed review"
            )
            base_score = 2.0
            confidence = 0.70

    # Geographic boundary analysis
    jurisdictions = [p.get("jurisdiction", "Unknown") for p in class_projects]
    unique_jurisdictions = set(jurisdictions)

    if unique_jurisdictions:
        evidence.append(
            f"Geographic boundaries clearly defined across {len(unique_jurisdictions)} jurisdictions"
        )

    # Project distribution
    if len(class_projects) > 10:
        evidence.append(
            f"Distributed implementation ({len(class_projects)} projects) reduces systemic leakage risk"
        )
        score = min(3.0, base_score + 0.1)
    else:
        score = base_score

    return CriterionScore(
        criterion_name="Leakage",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Geographic analysis: {len(class_projects)} projects"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_traceability(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Traceability criterion.

    Assesses transparency and traceability of credits throughout their lifecycle.

    Scoring factors:
    - Blockchain infrastructure (Regen Registry native)
    - Public data accessibility
    - Batch and project tracking
    - Credit class identification

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Traceability criterion
    """
    evidence = []
    data_sources = ["Regen Registry Infrastructure", "Blockchain Analysis", "Public Data Accessibility"]

    # Regen Registry provides inherent traceability advantages
    evidence.append(
        "Regen Registry native blockchain infrastructure provides immutable traceability"
    )
    evidence.append(
        "Public accessibility of batch data and project information through blockchain"
    )
    evidence.append(
        "Transparent ownership tracking through blockchain records prevents double-counting"
    )

    # Query projects and batches for traceability assessment
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    # Credit class identification
    evidence.append(
        f"Native Credit Class identification ({credit_class_id}) ensures systematic tracking"
    )

    # Batch-level traceability
    if class_batches:
        evidence.append(
            f"Batch-level traceability verified across {len(class_batches)} credit issuances"
        )

    # Score: Regen Registry provides excellent traceability
    # All methodologies on Regen benefit equally from infrastructure
    score = 3.0  # Strong - blockchain provides perfect traceability
    confidence = 0.95  # Very high confidence - verifiable blockchain infrastructure

    return CriterionScore(
        criterion_name="Traceability",
        score=score,
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            "Regen Registry Infrastructure",
            f"Blockchain verification: {len(class_batches)} batches tracked"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_cost_efficiency(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Cost Efficiency criterion.

    Assesses the cost-effectiveness of credits relative to market benchmarks.

    Scoring factors:
    - Market price analysis from sell orders
    - Price comparison to market averages
    - Credit availability and liquidity

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Cost Efficiency criterion
    """
    evidence = []
    data_sources = ["Marketplace Data", "Sell Orders Analysis", "Market Benchmarks"]

    # Query sell orders for price analysis
    sell_orders_response = await client.query_sell_orders()
    sell_orders = sell_orders_response.get('sell_orders', [])

    # Query projects and batches for this class
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    # Find sell orders for this credit class
    batch_denoms = [b.get("denom") for b in class_batches if b.get("denom")]
    class_sell_orders = [
        order for order in sell_orders
        if order.get("batch_key", {}).get("batch_denom") in batch_denoms
    ]

    # Calculate average price if orders exist
    if class_sell_orders:
        try:
            prices = [
                float(order.get("ask_price", 0))
                for order in class_sell_orders
                if order.get("ask_price")
            ]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)

                evidence.append(
                    f"Average market price: ${avg_price:.2f} per credit"
                )
                evidence.append(
                    f"Price range: ${min_price:.2f} - ${max_price:.2f} (market spread: ${max_price - min_price:.2f})"
                )
                evidence.append(
                    f"Active sell orders: {len(class_sell_orders)} orders providing price discovery"
                )

                # Score based on price competitiveness
                # Voluntary carbon market avg ~$4-8
                # Soil carbon premium ~$6-10
                # Lower prices = better cost efficiency
                if avg_price < 5:
                    score = 3.0
                    evidence.append("Highly competitive pricing below market average")
                elif avg_price < 8:
                    score = 2.5
                    evidence.append("Competitive pricing in market range")
                elif avg_price < 12:
                    score = 2.0
                    evidence.append("Moderate pricing with quality premium")
                else:
                    score = 1.5
                    evidence.append("Premium pricing may limit cost efficiency")

                confidence = 0.80
            else:
                # No valid prices
                score = 2.0
                evidence.append("Market orders exist but pricing data limited")
                confidence = 0.60
        except (ValueError, TypeError):
            score = 2.0
            evidence.append("Market activity detected, pricing assessment pending")
            confidence = 0.60
    else:
        # No sell orders - estimate based on methodology type
        methodology_type = _infer_methodology_type(credit_class_id)
        evidence.append(
            f"No active sell orders - cost efficiency estimated from {methodology_type} benchmarks"
        )

        if methodology_type == "soil_carbon":
            evidence.append("Soil carbon typical pricing: $6-10/credit with quality premiums")
            score = 2.5
        elif methodology_type == "reforestation":
            evidence.append("Reforestation typical pricing: $5-8/credit")
            score = 2.3
        else:
            evidence.append(f"{methodology_type.title()} pricing varies by project characteristics")
            score = 2.0

        confidence = 0.65  # Lower confidence without market data

    return CriterionScore(
        criterion_name="Cost Efficiency",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Market analysis: {len(class_sell_orders)} active orders" if class_sell_orders else "Methodology benchmark estimates"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_permanence(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Permanence criterion.

    Assesses the long-term durability of carbon storage or environmental benefits.

    Scoring factors:
    - Methodology type inherent permanence characteristics
    - Storage duration potential
    - Monitoring patterns indicating permanence verification

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Permanence criterion
    """
    evidence = []
    data_sources = ["Methodology Type Analysis", "Permanence Literature", "Monitoring Patterns"]

    # Methodology type determines permanence characteristics
    methodology_type = _infer_methodology_type(credit_class_id)

    # Query batches for monitoring pattern analysis
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    if methodology_type == "soil_carbon":
        evidence.append(
            "Soil carbon storage provides inherent permanence with proper management"
        )
        evidence.append(
            "Agricultural practice changes support long-term carbon storage"
        )
        evidence.append(
            "Regenerative agriculture alignment enhances soil carbon stability"
        )
        base_score = 2.3  # Good - soil carbon has good but not perfect permanence
        confidence = 0.75
    elif methodology_type == "reforestation":
        evidence.append(
            "Forest carbon storage provides strong long-term permanence (100+ years potential)"
        )
        evidence.append(
            "Living biomass and soil carbon pools create multiple storage mechanisms"
        )
        base_score = 2.6  # Strong - forests have high permanence potential
        confidence = 0.80
    elif methodology_type == "blue_carbon":
        evidence.append(
            "Blue carbon (coastal/marine) storage provides excellent long-term permanence"
        )
        evidence.append(
            "Marine sediments offer multi-century storage potential"
        )
        base_score = 2.8  # Strong - blue carbon has very high permanence
        confidence = 0.82
    else:
        evidence.append(
            f"{methodology_type.title()} permanence characteristics require detailed assessment"
        )
        base_score = 2.0
        confidence = 0.70

    # Monitoring frequency supports permanence verification
    if class_batches and class_projects:
        batches_per_project = len(class_batches) / len(class_projects)
        if batches_per_project >= 4:
            evidence.append(
                f"Regular monitoring ({batches_per_project:.1f} batches/project) supports permanence verification"
            )
            score = min(3.0, base_score + 0.1)
        else:
            evidence.append(
                "Annual monitoring patterns detected for permanence tracking"
            )
            score = base_score
    else:
        score = base_score

    return CriterionScore(
        criterion_name="Permanence",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Methodology type: {methodology_type}",
            "Permanence characteristics literature"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_co_benefits(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Co-Benefits criterion.

    Assesses additional environmental and social benefits beyond carbon impact.

    Scoring factors:
    - Methodology type co-benefit potential
    - Geographic distribution (social benefit indicators)
    - Biodiversity and ecosystem service alignment

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Co-Benefits criterion
    """
    evidence = []
    data_sources = ["Methodology Type Analysis", "Geographic Analysis", "Co-Benefits Literature"]

    # Query projects for geographic analysis
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    # Methodology type determines co-benefit potential
    methodology_type = _infer_methodology_type(credit_class_id)

    if methodology_type == "soil_carbon":
        evidence.append(
            "Regenerative agriculture practices provide significant biodiversity benefits"
        )
        evidence.append(
            "Soil health improvements deliver multiple ecosystem service benefits"
        )
        evidence.append(
            "Agricultural projects support rural economic development and farmer livelihoods"
        )
        base_score = 2.4  # Good - soil carbon has strong co-benefits
        confidence = 0.78
    elif methodology_type == "reforestation":
        evidence.append(
            "Reforestation provides habitat creation and biodiversity restoration"
        )
        evidence.append(
            "Forest restoration supports watershed protection and air quality"
        )
        evidence.append(
            "Local community engagement creates social and economic co-benefits"
        )
        base_score = 2.6  # Strong - reforestation has excellent co-benefits
        confidence = 0.82
    elif methodology_type == "blue_carbon":
        evidence.append(
            "Coastal restoration protects marine biodiversity and fish habitat"
        )
        evidence.append(
            "Blue carbon projects provide coastal protection and storm resilience"
        )
        evidence.append(
            "Maritime communities benefit from improved ecosystem health"
        )
        base_score = 2.5  # Strong - blue carbon has strong coastal co-benefits
        confidence = 0.80
    elif methodology_type == "biodiversity":
        evidence.append(
            "Biodiversity conservation provides direct ecosystem preservation benefits"
        )
        evidence.append(
            "Habitat protection supports species conservation and ecological resilience"
        )
        base_score = 2.8  # Excellent - biodiversity focus has maximum co-benefits
        confidence = 0.85
    else:
        evidence.append(
            f"{methodology_type.title()} co-benefits require detailed assessment"
        )
        base_score = 2.0
        confidence = 0.70

    # Geographic diversity indicates broader social benefit reach
    jurisdictions = [p.get("jurisdiction", "Unknown") for p in class_projects]
    unique_jurisdictions = set(jurisdictions)

    if len(unique_jurisdictions) > 5:
        evidence.append(
            f"Geographic diversity ({len(unique_jurisdictions)} jurisdictions) amplifies social co-benefits"
        )
        score = min(3.0, base_score + 0.2)
    elif len(unique_jurisdictions) > 2:
        evidence.append(
            f"Multi-regional implementation ({len(unique_jurisdictions)} jurisdictions) supports diverse communities"
        )
        score = min(3.0, base_score + 0.1)
    else:
        score = base_score

    return CriterionScore(
        criterion_name="Co-Benefits",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Methodology type: {methodology_type}",
            f"Geographic analysis: {len(unique_jurisdictions)} jurisdictions"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_accuracy(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Accuracy criterion.

    Assesses the accuracy of measurement and quantification methods.

    Scoring factors:
    - Methodology type measurement protocols
    - Verification evidence from batch issuance
    - Project scale indicating protocol validation

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Accuracy criterion
    """
    evidence = []
    data_sources = ["Methodology Type Analysis", "Measurement Standards", "Verification Evidence"]

    # Query projects and batches
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    # Methodology type determines measurement accuracy characteristics
    methodology_type = _infer_methodology_type(credit_class_id)

    if methodology_type == "soil_carbon":
        evidence.append(
            "Soil sampling protocols typically employ laboratory analysis (e.g., DUMAS method)"
        )
        evidence.append(
            "Agricultural soil carbon measurement protocols align with research standards"
        )
        evidence.append(
            "Third-party verification indicated through Regen Registry implementation"
        )
        base_score = 2.6  # Strong - soil carbon has rigorous measurement protocols
        confidence = 0.82
    elif methodology_type == "reforestation":
        evidence.append(
            "Forestry measurement protocols use established allometric equations"
        )
        evidence.append(
            "Remote sensing and ground-truth validation support accuracy"
        )
        base_score = 2.5  # Strong - forestry has well-established protocols
        confidence = 0.80
    elif methodology_type == "blue_carbon":
        evidence.append(
            "Blue carbon measurement combines sediment coring with laboratory analysis"
        )
        evidence.append(
            "Marine carbon protocols follow peer-reviewed methodologies"
        )
        base_score = 2.4  # Good - blue carbon protocols are specialized but rigorous
        confidence = 0.78
    else:
        evidence.append(
            f"{methodology_type.title()} measurement protocols require detailed assessment"
        )
        base_score = 2.0
        confidence = 0.70

    # Batch issuance indicates verification and accuracy validation
    if class_batches:
        evidence.append(
            f"Measurement accuracy validated through {len(class_batches)} verified batch issuances"
        )

    # Project scale suggests protocol refinement
    if len(class_projects) > 10:
        evidence.append(
            f"Widespread implementation ({len(class_projects)} projects) validates measurement accuracy"
        )
        score = min(3.0, base_score + 0.2)
    elif len(class_projects) > 5:
        score = min(3.0, base_score + 0.1)
    else:
        score = base_score

    return CriterionScore(
        criterion_name="Accuracy",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Methodology type: {methodology_type}",
            f"Verification evidence: {len(class_batches)} batches"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


async def score_precision(credit_class_id: str, client: Any) -> CriterionScore:
    """Score Precision criterion.

    Assesses the repeatability and consistency of measurement protocols.

    Scoring factors:
    - Batch issuance consistency (measurement repeatability indicator)
    - Monitoring frequency regularity
    - Protocol standardization evidence

    Args:
        credit_class_id: Credit class ID
        client: Regen client instance

    Returns:
        CriterionScore for Precision criterion
    """
    evidence = []
    data_sources = ["Batch Issuance Patterns", "Monitoring Frequency", "Protocol Standards"]

    # Query projects and batches for pattern analysis
    projects_response = await client.query_projects()
    projects = projects_response.get('projects', [])
    class_projects = [p for p in projects if p.get("class_id") == credit_class_id]

    batches_response = await client.query_credit_batches()
    batches = batches_response.get('batches', [])
    class_batches = [
        b for b in batches
        if any(b.get("project_id") == p.get("id") for p in class_projects)
    ]

    # Calculate batch consistency (indicator of precision)
    if class_projects and len(class_projects) > 0:
        batches_per_project = len(class_batches) / len(class_projects)

        if batches_per_project >= 4:
            evidence.append(
                f"Consistent batch issuance patterns ({batches_per_project:.1f} batches/project) indicate standardized protocols"
            )
            consistency_score = 2.6
        elif batches_per_project >= 2:
            evidence.append(
                f"Regular batch issuance ({batches_per_project:.1f} batches/project) supports measurement repeatability"
            )
            consistency_score = 2.4
        elif batches_per_project >= 1:
            evidence.append(
                "Annual monitoring frequency supports precision requirements"
            )
            consistency_score = 2.2
        else:
            evidence.append(
                "Limited batch history - precision assessment pending more data"
            )
            consistency_score = 2.0
    else:
        consistency_score = 2.0
        evidence.append(
            "Insufficient data for precision assessment"
        )

    # Methodology type precision characteristics
    methodology_type = _infer_methodology_type(credit_class_id)

    if methodology_type == "soil_carbon":
        evidence.append(
            "Soil carbon measurement protocols emphasize statistical validation and repeatability"
        )
        evidence.append(
            "Laboratory standardization supports measurement precision"
        )
        method_precision = 0.1
    elif methodology_type == "reforestation":
        evidence.append(
            "Forestry measurement protocols use standardized inventory procedures"
        )
        method_precision = 0.0
    elif methodology_type == "blue_carbon":
        evidence.append(
            "Blue carbon protocols require multiple core samples for precision"
        )
        method_precision = 0.05
    else:
        evidence.append(
            f"{methodology_type.title()} precision protocols require detailed assessment"
        )
        method_precision = 0.0

    # Final score
    score = min(3.0, consistency_score + method_precision)

    # Confidence based on data availability
    if len(class_batches) > 20:
        confidence = 0.85
    elif len(class_batches) > 10:
        confidence = 0.80
    elif len(class_batches) > 5:
        confidence = 0.75
    else:
        confidence = 0.70

    return CriterionScore(
        criterion_name="Precision",
        score=round(score, 1),
        score_label=_determine_score_label(score),
        evidence=evidence,
        citations=[
            f"Batch pattern analysis: {len(class_batches)} batches across {len(class_projects)} projects"
        ],
        confidence=confidence,
        data_sources=data_sources
    )


# ============================================================================
# MAIN COMPARISON FUNCTION
# ============================================================================

async def compare_methodologies_nine_criteria(
    methodology_ids: List[str],
    buyer_preset: Union[str, BuyerPreset] = "high_integrity"
) -> List[MethodologyComparisonResult]:
    """Compare methodologies using 9-criteria framework.

    Main function for methodology comparison. Assesses all 9 criteria for each
    methodology and applies buyer-specific weighting.

    Args:
        methodology_ids: List of credit class IDs to compare
        buyer_preset: Buyer preset ID string or BuyerPreset object

    Returns:
        List of MethodologyComparisonResult objects, one per methodology

    Raises:
        ValueError: If buyer preset not found or methodology IDs invalid
    """
    start_time = datetime.now()

    # Validate and get buyer preset
    preset = _get_buyer_preset(buyer_preset)

    # Get Regen client
    client = get_regen_client()

    # Results list
    results = []

    # Process each methodology
    for methodology_id in methodology_ids:
        try:
            # Get methodology metadata
            metadata = await get_methodology_metadata(methodology_id)

            # Score all 9 criteria in parallel for performance
            scores_tasks = [
                score_mrv(methodology_id, client),
                score_additionality(methodology_id, client),
                score_leakage(methodology_id, client),
                score_traceability(methodology_id, client),
                score_cost_efficiency(methodology_id, client),
                score_permanence(methodology_id, client),
                score_co_benefits(methodology_id, client),
                score_accuracy(methodology_id, client),
                score_precision(methodology_id, client)
            ]

            # Execute all scoring functions in parallel
            criterion_scores = await asyncio.gather(*scores_tasks)

            # Create NineCriteriaScores object
            nine_criteria_scores = NineCriteriaScores(
                mrv=criterion_scores[0],
                additionality=criterion_scores[1],
                leakage=criterion_scores[2],
                traceability=criterion_scores[3],
                cost_efficiency=criterion_scores[4],
                permanence=criterion_scores[5],
                co_benefits=criterion_scores[6],
                accuracy=criterion_scores[7],
                precision=criterion_scores[8]
            )

            # Calculate scores
            overall_score = nine_criteria_scores.overall_score
            weighted_score = nine_criteria_scores.calculate_weighted_score(preset)
            evidence_quality = nine_criteria_scores.average_confidence

            # Identify key strengths and validation areas
            key_strengths = _identify_key_strengths(nine_criteria_scores)
            areas_for_validation = _identify_validation_areas(nine_criteria_scores)

            # Generate recommendation
            recommendation = _generate_recommendation(
                weighted_score,
                overall_score,
                evidence_quality
            )

            # Calculate response time
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000

            # Create result
            result = MethodologyComparisonResult(
                methodology=metadata,
                scores=nine_criteria_scores,
                buyer_preset=preset,
                weighted_score=weighted_score,
                overall_score=round(overall_score, 2),
                evidence_quality=round(evidence_quality, 2),
                recommendation=recommendation,
                key_strengths=key_strengths,
                areas_for_validation=areas_for_validation,
                response_time_ms=round(elapsed_time, 2),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "analysis_version": "1.0",
                    "buyer_preset_id": preset.preset_id,
                    "methodology_count": len(methodology_ids),
                    "data_sources": ["Regen Blockchain", "Methodology Type Analysis"]
                }
            )

            results.append(result)

        except Exception as e:
            logger.error(f"Error comparing methodology {methodology_id}: {str(e)}")
            raise ValueError(f"Failed to compare methodology {methodology_id}: {str(e)}")

    # Sort results by weighted score (highest first)
    results.sort(key=lambda r: r.weighted_score, reverse=True)

    return results


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_comparison_to_markdown(
    results: List[MethodologyComparisonResult],
    output_file: Optional[str] = None
) -> str:
    """Export comparison results to markdown format.

    Generates a buyer-facing one-pager comparison report.

    Args:
        results: List of comparison results
        output_file: Optional file path to write markdown

    Returns:
        Markdown string
    """
    if not results:
        return "# Methodology Comparison Report\n\nNo results to display.\n"

    # Get buyer preset info from first result (all should have same preset)
    buyer_preset = results[0].buyer_preset
    generated_date = datetime.now().strftime("%Y-%m-%d")

    # Build markdown content
    lines = []

    # Header
    lines.append("# Methodology Comparison Report")
    lines.append(f"**Generated:** {generated_date}")
    lines.append(f"**Buyer Profile:** {buyer_preset.preset_name}")
    lines.append(f"**Focus Areas:** {', '.join(buyer_preset.focus_areas)}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    if len(results) == 1:
        result = results[0]
        lines.append(f"Assessed **{result.methodology.methodology_name}** ({result.methodology.credit_class_id}) ")
        lines.append(f"for {buyer_preset.preset_name} buyer profile.")
        lines.append("")
        lines.append(f"**Overall Score:** {result.overall_score:.2f}/3.0")
        lines.append(f"**Weighted Score:** {result.weighted_score:.2f}/3.0 (optimized for {buyer_preset.preset_name})")
        lines.append(f"**Evidence Quality:** {result.evidence_quality:.2f} ({int(result.evidence_quality * 100)}% confidence)")
        lines.append(f"**Recommendation:** {result.recommendation}")
    else:
        lines.append(f"Compared **{len(results)} methodologies** for {buyer_preset.preset_name} buyer profile.")
        lines.append("")
        lines.append("**Ranking** (by weighted score):")
        for i, result in enumerate(results, 1):
            lines.append(f"{i}. **{result.methodology.methodology_name}** - {result.weighted_score:.2f}/3.0")
    lines.append("")

    # Comparison Matrix
    lines.append("## Comparison Matrix")
    lines.append("")

    if len(results) == 1:
        # Single methodology - vertical format
        result = results[0]
        lines.append("| Criterion | Score | Label | Weight | Confidence |")
        lines.append("|-----------|-------|-------|--------|------------|")

        criteria_data = [
            ("MRV", result.scores.mrv, buyer_preset.criteria_weights["mrv"]),
            ("Additionality", result.scores.additionality, buyer_preset.criteria_weights["additionality"]),
            ("Leakage", result.scores.leakage, buyer_preset.criteria_weights["leakage"]),
            ("Traceability", result.scores.traceability, buyer_preset.criteria_weights["traceability"]),
            ("Cost Efficiency", result.scores.cost_efficiency, buyer_preset.criteria_weights["cost_efficiency"]),
            ("Permanence", result.scores.permanence, buyer_preset.criteria_weights["permanence"]),
            ("Co-Benefits", result.scores.co_benefits, buyer_preset.criteria_weights["co_benefits"]),
            ("Accuracy", result.scores.accuracy, buyer_preset.criteria_weights["accuracy"]),
            ("Precision", result.scores.precision, buyer_preset.criteria_weights["precision"]),
        ]

        for criterion_name, criterion_score, weight in criteria_data:
            score_str = f"{criterion_score.score:.1f}"
            label_str = criterion_score.score_label
            weight_str = f"{weight*100:.0f}%"
            conf_str = f"{criterion_score.confidence:.2f}"

            lines.append(f"| {criterion_name} | {score_str} | {label_str} | {weight_str} | {conf_str} |")
    else:
        # Multiple methodologies - horizontal format
        # Header row
        header = "| Criterion | Weight |"
        for result in results:
            header += f" {result.methodology.credit_class_id} |"
        lines.append(header)

        # Separator row
        separator = "|-----------|--------|"
        for _ in results:
            separator += "------|"
        lines.append(separator)

        # Data rows
        criteria_names = [
            ("MRV", "mrv"),
            ("Additionality", "additionality"),
            ("Leakage", "leakage"),
            ("Traceability", "traceability"),
            ("Cost Efficiency", "cost_efficiency"),
            ("Permanence", "permanence"),
            ("Co-Benefits", "co_benefits"),
            ("Accuracy", "accuracy"),
            ("Precision", "precision"),
        ]

        for display_name, attr_name in criteria_names:
            weight = buyer_preset.criteria_weights[attr_name]
            row = f"| {display_name} | {weight*100:.0f}% |"

            for result in results:
                criterion = getattr(result.scores, attr_name)
                score_display = f"{criterion.score:.1f}"
                if criterion.score >= 2.5:
                    score_display += " ⭐"
                row += f" {score_display} |"

            lines.append(row)

        # Overall scores
        lines.append(f"| **Overall Score** | - |")
        for result in results:
            lines.append(f" **{result.overall_score:.2f}** |")
        lines.append("")

        lines.append(f"| **Weighted Score** | - |")
        for result in results:
            lines.append(f" **{result.weighted_score:.2f}** |")

    lines.append("")

    # Detailed Assessment for Each Methodology
    for result in results:
        lines.append(f"## {result.methodology.methodology_name} ({result.methodology.credit_class_id})")
        lines.append("")

        # Metadata
        lines.append("### Methodology Information")
        lines.append(f"- **Type:** {result.methodology.methodology_type}")
        lines.append(f"- **Status:** {result.methodology.status}")
        lines.append(f"- **Projects:** {result.methodology.project_count}")
        lines.append(f"- **Batches:** {result.methodology.batch_count}")
        if result.methodology.geographic_scope:
            lines.append(f"- **Geographic Scope:** {', '.join(result.methodology.geographic_scope[:5])}")
        lines.append("")

        # Key Strengths
        lines.append("### Key Strengths")
        if result.key_strengths:
            for strength in result.key_strengths:
                criterion_attr = strength.lower().replace(" ", "_").replace("-", "_")
                try:
                    criterion = getattr(result.scores, criterion_attr)
                    lines.append(f"- **{strength}** ({criterion.score:.1f}): {criterion.evidence[0]}")
                except:
                    lines.append(f"- **{strength}**")
        else:
            lines.append("- No criteria scored as Strong (≥2.5)")
        lines.append("")

        # Areas for Validation
        lines.append("### Areas for Validation")
        if result.areas_for_validation:
            lines.append("*Lower confidence areas requiring additional review:*")
            for area in result.areas_for_validation:
                criterion_attr = area.lower().replace(" ", "_").replace("-", "_")
                try:
                    criterion = getattr(result.scores, criterion_attr)
                    lines.append(f"- **{area}** (confidence: {criterion.confidence:.2f})")
                except:
                    lines.append(f"- **{area}**")
        else:
            lines.append("- All criteria have high confidence (≥0.8)")
        lines.append("")

        # Evidence Summaries (top 3 criteria by weight)
        lines.append("### Evidence Summary")
        top_criteria = buyer_preset.top_criteria[:3]
        for criterion_id, weight in top_criteria:
            try:
                criterion = getattr(result.scores, criterion_id)
                criterion_display = criterion.criterion_name
                lines.append(f"#### {criterion_display} (weight: {weight*100:.0f}%, score: {criterion.score:.1f})")
                lines.append(f"*{criterion.score_label} - Confidence: {criterion.confidence:.2f}*")
                lines.append("")
                for evidence in criterion.evidence[:3]:  # Top 3 evidence items
                    lines.append(f"- {evidence}")
                lines.append("")
            except:
                continue

        lines.append("---")
        lines.append("")

    # Footer
    lines.append("## Methodology Notes")
    lines.append("")
    lines.append("**Scoring Scale:**")
    lines.append("- 2.5-3.0: Strong ⭐")
    lines.append("- 2.0-2.4: Adequate")
    lines.append("- 1.0-1.9: Partial")
    lines.append("- 0.0-0.9: Insufficient")
    lines.append("")
    lines.append("**Confidence Levels:**")
    lines.append("- ≥0.8: High confidence")
    lines.append("- 0.6-0.79: Moderate confidence")
    lines.append("- <0.6: Low confidence (requires validation)")
    lines.append("")
    lines.append("**Data Sources:** Regen Network blockchain, credit class metadata, project data")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated with Regen MCP 9-Criteria Methodology Comparison Framework*")
    lines.append(f"*Report Date: {generated_date}*")

    # Join all lines
    markdown_content = "\n".join(lines)

    # Write to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(markdown_content)
            logger.info(f"Markdown report exported to {output_file}")
        except Exception as e:
            logger.error(f"Error writing markdown file: {e}")

    return markdown_content


def export_comparison_to_json(
    results: List[MethodologyComparisonResult],
    output_file: Optional[str] = None
) -> str:
    """Export comparison results to JSON format.

    Args:
        results: List of comparison results
        output_file: Optional file path to write JSON

    Returns:
        JSON string
    """
    # TODO: Implement JSON export
    # Will be implemented in Week 2
    pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_buyer_preset(preset_identifier: Union[str, BuyerPreset]) -> BuyerPreset:
    """Get buyer preset from identifier or object.

    Args:
        preset_identifier: Preset ID string or BuyerPreset object

    Returns:
        BuyerPreset object

    Raises:
        ValueError: If preset ID not found
    """
    if isinstance(preset_identifier, BuyerPreset):
        return preset_identifier

    if preset_identifier not in BUYER_PRESETS:
        available = ", ".join(BUYER_PRESETS.keys())
        raise ValueError(
            f"Unknown buyer preset: {preset_identifier}. "
            f"Available presets: {available}"
        )

    return BUYER_PRESETS[preset_identifier]


def _determine_score_label(score: float) -> str:
    """Determine human-readable label from numeric score.

    Args:
        score: Score on 0-3 scale

    Returns:
        Label string (Insufficient/Partial/Adequate/Strong)
    """
    if score >= 2.5:
        return "Strong"
    elif score >= 2.0:
        return "Adequate"
    elif score >= 1.0:
        return "Partial"
    else:
        return "Insufficient"


def _identify_key_strengths(scores: NineCriteriaScores) -> List[str]:
    """Identify criteria with strong scores (>= 2.5).

    Args:
        scores: NineCriteriaScores object

    Returns:
        List of criterion names with strong scores
    """
    criteria = [
        ("MRV", scores.mrv),
        ("Additionality", scores.additionality),
        ("Leakage", scores.leakage),
        ("Traceability", scores.traceability),
        ("Cost Efficiency", scores.cost_efficiency),
        ("Permanence", scores.permanence),
        ("Co-Benefits", scores.co_benefits),
        ("Accuracy", scores.accuracy),
        ("Precision", scores.precision)
    ]

    return [name for name, criterion in criteria if criterion.score >= 2.5]


def _identify_validation_areas(scores: NineCriteriaScores) -> List[str]:
    """Identify criteria needing validation (confidence < 0.8).

    Args:
        scores: NineCriteriaScores object

    Returns:
        List of criterion names needing validation
    """
    criteria = [
        ("MRV", scores.mrv),
        ("Additionality", scores.additionality),
        ("Leakage", scores.leakage),
        ("Traceability", scores.traceability),
        ("Cost Efficiency", scores.cost_efficiency),
        ("Permanence", scores.permanence),
        ("Co-Benefits", scores.co_benefits),
        ("Accuracy", scores.accuracy),
        ("Precision", scores.precision)
    ]

    return [name for name, criterion in criteria if criterion.confidence < 0.8]


def _generate_recommendation(
    weighted_score: float,
    overall_score: float,
    evidence_quality: float
) -> str:
    """Generate recommendation based on scores.

    Args:
        weighted_score: Weighted score for buyer preset
        overall_score: Unweighted average score
        evidence_quality: Average confidence

    Returns:
        Recommendation string
    """
    if overall_score >= 2.5 and evidence_quality >= 0.80:
        return "STRONGLY RECOMMENDED: High-quality methodology with excellent 9-criteria performance"
    elif overall_score >= 2.0 and evidence_quality >= 0.70:
        return "RECOMMENDED: Good methodology performance with adequate evidence backing"
    elif overall_score >= 1.5:
        return "CONDITIONAL: Consider with additional validation"
    else:
        return "NOT RECOMMENDED: Insufficient evidence or poor performance"
