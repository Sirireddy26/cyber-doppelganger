"""
Cyber Doppelgänger - Local Snapshot Buffer
Safe Adaptive Behavioural Identity & Continuous User Verification

Provides local-first disk buffering of privacy-validated feature snapshots.
Ensures zero data loss when backend is unreachable, with thread-safe file operations.
STRICT PRIVACY GUARANTEE: Persists solely aggregated numerical feature snapshots in JSONL.
Never persists raw keystrokes, individual keys, or screen contents.
"""

import os
import json
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from agent.features.feature_snapshot import FeatureSnapshot
from agent.privacy.privacy_filter import PrivacyFilter

logger = logging.getLogger("cyber-doppelganger.agent")


class LocalBuffer:
    """Thread-safe JSONL file-based buffer for feature snapshots."""

    def __init__(self, file_path: str = "agent/data/feature_snapshots.jsonl", max_entries: int = 5000):
        self.file_path = Path(file_path)
        self.max_entries = max_entries
        self._lock = threading.Lock()
        
        # Ensure parent directory exists
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create buffer directory {self.file_path.parent}: {e}")

    def write_snapshot(self, snapshot: FeatureSnapshot) -> bool:
        """
        Validates privacy policy and appends a single snapshot to the local JSONL buffer.
        """
        # 1. Enforce privacy filter validation
        snapshot_dict = snapshot.to_dict()
        PrivacyFilter.validate_snapshot_dict(snapshot_dict)

        # 2. Append to JSONL file with lock
        line = json.dumps(snapshot_dict) + "\n"
        with self._lock:
            try:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(line)
                return True
            except Exception as e:
                logger.error(f"Failed to write snapshot to local buffer: {e}")
                return False

    def read_pending_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Reads pending feature snapshots from local buffer.
        Gracefully handles corrupted or malformed lines.
        """
        if not self.file_path.exists():
            return []

        snapshots: List[Dict[str, Any]] = []
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            # Verify privacy compliance on read
                            PrivacyFilter.validate_snapshot_dict(data)
                            snapshots.append(data)
                            if len(snapshots) >= limit:
                                break
                        except json.JSONDecodeError:
                            logger.warning(f"Skipping malformed JSON line {line_num} in {self.file_path}")
                        except Exception as e:
                            logger.warning(f"Skipping invalid line {line_num} in {self.file_path}: {e}")
            except Exception as e:
                logger.error(f"Error reading snapshots from {self.file_path}: {e}")

        return snapshots

    def count(self) -> int:
        """Returns total number of recorded snapshots in the buffer."""
        if not self.file_path.exists():
            return 0
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return sum(1 for line in f if line.strip())
            except Exception:
                return 0

    def remove_oldest(self, count: int) -> int:
        """Removes the oldest N snapshots from the buffer file upon confirmed transmission."""
        if not self.file_path.exists() or count <= 0:
            return 0
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    lines = [l for l in f.readlines() if l.strip()]
                remaining = lines[count:]
                with open(self.file_path, "w", encoding="utf-8") as f:
                    f.writelines(remaining)
                return min(count, len(lines))
            except Exception as e:
                logger.error(f"Error removing sent records from buffer: {e}")
                return 0

    def clear(self) -> bool:
        """Truncates or removes the local buffer file (used primarily in testing)."""
        with self._lock:
            try:
                if self.file_path.exists():
                    self.file_path.unlink()
                return True
            except Exception as e:
                logger.error(f"Failed to clear buffer: {e}")
                return False
