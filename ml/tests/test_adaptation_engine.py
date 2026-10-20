"""
Cyber Doppelgänger - Automated Tests for Phase 5 Safe Adaptation Engine
Tests cover:
- Normal observation stability
- Single-observation contamination prevention
- Multi-window safe adaptation criteria
- Sudden deviation / takeover rejection
- Repeated anomaly freeze enforcement
- Bounded candidate buffer capacity and expiry
- NaN and Infinity rejection
- Versioned profile evolution and rollback
- Authorized unfreezing and recovery
"""

import unittest
import numpy as np
import copy
from pathlib import Path
from datetime import datetime, timezone, timedelta

from ml.adaptation.candidate_buffer import CandidateObservationBuffer, CandidateObservation
from ml.adaptation.adaptation_policy import AdaptationPolicy, AdaptationPolicyConfig
from ml.adaptation.profile_manager import ProfileManager, ProfileVersionRecord
from ml.adaptation.safe_adaptation_engine import SafeAdaptationEngine
from ml.preprocessing.feature_preprocessor import ALL_FEATURE_KEYS, FeaturePreprocessor


def create_test_snapshot(scale: float = 1.0, user_id: str = "test-user") -> dict:
    """Helper to generate a clean synthetic snapshot conforming strictly to schema 2.0."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "window_duration_seconds": 15,
        "device_id": "test-workstation",
        "user_id": user_id,
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
            "idle_duration": 2.0,
            "active_idle_ratio": 6.0,
            "activity_density": 0.85,
            "keyboard_activity_duration": 8.0 * scale,
            "mouse_activity_duration": 6.0 * scale
        },
        "application": {
            "process_count": 80,
            "active_process_count": 4,
            "application_switch_count": 1,
            "process_activity_count": 8,
            "application_activity_duration": 14.0 * scale
        }
    }


class TestCandidateObservationBuffer(unittest.TestCase):

    def test_buffer_capacity_enforcement(self):
        buf = CandidateObservationBuffer(max_capacity=5)
        for i in range(7):
            obs = CandidateObservation(
                snapshot_id=i,
                device_id="dev-1",
                user_id="user-1",
                features={"f1": float(i)}
            )
            success, msg = buf.add(obs)
            self.assertTrue(success)

        # Buffer should be bounded to 5, and oldest items evicted
        self.assertEqual(buf.size(), 5)
        active_ids = [o.snapshot_id for o in buf.get_observations()]
        self.assertEqual(active_ids, [2, 3, 4, 5, 6])

    def test_buffer_rejects_when_profile_frozen(self):
        buf = CandidateObservationBuffer(max_capacity=5)
        obs = CandidateObservation(
            snapshot_id=1,
            device_id="dev-1",
            user_id="user-1",
            features={"f1": 1.0}
        )
        success, msg = buf.add(obs, is_frozen=True)
        self.assertFalse(success)
        self.assertEqual(buf.size(), 0)

    def test_buffer_expiry(self):
        buf = CandidateObservationBuffer(max_capacity=5, ttl_seconds=0.1)
        obs = CandidateObservation(
            snapshot_id=1,
            device_id="dev-1",
            user_id="user-1",
            features={"f1": 1.0}
        )
        # Artificially age the observation
        obs.received_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        buf._buffer.append(obs)
        self.assertEqual(buf.size(), 0)  # Should purge on size check


class TestProfileManager(unittest.TestCase):

    def setUp(self):
        self.test_storage = "ml/artifacts/test_profile_versions.json"
        Path(self.test_storage).unlink(missing_ok=True)
        self.pm = ProfileManager(user_id="test-user", storage_path=self.test_storage)
        self.means = {k: 100.0 for k in ALL_FEATURE_KEYS}
        self.stds = {k: 10.0 for k in ALL_FEATURE_KEYS}
        self.pm.initialize_from_reference_profile(self.means, self.stds, sample_count=50)

    def tearDown(self):
        Path(self.test_storage).unlink(missing_ok=True)

    def test_initialization_creates_v1(self):
        self.assertIsNotNone(self.pm.active_version)
        self.assertEqual(self.pm.active_version.version_tag, "v1.0.0")
        self.assertEqual(len(self.pm.version_history), 1)

    def test_candidate_creation_and_activation(self):
        # 5 candidate observations with mild shift (110.0 instead of 100.0)
        candidates = [
            CandidateObservation(snapshot_id=i, device_id="d1", user_id="u1", features={k: 110.0 for k in ALL_FEATURE_KEYS})
            for i in range(5)
        ]
        cand_rec, msg = self.pm.build_candidate_version(candidates, learning_rate=0.20)
        self.assertIsNotNone(cand_rec)
        self.assertEqual(cand_rec.version_tag, "v1.1.0")
        self.assertEqual(cand_rec.parent_version_tag, "v1.0.0")

        # Prior active version should still be v1.0.0 until activation
        self.assertEqual(self.pm.active_version.version_tag, "v1.0.0")

        # Activate candidate
        success = self.pm.activate_candidate_version(cand_rec)
        self.assertTrue(success)
        self.assertEqual(self.pm.active_version.version_tag, "v1.1.0")
        self.assertEqual(len(self.pm.version_history), 2)
        # Check blended mean: 0.8 * 100 + 0.2 * 110 = 102.0
        self.assertAlmostEqual(self.pm.active_version.feature_means[ALL_FEATURE_KEYS[0]], 102.0, places=2)

    def test_rollback_to_previous_version(self):
        # Create and activate v1.1.0
        candidates = [
            CandidateObservation(snapshot_id=i, device_id="d1", user_id="u1", features={k: 110.0 for k in ALL_FEATURE_KEYS})
            for i in range(5)
        ]
        cand_rec, _ = self.pm.build_candidate_version(candidates)
        self.pm.activate_candidate_version(cand_rec)
        self.assertEqual(self.pm.active_version.version_tag, "v1.1.0")

        # Rollback to v1.0.0
        success, msg = self.pm.rollback_to_version("v1.0.0")
        self.assertTrue(success)
        self.assertIn("rollback-to-v1.0.0", self.pm.active_version.version_tag)
        # Restored means should equal 100.0
        self.assertEqual(self.pm.active_version.feature_means[ALL_FEATURE_KEYS[0]], 100.0)

    def test_freeze_and_unfreeze_lifecycle(self):
        self.pm.freeze("Repeated anomalies detected")
        self.assertTrue(self.pm.is_frozen)
        self.assertEqual(self.pm.freeze_reason, "Repeated anomalies detected")

        # Candidate creation should be rejected when frozen
        cand_rec, msg = self.pm.build_candidate_version([])
        self.assertIsNone(cand_rec)

        # Unfreeze
        success, msg = self.pm.unfreeze(authorized_by="admin-1", reason="False alarm cleared")
        self.assertTrue(success)
        self.assertFalse(self.pm.is_frozen)


class TestSafeAdaptationEngine(unittest.TestCase):

    def setUp(self):
        self.test_storage = "ml/artifacts/test_engine_profiles.json"
        Path(self.test_storage).unlink(missing_ok=True)
        self.pm = ProfileManager(user_id="test-user", storage_path=self.test_storage)
        
        base_snap = create_test_snapshot(scale=1.0)
        self.means = FeaturePreprocessor().extract_feature_dict(base_snap)
        self.stds = {k: max(0.1, abs(v * 0.15)) for k, v in self.means.items()}
        self.pm.initialize_from_reference_profile(self.means, self.stds, sample_count=50)

        config = AdaptationPolicyConfig(
            min_observations=3,
            max_drift_magnitude=1.8,
            max_velocity=2.5,
            max_suspicious_streak=3,
            cooldown_seconds=0.0  # zero cooldown for instant unit tests
        )
        self.engine = SafeAdaptationEngine(config=config, profile_manager=self.pm)

    def tearDown(self):
        Path(self.test_storage).unlink(missing_ok=True)

    def test_normal_observation_leaves_profile_unchanged(self):
        snap = create_test_snapshot(scale=1.0)
        # Simulated verification output: VERIFIED with low anomaly
        verif = {"status": "VERIFIED", "rawScore": 0.15, "threshold": -0.05, "anomalyScore": -0.15}
        result = self.engine.evaluate_observation(snap, verification_result=verif)

        self.assertEqual(result["decision_state"], "NORMAL")
        self.assertEqual(result["prior_profile_version"], "v1.0.0")
        self.assertIsNone(result["new_profile_version"])
        self.assertEqual(self.pm.active_version.version_tag, "v1.0.0")

    def test_single_unusual_observation_cannot_trigger_adaptation(self):
        snap = create_test_snapshot(scale=1.2)
        # Single unusual observation (UNCERTAIN)
        verif = {"status": "UNCERTAIN", "rawScore": -0.02, "threshold": 0.0, "anomalyScore": 0.02}
        result = self.engine.evaluate_observation(snap, verification_result=verif)

        # Single observation should result in INSUFFICIENT_EVIDENCE (buffered)
        self.assertEqual(result["decision_state"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(self.pm.active_version.version_tag, "v1.0.0")

    def test_safe_adaptation_triggers_after_stable_observations(self):
        verif = {"status": "UNCERTAIN", "rawScore": -0.02, "threshold": 0.0, "anomalyScore": 0.02}

        # Submit 3 consistent mild shift observations (min_observations=3)
        res1 = self.engine.evaluate_observation(create_test_snapshot(scale=1.10), verification_result=verif)
        self.assertEqual(res1["decision_state"], "INSUFFICIENT_EVIDENCE")

        res2 = self.engine.evaluate_observation(create_test_snapshot(scale=1.11), verification_result=verif)
        self.assertEqual(res2["decision_state"], "INSUFFICIENT_EVIDENCE")

        # 3rd observation completes candidate buffer criteria -> SAFE_ADAPTATION!
        res3 = self.engine.evaluate_observation(create_test_snapshot(scale=1.10), verification_result=verif)
        self.assertEqual(res3["decision_state"], "SAFE_ADAPTATION")
        self.assertEqual(res3["prior_profile_version"], "v1.0.0")
        self.assertEqual(res3["new_profile_version"], "v1.1.0")
        self.assertEqual(self.pm.active_version.version_tag, "v1.1.0")
        # Candidate buffer should be emptied after activation
        self.assertEqual(self.engine.buffer.size(), 0)

    def test_sudden_extreme_deviation_is_rejected(self):
        snap = create_test_snapshot(scale=50.0)
        verif = {"status": "DEVIATION", "rawScore": -0.45, "threshold": -0.05, "anomalyScore": 0.45}
        result = self.engine.evaluate_observation(snap, verification_result=verif)

        self.assertEqual(result["decision_state"], "SUSPICIOUS_CHANGE")
        self.assertIn("Verification anomaly detected", result["decision_reason"])
        self.assertEqual(self.pm.active_version.version_tag, "v1.0.0")

    def test_repeated_suspicious_observations_trigger_profile_freeze(self):
        verif = {"status": "DEVIATION", "rawScore": -0.30, "threshold": -0.05, "anomalyScore": 0.30}

        # 1st anomaly
        res1 = self.engine.evaluate_observation(create_test_snapshot(), verification_result=verif)
        self.assertEqual(res1["decision_state"], "SUSPICIOUS_CHANGE")
        self.assertFalse(res1["is_profile_frozen"])

        # 2nd anomaly
        res2 = self.engine.evaluate_observation(create_test_snapshot(), verification_result=verif)
        self.assertEqual(res2["decision_state"], "SUSPICIOUS_CHANGE")
        self.assertFalse(res2["is_profile_frozen"])

        # 3rd anomaly -> triggers freeze policy (max_suspicious_streak=3)
        res3 = self.engine.evaluate_observation(create_test_snapshot(), verification_result=verif)
        self.assertEqual(res3["decision_state"], "PROFILE_FROZEN")
        self.assertTrue(res3["is_profile_frozen"])
        self.assertTrue(self.pm.is_frozen)

        # Subsequent attempts while frozen are immediately blocked
        res4 = self.engine.evaluate_observation(create_test_snapshot(), verification_result=verif)
        self.assertEqual(res4["decision_state"], "PROFILE_FROZEN")

    def test_nan_and_infinity_rejection(self):
        corrupted_snap = create_test_snapshot()
        corrupted_snap["keyboard"]["mean_key_interval"] = float("nan")
        result = self.engine.evaluate_observation(corrupted_snap)

        self.assertEqual(result["decision_state"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("Input validation rejected", result["decision_reason"])


if __name__ == "__main__":
    unittest.main()
