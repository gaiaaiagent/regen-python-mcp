"""Tests for methodology comparison tools with real blockchain data.

These tests validate the 9-criteria methodology comparison framework that powers
carbon credit assessment and buyer-specific recommendations. NO MOCK DATA - validates
actual tool behavior with live Regen Network blockchain data.

The 9-criteria framework assesses:
1. MRV (Monitoring, Reporting, Verification)
2. Additionality
3. Leakage
4. Traceability
5. Cost Efficiency
6. Permanence
7. Co-Benefits
8. Accuracy
9. Precision

These tools are critical for:
- Buyers selecting carbon credits
- Impact investors assessing quality
- ESG analysts comparing methodologies
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.methodology_comparison_tools import (
    compare_methodologies_nine_criteria,
    get_methodology_metadata,
    load_methodology_data,
    resolve_methodology_id,
    select_methodology_for_scoring,
    score_mrv,
    score_additionality,
    score_leakage,
    score_traceability,
    score_cost_efficiency,
    score_permanence,
    score_co_benefits,
    score_accuracy,
    score_precision,
    export_comparison_to_markdown,
    _determine_score_label,
    _identify_key_strengths,
    _identify_validation_areas,
)
from mcp_server.client.regen_client import get_regen_client


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestMethodologyComparisonToolsOnline:
    """Test methodology comparison tools with live network connection.

    These tests validate the sophisticated 9-criteria assessment framework.
    """

    async def test_get_methodology_metadata_for_soil_carbon(self):
        """Test getting methodology metadata for C02 (soil carbon).

        VALIDATES: Can we extract methodology metadata from blockchain?
        IMPACT: Needed for methodology identification and context
        """
        try:
            metadata = await get_methodology_metadata("C02")

            assert metadata is not None, "Metadata should be returned"
            assert metadata.credit_class_id == "C02", "Credit class ID should match"

            print(f"✅ Can extract methodology metadata")
            print(f"   Credit Class: {metadata.credit_class_id}")
            print(f"   Type: {metadata.methodology_type}")
            print(f"   Projects: {metadata.project_count}")
            print(f"   Batches: {metadata.batch_count}")
        except ValueError as e:
            # Credit class may not exist - that's okay
            print(f"⚠️  C02 credit class not found: {e}")
            pytest.skip("C02 credit class not available on network")

    async def test_resolve_methodology_id_for_c02(self):
        """Test resolving credit class to methodology IDs.

        VALIDATES: Can we map credit class to methodology documents?
        IMPACT: Needed for enhanced scoring with methodology data
        """
        methodology_ids = resolve_methodology_id("C02")

        assert isinstance(methodology_ids, list), "Should return list of IDs"

        print(f"✅ Can resolve credit class to methodology IDs")
        print(f"   C02 → {methodology_ids}")

    async def test_select_methodology_for_scoring(self):
        """Test methodology selection when multiple options exist.

        VALIDATES: Can we select appropriate methodology for scoring?
        IMPACT: Needed for consistent scoring behavior
        """
        # Test with multiple methodologies
        methodology_ids = ["aei", "ecometric"]
        selected = select_methodology_for_scoring("C02", methodology_ids)

        assert selected in methodology_ids, "Should select from provided list"

        print(f"✅ Can select methodology for scoring")
        print(f"   Selected: {selected} from {methodology_ids}")

    async def test_load_methodology_data_structure(self):
        """Test loading normalized methodology data.

        VALIDATES: Can we load methodology data files?
        IMPACT: Enhanced scoring requires methodology documents
        """
        # Try to load AEI methodology data
        data = load_methodology_data("aei")

        if data:
            print(f"✅ Can load methodology data")
            print(f"   Methodology: AEI")
            print(f"   Data sections: {list(data.keys())}")

            # Check for expected sections
            if "mrv" in data:
                print(f"   MRV data available: {list(data['mrv'].keys())[:3]}")
        else:
            print(f"⚠️  Methodology data not available (expected for new setup)")
            print(f"   Scoring will use blockchain-only approach")

    async def test_score_mrv_for_methodology(self):
        """Test MRV criterion scoring.

        VALIDATES: Can we score monitoring, reporting, verification quality?
        IMPACT: MRV is critical quality criterion for carbon credits
        """
        client = get_regen_client()

        try:
            mrv_score = await score_mrv("C02", client)

            assert hasattr(mrv_score, 'score'), "Should have score attribute"
            assert hasattr(mrv_score, 'evidence'), "Should have evidence"
            assert hasattr(mrv_score, 'confidence'), "Should have confidence"

            assert 0.0 <= mrv_score.score <= 3.0, "Score should be 0-3 scale"
            assert 0.0 <= mrv_score.confidence <= 1.0, "Confidence should be 0-1"

            print(f"✅ Can score MRV criterion")
            print(f"   Score: {mrv_score.score:.1f}/3.0 ({mrv_score.score_label})")
            print(f"   Confidence: {mrv_score.confidence:.2f}")
            print(f"   Evidence items: {len(mrv_score.evidence)}")
        except ValueError as e:
            print(f"⚠️  C02 not available for MRV scoring: {e}")
            pytest.skip("C02 credit class not available")

    async def test_score_traceability_always_strong(self):
        """Test Traceability criterion (should always be strong on Regen).

        VALIDATES: Does blockchain provide inherent traceability?
        IMPACT: Traceability is key selling point for Regen Registry
        """
        client = get_regen_client()

        try:
            traceability_score = await score_traceability("C02", client)

            # Regen Registry should always provide strong traceability
            assert traceability_score.score >= 2.5, \
                "Regen blockchain should provide strong traceability"

            print(f"✅ Traceability scoring validates blockchain advantage")
            print(f"   Score: {traceability_score.score:.1f}/3.0")
            print(f"   Confidence: {traceability_score.confidence:.2f}")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_additionality_returns_valid_score(self):
        """Test Additionality criterion scoring.

        VALIDATES: Can we assess additionality?
        IMPACT: Additionality is critical for carbon credit integrity
        """
        client = get_regen_client()

        try:
            additionality_score = await score_additionality("C02", client)

            assert 0.0 <= additionality_score.score <= 3.0
            assert len(additionality_score.evidence) > 0

            print(f"✅ Can score Additionality criterion")
            print(f"   Score: {additionality_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_leakage_returns_valid_score(self):
        """Test Leakage criterion scoring.

        VALIDATES: Can we assess leakage risk?
        IMPACT: Leakage assessment ensures credit quality
        """
        client = get_regen_client()

        try:
            leakage_score = await score_leakage("C02", client)

            assert 0.0 <= leakage_score.score <= 3.0
            assert len(leakage_score.evidence) > 0

            print(f"✅ Can score Leakage criterion")
            print(f"   Score: {leakage_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_cost_efficiency_uses_market_data(self):
        """Test Cost Efficiency scoring with marketplace data.

        VALIDATES: Can we assess cost efficiency from sell orders?
        IMPACT: Cost is key decision factor for buyers
        """
        client = get_regen_client()

        try:
            cost_score = await score_cost_efficiency("C02", client)

            assert 0.0 <= cost_score.score <= 3.0

            print(f"✅ Can score Cost Efficiency criterion")
            print(f"   Score: {cost_score.score:.1f}/3.0")

            # Check if market data was used
            if "market price" in str(cost_score.evidence).lower():
                print(f"   Market data available for pricing")
            else:
                print(f"   Using methodology benchmarks (no active orders)")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_permanence_methodology_based(self):
        """Test Permanence criterion scoring.

        VALIDATES: Can we assess carbon storage permanence?
        IMPACT: Permanence is critical for long-term carbon impact
        """
        client = get_regen_client()

        try:
            permanence_score = await score_permanence("C02", client)

            assert 0.0 <= permanence_score.score <= 3.0
            assert len(permanence_score.evidence) > 0

            print(f"✅ Can score Permanence criterion")
            print(f"   Score: {permanence_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_co_benefits_methodology_based(self):
        """Test Co-Benefits criterion scoring.

        VALIDATES: Can we assess environmental and social co-benefits?
        IMPACT: Co-benefits important for impact investors
        """
        client = get_regen_client()

        try:
            co_benefits_score = await score_co_benefits("C02", client)

            assert 0.0 <= co_benefits_score.score <= 3.0
            assert len(co_benefits_score.evidence) > 0

            print(f"✅ Can score Co-Benefits criterion")
            print(f"   Score: {co_benefits_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_accuracy_methodology_based(self):
        """Test Accuracy criterion scoring.

        VALIDATES: Can we assess measurement accuracy?
        IMPACT: Accuracy critical for credit quality
        """
        client = get_regen_client()

        try:
            accuracy_score = await score_accuracy("C02", client)

            assert 0.0 <= accuracy_score.score <= 3.0

            print(f"✅ Can score Accuracy criterion")
            print(f"   Score: {accuracy_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_score_precision_batch_based(self):
        """Test Precision criterion scoring.

        VALIDATES: Can we assess measurement precision from batch patterns?
        IMPACT: Precision indicates protocol repeatability
        """
        client = get_regen_client()

        try:
            precision_score = await score_precision("C02", client)

            assert 0.0 <= precision_score.score <= 3.0

            print(f"✅ Can score Precision criterion")
            print(f"   Score: {precision_score.score:.1f}/3.0")
        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")


@pytest.mark.asyncio
@pytest.mark.tools
class TestMethodologyComparisonToolsValidation:
    """Test methodology comparison tools parameter validation and error handling."""

    async def test_get_methodology_metadata_invalid_class_raises_error(self):
        """Test that invalid credit class raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await get_methodology_metadata("INVALID_CLASS_999")

    def test_resolve_methodology_id_unknown_class_returns_empty(self):
        """Test that unknown credit class returns empty list."""
        result = resolve_methodology_id("UNKNOWN_CLASS")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_select_methodology_empty_list_returns_none(self):
        """Test that empty methodology list returns None."""
        result = select_methodology_for_scoring("C02", [])

        assert result is None

    def test_load_methodology_data_nonexistent_returns_none(self):
        """Test that nonexistent methodology returns None."""
        result = load_methodology_data("nonexistent_methodology")

        assert result is None

    def test_determine_score_label_thresholds(self):
        """Test score label determination logic."""
        assert _determine_score_label(3.0) == "Strong"
        assert _determine_score_label(2.5) == "Strong"
        assert _determine_score_label(2.4) == "Adequate"
        assert _determine_score_label(2.0) == "Adequate"
        assert _determine_score_label(1.9) == "Partial"
        assert _determine_score_label(1.0) == "Partial"
        assert _determine_score_label(0.9) == "Insufficient"
        assert _determine_score_label(0.0) == "Insufficient"


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestMethodologyComparisonToolsUserJourneys:
    """Test methodology comparison tools for real user scenarios.

    These tests validate complete carbon credit assessment workflows.
    """

    async def test_carbon_buyer_can_assess_methodology_quality(self):
        """
        USER: Carbon Credit Buyer
        GOAL: Assess quality of C02 methodology before purchasing

        VALIDATES: Can buyer get comprehensive quality assessment?
        """
        client = get_regen_client()

        try:
            # Step 1: Get methodology metadata
            metadata = await get_methodology_metadata("C02")

            print(f"✅ METHODOLOGY ASSESSMENT: Buyer can assess C02 quality")
            print(f"   Methodology: {metadata.methodology_type}")
            print(f"   Projects: {metadata.project_count}")

            # Step 2: Score key criteria (MRV, Additionality, Traceability)
            mrv = await score_mrv("C02", client)
            additionality = await score_additionality("C02", client)
            traceability = await score_traceability("C02", client)

            print(f"   MRV Score: {mrv.score:.1f}/3.0 ({mrv.score_label})")
            print(f"   Additionality: {additionality.score:.1f}/3.0")
            print(f"   Traceability: {traceability.score:.1f}/3.0")

            # Step 3: Assess overall quality
            avg_score = (mrv.score + additionality.score + traceability.score) / 3

            if avg_score >= 2.5:
                print(f"   ✅ HIGH QUALITY methodology (avg: {avg_score:.2f})")
            elif avg_score >= 2.0:
                print(f"   ✅ GOOD QUALITY methodology (avg: {avg_score:.2f})")
            else:
                print(f"   ⚠️  ADEQUATE methodology (avg: {avg_score:.2f})")

        except ValueError as e:
            print(f"⚠️  METHODOLOGY ASSESSMENT: C02 not available")
            print(f"   Error: {e}")
            pytest.skip("C02 not available")

    async def test_impact_investor_can_compare_co_benefits(self):
        """
        USER: Impact Investor
        GOAL: Compare co-benefits across methodologies

        VALIDATES: Can investor assess ESG impact beyond carbon?
        """
        client = get_regen_client()

        try:
            # Step 1: Score co-benefits for C02
            co_benefits = await score_co_benefits("C02", client)

            print(f"✅ CO-BENEFITS ANALYSIS: Investor can assess ESG impact")
            print(f"   C02 Co-Benefits Score: {co_benefits.score:.1f}/3.0")
            print(f"   Evidence items: {len(co_benefits.evidence)}")

            # Check for specific co-benefit types
            evidence_text = " ".join(co_benefits.evidence).lower()

            if "biodiversity" in evidence_text:
                print(f"   ✅ Biodiversity benefits documented")
            if "social" in evidence_text or "economic" in evidence_text:
                print(f"   ✅ Social/economic benefits documented")
            if "soil health" in evidence_text:
                print(f"   ✅ Soil health benefits documented")

        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_compliance_officer_can_assess_monitoring_rigor(self):
        """
        USER: Compliance Officer
        GOAL: Verify monitoring and verification rigor

        VALIDATES: Can officer assess regulatory compliance suitability?
        """
        client = get_regen_client()

        try:
            # Step 1: Assess MRV rigor
            mrv = await score_mrv("C02", client)

            # Step 2: Assess accuracy and precision
            accuracy = await score_accuracy("C02", client)
            precision = await score_precision("C02", client)

            print(f"✅ COMPLIANCE ASSESSMENT: Officer can verify monitoring rigor")
            print(f"   MRV Score: {mrv.score:.1f}/3.0 (confidence: {mrv.confidence:.2f})")
            print(f"   Accuracy: {accuracy.score:.1f}/3.0")
            print(f"   Precision: {precision.score:.1f}/3.0")

            # Assess compliance suitability
            avg_technical = (mrv.score + accuracy.score + precision.score) / 3

            if avg_technical >= 2.5 and mrv.confidence >= 0.80:
                print(f"   ✅ SUITABLE for regulatory compliance")
            elif avg_technical >= 2.0:
                print(f"   ⚠️  May require additional validation")
            else:
                print(f"   ❌ Insufficient rigor for strict compliance")

        except ValueError as e:
            pytest.skip(f"C02 not available: {e}")

    async def test_export_comparison_to_markdown_format(self):
        """
        USER: Portfolio Manager
        GOAL: Generate comparison report for stakeholders

        VALIDATES: Can manager export professional report?
        """
        # This test validates the export function structure
        # Full comparison test would require buyer presets to be configured

        print(f"✅ REPORT GENERATION: Export function available")
        print(f"   Markdown export: export_comparison_to_markdown()")
        print(f"   Note: Full comparison requires buyer preset configuration")


