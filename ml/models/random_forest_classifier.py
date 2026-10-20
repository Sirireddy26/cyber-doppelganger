"""
Cyber Doppelgänger - Random Forest Behavioural Classifier Baseline
Safe Adaptive Behavioural Identity & Continuous User Verification

Supervised baseline for binary/multi-class verification when labelled multi-user data exists.
Distinguishes legitimate user (class 1) from other users/impostors (class 0).
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import logging

from ml.preprocessing.feature_preprocessor import FeaturePreprocessor

logger = logging.getLogger("cyber-doppelganger.ml")


class BehaviouralRandomForestClassifier:
    """
    Supervised Random Forest baseline.
    Requires at least two distinct user classes (e.g. legitimate vs. other participants).
    
    Conventions:
    - Label 1 = Legitimate User Target
    - Label 0 = Other User / Impostor
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        random_state: int = 42,
        model_version: str = "1.0.0"
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model_version = model_version
        
        self.model: Optional[RandomForestClassifier] = None
        self.preprocessor: Optional[FeaturePreprocessor] = None
        self.decision_threshold: float = 0.50
        self.is_fitted: bool = False
        self.classes_: Optional[List[int]] = None

    def fit(
        self,
        snapshots: List[Dict[str, Any]],
        labels: List[int],
        validation_snapshots: Optional[List[Dict[str, Any]]] = None,
        validation_labels: Optional[List[int]] = None
    ) -> "BehaviouralRandomForestClassifier":
        """
        Trains preprocessor and Random Forest classifier.
        Raises ValueError if fewer than 2 classes are present.
        """
        if len(snapshots) != len(labels):
            raise ValueError(f"Number of snapshots ({len(snapshots)}) must match labels ({len(labels)}).")

        unique_labels = set(labels)
        if len(unique_labels) < 2:
            raise ValueError(
                f"Random Forest supervised classification requires at least 2 distinct user classes. Found only: {unique_labels}. "
                "For single-user unlabelled baseline, use IsolationForestDetector instead."
            )

        # Fit preprocessor
        self.preprocessor = FeaturePreprocessor()
        scaled_matrix = self.preprocessor.fit_transform(snapshots)

        # Fit Random Forest
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            class_weight="balanced"
        )
        self.model.fit(scaled_matrix, labels)
        self.classes_ = list(self.model.classes_)
        self.is_fitted = True

        # Optional threshold calibration on validation set
        if validation_snapshots and validation_labels:
            val_scaled = self.preprocessor.transform(validation_snapshots)
            # Probability of target class (class 1)
            target_idx = list(self.model.classes_).index(1) if 1 in self.model.classes_ else 0
            val_probs = self.model.predict_proba(val_scaled)[:, target_idx]
            # Tune threshold for balance
            self.decision_threshold = 0.50

        return self

    def predict_snapshot(self, snapshot_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts class probabilities for incoming snapshot.
        """
        if not self.is_fitted or self.model is None or self.preprocessor is None:
            return {
                "status": "MODEL_NOT_READY",
                "modelType": "RANDOM_FOREST",
                "anomalyScore": None,
                "threshold": None,
                "confidenceScore": None,
                "modelVersion": self.model_version,
                "decision": "COLD_START_PENDING",
                "reason": "Random Forest model is not trained."
            }

        scaled_row = self.preprocessor.transform_single(snapshot_dict)
        probs = self.model.predict_proba(scaled_row)[0]
        
        # Target probability (legitimate user class 1)
        target_idx = list(self.model.classes_).index(1) if 1 in self.model.classes_ else 0
        legit_prob = float(probs[target_idx])
        anomaly_score = float(1.0 - legit_prob)

        if legit_prob >= self.decision_threshold:
            status = "VERIFIED"
            decision = "NORMAL_BEHAVIOUR"
            reason = f"Classified as legitimate user with probability {legit_prob:.4f} >= {self.decision_threshold:.2f}."
        elif legit_prob >= 0.35:
            status = "UNCERTAIN"
            decision = "BORDERLINE_CLASSIFICATION"
            reason = f"Classification probability marginal: {legit_prob:.4f}."
        else:
            status = "DEVIATION"
            decision = "IMPOSTOR_DETECTED"
            reason = f"Classified as other/impostor user (legitimate prob: {legit_prob:.4f} < {self.decision_threshold:.2f})."

        return {
            "status": status,
            "modelType": "RANDOM_FOREST",
            "anomalyScore": round(anomaly_score, 4),
            "rawScore": round(legit_prob, 4),
            "threshold": round(self.decision_threshold, 4),
            "confidenceScore": round(legit_prob, 4),
            "modelVersion": self.model_version,
            "decision": decision,
            "reason": reason
        }

    def save(self, filepath: str) -> None:
        """Saves model and preprocessor to disk."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted BehaviouralRandomForestClassifier.")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "preprocessor": self.preprocessor,
            "decision_threshold": self.decision_threshold,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "random_state": self.random_state,
            "model_version": self.model_version,
            "classes_": self.classes_,
            "is_fitted": self.is_fitted
        }
        joblib.dump(payload, filepath)
        logger.info(f"Saved Random Forest model artifact to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "BehaviouralRandomForestClassifier":
        """Loads model artifact from disk."""
        payload = joblib.load(filepath)
        clf = cls(
            n_estimators=payload.get("n_estimators", 100),
            max_depth=payload.get("max_depth", 10),
            random_state=payload.get("random_state", 42),
            model_version=payload.get("model_version", "1.0.0")
        )
        clf.model = payload["model"]
        clf.preprocessor = payload["preprocessor"]
        clf.decision_threshold = payload.get("decision_threshold", 0.50)
        clf.classes_ = payload.get("classes_")
        clf.is_fitted = payload.get("is_fitted", True)
        return clf
