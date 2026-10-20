"""
Cyber Doppelgänger — Phase 7: Experimental Baselines & Proposed Method Wrappers
Safe Adaptive Behavioural Identity & Continuous User Verification

Implements strictly isolated instances of:
  - Baseline A: Static Reference Profile (Zero adaptation, fixed v1.0.0 baseline)
  - Baseline B: Conventional Adaptation (Naive EMA / sliding-window without risk gating)
  - Proposed Method: Risk-Guided Safe Adaptation Engine (SafeAdaptationEngine)

CRITICAL INVARIANT:
All experimental methods run in sandboxed temporary directories or memory,
ensuring the live production profile is NEVER modified by experimental benchmarks.
"""

import copy
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from ml.adaptation.adaptation_policy import AdaptationPolicyConfig
from ml.adaptation.profile_manager import ProfileManager, ProfileVersionRecord
from ml.adaptation.safe_adaptation_engine import SafeAdaptationEngine


class StaticProfileBaseline:
    """
    Baseline A: Static Reference Profile.
    The enrolled profile parameters remain strictly frozen at v1.0.0.
    Zero adaptation, zero candidate buffer accumulation.
    """

    def __init__(self, baseline_stats: Dict[str, Dict[str, float]], threshold_sigma: float = 1.8):
        self.name = "Baseline A (Static Profile)"
        self.baseline_stats = copy.deepcopy(baseline_stats)
        self.threshold_sigma = threshold_sigma
        self.version = "v1.0.0"
        self.adaptations_count = 0
        self.contaminated_samples_absorbed = 0

    def evaluate(self, snapshot_features: Dict[str, float], is_intruder: bool = False) -> Dict[str, Any]:
        t0 = time.perf_counter()
        sq_dist = 0.0
        n_feats = len(snapshot_features)

        for k, v in snapshot_features.items():
            stat = self.baseline_stats.get(k, {"mean": 0.0, "std": 1.0})
            std = stat["std"] if stat["std"] > 1e-4 else 1.0
            sq_dist += ((v - stat["mean"]) / std) ** 2

        norm_dist = float(np.sqrt(sq_dist / max(1, n_feats)))
        is_normal = (norm_dist < self.threshold_sigma)
        decision = "NORMAL" if is_normal else "SUSPICIOUS_CHANGE"

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "baseline": "STATIC_BASELINE",
            "decision": decision,
            "profile_version": self.version,
            "adapted": False,
            "drift_magnitude": norm_dist,
            "is_frozen": False,
            "latency_ms": latency_ms,
            "raw_score": float(0.12 - (norm_dist * 0.08)),
            "is_intruder": is_intruder
        }


class ConventionalAdaptationBaseline:
    """
    Baseline B: Conventional Adaptation (Unconstrained Naive Sliding Window / EMA).
    Updates reference distribution statistics on every single observation without
    candidate buffering, drift bound checks, velocity gates, or streak anomaly freezes.
    Tracks profile contamination whenever an intruder observation is absorbed.
    """

    def __init__(self, baseline_stats: Dict[str, Dict[str, float]], alpha: float = 0.15, threshold_sigma: float = 1.8):
        self.name = "Baseline B (Conventional Adaptation)"
        self.stats = copy.deepcopy(baseline_stats)
        self.alpha = alpha  # Smoothing factor
        self.threshold_sigma = threshold_sigma
        self.version_counter = 0
        self.version = "v1.0.0"
        self.adaptations_count = 0
        self.contaminated_samples_absorbed = 0

    def evaluate(self, snapshot_features: Dict[str, float], is_intruder: bool = False) -> Dict[str, Any]:
        t0 = time.perf_counter()
        sq_dist = 0.0
        n_feats = len(snapshot_features)

        for k, v in snapshot_features.items():
            stat = self.stats.get(k, {"mean": 0.0, "std": 1.0})
            std = stat["std"] if stat["std"] > 1e-4 else 1.0
            sq_dist += ((v - stat["mean"]) / std) ** 2

        norm_dist = float(np.sqrt(sq_dist / max(1, n_feats)))

        # Naive adaptation blindly updates running means on every observation
        for k, v in snapshot_features.items():
            if k in self.stats:
                old_m = self.stats[k]["mean"]
                self.stats[k]["mean"] = (1.0 - self.alpha) * old_m + self.alpha * float(v)

        self.adaptations_count += 1
        self.version_counter += 1
        self.version = f"v1.{self.version_counter}.0"

        if is_intruder:
            self.contaminated_samples_absorbed += 1

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "baseline": "CONVENTIONAL_ADAPTATION",
            "decision": "SAFE_ADAPTATION",  # Blindly adapts every observation
            "profile_version": self.version,
            "adapted": True,
            "drift_magnitude": norm_dist,
            "is_frozen": False,
            "latency_ms": latency_ms,
            "raw_score": float(0.12 - (norm_dist * 0.08)),
            "is_intruder": is_intruder
        }


