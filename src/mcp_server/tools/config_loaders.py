"""Configuration loaders for externalized data sources.

This module provides loaders for YAML/JSON configuration files that replace
hardcoded values throughout the scoring system.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..models.methodology import BuyerPreset

logger = logging.getLogger(__name__)


# ============================================================================
# PATH RESOLUTION
# ============================================================================

def get_config_dir() -> Path:
    """Get the config directory path."""
    # Navigate from this file to project root, then to config/
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent.parent
    config_dir = project_root / "config"

    if not config_dir.exists():
        raise FileNotFoundError(
            f"Config directory not found: {config_dir}. "
            "Please ensure config/ directory exists in project root."
        )

    return config_dir


def get_data_dir() -> Path:
    """Get the data directory path."""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent.parent
    data_dir = project_root / "data"

    if not data_dir.exists():
        # Create if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


# ============================================================================
# BUYER PRESET LOADER
# ============================================================================

class BuyerPresetLoader:
    """Loads buyer presets from YAML configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize loader.

        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir is None:
            config_dir = get_config_dir()

        self.presets_dir = config_dir / "buyer_presets"

        if not self.presets_dir.exists():
            raise FileNotFoundError(
                f"Buyer presets directory not found: {self.presets_dir}"
            )

        self._cache: Dict[str, BuyerPreset] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all buyer preset YAML files."""
        logger.info(f"Loading buyer presets from {self.presets_dir}")

        for yaml_file in self.presets_dir.glob("*.yaml"):
            if yaml_file.stem == "README":
                continue

            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                # Validate required fields
                self._validate_preset_data(data, yaml_file)

                # Create BuyerPreset instance
                preset = BuyerPreset(
                    preset_id=data["preset_id"],
                    preset_name=data["preset_name"],
                    description=data.get("description", ""),
                    criteria_weights=data["criteria_weights"],
                    focus_areas=data.get("focus_areas", []),
                    target_buyers=data.get("target_buyers", [])
                )

                # Validate weights sum to 1.0
                total_weight = sum(preset.criteria_weights.values())
                if not (0.99 <= total_weight <= 1.01):
                    raise ValueError(
                        f"Criteria weights in {yaml_file.name} sum to {total_weight}, not 1.0"
                    )

                self._cache[preset.preset_id] = preset
                logger.info(f"Loaded buyer preset: {preset.preset_id}")

            except Exception as e:
                logger.error(f"Error loading buyer preset {yaml_file.name}: {e}")
                raise

        logger.info(f"Loaded {len(self._cache)} buyer presets")

    def _validate_preset_data(self, data: dict, file_path: Path) -> None:
        """Validate preset data structure.

        Args:
            data: Parsed YAML data
            file_path: Path to YAML file (for error messages)

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["preset_id", "preset_name", "criteria_weights"]
        for field in required_fields:
            if field not in data:
                raise ValueError(
                    f"Missing required field '{field}' in {file_path.name}"
                )

        # Validate all 9 criteria are present
        required_criteria = [
            "mrv", "additionality", "leakage", "traceability",
            "cost_efficiency", "permanence", "co_benefits",
            "accuracy", "precision"
        ]

        weights = data["criteria_weights"]
        for criterion in required_criteria:
            if criterion not in weights:
                raise ValueError(
                    f"Missing criterion '{criterion}' in {file_path.name}"
                )

            # Validate weight is numeric and in range [0, 1]
            weight = weights[criterion]
            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Weight for '{criterion}' must be numeric in {file_path.name}"
                )
            if not (0.0 <= weight <= 1.0):
                raise ValueError(
                    f"Weight for '{criterion}' must be between 0.0 and 1.0 in {file_path.name}"
                )

    def get_preset(self, preset_id: str) -> Optional[BuyerPreset]:
        """Get buyer preset by ID.

        Args:
            preset_id: Preset identifier

        Returns:
            BuyerPreset instance or None if not found
        """
        return self._cache.get(preset_id)

    def get_all_presets(self) -> Dict[str, BuyerPreset]:
        """Get all loaded buyer presets.

        Returns:
            Dictionary mapping preset_id to BuyerPreset
        """
        return self._cache.copy()

    def list_preset_ids(self) -> List[str]:
        """Get list of all preset IDs.

        Returns:
            List of preset identifiers
        """
        return list(self._cache.keys())

    def reload(self) -> None:
        """Reload all presets from disk."""
        self._cache.clear()
        self._load_all()


# ============================================================================
# SCORING THRESHOLDS LOADER
# ============================================================================

