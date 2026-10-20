"""
Cyber Doppelgänger - Privacy-Safe Keyboard Behavioural Collector
Safe Adaptive Behavioural Identity & Continuous User Verification

Observes keyboard interaction rhythms using pynput.
CRITICAL PRIVACY GUARANTEE:
NEVER logs or stores key names, characters, letters, symbols, words, or passwords.
The callback captures ONLY monotonic timestamps. All raw event data is held
transiently in memory and discarded immediately upon feature extraction.
"""

import threading
import time
from typing import List, Dict, Any, Optional
import logging

try:
    from pynput import keyboard
    PYNPUT_KEYBOARD_AVAILABLE = True
except ImportError:
    keyboard = None
    PYNPUT_KEYBOARD_AVAILABLE = False

from agent.collectors.base import BaseCollector
from agent.features.keyboard_features import KeyboardFeatures, calculate_keyboard_features
from agent.configuration.settings import settings

logger = logging.getLogger("cyber-doppelganger.agent")


class KeyboardCollector(BaseCollector):
    """
    Asynchronous, privacy-preserving keystroke dynamics collector.
    
    Captures ONLY timing intervals between consecutive keystrokes.
    Content is permanently discarded at the hardware/OS hook level.
    """

    def __init__(self, pause_threshold_seconds: Optional[float] = None):
        super().__init__(name="KeyboardCollector")
        self.pause_threshold_seconds = (
            pause_threshold_seconds if pause_threshold_seconds is not None
            else settings.KEYBOARD_PAUSE_THRESHOLD_SECONDS
        )
        self._timestamps: List[float] = []
        self._lock = threading.Lock()
        self._listener: Optional[Any] = None
        self._total_collected_lifetime: int = 0
        self._error_state: Optional[str] = None

    def _on_press(self, key: Any) -> None:
        """
        Callback executed on keyboard press.
        PRIVACY ENFORCEMENT: Never touches key.char, key.name, or any key representation.
        Captures ONLY the monotonic timestamp.
        """
        now = time.monotonic()
        with self._lock:
            self._timestamps.append(now)
            self._total_collected_lifetime += 1

    def start(self) -> None:
        """Starts asynchronous background keyboard listener."""
        if self._is_active:
            return

        if not PYNPUT_KEYBOARD_AVAILABLE:
            self._error_state = "pynput.keyboard library not available"
            logger.warning(f"{self.name}: {self._error_state}")
            return

        try:
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.daemon = True
            self._listener.start()
            self._is_active = True
            self._error_state = None
            logger.info(f"{self.name} started successfully (Zero-content privacy mode active).")
        except Exception as e:
            self._error_state = str(e)
            self._is_active = False
            logger.error(f"Failed to start {self.name}: {e}")

    def stop(self) -> None:
        """Stops background keyboard listener and clears transient state."""
        if not self._is_active and not self._listener:
            return

        self._is_active = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception as e:
                logger.debug(f"Error stopping keyboard listener: {e}")
            self._listener = None
        logger.info(f"{self.name} stopped.")

    def flush_events(self) -> List[float]:
        """
        Atomically retrieves and clears buffered monotonic timestamps.
        Returns list of floats (timestamps).
        """
        with self._lock:
            flushed = list(self._timestamps)
            self._timestamps.clear()
            return flushed

    def extract_features(self) -> KeyboardFeatures:
        """
        Atomically flushes in-memory timestamps and computes derived numerical features.
        Raw timestamps are discarded immediately upon calculation.
        """
        timestamps = self.flush_events()
        return calculate_keyboard_features(
            timestamps=timestamps,
            pause_threshold_seconds=self.pause_threshold_seconds
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns collector operational health and status metadata."""
        with self._lock:
            pending_count = len(self._timestamps)
        return {
            "name": self.name,
            "active": self._is_active,
            "collection_enabled": True,
            "privacy_mode": "ZERO_CONTENT_RECORDING",
            "buffered_event_count": pending_count,
            "lifetime_events": self._total_collected_lifetime,
            "pause_threshold_seconds": self.pause_threshold_seconds,
            "error": self._error_state
        }
