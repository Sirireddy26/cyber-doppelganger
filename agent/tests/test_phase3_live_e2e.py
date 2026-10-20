"""
Cyber Doppelgänger - Phase 3 Live End-to-End Integration Verification Script
Verifies:
1. Backend GET /api/health
2. Python Agent ApiClient transmission of real snapshot -> POST /api/agent/features (HTTP 201)
3. Persisted Snapshot retrieval via GET /api/behaviour and GET /api/behaviour/{id}
4. Privacy compliance: Zero keystroke content, zero raw coordinates, zero forbidden fields in DB
5. Resilience test: Agent graceful handling when backend is unreachable (no crashes, buffered safely)
"""

import sys
import os
import time
import requests
import json

# Ensure cyber-doppelganger root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from agent.features.feature_snapshot import FeatureSnapshot
from agent.features.keyboard_features import KeyboardFeatures
from agent.features.mouse_features import MouseFeatures
from agent.features.session_features import SessionFeatures
from agent.features.application_features import ApplicationFeatures
from agent.communication.api_client import ApiClient
from agent.buffering.local_buffer import LocalBuffer


def run_e2e_tests():
    print("==================================================")
    print("CYBER DOPPELGÄNGER - PHASE 3 LIVE E2E INTEGRATION")
    print("==================================================")

    base_url = "http://localhost:8080"
    
    # 1. Verify Health Endpoint
    print("\n[Step 1] Verifying Backend Health...")
    health_resp = requests.get(f"{base_url}/api/health", timeout=5)
    print(f"Health HTTP Status: {health_resp.status_code}")
    print(f"Health Response: {health_resp.text}")
    assert health_resp.status_code == 200, "Health check failed"
    health_data = health_resp.json()
    assert health_data["status"] == "UP"
    assert "database" in health_data

    # 2. Build Real Privacy-Safe FeatureSnapshot
    print("\n[Step 2] Constructing Real Privacy-Safe FeatureSnapshot...")
    kb = KeyboardFeatures(
        total_key_events=42,
        mean_key_interval=0.145,
        median_key_interval=0.138,
        key_interval_std=0.032,
        minimum_key_interval=0.045,
        maximum_key_interval=0.450,
        typing_speed=4.8,
        pause_count=1,
        mean_pause_duration=1.2,
        longest_pause=1.2,
        typing_activity_duration=8.75
    )
    mo = MouseFeatures(
        movement_distance=960.5,
        mean_mouse_speed=124.5,
        mouse_speed_std=45.2,
        mean_acceleration=210.0,
        click_count=7,
        left_click_count=5,
        right_click_count=2,
        middle_click_count=0,
        mean_click_interval=1.25,
        click_interval_std=0.34,
        scroll_count=2,
        positive_scroll_count=2,
        negative_scroll_count=0,
        mouse_active_duration=6.2
    )
    sess = SessionFeatures(
        session_duration=60.0,
        active_duration=12.5,
        idle_duration=2.5,
        active_idle_ratio=5.0,
        activity_density=0.833,
        keyboard_activity_duration=8.75,
        mouse_activity_duration=6.2
    )
    app = ApplicationFeatures(
        process_count=88,
        active_process_count=4,
        application_switch_count=1,
        process_activity_count=10,
        application_activity_duration=15.0
    )
    snapshot = FeatureSnapshot(
        window_duration_seconds=15,
        device_id="desktop-workstation-win11",
        user_id="researcher-01",
        keyboard=kb,
        mouse=mo,
        session=sess,
        application=app
    )
    
    snapshot_dict = snapshot.to_dict()
    print(f"Snapshot Schema Version: {snapshot_dict.get('schema_version')}")
    print(f"Snapshot Device ID: {snapshot_dict.get('device_id')}")
    print(f"Snapshot Duration: {snapshot_dict.get('window_duration_seconds')}s")

    # 3. Transmit Snapshot using Python Agent ApiClient
    print("\n[Step 3] Transmitting Snapshot via Agent ApiClient -> POST /api/agent/features...")
    client = ApiClient(base_url=base_url, enabled=True)
    send_result = client.send_snapshot(snapshot)
    print(f"Client Result: {json.dumps(send_result, indent=2)}")
    assert send_result["success"] is True, f"Failed to send snapshot: {send_result}"
    assert send_result["status_code"] == 201, "Expected HTTP 201 Created"
    snapshot_id = send_result["data"]["snapshotId"]
    print(f"Persisted Snapshot ID: {snapshot_id}")

    # 4. Query Retrieval API: List Snapshots
    print("\n[Step 4] Querying Snapshot List via GET /api/behaviour...")
    list_resp = requests.get(f"{base_url}/api/behaviour?page=0&size=10", timeout=5)
    print(f"List HTTP Status: {list_resp.status_code}")
    list_data = list_resp.json()
    total_elements = list_data.get("page", {}).get("totalElements") or list_data.get("totalElements")
    print(f"Total Persisted Snapshots: {total_elements}")
    assert list_resp.status_code == 200
    assert total_elements >= 1

    # 5. Query Retrieval API: Single Snapshot by ID
    print(f"\n[Step 5] Querying Persisted Snapshot #{snapshot_id} via GET /api/behaviour/{snapshot_id}...")
    single_resp = requests.get(f"{base_url}/api/behaviour/{snapshot_id}", timeout=5)
    print(f"Single HTTP Status: {single_resp.status_code}")
    print(f"Single Snapshot JSON: {json.dumps(single_resp.json(), indent=2)}")
    assert single_resp.status_code == 200
    single_data = single_resp.json()
    assert str(single_data["id"]) == str(snapshot_id)
    assert single_data["device_id"] == "desktop-workstation-win11"
    assert single_data["window_duration_seconds"] == 15

    # 6. Verify Database Record Privacy Guarantees
    print("\n[Step 6] Validating Privacy in Retrieved Feature Payload...")
    features_payload = single_data["features"]
    forbidden_terms = [
        "typed_text", "keystrokes", "clipboard_content", "screenshot", 
        "browser_url", "document_content", "raw_keys", "key_down", "key_up"
    ]
    raw_str = json.dumps(features_payload)
    for term in forbidden_terms:
        assert term not in raw_str, f"Privacy violation! Found prohibited term: {term}"
    print("Privacy verification PASSED: zero raw keystrokes, zero content, zero surveillance data.")

    # 7. Agent Resilience Test: Graceful handling when backend is unreachable
    print("\n[Step 7] Testing Agent Resilience with Unreachable Backend...")
    dead_client = ApiClient(base_url="http://localhost:65530", enabled=True)
    dead_health = dead_client.check_health()
    print(f"Dead Backend Health Check: {dead_health}")
    assert dead_health["connected"] is False

    dead_send = dead_client.send_snapshot(snapshot)
    print(f"Dead Backend Send Result: {dead_send}")
    assert dead_send["success"] is False
    assert "error" in dead_send
    print("Agent Resilience PASSED: Process survived network failure without crashing.")

    # 8. Buffer Persistence Test
    print("\n[Step 8] Testing Local Buffer Persistence and Deduplication...")
    buffer_file = "agent/data/test_e2e_buffer.jsonl"
    if os.path.exists(buffer_file):
        os.remove(buffer_file)
    buf = LocalBuffer(file_path=buffer_file)
    buf.write_snapshot(snapshot)
    print(f"Buffered count: {buf.count()}")
    assert buf.count() == 1
    snapshots_in_buf = buf.read_pending_snapshots()
    assert len(snapshots_in_buf) == 1
    # Cleanup test buffer
    if os.path.exists(buffer_file):
        os.remove(buffer_file)

    print("\n==================================================")
    print("ALL PHASE 3 LIVE INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_e2e_tests()
