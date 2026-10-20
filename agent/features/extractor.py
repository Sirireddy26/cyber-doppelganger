"""
Cyber Doppelgänger - Feature Extraction Interface
Phase 1 Foundation: Interface & schema definition.
Actual statistical aggregation algorithms are prepared for Phase 2 integration.
"""

from typing import List, Dict, Any
from agent.privacy.privacy_guard import PrivacyGuard

class FeatureExtractor:
    """Interface for converting raw event timestamps and kinematics into feature vectors."""

    FEATURE_SCHEMA = [
        "dwell_mean_ms", "dwell_std_ms", "dwell_median_ms",
        "flight_mean_ms", "flight_std_ms",
        "press_latency_mean_ms", "press_latency_std_ms",
        "mouse_velocity_mean", "mouse_velocity_max", "mouse_velocity_std",
        "mouse_accel_mean", "mouse_accel_std",
        "click_duration_mean_ms", "click_duration_std_ms",
        "keystroke_rate_hz", "mouse_event_rate_hz"
    ]

    @classmethod
    def get_feature_dimension(cls) -> int:
        return len(cls.FEATURE_SCHEMA)

    @classmethod
    def validate_features(cls, features: Dict[str, Any]) -> bool:
        """Ensures extracted features comply with privacy and numerical constraints."""
        return PrivacyGuard.is_feature_vector_compliant(features)
