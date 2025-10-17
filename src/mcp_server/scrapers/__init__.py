"""Scrapers for external methodology documents.

This module provides scrapers for extracting methodology information
from the Regen Registry and other external sources.
"""

from .registry_scraper import (
    RegistryScraper,
    scrape_aei_methodology,
    scrape_ecometric_methodology
)

__all__ = [
    "RegistryScraper",
    "scrape_aei_methodology",
    "scrape_ecometric_methodology"
]
