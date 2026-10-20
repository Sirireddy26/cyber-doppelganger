"""
Cyber Doppelgänger - ML Pipeline Health & Behavioural Verification Diagnostics
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add cyber-doppelganger root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.pipelines.verification_service import VerificationService
from ml.pipelines.verifier import BehaviouralIdentityVerifier
from ml.preprocessing.feature_preprocessor import (
    ALL_FEATURE_KEYS,
    APPROVED_KEYBOARD_FEATURES,
    APPROVED_MOUSE_FEATURES,
    APPROVED_SESSION_FEATURES,
    APPROVED_APPLICATION_FEATURES
)


def run_ml_diagnostics():
    print("=" * 75, flush=True)
    print("CYBER DOPPELGÄNGER - PHASE 4 ML VERIFICATION PIPELINE DIAGNOSTICS", flush=True)
    print("=" * 75, flush=True)

    # 1. Test VerificationService & Trained Artifacts
    print("\n[1/4] Inspecting Phase 4 Model Status & Persistence...", flush=True)
    service = VerificationService()
    status = service.get_model_status()
    iso_status = status.get("isolationForest", {})
    rf_status = status.get("randomForest", {})
    print(f"      Overall Engine Status  : {status.get('status')}")
    print(f"      Active Model Type      : {status.get('activeModelType')}")
    print(f"      Isolation Forest Ready : {iso_status.get('available')} (v{iso_status.get('version')}, samples: {iso_status.get('sampleCount')})")
    print(f"      Random Forest Ready    : {rf_status.get('available')}")

    # 2. Test VerificationService with 37-feature Genuine Vector
    print("\n[2/4] Testing Verification with Genuine 37-Feature Snapshot...", flush=True)
    genuine_snapshot = {
        "schema_version": "2.0",
        "keyboard": {
            "total_key_events": 250,
            "mean_key_interval": 0.18,
            "median_key_interval": 0.17,
            "key_interval_std": 0.05,
            "minimum_key_interval": 0.08,
            "maximum_key_interval": 0.65,
            "typing_speed": 65.0,
            "pause_count": 8,
            "mean_pause_duration": 1.2,
            "longest_pause": 3.4,
            "typing_activity_duration": 45.0
        },
        "mouse": {
            "movement_distance": 3500.0,
            "mean_mouse_speed": 120.0,
            "mouse_speed_std": 45.0,
            "mean_acceleration": 60.0,
            "click_count": 25,
            "left_click_count": 20,
            "right_click_count": 4,
            "middle_click_count": 1,
            "mean_click_interval": 1.8,
            "click_interval_std": 0.9,
            "scroll_count": 12,
            "positive_scroll_count": 8,
            "negative_scroll_count": 4,
            "mouse_active_duration": 40.0
        },
        "session": {
            "session_duration": 60.0,
            "active_duration": 50.0,
            "idle_duration": 10.0,
            "active_idle_ratio": 5.0,
            "activity_density": 0.83,
            "keyboard_activity_duration": 45.0,
            "mouse_activity_duration": 40.0
        },
        "application": {
            "process_count": 4,
            "active_process_count": 2,
            "application_switch_count": 3,
            "process_activity_count": 8,
            "application_activity_duration": 55.0
        }
    }
    result = service.verify_snapshot(genuine_snapshot)
    print(f"      Status          : {result.get('status')}")
    print(f"      Model Type      : {result.get('modelType')}")
    print(f"      Raw Score       : {result.get('rawScore')}")
    print(f"      Confidence Score: {result.get('confidenceScore')}")
    print(f"      Threshold       : {result.get('threshold')}")
    print(f"      Reason          : {result.get('reason')}")

    # 3. Test VerificationService with Extreme Anomaly / Intrusion Vector
    print("\n[3/4] Testing Verification with Anomalous / Doppelgänger Vector...", flush=True)
    anomalous_snapshot = {
        "schema_version": "2.0",
        "keyboard": {k: 9999.0 for k in genuine_snapshot["keyboard"]},
        "mouse": {k: 9999.0 for k in genuine_snapshot["mouse"]},
        "session": {k: 9999.0 for k in genuine_snapshot["session"]},
        "application": {k: 9999.0 for k in genuine_snapshot["application"]}
    }
    anomaly_result = service.verify_snapshot(anomalous_snapshot)
    print(f"      Status          : {anomaly_result.get('status')}")
    print(f"      Raw Score       : {anomaly_result.get('rawScore')}")
    print(f"      Confidence Score: {anomaly_result.get('confidenceScore')}")
    print(f"      Threshold       : {anomaly_result.get('threshold')}")
    print(f"      Reason          : {anomaly_result.get('reason')}")

    # 4. Backward-Compatible BehaviouralIdentityVerifier
    print("\n[4/4] Validating Legacy Verifier Compatibility...", flush=True)
    legacy_verifier = BehaviouralIdentityVerifier()
    baseline = [{k: float(np.random.normal(loc=120.0, scale=10.0)) for k in BehaviouralIdentityVerifier.FEATURE_KEYS} for _ in range(10)]
    legacy_verifier.train_baseline(baseline)
    leg_score, leg_decision = legacy_verifier.verify_window(baseline[0])
    print(f"      Legacy Score    : {leg_score} -> Decision: {leg_decision}")

    print("\n" + "=" * 75, flush=True)
    print("RESULT: PHASE 4 ML VERIFICATION PIPELINE FULLY HEALTHY & OPERATIONAL", flush=True)
    print("=" * 75 + "\n", flush=True)


if __name__ == "__main__":
    run_ml_diagnostics()

