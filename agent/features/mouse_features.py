"""
Cyber Doppelgänger - Mouse Behavioural Features
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates derived numerical movement dynamics, click intervals, and scroll counts.
STRICT PRIVACY GUARANTEE: Never captures, stores, or logs screen coordinates long-term,
screenshots, cursor images, clicked text, or UI elements.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import math
import numpy as np


@dataclass
class MouseFeatures:
    """
    Privacy-safe numerical features derived from mouse movement kinematics and interactions.
    
    Feature definitions:
    - movement_distance: Total cumulative Euclidean distance traversed by mouse cursor (unit: pixels).
    - mean_mouse_speed: Mean cursor velocity across valid movement segments (unit: pixels/second).
    - mouse_speed_std: Standard deviation of movement velocities (unit: pixels/second).
    - mean_acceleration: Mean rate of change of cursor velocity (unit: pixels/second^2).
    - click_count: Total mouse clicks recorded during the window (unit: count).
    - left_click_count: Number of left mouse button clicks (unit: count).
    - right_click_count: Number of right mouse button clicks (unit: count).
    - middle_click_count: Number of middle mouse button clicks (unit: count).
    - mean_click_interval: Mean time between consecutive click events (unit: seconds).
    - click_interval_std: Standard deviation of intervals between clicks (unit: seconds).
    - scroll_count: Total scroll wheel steps recorded (unit: count).
    - positive_scroll_count: Number of upward / positive scroll steps (unit: count).
    - negative_scroll_count: Number of downward / negative scroll steps (unit: count).
    - mouse_active_duration: Total duration of active mouse interaction (unit: seconds).
    """
    movement_distance: float = 0.0
    mean_mouse_speed: float = 0.0
    mouse_speed_std: float = 0.0
    mean_acceleration: float = 0.0
    click_count: int = 0
    left_click_count: int = 0
    right_click_count: int = 0
    middle_click_count: int = 0
    mean_click_interval: float = 0.0
    click_interval_std: float = 0.0
    scroll_count: int = 0
    positive_scroll_count: int = 0
    negative_scroll_count: int = 0
    mouse_active_duration: float = 0.0

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


def calculate_mouse_features(
    movement_samples: List[Tuple[float, float, float]],  # (dx, dy, dt) or (dist, dt, speed)
    clicks: List[Tuple[float, str]],                    # (timestamp, button_type)
    scrolls: List[Tuple[float, int, int]]               # (timestamp, dx, dy)
) -> MouseFeatures:
    """
    Calculates derived mouse features from short-lived in-memory movement and event summaries.
    
    Parameters:
    - movement_samples: List of (distance_pixels, dt_seconds, speed_px_per_s) tuples.
    - clicks: List of (timestamp, button_name) tuples.
    - scrolls: List of (timestamp, dx, dy) tuples.
    
    Returns:
    - MouseFeatures dataclass populated with valid, finite numerical features.
    """
    # 1. Movement Calculations
    total_distance = 0.0
    speeds: List[float] = []
    accelerations: List[float] = []
    movement_active_dt = 0.0

    if movement_samples:
        prev_speed = 0.0
        for dist, dt, speed in movement_samples:
            if dt > 0.0 and not math.isnan(dist) and not math.isinf(dist) and dist >= 0.0:
                total_distance += dist
                movement_active_dt += dt
                if not math.isnan(speed) and not math.isinf(speed):
                    speeds.append(speed)
                    if dt > 1e-4:
                        accel = abs(speed - prev_speed) / dt
                        if not math.isnan(accel) and not math.isinf(accel):
                            accelerations.append(accel)
                    prev_speed = speed

    mean_speed = float(np.mean(speeds)) if speeds else 0.0
    speed_std = float(np.std(speeds)) if len(speeds) > 1 else 0.0
    mean_accel = float(np.mean(accelerations)) if accelerations else 0.0

    # 2. Click Calculations
    left_count = 0
    right_count = 0
    middle_count = 0
    click_timestamps: List[float] = []

    for ts, button in clicks:
        btn_lower = str(button).lower()
        if "left" in btn_lower:
            left_count += 1
        elif "right" in btn_lower:
            right_count += 1
        elif "middle" in btn_lower:
            middle_count += 1
        else:
            left_count += 1
        click_timestamps.append(ts)

    total_clicks = len(clicks)
    mean_click_int = 0.0
    click_int_std = 0.0

    if total_clicks > 1:
        click_timestamps.sort()
        click_intervals = [
            click_timestamps[i] - click_timestamps[i - 1]
            for i in range(1, len(click_timestamps))
            if (click_timestamps[i] - click_timestamps[i - 1]) >= 0.0
        ]
        if click_intervals:
            arr_ci = np.array(click_intervals, dtype=float)
            mean_click_int = float(np.mean(arr_ci))
            click_int_std = float(np.std(arr_ci)) if len(arr_ci) > 1 else 0.0

    # 3. Scroll Calculations
    pos_scrolls = 0
    neg_scrolls = 0
    total_scrolls = len(scrolls)

    for _, _, dy in scrolls:
        if dy > 0:
            pos_scrolls += 1
        elif dy < 0:
            neg_scrolls += 1

    # Total mouse active duration (movement time + estimated interaction span)
    mouse_active_duration = max(movement_active_dt, 0.0)

    def _safe_float(val: float) -> float:
        return 0.0 if (np.isnan(val) or np.isinf(val)) else float(val)

    return MouseFeatures(
        movement_distance=_safe_float(total_distance),
        mean_mouse_speed=_safe_float(mean_speed),
        mouse_speed_std=_safe_float(speed_std),
        mean_acceleration=_safe_float(mean_accel),
        click_count=total_clicks,
        left_click_count=left_count,
        right_click_count=right_count,
        middle_click_count=middle_count,
        mean_click_interval=_safe_float(mean_click_int),
        click_interval_std=_safe_float(click_int_std),
        scroll_count=total_scrolls,
        positive_scroll_count=pos_scrolls,
        negative_scroll_count=neg_scrolls,
        mouse_active_duration=_safe_float(mouse_active_duration)
    )
