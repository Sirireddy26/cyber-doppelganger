"""
Cyber Doppelgänger - Behavioral Verification Service
Safe Adaptive Behavioural Identity & Continuous User Verification

Coordinates feature preprocessing, model artifact loading, and verification scoring.
Distinguishes between Isolation Forest anomaly detection and Random Forest classification.
Gracefully handles missing or uncalibrated models (returning MODEL_NOT_READY).
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from ml.preprocessing.feature_preprocessor import FeaturePreprocessor, FeaturePreprocessingError
from ml.anomaly_detection.isolation_forest_detector import IsolationForestDetector
from ml.models.random_forest_classifier import BehaviouralRandomForestClassifier

logger = logging.getLogger("cyber-doppelganger.ml")

DEFAULT_MODEL_DIR = Path("ml/artifacts")


class VerificationService:
    """
    High-level verification engine for Phase 4.
    Evaluates incoming behavioral feature snapshots against persisted models.
    """

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = Path(model_dir or DEFAULT_MODEL_DIR)
        self.iso_detector: Optional[IsolationForestDetector] = None
        self.rf_classifier: Optional[BehaviouralRandomForestClassifier] = None
        self.active_model_type: str = "ISOLATION_FOREST"
        self._load_active_models()

    def _load_active_models(self) -> None:
        """Attempts to load persisted model artifacts from model directory."""
        iso_path = self.model_dir / "isolation_forest.joblib"
        if iso_path.exists():
            try:
                self.iso_detector = IsolationForestDetector.load(str(iso_path))
                logger.info(f"Loaded Isolation Forest model from {iso_path}")
            except Exception as e:
                logger.warning(f"Failed to load Isolation Forest from {iso_path}: {e}")
                self.iso_detector = None

        rf_path = self.model_dir / "random_forest.joblib"
        if rf_path.exists():
            try:
                self.rf_classifier = BehaviouralRandomForestClassifier.load(str(rf_path))
                logger.info(f"Loaded Random Forest model from {rf_path}")
            except Exception as e:
                logger.warning(f"Failed to load Random Forest from {rf_path}: {e}")
                self.rf_classifier = None

    def get_model_status(self) -> Dict[str, Any]:
        """Returns model readiness and version metadata."""
        self._load_active_models()

        iso_ready = self.iso_detector is not None and self.iso_detector.is_fitted
        rf_ready = self.rf_classifier is not None and self.rf_classifier.is_fitted

        return {
            "status": "READY" if (iso_ready or rf_ready) else "MODEL_NOT_READY",
            "activeModelType": self.active_model_type,
            "active_model_type": self.active_model_type,
            "isolationForest": {
                "available": iso_ready,
                "version": self.iso_detector.model_version if iso_ready else None,
                "threshold": self.iso_detector.threshold if iso_ready else None,
                "sampleCount": self.iso_detector.reference_profile.sample_count if (iso_ready and self.iso_detector.reference_profile) else 0
            },
            "isolation_forest": {
                "available": iso_ready,
                "version": self.iso_detector.model_version if iso_ready else None,
                "threshold": self.iso_detector.threshold if iso_ready else None,
                "sample_count": self.iso_detector.reference_profile.sample_count if (iso_ready and self.iso_detector.reference_profile) else 0
            },
            "randomForest": {
                "available": rf_ready,
                "version": self.rf_classifier.model_version if rf_ready else None,
                "threshold": self.rf_classifier.decision_threshold if rf_ready else None
            },
            "random_forest": {
                "available": rf_ready,
                "version": self.rf_classifier.model_version if rf_ready else None,
                "threshold": self.rf_classifier.decision_threshold if rf_ready else None
            }
        }

    def verify_snapshot(
        self,
        snapshot_dict: Dict[str, Any],
        preferred_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes an incoming snapshot and returns a standardized verification result.
        """
        # Ensure latest model artifacts are loaded
        if self.iso_detector is None and self.rf_classifier is None:
            self._load_active_models()

        model_type = (preferred_model or self.active_model_type).upper()

        if model_type == "RANDOM_FOREST":
            if self.rf_classifier is None or not self.rf_classifier.is_fitted:
                return {
                    "status": "MODEL_NOT_READY",
                    "modelType": "RANDOM_FOREST",
                    "anomalyScore": None,
                    "threshold": None,
                    "confidenceScore": None,
                    "modelVersion": "NONE",
                    "decision": "COLD_START_PENDING",
                    "reason": "Random Forest baseline model is not trained or loaded."
                }
            return self.rf_classifier.predict_snapshot(snapshot_dict)

        else:  # Default to ISOLATION_FOREST
            if self.iso_detector is None or not self.iso_detector.is_fitted:
                return {
                    "status": "MODEL_NOT_READY",
                    "modelType": "ISOLATION_FOREST",
                    "anomalyScore": None,
                    "threshold": None,
                    "confidenceScore": None,
                    "modelVersion": "NONE",
                    "decision": "COLD_START_PENDING",
                    "reason": "Isolation Forest baseline model is not trained or loaded. Baseline enrollment required."
                }
            return self.iso_detector.predict_snapshot(snapshot_dict)
