"""
Cyber Doppelgänger - Unit Tests for Mouse Behavioural Features
Tests movement kinematics, click counting, scroll tracking, and edge cases.
"""

import unittest
import numpy as np

from agent.features.mouse_features import (
    MouseFeatures,
    calculate_mouse_features
)


class TestMouseFeatures(unittest.TestCase):

    def test_no_movement_no_clicks(self):
        """Empty input data produces safe zeroed metrics without NaN/inf."""
        features = calculate_mouse_features([], [], [])
        self.assertEqual(features.movement_distance, 0.0)
        self.assertEqual(features.mean_mouse_speed, 0.0)
        self.assertEqual(features.click_count, 0)
        self.assertEqual(features.scroll_count, 0)
        self.assertFalse(np.isnan(features.mean_mouse_speed))

    def test_normal_movement_kinematics(self):
        """Valid movements calculate correct distance, speed, and acceleration."""
        # 3 movements: (dist=100px, dt=0.5s, speed=200px/s)
        movements = [
            (100.0, 0.5, 200.0),
            (150.0, 0.5, 300.0),
            (50.0, 0.5, 100.0)
        ]
        features = calculate_mouse_features(movements, [], [])

        self.assertAlmostEqual(features.movement_distance, 300.0, places=2)
        self.assertAlmostEqual(features.mean_mouse_speed, 200.0, places=2)
        self.assertGreater(features.mouse_speed_std, 0.0)
        self.assertGreater(features.mean_acceleration, 0.0)

    def test_zero_time_interval_protection(self):
        """Zero dt is handled gracefully without division by zero or NaN."""
        movements = [
            (50.0, 0.0, 0.0),
            (100.0, 0.2, 500.0)
        ]
        features = calculate_mouse_features(movements, [], [])
        self.assertFalse(np.isnan(features.mean_mouse_speed))
        self.assertFalse(np.isinf(features.mean_mouse_speed))

    def test_click_counting_and_intervals(self):
        """Accurately tallies left, right, middle clicks and computes click intervals."""
        clicks = [
            (1.0, "left"),
            (1.5, "left"),
            (2.0, "right"),
            (3.0, "middle")
        ]
        features = calculate_mouse_features([], clicks, [])

        self.assertEqual(features.click_count, 4)
        self.assertEqual(features.left_click_count, 2)
        self.assertEqual(features.right_click_count, 1)
        self.assertEqual(features.middle_click_count, 1)
        # Intervals: 0.5, 0.5, 1.0 -> mean = 2.0 / 3 = 0.6667
        self.assertAlmostEqual(features.mean_click_interval, 0.6667, places=3)

    def test_scroll_counting(self):
        """Counts positive (up) and negative (down) scroll events."""
        scrolls = [
            (1.0, 0, 1),
            (1.1, 0, 1),
            (1.2, 0, -1),
            (1.3, 0, -1),
            (1.4, 0, -1)
        ]
        features = calculate_mouse_features([], [], scrolls)

        self.assertEqual(features.scroll_count, 5)
        self.assertEqual(features.positive_scroll_count, 2)
        self.assertEqual(features.negative_scroll_count, 3)

    def test_no_nan_or_infinity_in_dict(self):
        features = calculate_mouse_features([], [], [])
        d = features.to_dict()
        for k, v in d.items():
            if isinstance(v, float):
                self.assertFalse(np.isnan(v), f"Field {k} is NaN")
                self.assertFalse(np.isinf(v), f"Field {k} is Inf")


if __name__ == "__main__":
    unittest.main()
