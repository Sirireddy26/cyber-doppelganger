"""
Cyber Doppelgänger - Privacy-Safe Session State Collector
Safe Adaptive Behavioural Identity & Continuous User Verification

Tracks session continuity, active interaction spans, and idle states.
STRICT PRIVACY GUARANTEE:
Never captures application names, window titles, or content.
Maintains solely temporal duration counters (seconds active vs. idle).
"""

import threading
import time
from typing import Dict, Any, Optional
import logging

from agent.collectors.base import BaseCollector
from agent.features.session_features import SessionFeatures, calculate_session_features
from agent.configuration.settings import settings

logger = logging.getLogger("cyber-doppelganger.agent")


class SessionCollector(BaseCollector):
    """
    Tracks overall session lifetime, active interaction time, and idle gaps.
    """

    def __init__(self, idle_threshold_seconds: Optional[float] = None):
        super().__init__(name="SessionCollector")
        self.idle_threshold_seconds = (
            idle_threshold_seconds if idle_threshold_seconds is not None
            else settings.IDLE_THRESHOLD_SECONDS
        )
        self._session_start_time = time.monotonic()
        self._last_interaction_time = time.monotonic()
        self._lock = threading.Lock()
        self._windows_completed: int = 0
        self._error_state: Optional[str] = None

    def record_interaction(self) -> None:
        """Notifies the session collector that user activity occurred."""
        with self._lock:
            self._last_interaction_time = time.monotonic()

    def start(self) -> None:
        """Starts session tracking."""
        if self._is_active:
            return
        self._session_start_time = time.monotonic()
        self._last_interaction_time = time.monotonic()
        self._is_active = True
        logger.info(f"{self.name} started (Session continuity tracking active).")

    def stop(self) -> None:
        """Stops session tracking."""
        self._is_active = False
        logger.info(f"{self.name} stopped.")

    def flush_events(self) -> Dict[str, Any]:
        """Atomically returns and increments completed window counter."""
        with self._lock:
            now = time.monotonic()
            session_elapsed = now - self._session_start_time
            idle_time = now - self._last_interaction_time
            self._windows_completed += 1
            return {
                "session_elapsed": session_elapsed,
                "current_idle_gap": idle_time,
                "windows_completed": self._windows_completed
            }

    def extract_features(
        self,
        window_duration: float,
        keyboard_active_sec: float,
        mouse_active_sec: float
    ) -> SessionFeatures:
        """
        Calculates SessionFeatures for the current aggregation window.
        """
        now = time.monotonic()
        session_elapsed = now - self._session_start_time
        return calculate_session_features(
            session_elapsed=session_elapsed,
            window_duration=window_duration,
            keyboard_active_sec=keyboard_active_sec,
            mouse_active_sec=mouse_active_sec,
            idle_threshold_seconds=self.idle_threshold_seconds
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns collector operational status."""
        with self._lock:
            now = time.monotonic()
            uptime = now - self._session_start_time
            idle_gap = now - self._last_interaction_time
            win_count = self._windows_completed

        return {
            "name": self.name,
            "active": self._is_active,
            "collection_enabled": True,
            "privacy_mode": "TEMPORAL_DURATIONS_ONLY",
            "session_uptime_seconds": round(uptime, 1),
            "current_idle_seconds": round(idle_gap, 1),
            "windows_completed": win_count,
            "idle_threshold_seconds": self.idle_threshold_seconds,
            "error": self._error_state
        }
