"""
Cyber Doppelgänger - Session Behavioural Features
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates session activity, engagement density, and idle durations.
STRICT PRIVACY GUARANTEE: Never tracks document titles, URLs, or content.
Maintains strictly temporal metadata about active vs. idle interaction states.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any
import math
import numpy as np


@dataclass
class SessionFeatures:
    """
    Privacy-safe numerical features representing interaction session continuity.
    
    Feature definitions:
    - session_duration: Total elapsed seconds since monitoring session initiated (unit: seconds).
    - active_duration: Total seconds within the current window showing user interaction (unit: seconds).
    - idle_duration: Total seconds within the window without interaction (unit: seconds).
    - active_idle_ratio: Ratio of active duration to idle duration (unit: dimensionless).
    - activity_density: Proportion of window containing active engagement (range: [0.0, 1.0]).
    - keyboard_activity_duration: Seconds within window spent actively typing (unit: seconds).
    - mouse_activity_duration: Seconds within window spent in active mouse movement/clicking (unit: seconds).
    """
    session_duration: float = 0.0
    active_duration: float = 0.0
    idle_duration: float = 0.0
    active_idle_ratio: float = 0.0
    activity_density: float = 0.0
    keyboard_activity_duration: float = 0.0
    mouse_activity_duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Returns clean dictionary with guaranteed finite floating-point numbers."""
        raw = asdict(self)
        clean = {}
        for k, v in raw.items():
            if isinstance(v, float):
                clean[k] = 0.0 if (np.isnan(v) or np.isinf(v)) else round(float(v), 4)
            else:
                clean[k] = v
        return clean


def calculate_session_features(
    session_elapsed: float,
    window_duration: float,
    keyboard_active_sec: float,
    mouse_active_sec: float,
    idle_threshold_seconds: float = 60.0
) -> SessionFeatures:
    """
    Calculates derived session engagement features for an aggregation window.
    
    Parameters:
    - session_elapsed: Total seconds elapsed since agent process launched.
    - window_duration: Aggregation window length in seconds.
    - keyboard_active_sec: Active typing duration in seconds.
    - mouse_active_sec: Active mouse movement/click duration in seconds.
    - idle_threshold_seconds: Configured inactivity threshold in seconds.
    
    Returns:
    - SessionFeatures dataclass populated with finite numerical features.
    """
    win_sec = max(1.0, float(window_duration))
    kb_act = max(0.0, float(keyboard_active_sec))
    mo_act = max(0.0, float(mouse_active_sec))

    # Active duration is bounded by the window length (union of active modalities)
    # Estimate active interaction as max or capped sum
    active_dur = min(win_sec, max(kb_act, mo_act, min(win_sec, kb_act + mo_act * 0.5)))
    idle_dur = max(0.0, win_sec - active_dur)

    # Active/idle ratio: safe calculation avoiding division by zero
    if idle_dur > 0.01:
        ratio = active_dur / idle_dur
    else:
        # If user was 100% active, represent ratio safely as active_dur
        ratio = active_dur if active_dur > 0.0 else 0.0

    # Activity density: active fraction of the aggregation window
    density = max(0.0, min(1.0, active_dur / win_sec))

    def _safe_float(val: float) -> float:
        return 0.0 if (np.isnan(val) or np.isinf(val)) else float(val)

    return SessionFeatures(
        session_duration=_safe_float(session_elapsed),
        active_duration=_safe_float(active_dur),
        idle_duration=_safe_float(idle_dur),
        active_idle_ratio=_safe_float(ratio),
        activity_density=_safe_float(density),
        keyboard_activity_duration=_safe_float(kb_act),
        mouse_activity_duration=_safe_float(mo_act)
    )
