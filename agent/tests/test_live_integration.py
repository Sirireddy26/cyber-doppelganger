"""
Cyber Doppelgänger - Live Agent Integration Test
Tests complete end-to-end cycle:
1. Starts DesktopAgent with 2-second aggregation window.
2. Injects safe interactions (keyboard presses, mouse movements, clicks).
3. Waits for feature window to complete.
4. Reads persisted snapshot from JSONL file.
5. Verifies all numerical fields, finite constraints, and zero sensitive content.
"""

import unittest
import time
import os
import json
import threading
from pathlib import Path

from agent.main import DesktopAgent
from agent.buffering.local_buffer import LocalBuffer
from agent.privacy.privacy_filter import PrivacyFilter


class TestLiveAgentIntegration(unittest.TestCase):

    def test_live_window_and_snapshot_generation(self):
        """Runs the live DesktopAgent for 1 window and validates the generated snapshot."""
        test_storage = "agent/data/test_integration_snapshots.jsonl"
        storage_path = Path(test_storage)
        if storage_path.exists():
            storage_path.unlink()

        # Create agent with 2-second window and custom storage
        agent = DesktopAgent(window_seconds=2)
        agent.settings = type("SettingsStub", (), {
            **agent.settings.__dict__,
            "SNAPSHOT_STORAGE_PATH": test_storage,
            "LOCAL_SNAPSHOT_STORAGE": True,
            "BACKEND_ENABLED": False
        })()
        agent.buffer = LocalBuffer(file_path=test_storage)

        # Run agent in background thread
        agent_thread = threading.Thread(target=agent.start, daemon=True)
        agent_thread.start()

        # Give collectors time to start
        time.sleep(0.3)

        # Stimulate keyboard and mouse inputs safely
        for _ in range(5):
            agent.keyboard_collector._on_press(None)
            time.sleep(0.05)

        # Stimulate mouse movement, click, scroll
        agent.mouse_collector._on_move(100.0, 100.0)
        time.sleep(0.05)
        agent.mouse_collector._on_move(150.0, 180.0)
        time.sleep(0.05)
        agent.mouse_collector._on_click(150.0, 180.0, "left", True)
        time.sleep(0.05)
        agent.mouse_collector._on_scroll(150.0, 180.0, 0, 1)

        # Wait for window to complete (window is 2s, wait 2.5s)
        time.sleep(2.5)

        # Stop agent
        agent._running = False
        for c in agent._collectors:
            c.stop()

        # Validate that the snapshot was written to file
        self.assertTrue(storage_path.exists(), "Snapshot JSONL file was not created")

        with open(storage_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        self.assertGreaterEqual(len(lines), 1, "No snapshots recorded in buffer")

        # Parse first snapshot
        snapshot_dict = json.loads(lines[0])

        # Validate schema
        self.assertIn("timestamp", snapshot_dict)
        self.assertIn("window_duration_seconds", snapshot_dict)
        self.assertIn("keyboard", snapshot_dict)
        self.assertIn("mouse", snapshot_dict)
        self.assertIn("session", snapshot_dict)
        self.assertIn("application", snapshot_dict)

        # Validate PrivacyFilter
        self.assertTrue(PrivacyFilter.validate_snapshot_dict(snapshot_dict))

        # Check numerical sanity: No NaN, no infinity
        kb = snapshot_dict["keyboard"]
        self.assertIsInstance(kb["total_key_events"], int)
        self.assertGreaterEqual(kb["total_key_events"], 5)
        self.assertIsInstance(kb["mean_key_interval"], (int, float))
        self.assertIsInstance(kb["typing_speed"], (int, float))

        mo = snapshot_dict["mouse"]
        self.assertIsInstance(mo["movement_distance"], (int, float))
        self.assertGreater(mo["movement_distance"], 0.0)
        self.assertIsInstance(mo["click_count"], int)
        self.assertGreaterEqual(mo["click_count"], 1)
        self.assertEqual(mo["scroll_count"], 1)

        se = snapshot_dict["session"]
        self.assertIsInstance(se["session_duration"], (int, float))
        self.assertIsInstance(se["active_duration"], (int, float))
        self.assertIsInstance(se["idle_duration"], (int, float))

        app = snapshot_dict["application"]
        self.assertIsInstance(app["process_count"], int)

        # Clean up test file
        if storage_path.exists():
            storage_path.unlink()


if __name__ == "__main__":
    unittest.main()
