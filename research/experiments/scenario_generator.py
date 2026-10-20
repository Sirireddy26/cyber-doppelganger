"""
Cyber Doppelgänger — Phase 7: Controlled Behavioural Scenario Generator
Safe Adaptive Behavioural Identity & Continuous User Verification

Generates isolated, reproducible, and mathematically rigorous behavioural scenarios
for empirical and synthetic benchmarking.

Anchored on authentic baseline feature distributions (v1.0.0, 435 genuine enrollment samples).
All synthetic transformations are strictly deterministic given a fixed random seed.
"""

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Canonical approved feature keys (37 features)
APPROVED_NUMERICAL_FEATURES: List[str] = [
    # Keyboard Dynamics
    "total_key_events", "mean_key_interval", "median_key_interval", "key_interval_std",
    "minimum_key_interval", "maximum_key_interval", "typing_speed", "pause_count",
    "mean_pause_duration", "longest_pause", "typing_activity_duration",
    # Mouse Kinematics
    "movement_distance", "mean_mouse_speed", "mouse_speed_std", "mean_acceleration",
    "click_count", "left_click_count", "right_click_count", "middle_click_count",
    "mean_click_interval", "click_interval_std", "scroll_count", "positive_scroll_count",
    "negative_scroll_count", "mouse_active_duration",
    # Session & System Dynamics
    "session_duration", "active_duration", "idle_duration", "active_idle_ratio",
    "activity_density", "keyboard_activity_duration", "mouse_activity_duration",
    "process_count", "active_process_count", "application_switch_count",
    "process_activity_count", "application_activity_duration"
]


def load_enrolled_baseline_stats(storage_path: Optional[Path] = None) -> Dict[str, Dict[str, float]]:
    """
    Loads authentic v1.0.0 baseline reference statistics from the enrolled profile artifact.
    Falls back to mathematically sound defaults if file is missing.
    """
    path = storage_path or (PROJECT_ROOT / "ml" / "artifacts" / "profile_versions.json")
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                versions = data.get("versions", [])
                if versions:
                    v1 = versions[0]
                    means = v1.get("feature_means", {})
                    stds = v1.get("feature_stds", {})
                    stats = {}
                    for k in APPROVED_NUMERICAL_FEATURES:
                        m = float(means.get(k, 100.0))
                        s = float(stds.get(k, 15.0))
                        stats[k] = {"mean": m, "std": max(0.01, s)}
                    return stats
        except Exception:
            pass

    # Fallback default statistics
    return {
        k: {
            "mean": 120.0 if "key" in k else (250.0 if "mouse" in k or "movement" in k else 15.0),
            "std": 15.0
        }
        for k in APPROVED_NUMERICAL_FEATURES
    }


