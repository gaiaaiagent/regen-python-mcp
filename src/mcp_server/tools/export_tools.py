"""Export tools for methodology comparison reports."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def format_score_stars(score: float) -> str:
    """Format score as star rating (0-3 scale).

    Args:
        score: Score between 0.0 and 3.0

    Returns:
        Star rating string (e.g., "★★★", "★★☆", "★☆☆")
    """
    full_stars = int(score)
    half_star = (score - full_stars) >= 0.5
    empty_stars = 3 - full_stars - (1 if half_star else 0)

    return "★" * full_stars + ("⯨" if half_star else "") + "☆" * empty_stars


def format_confidence(confidence: float) -> str:
    """Format confidence as percentage.

    Args:
        confidence: Confidence value between 0.0 and 1.0

    Returns:
        Confidence percentage as string (e.g., "85")
    """
    return str(int(confidence * 100))


def format_evidence_brief(evidence: List[str], max_length: int = 100) -> str:
    """Format evidence list as brief summary.

    Args:
        evidence: List of evidence strings
        max_length: Maximum length of output string

    Returns:
        Brief evidence summary
    """
    if not evidence:
        return "No evidence available"

    # Take first evidence item and truncate if needed
    first_evidence = evidence[0]
    if len(first_evidence) > max_length:
        return first_evidence[:max_length - 3] + "..."
    return first_evidence


def generate_comparison_onepager(
    comparison_results: List[Any],
    buyer_preset: str,
    output_format: str = "markdown"
) -> str:
    """Generate one-pager comparison report.

    Args:
        comparison_results: List of MethodologyComparisonResult objects from compare_methodologies_nine_criteria
        buyer_preset: Buyer preset used (e.g., "high_integrity", "eu_risk_sensitive", "net_zero")
        output_format: "markdown" or "html"

    Returns:
        Formatted report as string
    """
    if not comparison_results:
        raise ValueError("No comparison results provided")

    # Load template
    template_dir = Path(__file__).parent.parent / "templates"
    template_file = template_dir / "methodology_comparison_onepager.md"

    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    template = template_file.read_text()

    # For single methodology comparison, use first result
    result = comparison_results[0]

    # Extract criterion scores
    scores = result.scores

    # Build buyer preset focus areas
    preset_focus = {
        "high_integrity": "MRV, additionality, and permanence",
        "eu_risk_sensitive": "leakage risk, traceability, and co-benefits",
        "net_zero": "cost-efficiency, accuracy, and volume availability"
    }

    # Build key findings list
    key_findings_list = []
    if result.key_strengths:
        key_findings_list.extend([f"- {strength}" for strength in result.key_strengths[:3]])
    else:
        key_findings_list.append("- Comprehensive methodology analysis completed")
        key_findings_list.append(f"- Overall score: {result.overall_score:.2f}/3.0")
        key_findings_list.append(f"- Weighted score: {result.weighted_score:.2f}/3.0")

    key_findings = "\n".join(key_findings_list)

    # Build methodology overview
    methodology_overview = f"""### {result.methodology.methodology_name}
- **Credit Class**: {result.methodology.credit_class_id}
- **Methodology ID**: {result.methodology.methodology_id}
- **Overall Score**: {result.overall_score:.2f}/3.0
- **Weighted Score ({buyer_preset.replace('_', ' ').title()})**: {result.weighted_score:.2f}/3.0
- **Evidence Quality**: {result.evidence_quality:.0%}
"""

    # Build key strengths section
    strengths_text = "\n".join([f"- {strength}" for strength in result.key_strengths]) if result.key_strengths else "- Strong methodology framework"

    # Build areas for validation section
    validation_text = "\n".join([f"- {area}" for area in result.areas_for_validation]) if result.areas_for_validation else "_No significant validation concerns identified_"

    # Build data sources list
    all_data_sources = set()
    all_data_sources.update(scores.mrv.data_sources)
    all_data_sources.update(scores.additionality.data_sources)
    all_data_sources.update(scores.leakage.data_sources)
    data_sources_text = "\n".join([f"- {source}" for source in sorted(all_data_sources)])

    # Build citations
    methodology_citations_set = set()
    blockchain_citations_set = set()

    for criterion in [scores.mrv, scores.additionality, scores.leakage, scores.traceability,
                      scores.cost_efficiency, scores.permanence, scores.co_benefits,
                      scores.accuracy, scores.precision]:
        for source in criterion.data_sources:
            if "Methodology Document" in source:
                methodology_citations_set.add(source)
            elif "Blockchain" in source or "Regen" in source:
                blockchain_citations_set.add(source)

    methodology_citations = "\n".join([f"- {cit}" for cit in sorted(methodology_citations_set)]) or "_No methodology documents referenced_"
    blockchain_citations = "\n".join([f"- {cit}" for cit in sorted(blockchain_citations_set)]) or "_No blockchain data sources_"

    # Build next steps
    next_steps = """1. Review detailed evidence for high-priority criteria
2. Validate methodology documentation and project data
3. Consider portfolio diversification across methodologies
4. Monitor market pricing and availability trends"""

    # Executive summary
    executive_summary = f"""This report analyzes the **{result.methodology.methodology_name}** methodology using a comprehensive 9-criteria framework.
The methodology achieved an overall score of **{result.overall_score:.2f}/3.0** and a weighted score of **{result.weighted_score:.2f}/3.0**
under the {buyer_preset.replace('_', ' ').title()} buyer profile. The analysis is based on {int(result.evidence_quality * 100)}% evidence quality with
{len(result.key_strengths)} identified strengths."""

    # Recommendation
    recommendation = result.recommendation

    recommendation_detail = f"""The methodology scores **{result.weighted_score:.2f}/3.0** under your selected buyer profile, indicating
{_interpret_score(result.weighted_score)}."""

    recommendation_rationale = f"""This recommendation is based on:
