"""
Cyber Doppelgänger - Event Buffering Module
Phase 1 Foundation: Thread-safe event buffer interface.
"""

import threading
from typing import List, Dict, Any

class EventBuffer:
    """Thread-safe event buffer with capacity limits."""

    def __init__(self, max_capacity: int = 1000):
        self._max_capacity = max_capacity
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add(self, event: Dict[str, Any]) -> bool:
        """Adds an event to the buffer. Drops oldest if capacity exceeded."""
        with self._lock:
            if len(self._buffer) >= self._max_capacity:
                self._buffer.pop(0)
            self._buffer.append(event)
            return True

    def flush(self) -> List[Dict[str, Any]]:
        """Atomically retrieves all events and empties buffer."""
        with self._lock:
            flushed = list(self._buffer)
            self._buffer.clear()
            return flushed

    def size(self) -> int:
        with self._lock:
            return len(self._buffer)
