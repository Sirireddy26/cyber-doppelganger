"""
Cyber Doppelgänger - System State Context Collector
Captures hardware utilization baselines without inspecting user content or documents.
"""

import time
import psutil
from typing import Dict
from agent.collector.privacy_guard import PrivacyGuard

class SystemStateCollector:
    """Collects anonymous hardware load metrics via psutil."""

    @staticmethod
    def get_system_snapshot() -> Dict[str, float]:
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        snapshot = {
            "timestamp_ms": round(time.time() * 1000.0, 2),
            "cpu_usage_pct": float(cpu_pct),
            "memory_usage_pct": float(mem.percent),
            "available_memory_mb": float(mem.available / (1024 * 1024))
        }
        PrivacyGuard.sanitize_event(snapshot)
        return snapshot