- Overall methodology quality: {result.overall_score:.2f}/3.0
- Alignment with {buyer_preset.replace('_', ' ').title()} priorities
- Evidence quality: {result.evidence_quality:.0%}
- {len(result.key_strengths)} identified strengths"""

    # Build template variables
    template_vars = {
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "buyer_preset_name": buyer_preset.replace("_", " ").title(),
        "methodology_names": result.methodology.methodology_name,
        "executive_summary": executive_summary,
        "key_findings": key_findings,
        "recommendation": recommendation,
        "methodology_overviews": methodology_overview,

        # Criterion scores
        "mrv_score": f"{scores.mrv.score:.1f}",
        "mrv_stars": format_score_stars(scores.mrv.score),
        "mrv_confidence": format_confidence(scores.mrv.confidence),
        "mrv_evidence": format_evidence_brief(scores.mrv.evidence),

        "additionality_score": f"{scores.additionality.score:.1f}",
        "additionality_stars": format_score_stars(scores.additionality.score),
        "additionality_confidence": format_confidence(scores.additionality.confidence),
        "additionality_evidence": format_evidence_brief(scores.additionality.evidence),

        "leakage_score": f"{scores.leakage.score:.1f}",
        "leakage_stars": format_score_stars(scores.leakage.score),
        "leakage_confidence": format_confidence(scores.leakage.confidence),
        "leakage_evidence": format_evidence_brief(scores.leakage.evidence),

        "traceability_score": f"{scores.traceability.score:.1f}",
        "traceability_stars": format_score_stars(scores.traceability.score),
        "traceability_confidence": format_confidence(scores.traceability.confidence),
        "traceability_evidence": format_evidence_brief(scores.traceability.evidence),

        "cost_efficiency_score": f"{scores.cost_efficiency.score:.1f}",
        "cost_efficiency_stars": format_score_stars(scores.cost_efficiency.score),
        "cost_efficiency_confidence": format_confidence(scores.cost_efficiency.confidence),
        "cost_efficiency_evidence": format_evidence_brief(scores.cost_efficiency.evidence),

        "permanence_score": f"{scores.permanence.score:.1f}",
        "permanence_stars": format_score_stars(scores.permanence.score),
        "permanence_confidence": format_confidence(scores.permanence.confidence),
        "permanence_evidence": format_evidence_brief(scores.permanence.evidence),

        "co_benefits_score": f"{scores.co_benefits.score:.1f}",
        "co_benefits_stars": format_score_stars(scores.co_benefits.score),
        "co_benefits_confidence": format_confidence(scores.co_benefits.confidence),
        "co_benefits_evidence": format_evidence_brief(scores.co_benefits.evidence),

        "accuracy_score": f"{scores.accuracy.score:.1f}",
        "accuracy_stars": format_score_stars(scores.accuracy.score),
        "accuracy_confidence": format_confidence(scores.accuracy.confidence),
        "accuracy_evidence": format_evidence_brief(scores.accuracy.evidence),

        "precision_score": f"{scores.precision.score:.1f}",
        "precision_stars": format_score_stars(scores.precision.score),
        "precision_confidence": format_confidence(scores.precision.confidence),
        "precision_evidence": format_evidence_brief(scores.precision.evidence),

        # Overall scores
        "overall_score": f"{result.overall_score:.2f}",
        "weighted_score": f"{result.weighted_score:.2f}",
        "evidence_quality": f"{int(result.evidence_quality * 100)}",
        "response_time_ms": f"{int(result.response_time_ms)}",

        # Analysis sections
        "key_strengths": strengths_text,
        "areas_for_validation": validation_text,
        "comparative_insights": f"Methodology demonstrates {_interpret_score(result.overall_score)} performance across 9 criteria.",

        # Recommendation sections
        "focus_areas": preset_focus.get(buyer_preset, "comprehensive quality assessment"),
        "recommendation_detail": recommendation_detail,
        "recommendation_rationale": recommendation_rationale,
        "next_steps": next_steps,

        # Sources
        "data_sources": data_sources_text,
        "methodology_citations": methodology_citations,
        "blockchain_citations": blockchain_citations,
    }

    # Render template
    report = template.format(**template_vars)

    if output_format == "html":
        try:
            import markdown
            report = markdown.markdown(report, extensions=['tables'])
        except ImportError:
            logger.warning("markdown package not installed, returning plain markdown")

    return report


def _interpret_score(score: float) -> str:
    """Interpret a score value as a qualitative rating.

    Args:
        score: Score between 0.0 and 3.0

    Returns:
        Qualitative interpretation
    """
    if score >= 2.7:
        return "excellent"
    elif score >= 2.3:
        return "strong"
    elif score >= 2.0:
        return "good"
    elif score >= 1.5:
        return "moderate"
    else:
        return "limited"


def save_report_to_file(
    report_content: str,
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None,
    format: str = "markdown"
) -> Path:
    """Save report to file.

    Args:
        report_content: Report content as string
        output_dir: Output directory (defaults to current directory)
        filename: Custom filename (defaults to timestamped name)
        format: File format ("markdown" or "html")

    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = Path.cwd() / "reports"

    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "html" if format == "html" else "md"
        filename = f"methodology_comparison_{timestamp}.{extension}"

    output_path = output_dir / filename
    output_path.write_text(report_content)

    logger.info(f"Report saved to: {output_path}")
    return output_path
