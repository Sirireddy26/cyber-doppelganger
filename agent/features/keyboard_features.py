"""
Cyber Doppelgänger - Keyboard Behavioural Features
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates derived numerical timing statistics from anonymous keystroke timestamps.
STRICT PRIVACY GUARANTEE: Never receives, handles, or stores typed characters,
key codes, key names, or passwords.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class KeyboardFeatures:
    """
    Privacy-safe numerical features derived from keystroke event timing.
    
    Feature definitions:
    - total_key_events: Total number of keyboard events recorded during the window (unit: count).
    - mean_key_interval: Mean time between consecutive keystroke events (unit: seconds).
    - median_key_interval: Median time between consecutive keystroke events (unit: seconds).
    - key_interval_std: Standard deviation of intervals between consecutive events (unit: seconds).
    - minimum_key_interval: Shortest observed inter-key interval (unit: seconds).
    - maximum_key_interval: Longest observed inter-key interval (unit: seconds).
    - typing_speed: Event-rate typing frequency (events per active second, NOT words-per-minute).
    - pause_count: Number of inter-event gaps exceeding the configured pause threshold (unit: count).
    - mean_pause_duration: Mean duration of detected pauses (unit: seconds).
    - longest_pause: Longest single pause duration observed in the window (unit: seconds).
    - typing_activity_duration: Sum of active typing duration within the window (unit: seconds).
    """
    total_key_events: int = 0
    mean_key_interval: float = 0.0
    median_key_interval: float = 0.0
    key_interval_std: float = 0.0
    minimum_key_interval: float = 0.0
    maximum_key_interval: float = 0.0
    typing_speed: float = 0.0
    pause_count: int = 0
    mean_pause_duration: float = 0.0
    longest_pause: float = 0.0
    typing_activity_duration: float = 0.0

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


def calculate_keyboard_features(
    timestamps: List[float],
    pause_threshold_seconds: float = 1.0
) -> KeyboardFeatures:
    """
    Calculates derived keyboard timing features from a sequence of monotonic timestamps.
    
    Parameters:
    - timestamps: Monotonically increasing list of event timestamps (in seconds).
    - pause_threshold_seconds: Interval threshold above which an inter-key gap is classified as a pause.
    
    Returns:
    - KeyboardFeatures dataclass populated with valid, finite numerical features.
    """
    if not timestamps or len(timestamps) == 0:
        return KeyboardFeatures()

    total_events = len(timestamps)

    if total_events == 1:
        return KeyboardFeatures(
            total_key_events=1,
            mean_key_interval=0.0,
            median_key_interval=0.0,
            key_interval_std=0.0,
            minimum_key_interval=0.0,
            maximum_key_interval=0.0,
            typing_speed=0.0,
            pause_count=0,
            mean_pause_duration=0.0,
            longest_pause=0.0,
            typing_activity_duration=0.0
        )

    # Sort timestamps to ensure monotonicity in case of asynchronous thread insertion
    sorted_ts = sorted(timestamps)
    raw_intervals = [sorted_ts[i] - sorted_ts[i - 1] for i in range(1, len(sorted_ts))]

    # Filter out invalid or negative intervals due to any edge-case clock anomaly
    intervals = [dt for dt in raw_intervals if dt >= 0.0]

    if not intervals:
        return KeyboardFeatures(total_key_events=total_events)

    # Calculate intervals statistics
    arr = np.array(intervals, dtype=float)
    mean_interval = float(np.mean(arr))
    median_interval = float(np.median(arr))
    interval_std = float(np.std(arr)) if len(arr) > 1 else 0.0
    min_interval = float(np.min(arr))
    max_interval = float(np.max(arr))

    # Detect pauses: intervals exceeding pause_threshold_seconds
    pauses = [dt for dt in intervals if dt >= pause_threshold_seconds]
    pause_count = len(pauses)
    mean_pause_dur = float(np.mean(pauses)) if pauses else 0.0
    longest_pause = float(np.max(pauses)) if pauses else 0.0

    # Total typing span from first to last event
    total_span = sorted_ts[-1] - sorted_ts[0]

    # Active typing duration = total span minus non-active pause duration
    total_pause_time = sum(pauses) if pauses else 0.0
    active_duration = max(0.0, total_span - total_pause_time)

    # If all time was pauses or active_duration is very small, use span or small delta
    if active_duration <= 0.0:
        # If there are events within sub-threshold intervals, sum them
        non_pause_intervals = [dt for dt in intervals if dt < pause_threshold_seconds]
        active_duration = sum(non_pause_intervals) if non_pause_intervals else 0.1

    # Typing speed is an EVENT-RATE METRIC (events per active second), NOT words-per-minute (WPM)
    typing_speed = float(total_events / active_duration) if active_duration > 0.0 else 0.0

    # Guard against NaN/inf
    def _safe_float(val: float) -> float:
        return 0.0 if (np.isnan(val) or np.isinf(val)) else float(val)

    return KeyboardFeatures(
        total_key_events=total_events,
        mean_key_interval=_safe_float(mean_interval),
        median_key_interval=_safe_float(median_interval),
        key_interval_std=_safe_float(interval_std),
        minimum_key_interval=_safe_float(min_interval),
        maximum_key_interval=_safe_float(max_interval),
        typing_speed=_safe_float(typing_speed),
        pause_count=pause_count,
        mean_pause_duration=_safe_float(mean_pause_dur),
        longest_pause=_safe_float(longest_pause),
        typing_activity_duration=_safe_float(active_duration)
    )
