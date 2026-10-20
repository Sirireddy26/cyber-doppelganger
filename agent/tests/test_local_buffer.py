"""
Cyber Doppelgänger - Unit Tests for Local Buffer
Tests file-based snapshot persistence, reading pending snapshots, and malformed line recovery.
"""

import unittest
import tempfile
import os
from pathlib import Path

from agent.buffering.local_buffer import LocalBuffer
from agent.features.feature_snapshot import FeatureSnapshot
from agent.features.keyboard_features import KeyboardFeatures


class TestLocalBuffer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.buffer_file = os.path.join(self.temp_dir.name, "test_snapshots.jsonl")
        self.buffer = LocalBuffer(file_path=self.buffer_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_write_and_read_snapshot(self):
        """Writes snapshot to buffer and reads it back successfully."""
        snapshot = FeatureSnapshot(
            keyboard=KeyboardFeatures(total_key_events=25)
        )
        success = self.buffer.write_snapshot(snapshot)
        self.assertTrue(success)
        self.assertEqual(self.buffer.count(), 1)

        pending = self.buffer.read_pending_snapshots()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["keyboard"]["total_key_events"], 25)

    def test_recovers_from_corrupted_json_lines(self):
        """Gracefully ignores malformed JSON lines without crashing."""
        # Write 1 valid snapshot
        self.buffer.write_snapshot(FeatureSnapshot(keyboard=KeyboardFeatures(total_key_events=10)))

        # Append corrupted line manually
        with open(self.buffer_file, "a", encoding="utf-8") as f:
            f.write("THIS_IS_NOT_VALID_JSON\n")

        # Write another valid snapshot
        self.buffer.write_snapshot(FeatureSnapshot(keyboard=KeyboardFeatures(total_key_events=20)))

        # Reader should safely return the 2 valid snapshots
        pending = self.buffer.read_pending_snapshots()
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0]["keyboard"]["total_key_events"], 10)
        self.assertEqual(pending[1]["keyboard"]["total_key_events"], 20)


if __name__ == "__main__":
    unittest.main()
