"""
Cyber Doppelgänger - Isolation Forest Behavioural Anomaly Detector
Safe Adaptive Behavioural Identity & Continuous User Verification

Fits an unsupervised baseline on legitimate reference feature distributions.
Scores incoming feature vectors relative to the reference baseline.
IMPORTANT: An anomaly score indicates behavioral deviation, NOT definitive proof of an attack.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import logging

from ml.preprocessing.feature_preprocessor import FeaturePreprocessor, FeaturePreprocessingError
from ml.models.reference_profile import ReferenceProfile

logger = logging.getLogger("cyber-doppelganger.ml")


class IsolationForestDetector:
    """
    Anomaly detection baseline using Scikit-Learn IsolationForest.
    
    Score Conventions:
    - raw_score: Output of model.decision_function(X). Positive (> 0) means inlier/normal;
      negative (< 0) means outlier/anomalous relative to training data.
    - anomaly_score: -raw_score (Higher values indicate higher deviation).
    - confidence_score: Logistic calibration 1 / (1 + exp(-raw_score * 4.0)) [range: 0.0 - 1.0],
      representing behavioral congruence with reference profile.
    - threshold: Decision boundary on raw_score (default: 0.0, or calibrated on validation set).
    - status:
        * VERIFIED: raw_score >= threshold
        * UNCERTAIN: threshold - 0.05 <= raw_score < threshold
        * DEVIATION: raw_score < threshold - 0.05
    """

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.05,
        random_state: int = 42,
        model_version: str = "1.0.0"
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model_version = model_version
        
        self.threshold: float = 0.0
        self.uncertainty_margin: float = 0.02
        self.model: Optional[IsolationForest] = None
        self.preprocessor: Optional[FeaturePreprocessor] = None
        self.reference_profile: Optional[ReferenceProfile] = None
        self.is_fitted: bool = False

    def fit(
        self,
        training_snapshots: List[Dict[str, Any]],
        user_id: str = "DEFAULT_USER",
        validation_snapshots: Optional[List[Dict[str, Any]]] = None
    ) -> "IsolationForestDetector":
        """
        Trains preprocessor, reference profile, and Isolation Forest on legitimate snapshots.
        """
        if len(training_snapshots) < 5:
            raise ValueError(
                f"Insufficient training samples ({len(training_snapshots)}). "
                "At least 5 legitimate feature snapshots are required to fit a baseline."
            )

        # 1. Fit preprocessor
        self.preprocessor = FeaturePreprocessor()
        scaled_matrix = self.preprocessor.fit_transform(training_snapshots)

        # 2. Fit reference profile (unscaled statistics)
        self.reference_profile = ReferenceProfile(
            user_id=user_id,
            model_version=self.model_version
        )
        self.reference_profile.fit_from_snapshots(training_snapshots, self.preprocessor)

        # 3. Fit Isolation Forest
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.model.fit(scaled_matrix)
        self.is_fitted = True

        # 4. Threshold calibration
        if validation_snapshots and len(validation_snapshots) >= 5:
            val_scaled = self.preprocessor.transform(validation_snapshots)
            val_scores = self.model.decision_function(val_scaled)
            # Set threshold to 5th percentile of validation set to bound false rejections
            self.threshold = float(np.percentile(val_scores, 5))
            logger.info(f"Calibrated Isolation Forest threshold to {self.threshold:.4f} using validation set.")
        else:
            # When no validation set is provided, calibrate threshold to 5th percentile of training data
            train_scores = self.model.decision_function(scaled_matrix)
            self.threshold = float(np.percentile(train_scores, 5))
            logger.info(f"Calibrated Isolation Forest threshold to {self.threshold:.4f} using training set.")

        return self

    def predict_snapshot(self, snapshot_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scores an incoming feature snapshot against the trained reference model.
        Returns structured verification dictionary.
        """
        if not self.is_fitted or self.model is None or self.preprocessor is None:
            return {
                "status": "MODEL_NOT_READY",
                "modelType": "ISOLATION_FOREST",
                "anomalyScore": None,
                "threshold": None,
                "confidenceScore": None,
                "modelVersion": self.model_version,
                "decision": "COLD_START_PENDING",
                "reason": "Model is not fitted. Baseline training required."
            }

        # Transform single snapshot
        scaled_row = self.preprocessor.transform_single(snapshot_dict)
        raw_score = float(self.model.decision_function(scaled_row)[0])
        anomaly_score = float(-raw_score)

        # Logistic calibration: 1 / (1 + exp(-4 * raw_score))
        confidence = float(1.0 / (1.0 + np.exp(-raw_score * 4.0)))
        confidence = round(max(0.0, min(1.0, confidence)), 4)

        # Determine status and decision
        if raw_score >= self.threshold:
            status = "VERIFIED"
            decision = "NORMAL_BEHAVIOUR"
            reason = f"Feature vector consistent with reference profile (score: {raw_score:+.4f} >= {self.threshold:.4f})."
        elif raw_score >= (self.threshold - self.uncertainty_margin):
            status = "UNCERTAIN"
            decision = "BORDERLINE_DEVIATION"
            reason = f"Feature vector in marginal boundary region (score: {raw_score:+.4f})."
        else:
            status = "DEVIATION"
            decision = "ANOMALOUS_BEHAVIOUR"
            reason = f"Feature vector exhibits significant deviation from reference profile (score: {raw_score:+.4f} < {self.threshold:.4f})."

        return {
            "status": status,
            "modelType": "ISOLATION_FOREST",
            "anomalyScore": round(anomaly_score, 4),
            "rawScore": round(raw_score, 4),
            "threshold": round(self.threshold, 4),
            "confidenceScore": confidence,
            "modelVersion": self.model_version,
            "decision": decision,
            "reason": reason
        }

    def save(self, filepath: str) -> None:
        """Persists trained model, preprocessor, and reference profile."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted IsolationForestDetector.")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "preprocessor": self.preprocessor,
            "reference_profile": self.reference_profile.to_dict() if self.reference_profile else None,
            "threshold": self.threshold,
            "uncertainty_margin": self.uncertainty_margin,
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "model_version": self.model_version,
            "is_fitted": self.is_fitted
        }
        joblib.dump(payload, filepath)
        logger.info(f"Saved Isolation Forest model artifact to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "IsolationForestDetector":
        """Loads model artifact safely with joblib."""
        payload = joblib.load(filepath)
        detector = cls(
            n_estimators=payload.get("n_estimators", 100),
            contamination=payload.get("contamination", 0.05),
            random_state=payload.get("random_state", 42),
            model_version=payload.get("model_version", "1.0.0")
        )
        detector.model = payload["model"]
        detector.preprocessor = payload["preprocessor"]
        detector.threshold = payload.get("threshold", 0.0)
        detector.uncertainty_margin = payload.get("uncertainty_margin", 0.05)
        detector.is_fitted = payload.get("is_fitted", True)

        ref_dict = payload.get("reference_profile")
        if ref_dict:
            detector.reference_profile = ReferenceProfile(
                user_id=ref_dict.get("user_id", "DEFAULT_USER"),
                model_version=ref_dict.get("model_version", "1.0.0")
            )
            detector.reference_profile.sample_count = ref_dict.get("sample_count", 0)
            detector.reference_profile.feature_means = ref_dict.get("feature_means", {})
            detector.reference_profile.feature_stds = ref_dict.get("feature_stds", {})
            detector.reference_profile.feature_medians = ref_dict.get("feature_medians", {})
            detector.reference_profile.feature_iqrs = ref_dict.get("feature_iqrs", {})
            detector.reference_profile.zero_variance_features = ref_dict.get("zero_variance_features", [])

        return detector
