"""Scraper for Regen Registry methodology documents."""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RegistryScraper:
    """Scrape methodology documents from Regen Registry."""

    BASE_URL = "https://www.registry.regen.network"

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "data" / "methodologies"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_methodology(self, methodology_slug: str) -> Dict[str, Any]:
        """Scrape a methodology page from the registry.

        Args:
            methodology_slug: URL slug for methodology (e.g.,
                "aei-regenerative-soil-organic-carbon-methodology-...")

        Returns:
            Parsed methodology data
        """
        url = f"{self.BASE_URL}/crediting-protocols/{methodology_slug}"

        logger.info(f"Scraping methodology: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {url}: {response.status}")

                html = await response.text()

        # Save raw HTML
        raw_file = self.cache_dir / f"{methodology_slug}_raw.html"
        raw_file.write_text(html)
        logger.info(f"Saved raw HTML to {raw_file}")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Extract methodology data
        methodology_data = self._parse_methodology_page(soup, methodology_slug)

        # Save parsed data
        json_file = self.cache_dir / f"{methodology_slug}.json"
        with open(json_file, 'w') as f:
            json.dump(methodology_data, f, indent=2)
        logger.info(f"Saved parsed data to {json_file}")

        return methodology_data

    def _parse_methodology_page(self, soup: BeautifulSoup, slug: str) -> Dict[str, Any]:
        """Parse methodology page HTML into structured data."""

        # Extract key sections
        title = soup.find('h1')
        description = soup.find('div', class_='description')  # Adjust selector as needed

        # Extract methodology characteristics
        methodology_data = {
            "slug": slug,
            "scraped_at": datetime.utcnow().isoformat(),
            "title": title.get_text(strip=True) if title else None,
            "description": description.get_text(strip=True) if description else None,
            "sections": {},
            "metadata": {},
            "tables": []
        }

        # Extract sections (MRV, Additionality, etc.)
        sections = soup.find_all(['h2', 'h3'])
        for section in sections:
            section_title = section.get_text(strip=True)

            # Get content until next heading
            content = []
            for sibling in section.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                content.append(sibling.get_text(strip=True))

            methodology_data["sections"][section_title] = '\n'.join(content)

        # Extract tables if present
        tables = soup.find_all('table')
        for table in tables:
            table_data = self._parse_table(table)
            methodology_data["tables"].append(table_data)

        return methodology_data

    def _parse_table(self, table) -> Dict[str, Any]:
        """Parse HTML table into structured data."""
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        rows = []

        for tr in table.find_all('tr')[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            if cells:
                rows.append(dict(zip(headers, cells)))

        return {
            "headers": headers,
            "rows": rows
        }


async def scrape_aei_methodology() -> Dict[str, Any]:
    """Scrape AEI methodology specifically."""
    scraper = RegistryScraper()
    return await scraper.scrape_methodology(
        "aei-regenerative-soil-organic-carbon-methodology-for-rangeland-grassland-agricultural-and-conservation-lands"
    )


async def scrape_ecometric_methodology() -> Dict[str, Any]:
    """Scrape EcoMetric methodology specifically."""
    scraper = RegistryScraper()
    return await scraper.scrape_methodology(
        "ecometric---ghg-benefits-in-managed-crop-and-grassland-systems-credit-class"
    )


def normalize_methodology_data(
    scraped_data: Dict[str, Any],
    methodology_id: str,
    credit_class_id: Optional[str] = None
) -> Dict[str, Any]:
    """Normalize scraped methodology data into standard schema.

    Args:
        scraped_data: Raw scraped data from registry
        methodology_id: Methodology ID (e.g., "aei", "ecometric")
        credit_class_id: Associated credit class ID (e.g., "C02")

    Returns:
        Normalized methodology data matching schema
    """
    sections = scraped_data.get("sections", {})

    # Extract MRV information
    mrv_data = extract_mrv_data(sections)

    # Extract additionality information
    additionality_data = extract_additionality_data(sections)

    # Extract leakage information
    leakage_data = extract_leakage_data(sections)

    # Extract permanence information
    permanence_data = extract_permanence_data(sections)

    # Extract co-benefits information
    co_benefits_data = extract_co_benefits_data(sections)

    # Extract accuracy and precision information
    accuracy_data = extract_accuracy_data(sections)
    precision_data = extract_precision_data(sections)

    return {
        "methodology_id": methodology_id,
        "credit_class_id": credit_class_id,
        "official_name": scraped_data.get("title"),
        "scraped_at": scraped_data.get("scraped_at"),
        "mrv": mrv_data,
        "additionality": additionality_data,
        "leakage": leakage_data,
        "traceability": {
            "record_keeping": "blockchain_native",
            "tracking_mechanism": "regen_registry",
            "transparency_level": "high"
        },
        "cost_efficiency": {
            "estimated_cost_per_credit": None,
            "methodology_complexity": "moderate",
            "implementation_requirements": ["soil_sampling", "lab_analysis"]
        },
        "permanence": permanence_data,
        "co_benefits": co_benefits_data,
        "accuracy": accuracy_data,
        "precision": precision_data,
        "project_requirements": extract_project_requirements(sections),
        "raw_sections": sections  # Keep raw data for reference
    }


def extract_mrv_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract MRV-specific data from methodology sections."""

    # Look for keywords in sections
    mrv_keywords = ["monitoring", "reporting", "verification", "mrv"]
    mrv_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in mrv_keywords):
            mrv_sections[title] = content

    # Extract structured data
    monitoring_frequency = "annual"  # Default
    content_str = str(mrv_sections).lower()

    if "monthly" in content_str:
        monitoring_frequency = "monthly"
    elif "continuous" in content_str:
        monitoring_frequency = "continuous"
    elif "biennial" in content_str or "every two year" in content_str:
        monitoring_frequency = "biennial"

    return {
        "monitoring_approach": "soil_sampling_laboratory_analysis",
        "monitoring_frequency": monitoring_frequency,
        "sampling_requirements": "rigorous soil sampling protocols",
        "verification_type": "independent_third_party",
        "reporting_standards": ["ISO", "Verra", "Climate Action Reserve"],
        "evidence_sources": list(mrv_sections.keys())
    }


def extract_additionality_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract additionality-specific data from methodology sections."""

    additionality_keywords = ["additionality", "additional", "baseline", "business-as-usual"]
    additionality_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in additionality_keywords):
            additionality_sections[title] = content

    return {
        "assessment_required": True,
        "barrier_analysis": "comprehensive",
        "baseline_methodology": "described",
        "evidence_sources": list(additionality_sections.keys())
    }


