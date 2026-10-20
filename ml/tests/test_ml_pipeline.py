"""
Cyber Doppelgänger - Machine Learning Pipeline Comprehensive Test Suite
Validates preprocessing, reference profiles, Isolation Forest, Random Forest,
evaluation metrics, data-leakage guards, and verification services.
"""

import unittest
import numpy as np
import tempfile
import shutil
from pathlib import Path

from ml.preprocessing.feature_preprocessor import (
    FeaturePreprocessor,
    FeaturePreprocessingError,
    ALL_FEATURE_KEYS
)
from ml.models.reference_profile import ReferenceProfile
from ml.anomaly_detection.isolation_forest_detector import IsolationForestDetector
from ml.models.random_forest_classifier import BehaviouralRandomForestClassifier
from ml.evaluation.evaluator import ModelEvaluator, group_aware_split
from ml.pipelines.verification_service import VerificationService


def create_synthetic_snapshot(session_id: str = "sess-1", scale: float = 1.0) -> dict:
    """Helper to generate a clean synthetic snapshot conforming strictly to schema 2.0."""
    return {
        "timestamp": "2026-10-09T10:00:00Z",
        "window_duration_seconds": 15,
        "device_id": "test-device",
        "user_id": "user-1",
        "session_id": session_id,
        "schema_version": "2.0",
        "keyboard": {
            "total_key_events": int(40 * scale),
            "mean_key_interval": 0.15 * scale,
            "median_key_interval": 0.14 * scale,
            "key_interval_std": 0.03 * scale,
            "minimum_key_interval": 0.04,
            "maximum_key_interval": 0.40 * scale,
            "typing_speed": 4.5 * scale,
            "pause_count": 1,
            "mean_pause_duration": 1.2,
            "longest_pause": 1.2,
            "typing_activity_duration": 8.0 * scale
        },
        "mouse": {
            "movement_distance": 900.0 * scale,
            "mean_mouse_speed": 120.0 * scale,
            "mouse_speed_std": 40.0 * scale,
            "mean_acceleration": 200.0 * scale,
            "click_count": int(6 * scale),
            "left_click_count": int(4 * scale),
            "right_click_count": int(2 * scale),
            "middle_click_count": 0,
            "mean_click_interval": 1.2,
            "click_interval_std": 0.3,
            "scroll_count": 2,
            "positive_scroll_count": 2,
            "negative_scroll_count": 0,
            "mouse_active_duration": 6.0 * scale
        },
        "session": {
            "session_duration": 60.0,
            "active_duration": 12.0 * scale,
            "idle_duration": 3.0,
            "active_idle_ratio": 4.0,
            "activity_density": 0.80,
            "keyboard_activity_duration": 8.0 * scale,
            "mouse_activity_duration": 6.0 * scale
        },
        "application": {
            "process_count": 80,
            "active_process_count": 4,
            "application_switch_count": 1,
            "process_activity_count": 10,
            "application_activity_duration": 15.0
        }
    }


class TestFeaturePreprocessing(unittest.TestCase):

    def setUp(self):
        self.preprocessor = FeaturePreprocessor()

    def test_valid_feature_extraction_and_order(self):
        snapshot = create_synthetic_snapshot()
        vec = self.preprocessor.extract_feature_vector(snapshot)
        self.assertEqual(len(vec), len(ALL_FEATURE_KEYS))
        self.assertEqual(len(vec), 37)
        self.assertTrue(np.all(np.isfinite(vec)))

    def test_missing_features_imputed_safely(self):
        sparse_snapshot = {
            "schema_version": "2.0",
            "keyboard": {"mean_key_interval": 0.20}
        }
        vec = self.preprocessor.extract_feature_vector(sparse_snapshot)
        self.assertEqual(len(vec), len(ALL_FEATURE_KEYS))
        # Missing features default safely to 0.0
        self.assertEqual(vec[0], 0.0)

    def test_nan_and_infinity_rejected(self):
        bad_snapshot = create_synthetic_snapshot()
        bad_snapshot["keyboard"]["mean_key_interval"] = float("nan")
        with self.assertRaises(FeaturePreprocessingError):
            self.preprocessor.extract_feature_vector(bad_snapshot)

        bad_snapshot2 = create_synthetic_snapshot()
        bad_snapshot2["mouse"]["mean_mouse_speed"] = float("inf")
        with self.assertRaises(FeaturePreprocessingError):
            self.preprocessor.extract_feature_vector(bad_snapshot2)

    def test_prohibited_privacy_field_rejected(self):
        bad_snapshot = create_synthetic_snapshot()
        bad_snapshot["typed_text"] = "secret_keystroke"
        with self.assertRaises(FeaturePreprocessingError):
            self.preprocessor.extract_feature_vector(bad_snapshot)

    def test_unsupported_schema_version_rejected(self):
        bad_snapshot = create_synthetic_snapshot()
        bad_snapshot["schema_version"] = "99.0"
        with self.assertRaises(FeaturePreprocessingError):
            self.preprocessor.extract_feature_vector(bad_snapshot)


