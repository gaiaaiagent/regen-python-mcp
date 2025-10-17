"""Real data fixture manager for tests.

This module manages capture, caching, and versioning of real Regen Network
blockchain data for use in tests. Following the principle: NO MOCK DATA.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class FixtureManager:
    """Manages real blockchain data fixtures with versioning and TTL."""

    def __init__(self, fixtures_dir: Optional[Path] = None):
        """Initialize fixture manager.

        Args:
            fixtures_dir: Directory to store fixtures. Defaults to data/test_fixtures/
        """
        if fixtures_dir is None:
            # Default to data/test_fixtures in project root
            project_root = Path(__file__).parent.parent.parent
            fixtures_dir = project_root / "data" / "test_fixtures"

        self.fixtures_dir = Path(fixtures_dir)
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.fixtures_dir / "metadata.json"
        self._ensure_metadata()

    def _ensure_metadata(self) -> None:
        """Ensure metadata file exists."""
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> Dict[str, Any]:
        """Load fixture metadata."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
            return {}

    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save fixture metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _update_metadata(self, fixture_name: str, info: Dict[str, Any]) -> None:
        """Update metadata for a fixture."""
        metadata = self._load_metadata()
        metadata[fixture_name] = info
        self._save_metadata(metadata)

    def _is_fresh(self, capture_time_str: str, ttl_days: int) -> bool:
        """Check if cached data is still fresh."""
        try:
            capture_time = datetime.fromisoformat(capture_time_str)
            age = datetime.now() - capture_time
            return age < timedelta(days=ttl_days)
        except Exception as e:
            logger.warning(f"Failed to parse capture time: {e}")
            return False

    async def get_or_capture(
        self,
        fixture_name: str,
        capture_func: Callable,
        ttl_days: int = 30,
        category: str = "client",
        force_refresh: bool = False
    ) -> Any:
        """Get cached fixture or capture fresh data from blockchain.

        Args:
            fixture_name: Name of the fixture (e.g., "credit_types")
            capture_func: Async function to capture fresh data
            ttl_days: Time-to-live in days before data is considered stale
            category: Fixture category (client, tools, integration)
            force_refresh: Force capture fresh data even if cached

        Returns:
            Real blockchain data (either cached or freshly captured)
        """
        # Build path
        category_dir = self.fixtures_dir / category
        category_dir.mkdir(exist_ok=True)
        fixture_path = category_dir / f"{fixture_name}.json"

        # Check if we can use cached data
        if not force_refresh and fixture_path.exists():
            metadata = self._load_metadata()
            fixture_meta = metadata.get(f"{category}/{fixture_name}", {})
            capture_time = fixture_meta.get("captured_at")

            if capture_time and self._is_fresh(capture_time, ttl_days):
                logger.info(f"Using cached fixture: {category}/{fixture_name}")
                with open(fixture_path, 'r') as f:
                    return json.load(f)
            else:
                logger.info(f"Fixture stale, capturing fresh: {category}/{fixture_name}")
        else:
            logger.info(f"Capturing fresh data for: {category}/{fixture_name}")

        # Capture fresh data from blockchain
        try:
            data = await capture_func()
        except Exception as e:
            logger.error(f"Failed to capture data for {fixture_name}: {e}")
            # If we have stale cached data, use it as fallback
            if fixture_path.exists():
                logger.warning(f"Using stale cache as fallback: {fixture_name}")
                with open(fixture_path, 'r') as f:
                    return json.load(f)
            raise

        # Save fixture
        with open(fixture_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        # Update metadata
        self._update_metadata(f"{category}/{fixture_name}", {
            "captured_at": datetime.now().isoformat(),
            "ttl_days": ttl_days,
            "source": "real_blockchain",
            "network": "regen-1",
            "notes": f"Captured via {capture_func.__name__ if hasattr(capture_func, '__name__') else 'capture_func'}"
        })

        logger.info(f"Captured and saved: {category}/{fixture_name} ({len(json.dumps(data))} bytes)")
        return data

    def invalidate(self, fixture_name: str, category: str = "client") -> None:
        """Invalidate a cached fixture, forcing fresh capture on next access.

        Args:
            fixture_name: Name of the fixture to invalidate
            category: Fixture category
        """
        fixture_path = self.fixtures_dir / category / f"{fixture_name}.json"
        if fixture_path.exists():
            fixture_path.unlink()
            logger.info(f"Invalidated fixture: {category}/{fixture_name}")

        # Update metadata
        metadata = self._load_metadata()
        key = f"{category}/{fixture_name}"
        if key in metadata:
            del metadata[key]
            self._save_metadata(metadata)

    def list_fixtures(self) -> Dict[str, Any]:
        """List all cached fixtures with metadata.

        Returns:
            Dictionary mapping fixture names to their metadata
        """
        return self._load_metadata()

    def get_fixture_age(self, fixture_name: str, category: str = "client") -> Optional[timedelta]:
        """Get the age of a cached fixture.

        Args:
            fixture_name: Name of the fixture
            category: Fixture category

        Returns:
            Age as timedelta, or None if fixture doesn't exist
        """
        metadata = self._load_metadata()
        fixture_meta = metadata.get(f"{category}/{fixture_name}")

        if not fixture_meta:
            return None

        capture_time_str = fixture_meta.get("captured_at")
        if not capture_time_str:
            return None

        try:
            capture_time = datetime.fromisoformat(capture_time_str)
            return datetime.now() - capture_time
        except Exception:
            return None


# Global fixture manager instance
_fixture_manager: Optional[FixtureManager] = None


def get_fixture_manager() -> FixtureManager:
    """Get global fixture manager instance (singleton)."""
    global _fixture_manager
    if _fixture_manager is None:
        _fixture_manager = FixtureManager()
    return _fixture_manager
