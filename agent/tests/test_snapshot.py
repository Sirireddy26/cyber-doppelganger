"""
Cyber Doppelgänger - Unit Tests for FeatureSnapshot
Tests schema structure, serialization, deserialization, and numerical integrity.
"""

import unittest
import json
import numpy as np

from agent.features.feature_snapshot import FeatureSnapshot
from agent.features.keyboard_features import KeyboardFeatures
from agent.features.mouse_features import MouseFeatures
from agent.features.session_features import SessionFeatures
from agent.features.application_features import ApplicationFeatures


class TestFeatureSnapshot(unittest.TestCase):

    def test_default_snapshot_initialization(self):
        """Default snapshot is valid, contains timestamp and zeroed sub-models."""
        snapshot = FeatureSnapshot()
        self.assertIsNotNone(snapshot.timestamp)
        self.assertEqual(snapshot.window_duration_seconds, 60)
        self.assertIsInstance(snapshot.keyboard, KeyboardFeatures)
        self.assertIsInstance(snapshot.mouse, MouseFeatures)
        self.assertIsInstance(snapshot.session, SessionFeatures)
        self.assertIsInstance(snapshot.application, ApplicationFeatures)

    def test_json_serialization_and_deserialization(self):
        """Serializes to JSON and parses back cleanly with identical values."""
        snapshot = FeatureSnapshot(
            window_duration_seconds=30,
            device_id="test-laptop",
            user_id="alice",
            keyboard=KeyboardFeatures(total_key_events=42, mean_key_interval=0.18),
            mouse=MouseFeatures(movement_distance=1250.5, click_count=8),
            session=SessionFeatures(session_duration=300.0, active_duration=25.0),
            application=ApplicationFeatures(process_count=180, application_switch_count=3)
        )

        json_str = snapshot.to_json()
        self.assertIsInstance(json_str, str)

        # Deserialize back
        recovered = FeatureSnapshot.from_json(json_str)
        self.assertEqual(recovered.window_duration_seconds, 30)
        self.assertEqual(recovered.device_id, "test-laptop")
        self.assertEqual(recovered.keyboard.total_key_events, 42)
        self.assertEqual(recovered.mouse.movement_distance, 1250.5)
        self.assertEqual(recovered.application.application_switch_count, 3)

    def test_no_nan_or_infinity_in_serialized_json(self):
        """Simulate NaN or infinity values and verify sanitization to 0.0."""
        snapshot = FeatureSnapshot(
            keyboard=KeyboardFeatures(
                mean_key_interval=float("nan"),
                typing_speed=float("inf")
            )
        )

        d = snapshot.to_dict()
        self.assertEqual(d["keyboard"]["mean_key_interval"], 0.0)
        self.assertEqual(d["keyboard"]["typing_speed"], 0.0)

        json_str = snapshot.to_json()
        self.assertNotIn("NaN", json_str)
        self.assertNotIn("Infinity", json_str)


if __name__ == "__main__":
    unittest.main()