class ScoringThresholdsLoader:
    """Loads scoring thresholds from YAML configuration files."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize loader.

        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir is None:
            config_dir = get_config_dir()

        self.thresholds_dir = config_dir / "scoring_thresholds"
        self._cache: Dict[str, dict] = {}

    def _load_yaml(self, filename: str) -> dict:
        """Load a YAML file from thresholds directory.

        Args:
            filename: YAML filename

        Returns:
            Parsed YAML data
        """
        file_path = self.thresholds_dir / filename

        if not file_path.exists():
            logger.warning(f"Threshold file not found: {filename}")
            return {}

        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            logger.info(f"Loaded thresholds from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading thresholds from {filename}: {e}")
            return {}

    def get_mrv_thresholds(self) -> dict:
        """Get MRV scoring thresholds."""
        if "mrv" not in self._cache:
            self._cache["mrv"] = self._load_yaml("mrv_thresholds.yaml")
        return self._cache["mrv"]

    def get_cost_efficiency_thresholds(self) -> dict:
        """Get cost efficiency scoring thresholds."""
        if "cost" not in self._cache:
            self._cache["cost"] = self._load_yaml("cost_efficiency_thresholds.yaml")
        return self._cache["cost"]

    def get_score_label_mappings(self) -> dict:
        """Get score label mappings (0-3 scale)."""
        if "labels" not in self._cache:
            self._cache["labels"] = self._load_yaml("score_label_mappings.yaml")
        return self._cache["labels"]

    def get_batch_frequency_thresholds(self) -> dict:
        """Get batch frequency thresholds."""
        if "batch_freq" not in self._cache:
            self._cache["batch_freq"] = self._load_yaml("batch_frequency_thresholds.yaml")
        return self._cache["batch_freq"]


# ============================================================================
# METHODOLOGY TYPE REGISTRY
# ============================================================================

class MethodologyTypeRegistry:
    """Registry of methodology type configurations."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize registry.

        Args:
            config_dir: Optional custom config directory path
        """
        if config_dir is None:
            config_dir = get_config_dir()

        self.types_dir = config_dir / "methodology_types"
        self._type_cache: Dict[str, dict] = {}
        self._registry_cache: Optional[dict] = None

    def _load_registry(self) -> dict:
        """Load type registry configuration."""
        if self._registry_cache is not None:
            return self._registry_cache

        registry_file = self.types_dir / "type_registry.yaml"

        if not registry_file.exists():
            logger.warning("Type registry file not found, using defaults")
            # Fallback to basic registry
            self._registry_cache = {
                "methodology_types": ["soil_carbon", "reforestation", "blue_carbon", "biodiversity"],
                "credit_class_mappings": {
                    "C01": "reforestation",
                    "C02": "soil_carbon",
                    "C03": "blue_carbon",
                    "BIO": "biodiversity"
                },
                "default_type": "unknown"
            }
            return self._registry_cache

        try:
            with open(registry_file, 'r') as f:
                self._registry_cache = yaml.safe_load(f)
            logger.info("Loaded methodology type registry")
            return self._registry_cache
        except Exception as e:
            logger.error(f"Error loading type registry: {e}")
            return {}

    def _load_type_config(self, type_id: str) -> dict:
        """Load configuration for a specific methodology type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Type configuration dictionary
        """
        if type_id in self._type_cache:
            return self._type_cache[type_id]

        config_file = self.types_dir / f"{type_id}.yaml"

        if not config_file.exists():
            logger.warning(f"Type config not found: {type_id}")
            self._type_cache[type_id] = {}
            return {}

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            self._type_cache[type_id] = config
            logger.info(f"Loaded type config: {type_id}")
            return config
        except Exception as e:
            logger.error(f"Error loading type config {type_id}: {e}")
            self._type_cache[type_id] = {}
            return {}

    def get_type_from_credit_class(self, credit_class_id: str) -> str:
        """Determine methodology type from credit class ID.

        Args:
            credit_class_id: Credit class ID (e.g., "C02")

        Returns:
            Methodology type identifier
        """
        registry = self._load_registry()

        # Try exact mapping first
        mappings = registry.get("credit_class_mappings", {})
        if credit_class_id in mappings:
            return mappings[credit_class_id]

        # Try pattern matching if available
        if "patterns" in mappings:
            import re
            for pattern_rule in mappings["patterns"]:
                if re.match(pattern_rule["pattern"], credit_class_id):
                    return pattern_rule["type"]

        # Default
        return registry.get("default_type", "unknown")

    def get_type_config(self, type_id: str) -> dict:
        """Get full configuration for a methodology type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Type configuration dictionary
        """
        return self._load_type_config(type_id)

    def get_permanence_config(self, type_id: str) -> dict:
        """Get permanence configuration for a type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Permanence configuration dictionary
        """
        config = self.get_type_config(type_id)
        return config.get("permanence", {})

    def get_accuracy_config(self, type_id: str) -> dict:
        """Get accuracy configuration for a type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Accuracy configuration dictionary
        """
        config = self.get_type_config(type_id)
        return config.get("accuracy", {})

    def get_leakage_config(self, type_id: str) -> dict:
        """Get leakage configuration for a type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Leakage configuration dictionary
        """
        config = self.get_type_config(type_id)
        return config.get("leakage", {})

    def get_co_benefits_config(self, type_id: str) -> dict:
        """Get co-benefits configuration for a type.

        Args:
            type_id: Methodology type identifier

        Returns:
            Co-benefits configuration dictionary
        """
        config = self.get_type_config(type_id)
        return config.get("co_benefits", {})


# ============================================================================
# GLOBAL SINGLETON INSTANCES
# ============================================================================

# These will be initialized on first import
_buyer_preset_loader: Optional[BuyerPresetLoader] = None
_scoring_thresholds: Optional[ScoringThresholdsLoader] = None
_type_registry: Optional[MethodologyTypeRegistry] = None


def get_buyer_preset_loader() -> BuyerPresetLoader:
    """Get global buyer preset loader instance."""
    global _buyer_preset_loader
    if _buyer_preset_loader is None:
        _buyer_preset_loader = BuyerPresetLoader()
    return _buyer_preset_loader


def get_scoring_thresholds() -> ScoringThresholdsLoader:
    """Get global scoring thresholds loader instance."""
    global _scoring_thresholds
    if _scoring_thresholds is None:
        _scoring_thresholds = ScoringThresholdsLoader()
    return _scoring_thresholds


def get_type_registry() -> MethodologyTypeRegistry:
    """Get global methodology type registry instance."""
    global _type_registry
    if _type_registry is None:
        _type_registry = MethodologyTypeRegistry()
    return _type_registry


def reload_all_configs() -> None:
    """Reload all configurations from disk."""
    global _buyer_preset_loader, _scoring_thresholds, _type_registry

    if _buyer_preset_loader is not None:
        _buyer_preset_loader.reload()

    # Reset others to force reload on next access
    _scoring_thresholds = None
    _type_registry = None

    logger.info("Reloaded all configurations")
