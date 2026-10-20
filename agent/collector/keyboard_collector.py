"""
Cyber Doppelgänger - Keyboard Behavioural Collector
Strict Privacy Guarantee: ZERO key names, ZERO characters, ZERO text stored.
Only millisecond timing intervals are processed.
"""

import time
import threading
from typing import List, Dict, Optional
from agent.collector.privacy_guard import PrivacyGuard

class KeystrokeTimingCollector:
    """
    Collects anonymous keystroke timing metrics:
    - Dwell Time: Duration a key is held down (ms)
    - Flight Time: Interval between releasing one key and pressing the next (ms)
    - Press Latency: Interval between consecutive key presses (ms)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._key_down_times: Dict[int, float] = {}  # Map anonymized internal id -> timestamp
        self._last_release_time: Optional[float] = None
        self._last_press_time: Optional[float] = None
        
        # Buffer of anonymous timing events
        self._events: List[Dict[str, float]] = []
        self._running = False
        self._listener = None

    def on_press(self, key) -> None:
        """
        Record key press timestamp.
        The key identifier is strictly converted to an opaque memory hash ID.
        No character or key name is ever retained.
        """
        now = time.time() * 1000.0  # ms
        key_id = id(key)

        with self._lock:
            flight_time = 0.0
            if self._last_release_time is not None:
                flight_time = max(0.0, now - self._last_release_time)

            press_latency = 0.0
            if self._last_press_time is not None:
                press_latency = max(0.0, now - self._last_press_time)

            self._key_down_times[key_id] = now
            self._last_press_time = now

            # Partial event to be completed on release
            event = {
                "timestamp_ms": now,
                "flight_time_ms": round(flight_time, 2),
                "press_latency_ms": round(press_latency, 2),
                "event_type": 1.0  # 1.0 = press
            }
            # Verify privacy guard compliance
            PrivacyGuard.sanitize_event(event)
            self._events.append(event)

    def on_release(self, key) -> None:
        """
        Calculate dwell time when key is released.
        """
        now = time.time() * 1000.0  # ms
        key_id = id(key)

        with self._lock:
            dwell_time = 0.0
            if key_id in self._key_down_times:
                press_time = self._key_down_times.pop(key_id)
                dwell_time = max(0.0, now - press_time)

            self._last_release_time = now

            event = {
                "timestamp_ms": now,
                "dwell_time_ms": round(dwell_time, 2),
                "event_type": 0.0  # 0.0 = release
            }
            PrivacyGuard.sanitize_event(event)
            self._events.append(event)

    def flush_events(self) -> List[Dict[str, float]]:
        """Atomically retrieves and clears buffered timing events."""
        with self._lock:
            flushed = list(self._events)
            self._events.clear()
            return flushed

    def get_event_count(self) -> int:
        with self._lock:
            return len(self._events)