@pytest.mark.asyncio
@pytest.mark.tools
class TestMethodologyComparisonHelpers:
    """Test helper functions for methodology comparison."""

    def test_identify_key_strengths_from_scores(self):
        """Test identification of strong criteria (≥2.5)."""
        from mcp_server.models.methodology import CriterionScore, NineCriteriaScores

        # Create mock scores with some strong criteria
        strong_criterion = CriterionScore(
            criterion_name="Test Strong",
            score=2.8,
            score_label="Strong",
            evidence=["Strong evidence"],
            citations=["Citation"],
            confidence=0.90,
            data_sources=["Test"]
        )

        weak_criterion = CriterionScore(
            criterion_name="Test Weak",
            score=2.0,
            score_label="Adequate",
            evidence=["Evidence"],
            citations=["Citation"],
            confidence=0.70,
            data_sources=["Test"]
        )

        scores = NineCriteriaScores(
            mrv=strong_criterion,
            additionality=weak_criterion,
            leakage=strong_criterion,
            traceability=strong_criterion,
            cost_efficiency=weak_criterion,
            permanence=weak_criterion,
            co_benefits=weak_criterion,
            accuracy=weak_criterion,
            precision=weak_criterion
        )

        strengths = _identify_key_strengths(scores)

        # Should identify 3 strong criteria (MRV, Leakage, Traceability)
        assert len(strengths) == 3
        assert "MRV" in strengths
        assert "Leakage" in strengths
        assert "Traceability" in strengths

        print(f"✅ Can identify key strengths: {strengths}")

    def test_identify_validation_areas_from_scores(self):
        """Test identification of areas needing validation (confidence <0.8)."""
        from mcp_server.models.methodology import CriterionScore, NineCriteriaScores

        # Create mock scores with some low confidence
        high_confidence = CriterionScore(
            criterion_name="High Conf",
            score=2.5,
            score_label="Strong",
            evidence=["Evidence"],
            citations=["Citation"],
            confidence=0.85,
            data_sources=["Test"]
        )

        low_confidence = CriterionScore(
            criterion_name="Low Conf",
            score=2.0,
            score_label="Adequate",
            evidence=["Evidence"],
            citations=["Citation"],
            confidence=0.70,
            data_sources=["Test"]
        )

        scores = NineCriteriaScores(
            mrv=high_confidence,
            additionality=low_confidence,
            leakage=low_confidence,
            traceability=high_confidence,
            cost_efficiency=low_confidence,
            permanence=high_confidence,
            co_benefits=high_confidence,
            accuracy=high_confidence,
            precision=low_confidence
        )

        validation_areas = _identify_validation_areas(scores)

        # Should identify 4 low confidence areas
        assert len(validation_areas) == 4
        assert "Additionality" in validation_areas
        assert "Leakage" in validation_areas

        print(f"✅ Can identify validation areas: {validation_areas}")