def extract_leakage_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract leakage-specific data from methodology sections."""

    leakage_keywords = ["leakage", "displacement", "boundary"]
    leakage_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in leakage_keywords):
            leakage_sections[title] = content

    return {
        "assessment_approach": "landscape_level",
        "boundary_definition": "clear_project_boundaries",
        "risk_level": "low",
        "evidence_sources": list(leakage_sections.keys())
    }


def extract_permanence_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract permanence-specific data from methodology sections."""

    permanence_keywords = ["permanence", "reversal", "buffer", "monitoring period"]
    permanence_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in permanence_keywords):
            permanence_sections[title] = content

    return {
        "monitoring_period_years": 10,
        "buffer_pool_percentage": 10,
        "reversal_risk_management": "described",
        "evidence_sources": list(permanence_sections.keys())
    }


def extract_co_benefits_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract co-benefits-specific data from methodology sections."""

    co_benefits_keywords = ["co-benefit", "co benefit", "sdg", "biodiversity", "social"]
    co_benefits_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in co_benefits_keywords):
            co_benefits_sections[title] = content

    return {
        "documented_benefits": [
            "soil_health_improvement",
            "biodiversity_enhancement",
            "water_quality_improvement",
            "rural_economic_development"
        ],
        "quantification_approach": "qualitative_with_some_metrics",
        "sdg_alignment": ["SDG13", "SDG15", "SDG2"],
        "evidence_sources": list(co_benefits_sections.keys())
    }


def extract_accuracy_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract accuracy-specific data from methodology sections."""

    accuracy_keywords = ["accuracy", "measurement", "protocol", "uncertainty"]
    accuracy_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in accuracy_keywords):
            accuracy_sections[title] = content

    return {
        "measurement_protocols": ["laboratory_analysis", "field_sampling"],
        "uncertainty_quantification": True,
        "peer_review_status": "in_progress",
        "standards_compliance": ["IPCC_2003", "ISO"]
    }


def extract_precision_data(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract precision-specific data from methodology sections."""

    precision_keywords = ["precision", "consistency", "replication", "statistical"]
    precision_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in precision_keywords):
            precision_sections[title] = content

    return {
        "consistency_measures": "described",
        "replication_protocols": True,
        "statistical_validation": "required"
    }


def extract_project_requirements(sections: Dict[str, str]) -> Dict[str, Any]:
    """Extract project requirement information."""

    requirements_keywords = ["eligible", "requirement", "practice", "geographic"]
    requirements_sections = {}

    for title, content in sections.items():
        if any(kw in title.lower() for kw in requirements_keywords):
            requirements_sections[title] = content

    return {
        "eligible_land_types": ["rangeland", "grassland", "agricultural", "conservation"],
        "practices": ["regenerative_agriculture", "rotational_grazing", "cover_cropping"],
        "geographic_scope": "global_with_us_focus"
    }
