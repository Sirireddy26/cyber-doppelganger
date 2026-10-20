"""
Cyber Doppelgänger - Unit Tests for Keyboard Behavioural Features
Tests timing extraction, pause detection, speed calculation, and edge cases.
"""

import unittest
import numpy as np

from agent.features.keyboard_features import (
    KeyboardFeatures,
    calculate_keyboard_features
)


class TestKeyboardFeatures(unittest.TestCase):

    def test_empty_events(self):
        """Empty events list must produce valid zeroed features with no NaN/inf."""
        features = calculate_keyboard_features([])
        self.assertEqual(features.total_key_events, 0)
        self.assertEqual(features.mean_key_interval, 0.0)
        self.assertEqual(features.typing_speed, 0.0)
        self.assertEqual(features.pause_count, 0)
        self.assertFalse(np.isnan(features.mean_key_interval))
        self.assertFalse(np.isinf(features.mean_key_interval))

    def test_single_event(self):
        """Single event has no interval but records count of 1."""
        features = calculate_keyboard_features([100.0])
        self.assertEqual(features.total_key_events, 1)
        self.assertEqual(features.mean_key_interval, 0.0)
        self.assertEqual(features.typing_speed, 0.0)
        self.assertEqual(features.pause_count, 0)

    def test_multiple_events_normal_typing(self):
        """Calculates correct intervals, speed, and standard deviation."""
        # Timestamps at 0.0, 0.2, 0.4, 0.6, 0.8 (intervals = 0.2s each)
        timestamps = [10.0, 10.2, 10.4, 10.6, 10.8]
        features = calculate_keyboard_features(timestamps, pause_threshold_seconds=1.0)

        self.assertEqual(features.total_key_events, 5)
        self.assertAlmostEqual(features.mean_key_interval, 0.2, places=3)
        self.assertAlmostEqual(features.median_key_interval, 0.2, places=3)
        self.assertAlmostEqual(features.minimum_key_interval, 0.2, places=3)
        self.assertAlmostEqual(features.maximum_key_interval, 0.2, places=3)
        self.assertEqual(features.pause_count, 0)
        self.assertGreater(features.typing_speed, 0.0)

    def test_pause_detection(self):
        """Detects pauses when inter-key gap exceeds threshold."""
        # Fast typing, 2.5s pause, then fast typing
        timestamps = [1.0, 1.2, 1.4, 3.9, 4.1]
        features = calculate_keyboard_features(timestamps, pause_threshold_seconds=1.0)

        self.assertEqual(features.total_key_events, 5)
        self.assertEqual(features.pause_count, 1)
        self.assertAlmostEqual(features.longest_pause, 2.5, places=2)
        self.assertAlmostEqual(features.mean_pause_duration, 2.5, places=2)

    def test_invalid_negative_interval_handling(self):
        """Clock anomalies or non-monotonic timestamps are handled safely."""
        # Unsorted or backwards timestamps
        timestamps = [5.0, 2.0, 4.0, 3.0]
        features = calculate_keyboard_features(timestamps)

        self.assertEqual(features.total_key_events, 4)
        self.assertFalse(np.isnan(features.mean_key_interval))
        self.assertFalse(np.isinf(features.mean_key_interval))
        self.assertGreaterEqual(features.mean_key_interval, 0.0)

    def test_no_nan_or_infinity_in_dict(self):
        """to_dict() must return strictly finite numbers."""
        features = calculate_keyboard_features([])
        d = features.to_dict()
        for k, v in d.items():
            if isinstance(v, float):
                self.assertFalse(np.isnan(v), f"Field {k} is NaN")
                self.assertFalse(np.isinf(v), f"Field {k} is Inf")


if __name__ == "__main__":
    unittest.main()
