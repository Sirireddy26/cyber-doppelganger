"""
Cyber Doppelgänger - Application / Process Behavioural Features
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates derived system process dynamics and task-switching metrics.
STRICT PRIVACY GUARANTEE: Never inspects or stores window titles, browser URLs,
document names, file paths, command-line arguments, or typed commands.
Aggregates process metrics purely as high-level numerical counts.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any
import numpy as np


@dataclass
class ApplicationFeatures:
    """
    Privacy-safe numerical features representing system activity and multitasking rhythm.
    
    Feature definitions:
    - process_count: Total number of active processes enumerated in the OS (unit: count).
    - active_process_count: Number of processes executing with active CPU activity (unit: count).
    - application_switch_count: Number of foreground application context switches detected (unit: count).
    - process_activity_count: Number of process state checks / transitions observed (unit: count).
    - application_activity_duration: Active application engagement time in the window (unit: seconds).
    """
    process_count: int = 0
    active_process_count: int = 0
    application_switch_count: int = 0
    process_activity_count: int = 0
    application_activity_duration: float = 0.0

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


def calculate_application_features(
    process_count: int,
    active_process_count: int,
    switch_count: int,
    activity_checks: int,
    active_duration: float
) -> ApplicationFeatures:
    """
    Calculates derived application and process features.
    
    Parameters:
    - process_count: Total running processes in the system.
    - active_process_count: Running processes actively consuming CPU.
    - switch_count: Frequency of foreground process changes.
    - activity_checks: Total process sampling checkpoints executed.
    - active_duration: Estimated active application engagement time.
    
    Returns:
    - ApplicationFeatures dataclass populated with finite numerical features.
    """
    def _safe_float(val: float) -> float:
        return 0.0 if (np.isnan(val) or np.isinf(val)) else float(val)

    return ApplicationFeatures(
        process_count=max(0, int(process_count)),
        active_process_count=max(0, int(active_process_count)),
        application_switch_count=max(0, int(switch_count)),
        process_activity_count=max(0, int(activity_checks)),
        application_activity_duration=_safe_float(max(0.0, float(active_duration)))
    )