class BehaviouralScenarioGenerator:
    """
    Deterministic generator of 9 controlled research scenarios for evaluating
    continuous verification and safe adaptation invariants.
    """

    def __init__(self, seed: int = 42, baseline_stats: Optional[Dict[str, Dict[str, float]]] = None):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.baseline_stats = baseline_stats or load_enrolled_baseline_stats()

    def _sample_around_baseline(self, shift_factor: float = 0.0, noise_sigma: float = 0.15) -> Dict[str, float]:
        """Samples a single feature snapshot with specific shift and noise."""
        snapshot = {}
        for k, stat in self.baseline_stats.items():
            mean = stat["mean"]
            std = stat["std"]
            val = mean + (shift_factor * std) + self.rng.normal(0, std * noise_sigma)
            snapshot[k] = float(max(0.0, val))
        return snapshot

    def generate_all_scenarios(self, window_count_override: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Generates all 9 controlled research scenarios."""
        n = window_count_override or 25
        return {
            "Scenario_1_Normal_Variation": self.scenario_1_normal_variation(n),
            "Scenario_2_Gradual_Evolution": self.scenario_2_gradual_evolution(n),
            "Scenario_3_Sudden_Deviation": self.scenario_3_sudden_deviation(n),
            "Scenario_4_Controlled_Takeover": self.scenario_4_controlled_takeover(n),
            "Scenario_5_Slow_Impersonation_Creep": self.scenario_5_slow_impersonation_creep(n),
            "Scenario_6_Repeated_Suspicious_Bursts": self.scenario_6_repeated_suspicious_bursts(n),
            "Scenario_7_Contamination_Poisoning": self.scenario_7_contamination_poisoning(n),
            "Scenario_8_Freeze_And_Recovery": self.scenario_8_freeze_and_recovery(n),
            "Scenario_9_Service_Outage_Resilience": self.scenario_9_service_outage_resilience(n),
        }

    def scenario_1_normal_variation(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 1: Normal Behavioural Variation
        Legitimate enrolled user operating under ambient natural variation (~0.15 sigma).
        Invariant: Profile remains v1.0.0 (no unnecessary adaptation, zero false rejections).
        """
        windows = []
        for i in range(n):
            snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": False,
                "label": "genuine_normal",
                "is_synthetic": True,
                "scenario_id": "SC1_NORMAL_VARIATION",
                "transformation_rule": "Gaussian noise N(0, 0.15*std) around v1.0.0 enrolled parameters"
            })
        return windows

    def scenario_2_gradual_evolution(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 2: Gradual Legitimate Evolution
        Legitimate user subtly shifts habits over consecutive windows (~1.05 to 1.25 sigma, high stability).
        Invariant: Multi-window candidate buffer safely absorbs drift and updates to v1.1.0 once stable.
        """
        windows = []
        for i in range(n):
            shift = 1.05 + (i / max(1, n)) * 0.20
            snap = self._sample_around_baseline(shift_factor=shift, noise_sigma=0.04)
            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": False,
                "label": "genuine_gradual_drift",
                "is_synthetic": True,
                "scenario_id": "SC2_GRADUAL_EVOLUTION",
                "transformation_rule": f"Benign linear shift factor={shift:.3f}*std with low variance noise N(0, 0.04*std)"
            })
        return windows

    def scenario_3_sudden_deviation(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 3: Sudden Behavioural Deviation
        Genuine session interrupted by an abrupt non-malicious spike (e.g. transient noise or task interruption).
        Invariant: Flagged as deviation, excluded from candidate buffer, profile unmodified.
        """
        windows = []
        for i in range(n):
            if 8 <= i <= 10:
                snap = self._sample_around_baseline(shift_factor=3.5, noise_sigma=0.40)
                label = "transient_deviation"
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "genuine_normal"

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": False,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC3_SUDDEN_DEVIATION",
                "transformation_rule": "Spike of 3.5*std applied for windows 8-10; otherwise normal baseline"
            })
        return windows

    def scenario_4_controlled_takeover(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 4: Controlled Simulated Takeover
        Genuine baseline session followed by an abrupt, drastic kinematic jump (5.0 sigma jump by intruder).
        Invariant: Immediate flagging as DEVIATION / SUSPICIOUS, zero contamination of reference profile.
        """
        windows = []
        cutoff = max(5, n // 3)
        for i in range(n):
            is_intruder = (i >= cutoff)
            if is_intruder:
                snap = self._sample_around_baseline(shift_factor=5.0, noise_sigma=0.50)
                label = "intruder_takeover"
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "genuine_normal"

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": is_intruder,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC4_CONTROLLED_TAKEOVER",
                "transformation_rule": "Windows 0 to cutoff: genuine; windows cutoff+: abrupt +5.0*std intruder jump"
            })
        return windows

    def scenario_5_slow_impersonation_creep(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 5: Slow Impersonation / Creep Drift Attack
        Adversary attempts subtle incremental mimicry (2.1 to 2.5 sigma drift creeping across windows).
        Invariant: Drift bound gating and buffer velocity checks detect non-conforming trajectory; profile never contaminated.
        """
        windows = []
        genuine_len = max(5, n // 4)
        for i in range(n):
            is_intruder = (i >= genuine_len)
            if is_intruder:
                creep_factor = 2.1 + ((i - genuine_len) / max(1, n - genuine_len)) * 0.40
                snap = self._sample_around_baseline(shift_factor=creep_factor, noise_sigma=0.10)
                label = "slow_creep_intruder"
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "genuine_normal"

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": is_intruder,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC5_SLOW_CREEP_ATTACK",
                "transformation_rule": "Windows genuine_len+: linear creeping shift from 2.1*std to 2.5*std"
            })
        return windows

    def scenario_6_repeated_suspicious_bursts(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 6: Repeated Suspicious Bursts
        Burst of anomalous observations testing streak anomaly threshold (3 consecutive anomalies).
        Invariant: Triggers automatic PROFILE_FROZEN, halts any further buffer intake, locks down reference profile.
        """
        windows = []
        for i in range(n):
            is_intruder = (5 <= i <= 9)
            if is_intruder:
                factor = 4.2 if (i % 2 == 0) else -3.5
                snap = self._sample_around_baseline(shift_factor=factor, noise_sigma=0.20)
                label = "suspicious_burst_attempt"
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "genuine_normal"

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": is_intruder,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC6_REPEATED_BURSTS",
                "transformation_rule": "Windows 5-9: high-variance alternating bursts ±4.0*std to test streak freeze"
            })
        return windows

    def scenario_7_contamination_poisoning(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 7: Profile Contamination Attempts
        Poisoning vectors injected intermittently between genuine observations to corrupt moving statistics.
        Invariant: Contamination rate is strictly 0.0% in SafeAdaptationEngine, but >0 in naive baseline.
        """
        windows = []
        for i in range(n):
            is_intruder = (i % 4 == 0 and i > 0)
            if is_intruder:
                snap = self._sample_around_baseline(shift_factor=3.8, noise_sigma=0.30)
                label = "poisoning_injection"
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "genuine_normal"

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": is_intruder,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC7_CONTAMINATION_POISONING",
                "transformation_rule": "Every 4th window injects +3.8*std poisoning vector into observation stream"
            })
        return windows

    def scenario_8_freeze_and_recovery(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 8: Freeze and Recovery Lifecycle
        Anomaly streak triggers freeze -> lockdown rejects updates -> authorized unfreeze executed -> normal recovery.
        Invariant: Verifies full state machine transitions and recovery success.
        """
        windows = []
        for i in range(n):
            if i < 4:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
                label = "pre_freeze_genuine"
                is_intruder = False
            elif 4 <= i <= 8:
                snap = self._sample_around_baseline(shift_factor=4.5, noise_sigma=0.20)
                label = "freeze_trigger_burst"
                is_intruder = True
            else:
                snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.12)
                label = "post_recovery_genuine"
                is_intruder = False

            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": is_intruder,
                "label": label,
                "is_synthetic": True,
                "scenario_id": "SC8_FREEZE_RECOVERY",
                "transformation_rule": "Windows 0-3 genuine -> 4-8 anomaly burst triggering freeze -> 9+ recovered normal"
            })
        return windows

    def scenario_9_service_outage_resilience(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        Scenario 9: Missing-Model and Service-Unavailable Resilience
        Upstream ML service outage occurs during continuous verification stream.
        Invariant: Fail-secure invariant: adaptation strictly halts, candidate buffer preserved, profile intact.
        """
        windows = []
        for i in range(n):
            snap = self._sample_around_baseline(shift_factor=0.0, noise_sigma=0.15)
            is_outage = (i >= 8 and i <= 14)
            windows.append({
                "window_index": i,
                "features": snap,
                "is_intruder": False,
                "label": "outage_simulated" if is_outage else "genuine_normal",
                "is_synthetic": True,
                "scenario_id": "SC9_SERVICE_OUTAGE",
                "simulate_service_outage": is_outage,
                "transformation_rule": "Normal features with simulate_service_outage=True for windows 8-14"
            })
        return windows