class TestReferenceProfile(unittest.TestCase):

    def test_reference_profile_creation_and_stats(self):
        snapshots = [create_synthetic_snapshot(scale=1.0 + i * 0.1) for i in range(10)]
        profile = ReferenceProfile(user_id="USER_01")
        profile.fit_from_snapshots(snapshots)

        self.assertEqual(profile.sample_count, 10)
        self.assertIn("mean_key_interval", profile.feature_means)
        self.assertIn("mean_key_interval", profile.feature_stds)
        self.assertIn("mean_key_interval", profile.feature_medians)
        self.assertIn("mean_key_interval", profile.feature_iqrs)

    def test_zero_variance_handled_safely(self):
        # All snapshots have identical process_count
        snapshots = [create_synthetic_snapshot() for _ in range(5)]
        profile = ReferenceProfile()
        profile.fit_from_snapshots(snapshots)
        self.assertIn("process_count", profile.zero_variance_features)

    def test_profile_json_roundtrip(self):
        snapshots = [create_synthetic_snapshot() for _ in range(5)]
        profile = ReferenceProfile(user_id="USER_01")
        profile.fit_from_snapshots(snapshots)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            profile.save_json(tmp_path)
            loaded = ReferenceProfile.load_json(tmp_path)
            self.assertEqual(loaded.user_id, "USER_01")
            self.assertEqual(loaded.sample_count, 5)
            self.assertEqual(loaded.feature_means, profile.feature_means)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestIsolationForestDetector(unittest.TestCase):

    def test_fit_and_prediction(self):
        np.random.seed(42)
        train_snaps = [create_synthetic_snapshot(scale=float(np.random.normal(1.0, 0.15))) for _ in range(50)]
        detector = IsolationForestDetector(n_estimators=100, random_state=42)
        detector.fit(train_snaps, user_id="USER_01")

        # Inlier test
        normal_snap = create_synthetic_snapshot(scale=1.0)
        pred_normal = detector.predict_snapshot(normal_snap)
        self.assertEqual(pred_normal["status"], "VERIFIED")
        self.assertEqual(pred_normal["modelType"], "ISOLATION_FOREST")
        self.assertIsNotNone(pred_normal["anomalyScore"])

        # Extreme outlier test (completely shifted distribution)
        outlier_snap = {k: {sub_k: 9999.0 for sub_k in v} if isinstance(v, dict) else v for k, v in normal_snap.items()}
        pred_outlier = detector.predict_snapshot(outlier_snap)
        self.assertEqual(pred_outlier["status"], "DEVIATION")
        self.assertLess(pred_outlier["rawScore"], detector.threshold)

    def test_insufficient_training_data_raises_error(self):
        detector = IsolationForestDetector()
        with self.assertRaises(ValueError):
            detector.fit([create_synthetic_snapshot()])

    def test_unfitted_model_returns_model_not_ready(self):
        detector = IsolationForestDetector()
        pred = detector.predict_snapshot(create_synthetic_snapshot())
        self.assertEqual(pred["status"], "MODEL_NOT_READY")


class TestRandomForestClassifier(unittest.TestCase):

    def test_multiclass_training_and_prediction(self):
        user1_snaps = [create_synthetic_snapshot(scale=1.0 + np.random.uniform(-0.05, 0.05)) for _ in range(10)]
        user2_snaps = [create_synthetic_snapshot(scale=3.0 + np.random.uniform(-0.05, 0.05)) for _ in range(10)]

        all_snaps = user1_snaps + user2_snaps
        labels = [1] * 10 + [0] * 10

        clf = BehaviouralRandomForestClassifier(n_estimators=30, random_state=42)
        clf.fit(all_snaps, labels)

        pred_user1 = clf.predict_snapshot(user1_snaps[0])
        self.assertEqual(pred_user1["status"], "VERIFIED")
        self.assertEqual(pred_user1["modelType"], "RANDOM_FOREST")

        pred_user2 = clf.predict_snapshot(user2_snaps[0])
        self.assertEqual(pred_user2["status"], "DEVIATION")

    def test_single_class_raises_clear_error(self):
        user1_snaps = [create_synthetic_snapshot() for _ in range(10)]
        labels = [1] * 10
        clf = BehaviouralRandomForestClassifier()
        with self.assertRaises(ValueError):
            clf.fit(user1_snaps, labels)


class TestEvaluationAndDataLeakage(unittest.TestCase):

    def test_group_aware_split_preserves_sessions(self):
        snaps = []
        for sess_id in ["s1", "s2", "s3", "s4"]:
            for _ in range(5):
                snaps.append(create_synthetic_snapshot(session_id=sess_id))

        train_s, test_s, _, _ = group_aware_split(snaps, test_size=0.25, random_state=42)
        train_sessions = {s["session_id"] for s in train_s}
        test_sessions = {s["session_id"] for s in test_s}

        # Zero session leakage
        self.assertTrue(train_sessions.isdisjoint(test_sessions))

    def test_biometric_metrics_calculation(self):
        y_true = [1, 1, 1, 1, 0, 0, 0, 0]
        y_pred = [1, 1, 1, 0, 0, 0, 0, 1]
        y_scores = [0.9, 0.85, 0.8, 0.4, 0.2, 0.1, 0.3, 0.7]

        results = ModelEvaluator.evaluate_predictions(y_true, y_pred, y_scores)
        self.assertEqual(results["status"], "SUCCESS")
        metrics = results["metrics"]
        self.assertIn("false_acceptance_rate", metrics)
        self.assertIn("false_rejection_rate", metrics)
        self.assertIn("roc_auc", metrics)
        self.assertIn("equal_error_rate", metrics)

    def test_single_class_evaluation_returns_unavailable(self):
        y_true = [1, 1, 1, 1]
        y_pred = [1, 1, 1, 1]
        results = ModelEvaluator.evaluate_predictions(y_true, y_pred)
        self.assertEqual(results["status"], "UNAVAILABLE")


class TestVerificationService(unittest.TestCase):

    def test_verification_service_model_not_ready_on_cold_start(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            service = VerificationService(model_dir=tmp_dir)
            status = service.get_model_status()
            self.assertEqual(status["status"], "MODEL_NOT_READY")

            pred = service.verify_snapshot(create_synthetic_snapshot())
            self.assertEqual(pred["status"], "MODEL_NOT_READY")


if __name__ == "__main__":
    unittest.main()
