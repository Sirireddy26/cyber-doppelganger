"""
Cyber Doppelgänger - Mouse Kinematics Behavioural Collector
Strict Privacy Guarantee: ZERO screenshots, ZERO screen pixels, ZERO window titles.
Only physical movement velocity, acceleration, and curvature are processed.
"""

import math
import time
import threading
from typing import List, Dict, Optional, Tuple
from agent.collector.privacy_guard import PrivacyGuard

class MouseKinematicsCollector:
    """
    Collects anonymous mouse kinematic metrics:
    - Speed / Velocity (pixels/ms)
    - Acceleration (pixels/ms^2)
    - Curvature / Tortuosity ratio
    - Click Duration (ms)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._last_point: Optional[Tuple[int, int, float]] = None # (x, y, timestamp_ms)
        self._last_velocity: float = 0.0
        self._click_start_times: Dict[str, float] = {}
        
        self._events: List[Dict[str, float]] = []

    def on_move(self, x: int, y: int) -> None:
        """Processes mouse movement coordinates to compute velocity & acceleration."""
        now = time.time() * 1000.0

        with self._lock:
            if self._last_point is not None:
                prev_x, prev_y, prev_t = self._last_point
                dt = max(1.0, now - prev_t)
                dx = x - prev_x
                dy = y - prev_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                velocity = distance / dt  # pixels per ms
                acceleration = (velocity - self._last_velocity) / dt

                event = {
                    "timestamp_ms": now,
                    "displacement_px": round(distance, 2),
                    "velocity_px_ms": round(velocity, 4),
                    "acceleration_px_ms2": round(acceleration, 6),
                    "delta_time_ms": round(dt, 2),
                    "event_type": 2.0  # 2.0 = move
                }
                PrivacyGuard.sanitize_event(event)
                self._events.append(event)
                self._last_velocity = velocity

            self._last_point = (x, y, now)

    def on_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Processes mouse click press and release to compute click duration."""
        now = time.time() * 1000.0
        btn_key = str(button)

        with self._lock:
            if pressed:
                self._click_start_times[btn_key] = now
            else:
                click_duration = 0.0
                if btn_key in self._click_start_times:
                    click_duration = max(0.0, now - self._click_start_times.pop(btn_key))

                event = {
                    "timestamp_ms": now,
                    "click_duration_ms": round(click_duration, 2),
                    "event_type": 3.0  # 3.0 = click
                }
                PrivacyGuard.sanitize_event(event)
                self._events.append(event)

    def flush_events(self) -> List[Dict[str, float]]:
        """Atomically retrieves and clears buffered kinematic events."""
        with self._lock:
            flushed = list(self._events)
            self._events.clear()
            return flushed

    def get_event_count(self) -> int:
        with self._lock:
            return len(self._events)
