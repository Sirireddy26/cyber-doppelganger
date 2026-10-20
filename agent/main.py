"""
Cyber Doppelgänger - Desktop Behavioural Agent
Main Entry Point & Lifecycle Controller

Phase 2: Privacy-Safe Desktop Behavioural Agent
Continuously monitors user interaction dynamics (keyboard timing, mouse kinematics,
session continuity, system process load) WITHOUT recording any user content.
Produces periodic privacy-validated FeatureSnapshots stored locally in JSONL.
"""

import sys
import os

# Ensure cyber-doppelganger root is at sys.path[0] and remove local directory to prevent package shadowing
_agent_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = os.path.dirname(_agent_dir)
if _agent_dir in sys.path:
    sys.path.remove(_agent_dir)
if _project_dir not in sys.path:
    sys.path.insert(0, _project_dir)

import signal
import threading
import time
import argparse
import logging
from typing import Dict, Any, Optional

from agent.configuration.settings import settings
from agent.logging.logger import logger
from agent.privacy.privacy_filter import PrivacyFilter, PrivacyViolationError
from agent.buffering.local_buffer import LocalBuffer
from agent.communication.api_client import ApiClient
from agent.collectors.keyboard.keyboard_collector import KeyboardCollector
from agent.collectors.mouse.mouse_collector import MouseCollector
from agent.collectors.application.application_collector import ApplicationCollector
from agent.collectors.session.session_collector import SessionCollector
from agent.features.feature_snapshot import FeatureSnapshot


