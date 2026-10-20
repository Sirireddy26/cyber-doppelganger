"""
Cyber Doppelgänger - Privacy-Safe Mouse Kinematics Collector
Safe Adaptive Behavioural Identity & Continuous User Verification

Observes mouse movement dynamics, click intervals, and scroll counts using pynput.
STRICT PRIVACY GUARANTEE:
NEVER captures screenshots, cursor images, screen pixels, UI labels, or clicked content.
Cursor coordinates (x, y) are held strictly transiently in volatile memory to calculate
instantaneous displacement (distance) and velocity, then discarded immediately.
No coordinate trajectories or positions are ever persisted.
"""

import threading
import time
import math
from typing import List, Dict, Any, Optional, Tuple
import logging

try:
    from pynput import mouse
    PYNPUT_MOUSE_AVAILABLE = True
except ImportError:
    mouse = None
    PYNPUT_MOUSE_AVAILABLE = False

from agent.collectors.base import BaseCollector
from agent.features.mouse_features import MouseFeatures, calculate_mouse_features

logger = logging.getLogger("cyber-doppelganger.agent")


class MouseCollector(BaseCollector):
    """
    Asynchronous mouse dynamics collector.
    
    Tracks kinematic derivatives (velocity, acceleration) and interaction rates.
    Coordinates are never stored; only delta displacements are buffered.
    """

    def __init__(self):
        super().__init__(name="MouseCollector")
        self._listener: Optional[Any] = None
        self._lock = threading.Lock()

        # Transient state for kinematic delta computation
        self._last_x: Optional[float] = None
        self._last_y: Optional[float] = None
        self._last_move_time: Optional[float] = None

        # Short-lived in-memory window buffers
        self._movement_samples: List[Tuple[float, float, float]] = []  # (distance, dt, speed)
        self._clicks: List[Tuple[float, str]] = []                     # (timestamp, button_name)
        self._scrolls: List[Tuple[float, int, int]] = []               # (timestamp, dx, dy)

        self._lifetime_moves: int = 0
        self._lifetime_clicks: int = 0
        self._lifetime_scrolls: int = 0
        self._error_state: Optional[str] = None

    def _on_move(self, x: float, y: float) -> None:
        """
        Callback for mouse displacement.
        Computes distance and speed relative to previous coordinate;
        coordinates themselves are NOT persisted into the feature buffer.
        """
        if x is None or y is None:
            return

        now = time.monotonic()
        with self._lock:
            if self._last_x is not None and self._last_y is not None and self._last_move_time is not None:
                dt = now - self._last_move_time
                # Filter jitter or sub-millisecond duplicate events
                if dt >= 0.001:
                    dx = x - self._last_x
                    dy = y - self._last_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    speed = dist / dt if dt > 0.0 else 0.0
                    
                    # Prevent non-finite values
                    if not (math.isnan(dist) or math.isinf(dist) or math.isnan(speed) or math.isinf(speed)):
                        self._movement_samples.append((dist, dt, speed))
                        self._lifetime_moves += 1

            self._last_x = float(x)
            self._last_y = float(y)
            self._last_move_time = now

    def _on_click(self, x: float, y: float, button: Any, pressed: bool) -> None:
        """
        Callback for mouse clicks.
        Only records press events with timestamp and button type.
        PRIVACY: Discards x and y coordinates! Never records clicked elements.
        """
        if not pressed:
            return

        now = time.monotonic()
        # Parse button name safely without logging arbitrary UI text
        btn_str = "other"
        if hasattr(button, "name"):
            btn_str = button.name.lower()
        elif "left" in str(button).lower():
            btn_str = "left"
        elif "right" in str(button).lower():
            btn_str = "right"
        elif "middle" in str(button).lower():
            btn_str = "middle"

        with self._lock:
            self._clicks.append((now, btn_str))
            self._lifetime_clicks += 1

    def _on_scroll(self, x: float, y: float, dx: int, dy: int) -> None:
        """
        Callback for mouse scroll events.
        PRIVACY: Discards coordinates; only records monotonic timestamp and wheel direction deltas.
        """
        now = time.monotonic()
        with self._lock:
            self._scrolls.append((now, int(dx), int(dy)))
            self._lifetime_scrolls += 1

    def start(self) -> None:
        """Starts asynchronous background mouse listener."""
        if self._is_active:
            return

        if not PYNPUT_MOUSE_AVAILABLE:
            self._error_state = "pynput.mouse library not available"
            logger.warning(f"{self.name}: {self._error_state}")
            return

        try:
            self._listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click,
                on_scroll=self._on_scroll
            )
            self._listener.daemon = True
            self._listener.start()
            self._is_active = True
            self._error_state = None
            logger.info(f"{self.name} started successfully (Coordinate-free privacy mode active).")
        except Exception as e:
            self._error_state = str(e)
            self._is_active = False
            logger.error(f"Failed to start {self.name}: {e}")

    def stop(self) -> None:
        """Stops background mouse listener."""
        if not self._is_active and not self._listener:
            return

        self._is_active = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception as e:
                logger.debug(f"Error stopping mouse listener: {e}")
            self._listener = None
        logger.info(f"{self.name} stopped.")

    def flush_events(self) -> Dict[str, Any]:
        """Atomically retrieves and clears buffered movement, click, and scroll samples."""
        with self._lock:
            flushed = {
                "movement_samples": list(self._movement_samples),
                "clicks": list(self._clicks),
                "scrolls": list(self._scrolls)
            }
            self._movement_samples.clear()
            self._clicks.clear()
            self._scrolls.clear()
            return flushed

    def extract_features(self) -> MouseFeatures:
        """
        Flushes in-memory events and calculates derived numerical kinematics.
        """
        events = self.flush_events()
        return calculate_mouse_features(
            movement_samples=events["movement_samples"],
            clicks=events["clicks"],
            scrolls=events["scrolls"]
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns collector operational status."""
        with self._lock:
            pending_moves = len(self._movement_samples)
            pending_clicks = len(self._clicks)
            pending_scrolls = len(self._scrolls)

        return {
            "name": self.name,
            "active": self._is_active,
            "collection_enabled": True,
            "privacy_mode": "ZERO_COORDINATE_PERSISTENCE",
            "buffered_movement_samples": pending_moves,
            "buffered_clicks": pending_clicks,
            "buffered_scrolls": pending_scrolls,
            "lifetime_moves": self._lifetime_moves,
            "lifetime_clicks": self._lifetime_clicks,
            "lifetime_scrolls": self._lifetime_scrolls,
            "error": self._error_state
        }
