"""
Cyber Doppelgänger - Desktop Agent Unit Tests
Tests configuration, privacy guard, collector lifecycles, and health status.
"""

import unittest
import sys
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from agent.configuration.settings import settings
from agent.privacy.privacy_guard import PrivacyGuard, PrivacyViolationError
from agent.collectors.keyboard.keyboard_collector import KeyboardCollector
from agent.collectors.mouse.mouse_collector import MouseCollector
from agent.collectors.application.application_collector import ApplicationCollector
from agent.collectors.session.session_collector import SessionCollector
from agent.buffering.buffer import EventBuffer
from agent.main import DesktopAgent


class TestAgentFoundation(unittest.TestCase):

    def test_settings_loaded(self):
        self.assertIsNotNone(settings.AGENT_NAME)
        self.assertFalse(settings.ALLOW_KEYSTROKE_LOGGING)
        self.assertFalse(settings.ALLOW_SCREEN_CAPTURE)
        self.assertFalse(settings.ALLOW_CLIPBOARD_INSPECTION)

    def test_privacy_guard_allows_safe_metrics(self):
        safe_event = {"dwell_time_ms": 115.0, "event_type": 1.0}
        sanitized = PrivacyGuard.sanitize_event(safe_event)
        self.assertEqual(sanitized["dwell_time_ms"], 115.0)

    def test_privacy_guard_blocks_character_logging(self):
        violation_event = {"char": "p", "dwell_time_ms": 115.0}
        with self.assertRaises(PrivacyViolationError):
            PrivacyGuard.sanitize_event(violation_event)

    def test_privacy_guard_blocks_screenshot_data(self):
        violation_event = {"screenshot": "binary_data"}
        with self.assertRaises(PrivacyViolationError):
            PrivacyGuard.sanitize_event(violation_event)

    def test_collector_lifecycle(self):
        kb = KeyboardCollector()
        self.assertFalse(kb.is_active)
        kb.start()
        self.assertTrue(kb.is_active)
        status = kb.get_status()
        self.assertTrue(status["collection_enabled"])
        kb.stop()
        self.assertFalse(kb.is_active)

    def test_buffer_capacity(self):
        buf = EventBuffer(max_capacity=5)
        for i in range(10):
            buf.add({"event_id": i})
        self.assertEqual(buf.size(), 5)
        flushed = buf.flush()
        self.assertEqual(len(flushed), 5)
        self.assertEqual(buf.size(), 0)

    def test_desktop_agent_health(self):
        agent = DesktopAgent()
        health = agent.get_health_status()
        self.assertTrue(health["privacy_guard_enforced"])
        self.assertEqual(health["privacy_mode"], "ENABLED")
        self.assertIn("keyboard_collector", health)
        self.assertIn("mouse_collector", health)


if __name__ == "__main__":
    unittest.main()
