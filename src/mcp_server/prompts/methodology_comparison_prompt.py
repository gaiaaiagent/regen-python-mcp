"""Methodology comparison prompt implementation using 9-criteria framework."""

from typing import Optional, List


async def methodology_comparison(
    methodology_ids: Optional[List[str]] = None,
    buyer_preset: Optional[str] = None
) -> str:
    """
    Guide users through 9-criteria methodology comparison workflow.

    Helps assess carbon credit methodologies using evidence-backed scoring
    across 9 criteria with buyer-specific weighting.
    """

    # Customize based on parameters
    if methodology_ids and len(methodology_ids) > 0:
        if len(methodology_ids) == 1:
            focus_section = f"""
**🎯 Focus: Assessing {methodology_ids[0]}**
You want to evaluate a single methodology using the 9-criteria framework.

We'll provide:
• Complete 9-criteria assessment
• Buyer-specific weighted score
• Evidence-backed scoring rationale
• Key strengths and validation areas
"""
        else:
            focus_section = f"""
**🎯 Focus: Comparing {len(methodology_ids)} Methodologies**
You want to compare: {', '.join(methodology_ids)}

We'll provide:
• Side-by-side 9-criteria comparison
• Buyer-weighted rankings
• Comparative strengths analysis
• Decision-making recommendations
"""
    else:
        focus_section = """
**🎯 Overview: 9-Criteria Methodology Comparison**
Learn how to compare carbon credit methodologies using evidence-backed scoring!

This framework helps buyers make informed decisions based on their priorities.
"""

    # Customize for buyer preset
    if buyer_preset:
        preset_info = _get_preset_description(buyer_preset)
        focus_section += f"\n{preset_info}\n"

    return f"""🔬 **Regen Methodology Comparison**

{focus_section}

**Understanding the 9-Criteria Framework:**

The framework assesses methodologies across nine key dimensions, each scored 0-3:
• **MRV** (Monitoring, Reporting, Verification)
• **Additionality** (Environmental benefits beyond business-as-usual)
• **Leakage** (Risk of emissions displacement)
• **Traceability** (Transparency and credit tracking)
• **Cost Efficiency** (Price competitiveness)
• **Permanence** (Long-term carbon storage)
• **Co-Benefits** (Social and environmental benefits)
• **Accuracy** (Measurement protocol rigor)
• **Precision** (Repeatability of measurements)

---

## 👥 **Buyer Presets** - Decision Profiles

### High-Integrity (Institutional Investors)
**Focus**: MRV (25%) + Additionality (25%) + Accuracy (15%)
```python
result = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C02"],
    buyer_preset="high_integrity"
)
```
**Best for**: Compliance buyers, institutional investors, corporate sustainability teams

### EU Risk-Sensitive (European Buyers)
**Focus**: Leakage (30%) + Traceability (30%) + Additionality (15%)
```python
result = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C02"],
    buyer_preset="eu_risk_sensitive"
)
```
**Best for**: EU corporate buyers, regulatory compliance teams, risk-averse investors

### Net-Zero (Corporate Sustainability)
**Focus**: Co-Benefits (30%) + Cost Efficiency (20%) + Permanence (20%)
```python
result = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C02"],
    buyer_preset="net_zero"
)
```
**Best for**: Net-zero committed companies, impact investors, sustainability officers

---

## 🔍 **Comparison Workflows**

### Workflow 1: Single Methodology Assessment
```python
# Assess one methodology
result = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C02"],
    buyer_preset="high_integrity"
)

# Access results
methodology = result[0]
print(f"Overall Score: {{methodology['overall_score']}}/3.0")
print(f"Weighted Score: {{methodology['weighted_score']}}/3.0")
print(f"Evidence Quality: {{methodology['evidence_quality']*100}}%")

# Check key strengths
print("\\nKey Strengths:")
for strength in methodology['key_strengths']:
    print(f"  • {{strength}}")

# Check areas needing validation
print("\\nValidation Areas:")
for area in methodology['areas_for_validation']:
    print(f"  • {{area}}")
```

### Workflow 2: Multi-Methodology Comparison
```python
# Compare multiple methodologies
results = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C01", "C02", "C03"],
    buyer_preset="eu_risk_sensitive"
)

# Results are sorted by weighted score (best first)
print("Ranking for EU Risk-Sensitive buyers:")
for i, method in enumerate(results, 1):
    print(f"{{i}}. {{method['methodology']['methodology_id']}}: {{method['weighted_score']}}/3.0")
    print(f"   Recommendation: {{method['recommendation']}}")
```

### Workflow 3: Criterion Deep Dive
```python
# Compare specific criterion across methodologies
results = compare_methodologies_nine_criteria_tool(
    methodology_ids=["C01", "C02"],
    buyer_preset="high_integrity"
)

print("MRV Comparison:")
for result in results:
    methodology_id = result['methodology']['methodology_id']
    mrv = result['scores']['mrv']

    print(f"\\n{{methodology_id}}: {{mrv['score']}}/3.0 ({{mrv['score_label']}})")
    print(f"  Confidence: {{mrv['confidence']*100}}%")
    print(f"  Evidence:")
    for evidence in mrv['evidence']:
        print(f"    • {{evidence}}")
```

---

## 📊 **Interpreting Scores**

**Score Scale (0-3):**
• **0.0-0.9**: Insufficient - Significant gaps or limited evidence
• **1.0-1.9**: Partial - Basic requirements met, areas for improvement
• **2.0-2.9**: Adequate - Good performance, meets standards
• **3.0**: Strong - Excellent performance, exceeds best practices

**Confidence Levels:**
• **0.8-1.0**: High confidence - Strong evidence base
• **0.6-0.79**: Medium confidence - Good evidence, some gaps
• **0.0-0.59**: Low confidence - Limited evidence, needs validation

**Key Metrics:**
• **Overall Score**: Unweighted average across all 9 criteria
• **Weighted Score**: Buyer-specific score based on preset priorities
• **Evidence Quality**: Average confidence across all assessments

---

## 💡 **Decision-Making Tips**

**When to Use Each Preset:**
• **High-Integrity**: Prioritize verification standards and additionality for compliance
• **EU Risk-Sensitive**: Focus on transparency and regulatory alignment
• **Net-Zero**: Balance cost-effectiveness with impact and permanence

**Red Flags to Watch:**
• Confidence scores <0.7 on priority criteria
• Multiple criteria with "Insufficient" scores
• Significant gaps in evidence documentation

**Best Practices:**
• Compare methodologies within same project type (soil carbon, reforestation, etc.)
• Review evidence items for transparency
• Check validation areas before purchase decisions
• Consider both overall and weighted scores

---

## 🎯 **Practice Exercises**

**Exercise 1: Basic Assessment**
```python
# Task: Assess C02 methodology with High-Integrity preset
# Expected: See scores across all 9 criteria with evidence
```

**Exercise 2: Preset Comparison**
```python
# Task: Score same methodology with all 3 presets, compare weighted scores
# Expected: Different weighted scores showing preset impact
```

**Exercise 3: Multi-Methodology Ranking**
```python
# Task: Compare C01, C02, C03 with Net-Zero preset
# Expected: Ranked list showing which methodology best fits Net-Zero priorities
```

---

## 📋 **Quick Reference**

**Available Buyer Presets:**
• `high_integrity` - MRV + Additionality focus
• `eu_risk_sensitive` - Leakage + Traceability focus
• `net_zero` - Co-Benefits + Cost + Permanence focus

**Credit Class IDs:**
Use `list_classes()` to see the current set of credit classes and their resolved names.
Examples: `C01` (Verified Carbon Standard), `C02` (Urban Forest Carbon Credit Class), `C07` (CarbonPlus Grasslands Credit Class), `BT01`, `MBS01`, `USS01`, `KSH01`.

**Performance Target:**
• Single methodology: ~2-5 seconds
• Multiple methodologies: ~5-10 seconds
• Response includes full evidence backing

---

Ready to compare carbon credit methodologies?

**What would you like to do?**
• Assess a specific methodology (provide credit class ID)
• Compare multiple methodologies (provide list of IDs)
• Learn more about buyer presets (ask about preset details)
• Understand the 9 criteria (ask about specific criterion)"""


def _get_preset_description(preset_id: str) -> str:
    """Get description for a specific buyer preset."""
    presets = {
        "high_integrity": """
**Buyer Profile: High-Integrity Institutional Investor**
Your priority is verification standards and additionality for compliance-grade credits.

Top Criteria:
• MRV (25%) - Monitoring and verification rigor
• Additionality (25%) - Beyond business-as-usual impact
• Accuracy (15%) - Measurement protocol quality
""",
        "eu_risk_sensitive": """
**Buyer Profile: EU Risk-Sensitive Buyer**
Your priority is regulatory compliance with focus on leakage prevention and transparency.

Top Criteria:
• Leakage (30%) - Emissions displacement risk
• Traceability (30%) - Full transparency and tracking
• Additionality (15%) - Genuine additional benefits
""",
        "net_zero": """
**Buyer Profile: Net-Zero Corporate Commitment**
Your priority is cost-effective credits with strong co-benefits and permanence.

Top Criteria:
• Co-Benefits (30%) - Social and environmental impact
• Cost Efficiency (20%) - Price competitiveness
• Permanence (20%) - Long-term carbon storage
"""
    }

    return presets.get(preset_id, "")
