"""
Cyber Doppelgänger - Adaptation Policy & Decision Rules
Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution

Defines configurable safety criteria, risk evaluation thresholds, and
the core 5 decision states:
- NORMAL
- SAFE_ADAPTATION
- SUSPICIOUS_CHANGE
- PROFILE_FROZEN
- INSUFFICIENT_EVIDENCE
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import numpy as np
import logging

logger = logging.getLogger("cyber-doppelganger.adaptation.policy")


@dataclass
class AdaptationPolicyConfig:
    """Configurable engineering defaults for profile evolution safety."""
    min_observations: int = 5
    max_capacity: int = 20
    max_drift_magnitude: float = 1.80  # Max standardized deviation permitted for legitimate adaptation
    max_velocity: float = 2.50         # Max sudden rate of change between adjacent observation windows
    min_stability: float = 0.35        # Minimum internal consistency among candidate observations
    max_suspicious_streak: int = 3     # Consecutive anomalies before auto-freezing profile
    cooldown_seconds: float = 60.0     # Minimum interval between successful profile adaptations
    policy_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdaptationPolicy:
    """
    Evaluates verification evidence, historical streaks, and candidate buffer
    dynamics to produce an explainable adaptation decision.
    """

    def __init__(self, config: Optional[AdaptationPolicyConfig] = None):
        self.config = config or AdaptationPolicyConfig()

    def compute_drift_magnitude(
        self,
        candidate_features: Dict[str, float],
        reference_means: Dict[str, float],
        reference_stds: Dict[str, float]
    ) -> float:
        """
        Computes standardized Euclidean distance (z-score space) of candidate
        features relative to the trusted reference profile.
        """
        if not reference_means or not candidate_features:
            return 0.0

        differences = []
        for key, mean_val in reference_means.items():
            if key in candidate_features:
                val = candidate_features[key]
                std_val = reference_stds.get(key, 1.0)
                # Safeguard zero-variance features
                effective_std = std_val if (std_val and std_val > 1e-4) else 1.0
                z = (val - mean_val) / effective_std
                differences.append(z ** 2)

        if not differences:
            return 0.0

        # Root mean squared standardized distance
        rms_z = float(np.sqrt(np.mean(differences)))
        return round(rms_z, 4)

    def compute_velocity(
        self,
        current_features: Dict[str, float],
        previous_features: Optional[Dict[str, float]],
        reference_stds: Dict[str, float]
    ) -> float:
        """
        Computes the rate of behavioral change between two adjacent observations.
        High velocity indicates sudden physical takeover or script injection.
        """
        if not previous_features or not current_features:
            return 0.0

        diffs = []
        for key, curr_val in current_features.items():
            if key in previous_features:
                prev_val = previous_features[key]
                std_val = reference_stds.get(key, 1.0)
                effective_std = std_val if (std_val and std_val > 1e-4) else 1.0
                step = (curr_val - prev_val) / effective_std
                diffs.append(step ** 2)

        if not diffs:
            return 0.0

        return round(float(np.sqrt(np.mean(diffs))), 4)

    def evaluate(
        self,
        verification_status: str,
        raw_score: float,
        threshold: float,
        candidate_count: int,
        drift_magnitude: float,
        velocity: float,
        stability_score: float,
        suspicious_streak: int,
        is_frozen: bool,
        seconds_since_last_adaptation: float
    ) -> Tuple[str, str]:
        """
        Evaluates input telemetry against the safety rules.
        Returns: (decision_state, reason)
        """
        # 1. Check if profile is already frozen
        if is_frozen:
            return (
                "PROFILE_FROZEN",
                f"Profile adaptation is locked due to security freeze policy. "
                f"Requires authorized manual recovery or re-enrollment."
            )

        # 2. Check if suspicious streak has crossed threshold
        if suspicious_streak >= self.config.max_suspicious_streak:
            return (
                "PROFILE_FROZEN",
                f"Triggered automatic security freeze: consecutive anomaly streak ({suspicious_streak}) "
                f"exceeded maximum tolerance ({self.config.max_suspicious_streak})."
            )

        # 3. Check for severe anomaly / sudden takeover
        if verification_status == "DEVIATION":
            return (
                "SUSPICIOUS_CHANGE",
                f"Verification anomaly detected (score: {raw_score:+.4f} < {threshold:+.4f}). "
                f"Observation rejected from adaptation to prevent reference poisoning."
            )

        if velocity > self.config.max_velocity:
            return (
                "SUSPICIOUS_CHANGE",
                f"Abrupt behavioral velocity spike ({velocity:.2f} > {self.config.max_velocity:.2f}). "
                f"Sudden shift rejected as potential session takeover attempt."
            )

        if drift_magnitude > (self.config.max_drift_magnitude * 1.5):
            return (
                "SUSPICIOUS_CHANGE",
                f"Excessive deviation magnitude ({drift_magnitude:.2f} > {self.config.max_drift_magnitude * 1.5:.2f}). "
                f"Large behavioral departure rejected from baseline adaptation."
            )

        # 4. Check for Nominal User Behaviour (No change required)
        if verification_status == "VERIFIED" and drift_magnitude <= (self.config.max_drift_magnitude * 0.5):
            return (
                "NORMAL",
                f"Observation conforms to trusted reference profile (score: {raw_score:+.4f}, drift: {drift_magnitude:.2f}). "
                f"Trusted profile preserved without modification."
            )

        # 5. Evaluate potential Safe Adaptation for gradual evolutionary change
        # Case where status is UNCERTAIN (mild shift) or observation is consistently accumulating
        if candidate_count < self.config.min_observations:
            return (
                "INSUFFICIENT_EVIDENCE",
                f"Observation queued in candidate buffer ({candidate_count}/{self.config.min_observations} windows). "
                f"More evidence required before considering profile adaptation."
            )

        # Sufficient observations accumulated -> evaluate safety gates
        if seconds_since_last_adaptation < self.config.cooldown_seconds:
            return (
                "INSUFFICIENT_EVIDENCE",
                f"Adaptation cooldown active ({seconds_since_last_adaptation:.1f}s < {self.config.cooldown_seconds}s). "
                f"Profile remains fixed during stabilization period."
            )

        if stability_score < self.config.min_stability:
            return (
                "INSUFFICIENT_EVIDENCE",
                f"Candidate observations exhibit low internal stability ({stability_score:.2f} < {self.config.min_stability:.2f}). "
                f"Unstable behavior cannot safely update the trusted baseline."
            )

        if drift_magnitude > self.config.max_drift_magnitude:
            return (
                "SUSPICIOUS_CHANGE",
                f"Accumulated drift magnitude ({drift_magnitude:.2f}) exceeds safe envelope ({self.config.max_drift_magnitude:.2f}). "
                f"Potential slow impersonation attack rejected."
            )

        # All safety criteria satisfied: candidate observations are stable, bounded, and verified!
        return (
            "SAFE_ADAPTATION",
            f"Validated safe profile adaptation: {candidate_count} consecutive stable observations "
            f"(stability: {stability_score:.2f}, drift: {drift_magnitude:.2f}) passed all safety gates."
        )
