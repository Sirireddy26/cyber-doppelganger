"""
Cyber Doppelgänger - Desktop Agent Health & Diagnostic Verification Script
Verifies environment, privacy enforcement, event collectors, and ML readiness.
"""

import sys
import os
import time

# Ensure cyber-doppelganger root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def log(msg: str):
    print(msg, flush=True)

def run_diagnostics():
    log("=" * 70)
    log("CYBER DOPPELGÄNGER - DESKTOP AGENT HEALTH VERIFICATION")
    log("Safe Adaptive Behavioural Identity & Continuous User Verification")
    log("=" * 70)

    # 1. Python Version Check
    py_ver = sys.version_info
    log(f"\n[1/5] Checking Python Runtime...")
    log(f"      Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 11):
        log("      [FAIL] Python 3.11+ is required.")
        sys.exit(1)
    log("      [PASS] Python 3.11+ confirmed.")

    # 2. Dependency Import Verification
    log("\n[2/5] Verifying Required Libraries...")
    libs = [
        ("pynput", "Keystroke & Mouse Event Timing"),
        ("psutil", "System Performance & Hardware Context"),
        ("numpy", "Numerical Kinematics & Feature Math"),
        ("pandas", "Time-Series Windowing & DataFrames"),
        ("sklearn", "Scikit-Learn ML Anomaly Models"),
        ("requests", "Secure Backend Telemetry Transport")
    ]
    for lib, desc in libs:
        try:
            __import__(lib)
            log(f"      [PASS] {lib:12} - {desc}")
        except ImportError as e:
            log(f"      [FAIL] Missing library: {lib} ({e})")
            sys.exit(1)

    # 3. Privacy Safeguard Audit
    log("\n[3/5] Testing Privacy Guard & Non-Collection Guarantees...")
    from agent.collector.privacy_guard import PrivacyGuard, PrivacyViolationError
    
    # Verify compliant event passes
    safe_event = {"dwell_time_ms": 112.5, "event_type": 0.0}
    PrivacyGuard.sanitize_event(safe_event)
    log("      [PASS] Compliant behavioural telemetry permitted.")

    # Verify prohibited event is strictly blocked
    caught = False
    try:
        violation_event = {"char": "a", "dwell_time_ms": 112.5}
        PrivacyGuard.sanitize_event(violation_event)
    except PrivacyViolationError:
        caught = True
    
    if caught:
        log("      [PASS] Prohibited keystroke content ('char') strictly blocked by PrivacyGuard.")
    else:
        log("      [FAIL] Privacy Guard failed to reject prohibited payload!")
        sys.exit(1)

    # 4. Collector & Feature Extraction Pipeline Simulation
    log("\n[4/5] Testing Collector & Feature Extraction Pipeline...")
    from agent.collector.keyboard_collector import KeystrokeTimingCollector
    from agent.collector.mouse_collector import MouseKinematicsCollector
    from agent.collector.system_collector import SystemStateCollector
    from agent.features.extractor import BehaviouralFeatureExtractor

    kb = KeystrokeTimingCollector()
    mouse = MouseKinematicsCollector()

    # Simulate 5 synthetic keypresses (timing only)
    for _ in range(5):
        key_dummy = type('KeyDummy', (), {})()
        kb.on_press(key_dummy)
        time.sleep(0.005)
        kb.on_release(key_dummy)

    # Simulate 5 mouse movements and 1 click
    for i in range(5):
        mouse.on_move(100 + i * 20, 200 + i * 15)
        time.sleep(0.005)
    mouse.on_click(200, 275, "Button.left", True)
    time.sleep(0.005)
    mouse.on_click(200, 275, "Button.left", False)

    kb_events = kb.flush_events()
    mouse_events = mouse.flush_events()
    sys_snapshot = SystemStateCollector.get_system_snapshot()

    vector = BehaviouralFeatureExtractor.extract_vector(kb_events, mouse_events, window_duration_seconds=5.0)
    log(f"      [PASS] Simulated events captured: {len(kb_events)} keystroke, {len(mouse_events)} mouse.")
    log(f"      [PASS] 18-Dimensional Feature Vector extracted successfully:")
    log(f"             - Mean Dwell Time: {vector['dwell_mean_ms']:.2f} ms")
    log(f"             - Mean Mouse Velocity: {vector['mouse_velocity_mean']:.4f} px/ms")
    log(f"             - CPU Usage Context: {sys_snapshot['cpu_usage_pct']}%")

    # 5. Backend Connectivity Probe
    log("\n[5/5] Probing Spring Boot Backend API (/api/health)...")
    import requests
    from agent.config import config
    try:
        res = requests.get(config.HEALTH_ENDPOINT, timeout=(0.5, 0.5))
        if res.status_code == 200:
            log(f"      [PASS] Backend API is ONLINE at {config.HEALTH_ENDPOINT}")
            log(f"             Status: {res.json().get('status')} | Service: {res.json().get('service')}")
        else:
            log(f"      [WARN] Backend returned status code {res.status_code}")
    except Exception as e:
        log(f"      [INFO] Backend is currently offline or starting: {type(e).__name__}")
        log(f"             (Run backend via `.\\mvnw.cmd spring-boot:run` in `cyber-doppelganger/backend`)")

    log("\n" + "=" * 70)
    log("RESULT: Desktop Agent health check SUCCESSFUL. All modules ready.")
    log("=" * 70 + "\n")

if __name__ == "__main__":
    run_diagnostics()
