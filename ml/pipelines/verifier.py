"""
Cyber Doppelgänger - Machine Learning Verification Pipeline
Implements behavioural anomaly detection and user trust scoring.
Models: Isolation Forest and One-Class SVM.
"""

from typing import Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class BehaviouralIdentityVerifier:
    """
    Behavioural Biometric Anomaly Detection Model.
    Learns genuine user typing cadence and mouse movement kinematics.
    """

    FEATURE_KEYS = [
        "dwell_mean_ms", "dwell_std_ms", "dwell_median_ms",
        "flight_mean_ms", "flight_std_ms",
        "press_latency_mean_ms", "press_latency_std_ms",
        "mouse_velocity_mean", "mouse_velocity_max", "mouse_velocity_std",
        "mouse_accel_mean", "mouse_accel_std",
        "click_duration_mean_ms", "click_duration_std_ms",
        "keystroke_rate_hz", "mouse_event_rate_hz"
    ]

    def __init__(self, contamination: float = 0.05):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=contamination, 
            random_state=42
        )
        self.is_fitted = False

    def _extract_feature_row(self, vector: Dict[str, float]) -> np.ndarray:
        return np.array([[vector.get(k, 0.0) for k in self.FEATURE_KEYS]], dtype=np.float64)

    def train_baseline(self, baseline_vectors: list[Dict[str, float]]) -> None:
        """Trains model on genuine user historical profile."""
        if len(baseline_vectors) < 5:
            raise ValueError("At least 5 baseline vectors required to initialize model profile.")

        matrix = np.array([
            [v.get(k, 0.0) for k in self.FEATURE_KEYS] 
            for v in baseline_vectors
        ], dtype=np.float64)

        scaled = self.scaler.fit_transform(matrix)
        self.model.fit(scaled)
        self.is_fitted = True

    def verify_window(self, vector: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculates user trust score (0.0 to 1.0) and recommended adaptation policy:
        - TRUSTED (Score >= 0.75)
        - PASSIVE_MONITOR (0.50 <= Score < 0.75)
        - REVERIFY_CHALLENGE (0.30 <= Score < 0.50)
        - STEP_UP_MFA (Score < 0.30)
        """
        if not self.is_fitted:
            # Cold-start profile default
            return 1.0, "PROVISIONAL_BASELINING"

        row = self._extract_feature_row(vector)
        scaled = self.scaler.transform(row)
        
        # Raw decision function output (higher = more normal, lower = anomaly)
        raw_score = float(self.model.decision_function(scaled)[0])
        # Map raw anomaly score to [0.0, 1.0] sigmoid/logistic scale
        trust_score = float(1.0 / (1.0 + np.exp(-raw_score * 4.0)))

        if trust_score >= 0.75:
            decision = "TRUSTED"
        elif trust_score >= 0.50:
            decision = "PASSIVE_MONITOR"
        elif trust_score >= 0.30:
            decision = "REVERIFY_CHALLENGE"
        else:
            decision = "STEP_UP_MFA"

        return round(trust_score, 4), decision
