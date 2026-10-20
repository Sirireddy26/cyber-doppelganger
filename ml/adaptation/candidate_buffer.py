"""
Cyber Doppelgänger - Candidate Observation Buffer
Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution

Maintains a bounded, privacy-safe queue of candidate behavioural observations
under evaluation for potential reference profile adaptation.
Strictly isolated from the trusted reference profile.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np
import logging

logger = logging.getLogger("cyber-doppelganger.adaptation.buffer")


class CandidateObservation:
    """Represents a single privacy-safe candidate behavioural observation."""

    def __init__(
        self,
        snapshot_id: Optional[int],
        device_id: str,
        user_id: Optional[str],
        features: Dict[str, float],
        timestamp: Optional[str] = None,
        raw_score: float = 0.0,
        anomaly_score: float = 0.0,
        confidence_score: float = 0.5
    ):
        self.snapshot_id = snapshot_id
        self.device_id = device_id
        self.user_id = user_id or "default-user"
        # Stored features MUST only be approved numerical values
        self.features: Dict[str, float] = {k: float(v) for k, v in features.items()}
        self.received_at: datetime = datetime.now(timezone.utc)
        self.timestamp = timestamp or self.received_at.isoformat()
        self.raw_score = raw_score
        self.anomaly_score = anomaly_score
        self.confidence_score = confidence_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "received_at": self.received_at.isoformat(),
            "raw_score": self.raw_score,
            "anomaly_score": self.anomaly_score,
            "confidence_score": self.confidence_score,
            "feature_count": len(self.features)
        }


class CandidateObservationBuffer:
    """
    Bounded, expiring candidate buffer holding observations being evaluated
    for gradual legitimate behavioral evolution.
    """

    def __init__(self, max_capacity: int = 20, ttl_seconds: float = 3600.0):
        self.max_capacity = max(5, max_capacity)
        self.ttl_seconds = ttl_seconds
        self._buffer: List[CandidateObservation] = []
        self._rejection_history: List[Dict[str, Any]] = []

    def clear(self) -> None:
        """Empties the candidate buffer completely."""
        self._buffer.clear()

    def size(self) -> int:
        """Returns the number of active, non-expired candidate observations."""
        self._purge_expired()
        return len(self._buffer)

    def is_full(self) -> bool:
        """Returns True if the buffer has reached maximum capacity."""
        self._purge_expired()
        return len(self._buffer) >= self.max_capacity

    def get_observations(self) -> List[CandidateObservation]:
        """Returns current valid observations in chronological order."""
        self._purge_expired()
        return list(self._buffer)

    def _purge_expired(self) -> int:
        """Removes observations older than ttl_seconds."""
        now = datetime.now(timezone.utc)
        initial_len = len(self._buffer)
        valid = []
        for obs in self._buffer:
            age_sec = (now - obs.received_at).total_seconds()
            if age_sec <= self.ttl_seconds:
                valid.append(obs)
            else:
                self._record_rejection(
                    obs.snapshot_id,
                    "EXPIRED",
                    f"Observation expired after {age_sec:.1f}s (TTL: {self.ttl_seconds}s)"
                )
        self._buffer = valid
        purged = initial_len - len(self._buffer)
        if purged > 0:
            logger.info(f"Purged {purged} expired observation(s) from candidate buffer.")
        return purged

    def _record_rejection(self, snapshot_id: Optional[int], code: str, reason: str) -> None:
        """Records metadata about rejected candidate observations."""
        self._rejection_history.append({
            "snapshot_id": snapshot_id,
            "rejection_code": code,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        # Keep rejection history bounded to last 50 entries
        if len(self._rejection_history) > 50:
            self._rejection_history.pop(0)

    def add(
        self,
        observation: CandidateObservation,
        is_frozen: bool = False
    ) -> Tuple[bool, str]:
        """
        Attempts to add an observation to the candidate buffer.
        Returns (success, message).
        """
        if is_frozen:
            self._record_rejection(
                observation.snapshot_id,
                "PROFILE_FROZEN",
                "Rejected observation: profile is in FROZEN state."
            )
            return False, "Cannot accumulate candidate observations while profile is frozen."

        self._purge_expired()

        if len(self._buffer) >= self.max_capacity:
            # Capacity policy: drop the oldest observation to prevent unbounded growth
            oldest = self._buffer.pop(0)
            self._record_rejection(
                oldest.snapshot_id,
                "BUFFER_OVERFLOW",
                "Evicted oldest observation due to buffer capacity limit."
            )

        self._buffer.append(observation)
        logger.debug(
            f"Added candidate observation {observation.snapshot_id}. "
            f"Buffer size: {len(self._buffer)}/{self.max_capacity}"
        )
        return True, "Observation queued in candidate buffer."

    def compute_stability(self, feature_keys: List[str]) -> Tuple[float, Dict[str, float]]:
        """
        Computes internal consistency (variance) among candidate observations.
        Higher stability score (close to 1.0) means candidate observations are
        consistent with each other rather than wildly fluctuating.
        """
        self._purge_expired()
        if len(self._buffer) < 2:
            return 1.0, {}

        matrix = np.array([
            [obs.features.get(k, 0.0) for k in feature_keys]
            for obs in self._buffer
        ], dtype=np.float64)

        # Standard deviations across features
        stds = np.std(matrix, axis=0)
        means = np.mean(matrix, axis=0)
        
        # Coefficient of variation per feature (std / mean), avoiding div by zero
        cvs = []
        feature_cvs: Dict[str, float] = {}
        for idx, k in enumerate(feature_keys):
            mean_val = abs(means[idx])
            std_val = stds[idx]
            if mean_val > 1e-4:
                cv = min(5.0, std_val / mean_val)
            else:
                cv = min(5.0, std_val)
            cvs.append(cv)
            feature_cvs[k] = round(float(cv), 4)

        # Average stability metric in [0.0, 1.0]
        mean_cv = float(np.mean(cvs)) if cvs else 0.0
        # Exponential decay mapping: CV of 0 -> 1.0; CV of 1.0 -> ~0.37
        stability_score = round(float(np.exp(-mean_cv)), 4)
        return stability_score, feature_cvs

    def get_summary(self) -> Dict[str, Any]:
        """Returns non-sensitive metadata summary of the candidate buffer."""
        self._purge_expired()
        return {
            "current_size": len(self._buffer),
            "max_capacity": self.max_capacity,
            "ttl_seconds": self.ttl_seconds,
            "oldest_timestamp": self._buffer[0].received_at.isoformat() if self._buffer else None,
            "newest_timestamp": self._buffer[-1].received_at.isoformat() if self._buffer else None,
            "recent_rejections": list(self._rejection_history[-5:])
        }