class SafeAdaptationWrapper:
    """
    Proposed Method: Risk-Guided Safe Adaptation Engine (SafeAdaptationEngine).
    Runs the full Phase 5/6 SafeAdaptationEngine in an isolated temporary sandbox.
    Enforces multi-window candidate buffering, drift bounds, velocity checks,
    stability gating, streak anomaly freezing, and atomic rollback lineage.
    """

    def __init__(self, baseline_stats: Dict[str, Dict[str, float]], policy_config: Optional[AdaptationPolicyConfig] = None):
        self.name = "Proposed Method (SafeAdaptationEngine)"
        self.baseline_stats = copy.deepcopy(baseline_stats)
        self.temp_dir = tempfile.mkdtemp(prefix="cd_exp_safe_")
        self.storage_path = os.path.join(self.temp_dir, "profile_versions.json")

        self.policy_config = policy_config or AdaptationPolicyConfig(
            min_observations=5,
            max_capacity=20,
            max_drift_magnitude=1.8,
            max_velocity=2.5,
            min_stability=0.35,
            max_suspicious_streak=3,
            cooldown_seconds=0.0
        )

        # Initialize isolated profile manager seeded with enrolled baseline stats
        self.pm = ProfileManager(storage_path=self.storage_path, user_id="eval-subject")
        self._seed_baseline_version()

        self.engine = SafeAdaptationEngine(config=self.policy_config, profile_manager=self.pm)
        self.adaptations_count = 0
        self.contaminated_samples_absorbed = 0
        self.freezes_count = 0
        self.recovery_count = 0

    def _seed_baseline_version(self):
        """Seeds initial v1.0.0 in isolated sandbox from baseline stats."""
        means = {k: stat["mean"] for k, stat in self.baseline_stats.items()}
        stds = {k: stat["std"] for k, stat in self.baseline_stats.items()}
        v1 = ProfileVersionRecord(
            version_tag="v1.0.0",
            parent_version_tag=None,
            user_id="eval-subject",
            sample_count=435,
            feature_means=means,
            feature_stds=stds,
            status="ACTIVE",
            reason="Initial enrolled baseline"
        )
        self.pm.version_history = [v1]
        self.pm.active_version = v1
        self.pm._save_to_disk()

    def evaluate(self, snapshot_features: Dict[str, float], is_intruder: bool = False,
                 simulate_service_outage: bool = False) -> Dict[str, Any]:
        t0 = time.perf_counter()

        if simulate_service_outage:
            verif_dict = {
                "status": "SERVICE_UNAVAILABLE",
                "error": "ML verification service connection timeout"
            }
            norm_dist = 0.0
        else:
            sq_dist = 0.0
            n_feats = len(snapshot_features)
            for k, v in snapshot_features.items():
                stat = self.baseline_stats.get(k, {"mean": 0.0, "std": 1.0})
                std = stat["std"] if stat["std"] > 1e-4 else 1.0
                sq_dist += ((v - stat["mean"]) / std) ** 2
            norm_dist = float(np.sqrt(sq_dist / max(1, n_feats)))

            raw_score = float(0.12 - (norm_dist * 0.08))
            status = "VERIFIED" if norm_dist < 1.8 else "DEVIATION"
            verif_dict = {
                "status": status,
                "rawScore": raw_score,
                "threshold": 0.0327,
                "anomalyScore": -raw_score,
                "confidenceScore": float(1.0 / (1.0 + np.exp(-raw_score * 4.0)))
            }

        decision_res = self.engine.evaluate_observation(
            snapshot_dict=snapshot_features,
            verification_result=verif_dict,
            device_id="eval-device-01",
            user_id="eval-subject"
        )

        state = decision_res.get("decision_state", "UNKNOWN")
        adapted = (state == "SAFE_ADAPTATION")

        if adapted:
            self.adaptations_count += 1
            if is_intruder:
                self.contaminated_samples_absorbed += 1
        elif state == "PROFILE_FROZEN":
            self.freezes_count += 1

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "baseline": "SAFE_ADAPTATION_ENGINE",
            "decision": state,
            "profile_version": self.pm.active_version.version_tag if self.pm.active_version else "v1.0.0",
            "adapted": adapted,
            "drift_magnitude": norm_dist,
            "is_frozen": self.pm.is_frozen,
            "freeze_reason": self.pm.freeze_reason,
            "candidate_count": self.engine.buffer.size(),
            "suspicious_streak": self.pm.suspicious_streak,
            "latency_ms": latency_ms,
            "raw_score": verif_dict.get("rawScore"),
            "is_intruder": is_intruder
        }

    def unfreeze(self, authorized_by: str = "security-admin", reason: str = "Evaluation recovery") -> Tuple[bool, str]:
        success, msg = self.engine.unfreeze(authorized_by=authorized_by, reason=reason)
        if success:
            self.recovery_count += 1
        return success, msg

    def rollback(self, target_version: str = "v1.0.0", reason: str = "Evaluation rollback") -> Tuple[bool, str]:
        return self.engine.rollback(target_version=target_version, reason=reason)

    def cleanup(self):
        """Cleans up the isolated temporary sandbox directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
