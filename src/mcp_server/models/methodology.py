"""Pydantic models for 9-criteria methodology comparison framework.

This module defines data models for carbon credit methodology assessment
using the 9-criteria framework (MRV, Additionality, Leakage, Traceability,
Cost Efficiency, Permanence, Co-Benefits, Accuracy, Precision).
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, validator

from .schemas import BaseRegenModel


class CriterionScore(BaseModel):
    """Individual 9-criteria assessment score with evidence backing.

    Represents assessment for a single criterion (e.g., MRV, Additionality)
    with supporting evidence, citations, and confidence metrics.

    Attributes:
        criterion_name: Name of criterion (e.g., "MRV", "Additionality")
        score: Numeric score on 0-3 scale
        score_label: Human-readable label (Insufficient/Partial/Adequate/Strong)
        evidence: List of evidence items supporting this score
        citations: Source citations for evidence
        confidence: Confidence level in this score (0-1)
        data_sources: Data sources used for scoring
    """

    criterion_name: str = Field(
        description="Criterion name (e.g., MRV, Additionality, Leakage)"
    )
    score: float = Field(
        ge=0.0, le=3.0,
        description="Score on 0-3 scale (0=Insufficient, 1=Partial, 2=Adequate, 3=Strong)"
    )
    score_label: Literal["Insufficient", "Partial", "Adequate", "Strong"] = Field(
        description="Human-readable score label"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Evidence items supporting this score"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="Source citations for evidence"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in this score (0-1 scale)"
    )
    data_sources: List[str] = Field(
        default_factory=list,
        description="Data sources used for scoring (e.g., 'blockchain', 'methodology_doc')"
    )

    @property
    def score_percentage(self) -> float:
        """Convert 0-3 score to percentage."""
        return (self.score / 3.0) * 100


class BuyerPreset(BaseModel):
    """Buyer preset configuration defining criteria weightings.

    Represents a buyer profile with specific priorities reflected in
    criteria weights that must sum to 1.0.

    Attributes:
        preset_name: Name of preset (e.g., "High-Integrity")
        preset_id: Machine-readable ID (e.g., "high_integrity")
        description: Brief description of preset focus
        criteria_weights: Dictionary mapping criterion names to weights (must sum to 1.0)
        focus_areas: Key focus areas for this preset
        target_buyers: Target buyer types
    """

    preset_name: str = Field(
        description="Human-readable preset name"
    )
    preset_id: str = Field(
        description="Machine-readable preset identifier"
    )
    description: str = Field(
        description="Brief description of preset purpose and focus"
    )
    criteria_weights: Dict[str, float] = Field(
        description="Criteria weights (keys: criterion IDs, values: 0-1 weights, must sum to 1.0)"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Key focus areas for this buyer profile"
    )
    target_buyers: List[str] = Field(
        default_factory=list,
        description="Target buyer types and personas"
    )

    @validator('criteria_weights')
    def validate_weights_sum(cls, v):
        """Ensure criteria weights sum to 1.0."""
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(f"Criteria weights must sum to 1.0, got {total}")
        return v

    @property
    def top_criteria(self) -> List[tuple]:
        """Get top 3 weighted criteria."""
        return sorted(self.criteria_weights.items(), key=lambda x: x[1], reverse=True)[:3]


class MethodologyMetadata(BaseModel):
    """Metadata about a methodology being assessed.

    Provides identification and contextual information about a carbon
    credit methodology on the Regen Network.

    Attributes:
        methodology_id: Unique identifier (e.g., "aei", "ecometric", "C02")
        credit_class_id: Blockchain credit class ID (e.g., "C02")
        methodology_name: Full methodology name
        developer: Methodology developer organization
        methodology_type: Type classification (e.g., "soil_carbon", "forestry")
        status: Current status (e.g., "active", "draft")
        geographic_scope: Geographic applicability
        project_count: Number of projects using this methodology
        batch_count: Number of credit batches issued
    """

    methodology_id: str = Field(
        description="Methodology identifier"
    )
    credit_class_id: Optional[str] = Field(
        None,
        description="Regen Ledger credit class ID"
    )
    methodology_name: str = Field(
        description="Full methodology name"
    )
    developer: Optional[str] = Field(
        None,
        description="Developer organization"
    )
    methodology_type: Optional[str] = Field(
        None,
        description="Methodology type classification"
    )
    status: Optional[str] = Field(
        None,
        description="Methodology status"
    )
    geographic_scope: List[str] = Field(
        default_factory=list,
        description="Geographic scope (jurisdictions)"
    )
    project_count: int = Field(
        default=0,
        ge=0,
        description="Number of projects"
    )
    batch_count: int = Field(
        default=0,
        ge=0,
        description="Number of credit batches"
    )


class NineCriteriaScores(BaseModel):
    """Complete 9-criteria scores for a methodology.

    Contains scores for all 9 criteria used in methodology comparison:
    MRV, Additionality, Leakage, Traceability, Cost Efficiency, Permanence,
    Co-Benefits, Accuracy, and Precision.
    """

    mrv: CriterionScore = Field(
        description="Monitoring, Reporting, Verification score"
    )
    additionality: CriterionScore = Field(
        description="Additionality assessment score"
    )
    leakage: CriterionScore = Field(
        description="Leakage risk score"
    )
    traceability: CriterionScore = Field(
        description="Traceability and transparency score"
    )
    cost_efficiency: CriterionScore = Field(
        description="Cost efficiency score"
    )
    permanence: CriterionScore = Field(
        description="Permanence and carbon storage duration score"
    )
    co_benefits: CriterionScore = Field(
        description="Co-benefits and SDG alignment score"
    )
    accuracy: CriterionScore = Field(
        description="Measurement accuracy score"
    )
    precision: CriterionScore = Field(
        description="Measurement precision and repeatability score"
    )

    @property
    def overall_score(self) -> float:
        """Calculate unweighted average score across all criteria."""
        scores = [
            self.mrv.score, self.additionality.score, self.leakage.score,
            self.traceability.score, self.cost_efficiency.score,
            self.permanence.score, self.co_benefits.score,
            self.accuracy.score, self.precision.score
        ]
        return sum(scores) / len(scores)

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all criteria."""
        confidences = [
            self.mrv.confidence, self.additionality.confidence,
            self.leakage.confidence, self.traceability.confidence,
            self.cost_efficiency.confidence, self.permanence.confidence,
            self.co_benefits.confidence, self.accuracy.confidence,
            self.precision.confidence
        ]
        return sum(confidences) / len(confidences)

    def calculate_weighted_score(self, buyer_preset: BuyerPreset) -> float:
        """Calculate weighted score based on buyer preset.

        Args:
            buyer_preset: BuyerPreset with criteria weights

        Returns:
            Weighted score (0-3 scale)
        """
        score = 0.0
        criterion_map = {
            "mrv": self.mrv.score,
            "additionality": self.additionality.score,
            "leakage": self.leakage.score,
            "traceability": self.traceability.score,
            "cost_efficiency": self.cost_efficiency.score,
            "permanence": self.permanence.score,
            "co_benefits": self.co_benefits.score,
            "accuracy": self.accuracy.score,
            "precision": self.precision.score
        }

        for criterion_id, weight in buyer_preset.criteria_weights.items():
            if criterion_id in criterion_map:
                score += criterion_map[criterion_id] * weight

        return round(score, 2)


