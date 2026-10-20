"""
Cyber Doppelgänger - Unit & Privacy Policy Tests
CRITICAL RESEARCH VERIFICATION: Enforces Zero-Content Biometrics.

Demonstrates and verifies:
1. When keyboard events are stimulated (e.g. key 'A' or 'SecretPassword123'),
   the final FeatureSnapshot NEVER contains 'A', 'a', 'key': 'A', or typed characters.
2. The final snapshot contains strictly derived numerical timing statistics.
3. System logs never output the typed character or password.
4. Forbidden fields (passwords, screenshots, clipboard, URLs) are rejected by PrivacyFilter.
"""

import unittest
import io
import json
import logging
from unittest.mock import MagicMock

from agent.privacy.privacy_filter import PrivacyFilter, PrivacyViolationError
from agent.collectors.keyboard.keyboard_collector import KeyboardCollector
from agent.features.feature_snapshot import FeatureSnapshot
from agent.features.keyboard_features import calculate_keyboard_features


class TestPrivacyEnforcement(unittest.TestCase):

    def test_keystroke_character_never_enters_snapshot_or_logs(self):
        """
        CRITICAL TEST (Section 28):
        Simulate keyboard events where a user types 'A' and 'SecretPass'.
        Verify:
        - The keyboard collector callback never captures the key content.
        - The resulting FeatureSnapshot does not contain 'A', 'a', or 'SecretPass'.
        - Logging does not output the sensitive key.
        """
        # Setup log capture
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        agent_logger = logging.getLogger("cyber-doppelganger.agent")
        agent_logger.addHandler(handler)
        agent_logger.setLevel(logging.DEBUG)

        try:
            collector = KeyboardCollector()
            
            # Simulate key presses with mock keys representing 'A' and 'SecretPass'
            mock_key_A = MagicMock()
            mock_key_A.char = 'A'
            mock_key_A.name = 'a'

            mock_key_B = MagicMock()
            mock_key_B.char = 'SecretPass'

            # Trigger raw collector callback
            collector._on_press(mock_key_A)
            collector._on_press(mock_key_B)

            # Extract features from collector
            features = collector.extract_features()
            self.assertEqual(features.total_key_events, 2)

            # Build FeatureSnapshot
            snapshot = FeatureSnapshot(
                keyboard=features,
                window_duration_seconds=60
            )
            snapshot_dict = snapshot.to_dict()
            snapshot_json = snapshot.to_json()

            # 1. Inspect snapshot dictionary keys and string values
            def _assert_no_sensitive_value(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        self.assertNotIn("A", str(k), "Forbidden key name found in snapshot")
                        self.assertNotIn("char", str(k).lower(), "Forbidden key name found in snapshot")
                        self.assertNotIn("password", str(k).lower(), "Forbidden key name found in snapshot")
                        _assert_no_sensitive_value(v)
                elif isinstance(obj, list):
                    for item in obj:
                        _assert_no_sensitive_value(item)
                elif isinstance(obj, str):
                    self.assertNotIn("SecretPass", obj)
                    # Characters 'A' or 'a' must not be stored as single character content representations
                    self.assertNotEqual(obj, "A")
                    self.assertNotEqual(obj, "a")

            _assert_no_sensitive_value(snapshot_dict)

            # 2. Inspect raw serialized JSON
            self.assertNotIn('"key":', snapshot_json)
            self.assertNotIn('"char":', snapshot_json)
            self.assertNotIn('"A"', snapshot_json)
            self.assertNotIn('"SecretPass"', snapshot_json)
            self.assertNotIn('"text":', snapshot_json)

            # 3. Inspect logs
            log_output = log_stream.getvalue()
            self.assertNotIn("SecretPass", log_output)
            self.assertNotIn("char 'A'", log_output)

        finally:
            agent_logger.removeHandler(handler)

    def test_privacy_filter_blocks_forbidden_fields(self):
        """Privacy filter rejects any dictionary containing prohibited fields."""
        prohibited_samples = [
            {"char": "a"},
            {"key_name": "Return"},
            {"text": "my search"},
            {"typed_text": "hello"},
            {"password": "secret"},
            {"clipboard": "copied data"},
            {"screenshot": b"binary"},
            {"browser_url": "https://bank.com"},
            {"window_title": "Document - Microsoft Word"},
            {"document_content": "Internal document"}
        ]

        for sample in prohibited_samples:
            with self.assertRaises(PrivacyViolationError, msg=f"Failed to reject {sample}"):
                PrivacyFilter.sanitize_event(sample)

    def test_privacy_filter_validates_nested_snapshot(self):
        """Privacy filter recursively inspects nested dictionaries inside snapshots."""
        valid_snapshot = {
            "timestamp": "2026-10-08T12:00:00Z",
            "window_duration_seconds": 60,
            "keyboard": {"total_key_events": 10, "mean_key_interval": 0.15},
            "mouse": {"movement_distance": 500.0, "click_count": 3},
            "session": {"session_duration": 60.0, "active_duration": 30.0},
            "application": {"process_count": 150}
        }
        self.assertTrue(PrivacyFilter.validate_snapshot_dict(valid_snapshot))

        # Tampered snapshot with nested password
        invalid_snapshot = dict(valid_snapshot)
        invalid_snapshot["keyboard"] = {"total_key_events": 10, "password": "leak"}
        with self.assertRaises(PrivacyViolationError):
            PrivacyFilter.validate_snapshot_dict(invalid_snapshot)

    def test_privacy_filter_never_logs_sensitive_value(self):
        """When rejecting forbidden fields, logs must NEVER print the sensitive payload."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        agent_logger = logging.getLogger("cyber-doppelganger.agent")
        agent_logger.addHandler(handler)

        try:
            secret_value = "SUPER_SECRET_PAYLOAD_998877"
            try:
                PrivacyFilter.sanitize_event({"password": secret_value})
            except PrivacyViolationError:
                pass

            logs = log_stream.getvalue()
            # Must NOT contain the secret value in logs
            self.assertNotIn(secret_value, logs)
        finally:
            agent_logger.removeHandler(handler)


if __name__ == "__main__":
    unittest.main()