class DesktopAgent:
    """Central manager for the Cyber Doppelgänger Desktop Behavioural Agent."""

    def __init__(self, window_seconds: Optional[int] = None):
        self.settings = settings
        self.window_duration = window_seconds or self.settings.AGGREGATION_WINDOW_SECONDS
        self.client = ApiClient()
        self.buffer = LocalBuffer(file_path=self.settings.SNAPSHOT_STORAGE_PATH)
        self._running = False
        self._shutdown_initiated = False

        # Initialize privacy-safe behavioural collectors
        self.keyboard_collector = KeyboardCollector(
            pause_threshold_seconds=self.settings.KEYBOARD_PAUSE_THRESHOLD_SECONDS
        )
        self.mouse_collector = MouseCollector()
        self.application_collector = ApplicationCollector()
        self.session_collector = SessionCollector(
            idle_threshold_seconds=self.settings.IDLE_THRESHOLD_SECONDS
        )

        self._collectors = [
            self.keyboard_collector,
            self.mouse_collector,
            self.application_collector,
            self.session_collector
        ]
        self._total_windows_completed = 0

    def get_health_status(self) -> Dict[str, Any]:
        """Evaluates health and returns diagnostic dictionary."""
        backend_check = self.client.check_health() if self.settings.BACKEND_ENABLED else {
            "connected": False,
            "message": "Backend disabled in configuration"
        }

        # Validate Privacy Filter enforcement
        privacy_test_passed = False
        try:
            PrivacyFilter.sanitize_event({"mean_key_interval": 0.18})
            try:
                PrivacyFilter.sanitize_event({"typed_text": "hello"})
            except PrivacyViolationError:
                privacy_test_passed = True
        except Exception:
            privacy_test_passed = False

        def _collector_state(c) -> str:
            if not c.is_active:
                return "READY" if not self._running else "STOPPED"
            return "RUNNING"

        return {
            "agent_status": "RUNNING" if self._running else "READY",
            "keyboard_collector": _collector_state(self.keyboard_collector),
            "mouse_collector": _collector_state(self.mouse_collector),
            "session_collector": _collector_state(self.session_collector),
            "application_collector": _collector_state(self.application_collector),
            "privacy_mode": "ENABLED",
            "privacy_guard_enforced": privacy_test_passed,
            "backend_enabled": self.settings.BACKEND_ENABLED,
            "backend_connected": backend_check.get("connected", False),
            "storage_path": self.settings.SNAPSHOT_STORAGE_PATH,
            "buffered_snapshots": self.buffer.count(),
            "windows_completed": self._total_windows_completed,
            "phase": "Phase 2 - Privacy-Safe Behavioural Agent"
        }

    def _process_feature_window(self) -> Optional[FeatureSnapshot]:
        """
        Executes an aggregation cycle:
        1. Flushes transient event metrics from all collectors.
        2. Computes derived statistical features.
        3. Constructs a FeatureSnapshot.
        4. Validates snapshot against strict privacy rules.
        5. Persists to local buffer and optionally forwards to backend.
        """
        try:
            # Extract features from collectors
            kb_features = self.keyboard_collector.extract_features()
            mo_features = self.mouse_collector.extract_features()
            app_features = self.application_collector.extract_features()
            
            # Session features use active durations from keyboard & mouse
            sess_features = self.session_collector.extract_features(
                window_duration=self.window_duration,
                keyboard_active_sec=kb_features.typing_activity_duration,
                mouse_active_sec=mo_features.mouse_active_duration
            )

            # Build candidate FeatureSnapshot
            snapshot = FeatureSnapshot(
                window_duration_seconds=self.window_duration,
                device_id=self.settings.DEVICE_ID,
                user_id=self.settings.USER_ID,
                keyboard=kb_features,
                mouse=mo_features,
                session=sess_features,
                application=app_features
            )

            # 4. Strict Privacy Validation
            snapshot_dict = snapshot.to_dict()
            PrivacyFilter.validate_snapshot_dict(snapshot_dict)

            # 5. Local Storage (JSONL)
            if self.settings.LOCAL_SNAPSHOT_STORAGE:
                self.buffer.write_snapshot(snapshot)

            # 6. Optional Backend Forwarding
            if self.settings.BACKEND_ENABLED:
                self.client.send_snapshot(snapshot)

            self._total_windows_completed += 1

            # Log safe aggregated summary (Strictly counts and durations, NO content)
            logger.info("--------------------------------------------------")
            logger.info(f"Feature window #{self._total_windows_completed} completed ({self.window_duration}s).")
            logger.info(f"  Keyboard events: {kb_features.total_key_events} (speed: {kb_features.typing_speed:.2f} evt/s, pauses: {kb_features.pause_count})")
            logger.info(f"  Mouse distance: {mo_features.movement_distance:.1f}px, Clicks: {mo_features.click_count}, Scrolls: {mo_features.scroll_count}")
            logger.info(f"  Session active: {sess_features.active_duration:.1f}s, Idle: {sess_features.idle_duration:.1f}s (Density: {sess_features.activity_density:.2f})")
            logger.info(f"  System processes: {app_features.process_count}, App switches: {app_features.application_switch_count}")
            logger.info("--------------------------------------------------")

            return snapshot

        except Exception as e:
            logger.error(f"Error during feature window processing: {e}")
            return None

    def start(self) -> None:
        """Starts the agent lifecycle and runs periodic aggregation windows."""
        print("==================================================")
        print("Cyber Doppelganger Behavioural Agent")
        print("Safe Adaptive Behavioural Identity & Continuous Verification")
        print("==================================================")
        print(f"Privacy mode:          ENABLED (Zero Content Surveillance)")
        print(f"Backend communication: {'ENABLED' if self.settings.BACKEND_ENABLED else 'DISABLED'}")
        print(f"Aggregation window:    {self.window_duration} seconds")
        print(f"Storage target:        {self.settings.SNAPSHOT_STORAGE_PATH}")
        print("")
        print("Collectors:")
        print("  Keyboard:    READY (Timing intervals only)")
        print("  Mouse:       READY (Kinematics & interaction rates)")
        print("  Session:     READY (Active/idle continuity)")
        print("  Application: READY (Anonymous PID context switches)")
        print("")
        print("Status: MONITORING (Press Ctrl+C to terminate cleanly)")
        print("==================================================")

        # Register signal handlers for clean OS shutdown if in main thread
        if threading.current_thread() is threading.main_thread():
            try:
                signal.signal(signal.SIGINT, self._handle_shutdown)
                signal.signal(signal.SIGTERM, self._handle_shutdown)
            except (ValueError, AttributeError):
                pass

        # Start collectors
        for c in self._collectors:
            try:
                c.start()
            except Exception as e:
                logger.warning(f"Failed to start collector {c.name}: {e}")

        self._running = True
        window_start = time.monotonic()

        # Monitoring loop
        try:
            while self._running:
                time.sleep(0.5)
                now = time.monotonic()
                if (now - window_start) >= self.window_duration:
                    self._process_feature_window()
                    window_start = time.monotonic()

        except KeyboardInterrupt:
            self._handle_shutdown(None, None)

    def _handle_shutdown(self, signum, frame) -> None:
        """Gracefully terminates collectors, processes final snapshot, and closes files."""
        if self._shutdown_initiated:
            return
        self._shutdown_initiated = True
        self._running = False

        print("\n[Shutdown] Stopping behavioural collectors...")
        for c in self._collectors:
            try:
                c.stop()
            except Exception as e:
                logger.debug(f"Error stopping collector {c.name}: {e}")

        # Process any pending activity into a safe final snapshot
        try:
            print("[Shutdown] Finalizing feature snapshot...")
            self._process_feature_window()
        except Exception:
            pass

        print("[Shutdown] Cyber Doppelgänger Desktop Agent stopped cleanly.\n")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Cyber Doppelgänger Desktop Agent")
    parser.add_argument("--health", action="store_true", help="Print agent health status and exit")
    parser.add_argument("--status", action="store_true", help="Print collector diagnostic status and exit")
    parser.add_argument("--version", action="store_true", help="Print agent version and exit")
    parser.add_argument("--window-seconds", type=int, default=None, help="Override aggregation window duration (seconds)")
    args = parser.parse_args()

    agent = DesktopAgent(window_seconds=args.window_seconds)

    if args.version:
        print(f"{settings.AGENT_NAME} {settings.AGENT_VERSION}")
        return

    if args.health:
        health = agent.get_health_status()
        print("\n--- CYBER DOPPELGANGER AGENT HEALTH ---")
        for k, v in health.items():
            print(f"  {k:25}: {v}")
        print("---------------------------------------\n")
        return

    if args.status:
        print("\n--- COLLECTOR INTERFACE STATUS ---")
        for c in agent._collectors:
            st = c.get_status()
            print(f"  [{st['name']}]: Active={st['active']} | Privacy={st.get('privacy_mode', 'N/A')} | Buffer={st.get('buffered_event_count', st.get('buffered_movement_samples', 0))}")
        print("----------------------------------\n")
        return

    # Default: Run agent monitoring lifecycle
    agent.start()


if __name__ == "__main__":
    main()
