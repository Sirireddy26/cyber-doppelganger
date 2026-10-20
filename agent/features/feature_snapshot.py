"""
Cyber Doppelgänger - Feature Snapshot Model
Safe Adaptive Behavioural Identity & Continuous User Verification

Defines the central schema for aggregated behavioural feature windows.
Guarantees strict numerical integrity (zero NaN/infinity) and privacy compliance.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Dict, Any, Optional
import math
import numpy as np

from agent.features.keyboard_features import KeyboardFeatures
from agent.features.mouse_features import MouseFeatures
from agent.features.session_features import SessionFeatures
from agent.features.application_features import ApplicationFeatures


def _sanitize_dict(obj: Any) -> Any:
    """Recursively replaces NaN and infinite values with 0.0 or 0."""
    if isinstance(obj, dict):
        return {k: _sanitize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_dict(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj) or np.isnan(obj) or np.isinf(obj):
            return 0.0
        return round(float(obj), 4)
    return obj


@dataclass
class FeatureSnapshot:
    """
    Central feature snapshot representing aggregated behavioural signals over a window.
    
    Attributes:
    - timestamp: ISO 8601 UTC timestamp of window completion.
    - window_duration_seconds: Window length in seconds (e.g., 60).
    - device_id: Anonymous identifier of workstation.
    - user_id: Configured identity pseudonym.
    - keyboard: Keyboard timing features.
    - mouse: Mouse movement and interaction features.
    - session: Session continuity and idle features.
    - application: System load and switching features.
    """
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    window_duration_seconds: int = 60
    device_id: str = "local-workstation-01"
    user_id: str = "default-user"
    schema_version: str = "2.0"
    keyboard: KeyboardFeatures = field(default_factory=KeyboardFeatures)
    mouse: MouseFeatures = field(default_factory=MouseFeatures)
    session: SessionFeatures = field(default_factory=SessionFeatures)
    application: ApplicationFeatures = field(default_factory=ApplicationFeatures)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes snapshot to dictionary with guaranteed finite values."""
        raw = {
            "timestamp": self.timestamp,
            "window_duration_seconds": self.window_duration_seconds,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "schema_version": self.schema_version,
            "keyboard": self.keyboard.to_dict(),
            "mouse": self.mouse.to_dict(),
            "session": self.session.to_dict(),
            "application": self.application.to_dict()
        }
        return _sanitize_dict(raw)

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serializes snapshot to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureSnapshot":
        """Reconstructs a FeatureSnapshot from a dictionary."""
        kb_data = data.get("keyboard", {})
        mo_data = data.get("mouse", {})
        se_data = data.get("session", {})
        ap_data = data.get("application", {})

        return cls(
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            window_duration_seconds=data.get("window_duration_seconds", 60),
            device_id=data.get("device_id", "local-workstation-01"),
            user_id=data.get("user_id", "default-user"),
            keyboard=KeyboardFeatures(**kb_data) if kb_data else KeyboardFeatures(),
            mouse=MouseFeatures(**mo_data) if mo_data else MouseFeatures(),
            session=SessionFeatures(**se_data) if se_data else SessionFeatures(),
            application=ApplicationFeatures(**ap_data) if ap_data else ApplicationFeatures()
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FeatureSnapshot":
        """Parses a FeatureSnapshot from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
