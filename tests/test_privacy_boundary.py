"""
Cyber Doppelgänger - Automated Privacy Boundary Verification Test
Verifies that identifiable user text (passwords, sentences, keystroke keys, clipboard, URLs)
is NEVER transmitted, ingested, or logged.
"""

import unittest
import json
import urllib.request
import urllib.error
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.privacy.privacy_filter import PrivacyFilter, PrivacyViolationError


class TestPrivacyBoundary(unittest.TestCase):

    def test_privacy_filter_rejects_typed_text(self):
        """Verifies that an identifiable typed sentence is rejected by PrivacyFilter."""
        identifiable_payload = {
            "timestamp": "2026-10-13T10:00:00Z",
            "device_id": "test-workstation",
            "keyboard": {
                "mean_dwell_time_ms": 95.0,
                "mean_flight_time_ms": 120.0,
                "typed_text": "SUPER_SECRET_PASSWORD_123"
            }
        }
        with self.assertRaises(PrivacyViolationError):
            PrivacyFilter.validate_snapshot_dict(identifiable_payload)

    def test_privacy_filter_rejects_passwords_and_urls(self):
        """Verifies that passwords, URLs, and clipboard fields are strictly forbidden."""
        for forbidden_key in ["password", "clipboard", "screenshot", "browser_url", "command_line"]:
            payload = {
                "timestamp": "2026-10-13T10:00:00Z",
                "device_id": "test-workstation",
                forbidden_key: "IDENTIFIABLE_SENSITIVE_DATA_999"
            }
            with self.assertRaises(PrivacyViolationError):
                PrivacyFilter.validate_snapshot_dict(payload)

    def test_privacy_filter_accepts_clean_kinematic_snapshot(self):
        """Verifies that purely numerical aggregated features pass validation."""
        clean_payload = {
            "timestamp": "2026-10-13T10:00:00Z",
            "window_duration_seconds": 60,
            "device_id": "test-workstation",
            "schema_version": "2.0",
            "keyboard": {
                "mean_dwell_time_ms": 92.5,
                "mean_flight_time_ms": 118.2,
                "typing_speed_wpm": 54.0,
                "backspace_rate": 0.04,
                "keystroke_count": 42
            },
            "mouse": {
                "mean_speed_pixels_per_second": 145.0,
                "mean_acceleration": 380.0,
                "jitter_metric": 0.05,
                "movement_efficiency": 0.88,
                "click_count": 5,
                "total_distance_pixels": 650.0
            }
        }
        self.assertTrue(PrivacyFilter.validate_snapshot_dict(clean_payload))

    def test_backend_privacy_api_endpoint_rejection(self):
        """Verifies that backend /api/agent/features strictly rejects identifiable strings."""
        url = "http://localhost:8080/api/agent/features"
        prohibited_payload = {
            "timestamp": "2026-10-13T10:00:00Z",
            "window_duration_seconds": 60,
            "device_id": "privacy-test-device",
            "schema_version": "2.0",
            "features": {
                "keyboard": {
                    "mean_dwell_time_ms": 90.0,
                    "mean_flight_time_ms": 120.0
                },
                "typed_text": "CRITICAL_SECRET_CREDENTIAL_DO_NOT_STORE"
            }
        }
        data = json.dumps(prohibited_payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req) as resp:
                self.fail(f"Expected 400 Bad Request, but received HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            # Backend should return 400 Bad Request with privacy violation
            self.assertEqual(e.code, 400)
            body = e.read().decode("utf-8")
            self.assertIn("Privacy Violation", body)
            self.assertIn("Prohibited content field", body)
            # Ensure the sensitive value itself is NOT in the error message
            self.assertNotIn("CRITICAL_SECRET_CREDENTIAL_DO_NOT_STORE", body)


if __name__ == "__main__":
    unittest.main()
