"""
Cyber Doppelgänger - Base Collector Interface
Defines the lifecycle and contract for all behavioural collectors.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """Abstract base class for all behavioural data collectors."""

    def __init__(self, name: str):
        self.name = name
        self._is_active = False

    @abstractmethod
    def start(self) -> None:
        """Starts the collector lifecycle."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops the collector lifecycle."""
        pass

    @property
    def is_active(self) -> bool:
        """Returns True if the collector is actively monitoring."""
        return self._is_active

    @abstractmethod
    def flush_events(self) -> List[Dict[str, Any]]:
        """Atomically retrieves and clears buffered events."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic and health status of the collector."""
        pass
