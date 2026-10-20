"""
Cyber Doppelgänger - Feature Preprocessing & Schema Validation
Safe Adaptive Behavioural Identity & Continuous User Verification

Defines approved numerical feature definitions, handles normalization,
guards against NaN/Infinity, rejects forbidden surveillance content,
and enforces fixed, deterministic feature ordering.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger("cyber-doppelganger.ml")

# Canonical list of approved privacy-safe numerical features (Order MUST remain stable)
APPROVED_KEYBOARD_FEATURES: List[str] = [
    "total_key_events",
    "mean_key_interval",
    "median_key_interval",
    "key_interval_std",
    "minimum_key_interval",
    "maximum_key_interval",
    "typing_speed",
    "pause_count",
    "mean_pause_duration",
    "longest_pause",
    "typing_activity_duration"
]

APPROVED_MOUSE_FEATURES: List[str] = [
    "movement_distance",
    "mean_mouse_speed",
    "mouse_speed_std",
    "mean_acceleration",
    "click_count",
    "left_click_count",
    "right_click_count",
    "middle_click_count",
    "mean_click_interval",
    "click_interval_std",
    "scroll_count",
    "positive_scroll_count",
    "negative_scroll_count",
    "mouse_active_duration"
]

APPROVED_SESSION_FEATURES: List[str] = [
    "session_duration",
    "active_duration",
    "idle_duration",
    "active_idle_ratio",
    "activity_density",
    "keyboard_activity_duration",
    "mouse_activity_duration"
]

APPROVED_APPLICATION_FEATURES: List[str] = [
    "process_count",
    "active_process_count",
    "application_switch_count",
    "process_activity_count",
    "application_activity_duration"
]

ALL_FEATURE_KEYS: List[str] = (
    APPROVED_KEYBOARD_FEATURES +
    APPROVED_MOUSE_FEATURES +
    APPROVED_SESSION_FEATURES +
    APPROVED_APPLICATION_FEATURES
)

# Forbidden surveillance field substrings
FORBIDDEN_CONTENT_TERMS: List[str] = [
    "typed_text", "keystroke", "key_name", "char", "text", "password",
    "screenshot", "screen_image", "clipboard", "browser_url", "url",
    "window_title", "document_content", "raw_key", "key_down", "key_up"
]

SUPPORTED_SCHEMA_VERSIONS = {"1.0", "2.0"}


class FeaturePreprocessingError(ValueError):
    """Raised when incoming features violate privacy, numeric validity, or schema constraints."""
    pass


class FeaturePreprocessor:
    """
    Validates, extracts, and standardizes behavioral feature vectors.
    Guarantees:
    - Zero data leakage (fitting strictly on training partitions).
    - Deterministic feature ordering.
    - Strict rejection of NaN, Infinity, and surveillance content.
    - Robust handling of missing non-critical metrics.
    """

    def __init__(self, schema_version: str = "2.0"):
        self.schema_version = schema_version
        self.feature_names = list(ALL_FEATURE_KEYS)
        self.scaler: Optional[StandardScaler] = None
        self.is_fitted = False

    def validate_raw_snapshot(self, snapshot_dict: Dict[str, Any]) -> None:
        """
        Validates structure, privacy compliance, and schema version.
        Raises FeaturePreprocessingError on violation.
        """
        if not isinstance(snapshot_dict, dict):
            raise FeaturePreprocessingError("Snapshot must be a valid JSON dictionary.")

        # 1. Schema version check
        schema_ver = str(snapshot_dict.get("schema_version", self.schema_version))
        if schema_ver not in SUPPORTED_SCHEMA_VERSIONS:
            raise FeaturePreprocessingError(
                f"Unsupported schema_version: '{schema_ver}'. Supported: {SUPPORTED_SCHEMA_VERSIONS}"
            )

        # 2. Strict privacy check: Reject prohibited surveillance fields anywhere in keys
        def _check_keys_recursive(d: Any):
            if isinstance(d, dict):
                for k, v in d.items():
                    k_lower = str(k).lower()
                    for term in FORBIDDEN_CONTENT_TERMS:
                        if term in k_lower:
                            raise FeaturePreprocessingError(
                                f"Privacy violation: Snapshot contains prohibited field '{k}'."
                            )
                    _check_keys_recursive(v)
            elif isinstance(d, list):
                for item in d:
                    _check_keys_recursive(item)

        _check_keys_recursive(snapshot_dict)

    def extract_feature_vector(self, snapshot_dict: Dict[str, Any]) -> np.ndarray:
        """
        Extracts 1D numpy array of numerical features in canonical order.
        Accepts both nested structure (snapshot['keyboard']['mean_key_interval'])
        or flat structure (snapshot['mean_key_interval']).
        """
        self.validate_raw_snapshot(snapshot_dict)

        # Build lookup table from snapshot
        flat_lookup: Dict[str, Any] = {}

        # If nested under 'features' or category names
        root_data = snapshot_dict.get("features", snapshot_dict)
        for cat in ["keyboard", "mouse", "session", "application"]:
            sub = root_data.get(cat, {})
            if isinstance(sub, dict):
                for k, v in sub.items():
                    flat_lookup[k] = v

        # Also pull top-level entries
        for k, v in root_data.items():
            if k not in ["keyboard", "mouse", "session", "application"]:
                flat_lookup[k] = v

        values: List[float] = []
        for feat in self.feature_names:
            val = flat_lookup.get(feat, 0.0)
            if val is None:
                val = 0.0

            try:
                f_val = float(val)
            except (ValueError, TypeError):
                raise FeaturePreprocessingError(f"Feature '{feat}' cannot be converted to float: {val}")

            if np.isnan(f_val) or np.isinf(f_val):
                raise FeaturePreprocessingError(f"Feature '{feat}' contains non-finite value: {f_val}")

            values.append(f_val)

        return np.array(values, dtype=np.float64)

    def extract_feature_dict(self, snapshot_dict: Dict[str, Any]) -> Dict[str, float]:
        """Extracts validated dictionary mapping feature names to floats."""
        vec = self.extract_feature_vector(snapshot_dict)
        return {k: float(vec[idx]) for idx, k in enumerate(self.feature_names)}

    def fit(self, snapshots: List[Dict[str, Any]]) -> "FeaturePreprocessor":
        """
        Fits StandardScaler on training snapshots.
        """
        if not snapshots:
            raise FeaturePreprocessingError("Cannot fit FeaturePreprocessor on empty snapshot list.")

        vectors = [self.extract_feature_vector(s) for s in snapshots]
        matrix = np.vstack(vectors)

        self.scaler = StandardScaler()
        self.scaler.fit(matrix)
        self.is_fitted = True
        return self

    def transform(self, snapshots: List[Dict[str, Any]]) -> np.ndarray:
        """
        Transforms snapshots into scaled feature matrix.
        """
        if not self.is_fitted or self.scaler is None:
            raise FeaturePreprocessingError("Preprocessor must be fitted before transforming.")

        vectors = [self.extract_feature_vector(s) for s in snapshots]
        matrix = np.vstack(vectors)
        return self.scaler.transform(matrix)

    def fit_transform(self, snapshots: List[Dict[str, Any]]) -> np.ndarray:
        return self.fit(snapshots).transform(snapshots)

    def transform_single(self, snapshot_dict: Dict[str, Any]) -> np.ndarray:
        """
        Transforms a single snapshot dictionary into a 2D scaled row vector (1, N).
        """
        if not self.is_fitted or self.scaler is None:
            raise FeaturePreprocessingError("Preprocessor must be fitted before transforming.")

        vec = self.extract_feature_vector(snapshot_dict).reshape(1, -1)
        return self.scaler.transform(vec)

    def save(self, filepath: str) -> None:
        """Saves fitted preprocessor state using joblib."""
        state = {
            "schema_version": self.schema_version,
            "feature_names": self.feature_names,
            "scaler": self.scaler,
            "is_fitted": self.is_fitted
        }
        joblib.dump(state, filepath)

    @classmethod
    def load(cls, filepath: str) -> "FeaturePreprocessor":
        """Loads fitted preprocessor state using joblib."""
        state = joblib.load(filepath)
        preprocessor = cls(schema_version=state.get("schema_version", "2.0"))
        preprocessor.feature_names = state["feature_names"]
        preprocessor.scaler = state["scaler"]
        preprocessor.is_fitted = state["is_fitted"]
        return preprocessor