class MethodologyComparisonResult(BaseRegenModel):
    """Complete methodology comparison result for 9-criteria framework.

    This is the main response model for methodology comparison operations,
    providing comprehensive assessment with buyer-specific weighting.

    Attributes:
        methodology: Methodology being assessed
        scores: All 9 criteria scores
        buyer_preset: Buyer preset used for weighting
        weighted_score: Weighted score based on buyer preset
        overall_score: Unweighted average score
        evidence_quality: Average confidence across all criteria
        recommendation: Overall recommendation based on scores
        key_strengths: Criteria with scores >= 2.5 (Strong)
        areas_for_validation: Criteria with confidence < 0.8
        response_time_ms: Response time in milliseconds
        metadata: Additional metadata (timestamp, version, etc.)
    """

    methodology: MethodologyMetadata = Field(
        description="Methodology being assessed"
    )
    scores: NineCriteriaScores = Field(
        description="All 9 criteria scores"
    )
    buyer_preset: BuyerPreset = Field(
        description="Buyer preset used for weighting"
    )
    weighted_score: float = Field(
        ge=0.0, le=3.0,
        description="Weighted score based on buyer preset"
    )
    overall_score: float = Field(
        ge=0.0, le=3.0,
        description="Unweighted average score"
    )
    evidence_quality: float = Field(
        ge=0.0, le=1.0,
        description="Average confidence across all criteria"
    )
    recommendation: str = Field(
        description="Overall recommendation based on scores"
    )
    key_strengths: List[str] = Field(
        default_factory=list,
        description="Criteria with scores >= 2.5 (Strong)"
    )
    areas_for_validation: List[str] = Field(
        default_factory=list,
        description="Criteria with confidence < 0.8"
    )
    response_time_ms: float = Field(
        ge=0,
        description="Response time in milliseconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (timestamp, version, etc.)"
    )


class ComparisonExportFormat(BaseModel):
    """Export-ready comparison data for markdown/PDF generation.

    Structured format optimized for report generation with all necessary
    information for creating buyer-facing one-pager documents.

    Attributes:
        comparison_title: Report title
        generated_at: Generation timestamp (ISO format)
        buyer_profile: Buyer preset name
        methodologies_compared: Methodology IDs compared
        comparison_table: Formatted comparison table data
        executive_summary: Executive summary text
        key_findings: Key findings and insights
        recommendations: Recommendation text
        citations: All citations used
    """

    comparison_title: str = Field(
        description="Report title"
    )
    generated_at: str = Field(
        description="Generation timestamp (ISO format)"
    )
    buyer_profile: str = Field(
        description="Buyer preset name"
    )
    methodologies_compared: List[str] = Field(
        description="Methodology IDs compared"
    )
    comparison_table: Dict[str, Any] = Field(
        description="Formatted comparison table data"
    )
    executive_summary: str = Field(
        description="Executive summary text"
    )
    key_findings: List[str] = Field(
        description="Key findings and insights"
    )
    recommendations: str = Field(
        description="Recommendation text"
    )
    citations: List[str] = Field(
        description="All citations used"
    )
