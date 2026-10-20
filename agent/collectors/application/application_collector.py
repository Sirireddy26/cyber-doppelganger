"""
Cyber Doppelgänger - Privacy-Conscious Application / Process Collector
Safe Adaptive Behavioural Identity & Continuous User Verification

Observes system process metrics and application switching rates using psutil and OS handles.
STRICT PRIVACY GUARANTEE:
NEVER collects or reads window titles, browser URLs, document names, command-line
arguments, terminal text, or file contents.
Foreground switches are tracked exclusively by comparing anonymous process IDs (PIDs).
All observations are aggregated immediately into numerical counters.
"""

import threading
import time
import sys
from typing import Dict, Any, Optional
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

from agent.collectors.base import BaseCollector
from agent.features.application_features import ApplicationFeatures, calculate_application_features

logger = logging.getLogger("cyber-doppelganger.agent")


class ApplicationCollector(BaseCollector):
    """
    Monitors process counts, active processes, and foreground task-switching rhythm.
    Zero content inspection: strictly monitors anonymous PID transitions and OS counts.
    """

    def __init__(self, sample_interval_seconds: float = 2.0):
        super().__init__(name="ApplicationCollector")
        self.sample_interval = sample_interval_seconds
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Transient in-window tracking
        self._last_foreground_pid: Optional[int] = None
        self._switch_count: int = 0
        self._sample_checks: int = 0
        self._latest_process_count: int = 0
        self._latest_active_count: int = 0
        self._active_duration: float = 0.0

        # Lifetime counters
        self._lifetime_switches: int = 0
        self._error_state: Optional[str] = None

    def _get_foreground_pid(self) -> Optional[int]:
        """
        Retrieves the PID of the foreground window on Windows using native Win32 API.
        PRIVACY: Never retrieves window title (no GetWindowText) or URL. Retrieves only integer PID.
        """
        if sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                if hwnd:
                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    return int(pid.value)
            except Exception:
                pass
        return None

    def _monitor_loop(self) -> None:
        """Background sampling loop for tracking process dynamics and PID switches."""
        last_check_time = time.monotonic()
        while not self._stop_event.is_set():
            try:
                now = time.monotonic()
                dt = now - last_check_time
                last_check_time = now

                # 1. Check foreground PID switch
                fg_pid = self._get_foreground_pid()
                with self._lock:
                    if fg_pid is not None:
                        if self._last_foreground_pid is not None and fg_pid != self._last_foreground_pid:
                            self._switch_count += 1
                            self._lifetime_switches += 1
                        self._last_foreground_pid = fg_pid

                    self._sample_checks += 1
                    self._active_duration += dt

                # 2. Update process counts if psutil available
                if PSUTIL_AVAILABLE:
                    try:
                        pids = psutil.pids()
                        p_count = len(pids)
                        # Estimate active processes (running or recently scheduled)
                        active_c = 0
                        for p in psutil.process_iter(['status']):
                            try:
                                if p.info['status'] == psutil.STATUS_RUNNING:
                                    active_c += 1
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

                        with self._lock:
                            self._latest_process_count = p_count
                            self._latest_active_count = max(active_c, 1)
                    except Exception:
                        pass

            except Exception as e:
                logger.debug(f"{self.name} sampling error: {e}")

            # Sleep until next check or stop event
            self._stop_event.wait(self.sample_interval)

    def start(self) -> None:
        """Starts background process monitoring thread."""
        if self._is_active:
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="AppCollectorThread")
        self._thread.start()
        self._is_active = True
        self._error_state = None
        logger.info(f"{self.name} started successfully (Zero-content process monitoring active).")

    def stop(self) -> None:
        """Stops background process monitoring thread."""
        if not self._is_active:
            return

        self._is_active = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            self._thread = None
        logger.info(f"{self.name} stopped.")

    def flush_events(self) -> Dict[str, Any]:
        """Atomically retrieves and clears window metrics."""
        with self._lock:
            data = {
                "process_count": self._latest_process_count,
                "active_process_count": self._latest_active_count,
                "switch_count": self._switch_count,
                "sample_checks": self._sample_checks,
                "active_duration": self._active_duration
            }
            self._switch_count = 0
            self._sample_checks = 0
            self._active_duration = 0.0
            return data

    def extract_features(self) -> ApplicationFeatures:
        """
        Atomically flushes window metrics and computes ApplicationFeatures.
        """
        data = self.flush_events()
        return calculate_application_features(
            process_count=data["process_count"],
            active_process_count=data["active_process_count"],
            switch_count=data["switch_count"],
            activity_checks=data["sample_checks"],
            active_duration=data["active_duration"]
        )

    def get_status(self) -> Dict[str, Any]:
        """Returns collector operational health and status metadata."""
        with self._lock:
            p_cnt = self._latest_process_count
            sw_cnt = self._switch_count
        return {
            "name": self.name,
            "active": self._is_active,
            "collection_enabled": True,
            "privacy_mode": "ZERO_CONTENT_PID_ONLY",
            "current_process_count": p_cnt,
            "window_switches": sw_cnt,
            "lifetime_switches": self._lifetime_switches,
            "error": self._error_state
        }
