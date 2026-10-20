"""
Cyber Doppelgänger - Unit Tests for Session Behavioural Features
Tests active duration, idle duration, ratio calculation, and zero-duration safety.
"""

import unittest
import numpy as np

from agent.features.session_features import (
    SessionFeatures,
    calculate_session_features
)


class TestSessionFeatures(unittest.TestCase):

    def test_active_and_idle_durations(self):
        """Calculates active duration and complementary idle duration accurately."""
        # 60s window, 20s typing, 10s mouse
        features = calculate_session_features(
            session_elapsed=120.0,
            window_duration=60.0,
            keyboard_active_sec=20.0,
            mouse_active_sec=10.0,
            idle_threshold_seconds=60.0
        )

        self.assertEqual(features.session_duration, 120.0)
        self.assertGreater(features.active_duration, 0.0)
        self.assertLessEqual(features.active_duration, 60.0)
        self.assertAlmostEqual(features.active_duration + features.idle_duration, 60.0, places=2)
        self.assertAlmostEqual(features.activity_density, features.active_duration / 60.0, places=2)

    def test_zero_duration_edge_cases(self):
        """Zero window duration handles division safely without error."""
        features = calculate_session_features(
            session_elapsed=0.0,
            window_duration=0.0,
            keyboard_active_sec=0.0,
            mouse_active_sec=0.0
        )

        self.assertEqual(features.session_duration, 0.0)
        self.assertFalse(np.isnan(features.active_idle_ratio))
        self.assertFalse(np.isinf(features.active_idle_ratio))
        self.assertFalse(np.isnan(features.activity_density))
        self.assertFalse(np.isinf(features.activity_density))

    def test_complete_inactivity(self):
        """Zero active input results in 100% idle duration and 0 density."""
        features = calculate_session_features(
            session_elapsed=300.0,
            window_duration=60.0,
            keyboard_active_sec=0.0,
            mouse_active_sec=0.0
        )

        self.assertEqual(features.active_duration, 0.0)
        self.assertEqual(features.idle_duration, 60.0)
        self.assertEqual(features.activity_density, 0.0)
        self.assertEqual(features.active_idle_ratio, 0.0)

    def test_no_nan_or_inf_in_dict(self):
        features = calculate_session_features(0.0, 60.0, 0.0, 0.0)
        d = features.to_dict()
        for k, v in d.items():
            if isinstance(v, float):
                self.assertFalse(np.isnan(v), f"Field {k} is NaN")
                self.assertFalse(np.isinf(v), f"Field {k} is Inf")


if __name__ == "__main__":
    unittest.main()
