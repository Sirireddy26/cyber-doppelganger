"""
Cyber Doppelgänger - Model Training & Evaluation CLI Workflow
Safe Adaptive Behavioural Identity & Continuous User Verification

Enables reproducible baseline training, threshold calibration, and evaluation.
Outputs real performance metrics and saves model artifacts to ml/artifacts/.
Strictly abides by research integrity: no synthetic data presented as real,
no fabricated accuracy claims.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.preprocessing.feature_preprocessor import FeaturePreprocessor
from ml.anomaly_detection.isolation_forest_detector import IsolationForestDetector
from ml.models.random_forest_classifier import BehaviouralRandomForestClassifier
from ml.evaluation.evaluator import ModelEvaluator, group_aware_split

ARTIFACTS_DIR = Path("ml/artifacts")


def load_snapshots_from_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Reads JSONL snapshots from file."""
    path = Path(file_path)
    if not path.exists():
        return []

    snapshots = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                snapshots.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Skipping corrupted line {idx} in {file_path}")
    return snapshots


def inspect_dataset(snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Inspects dataset volume, session count, and unique users."""
    user_ids = set()
    session_ids = set()
    durations = []

    for s in snapshots:
        u = s.get("user_id") or s.get("userId")
        sess = s.get("session_id") or s.get("sessionId")
        dur = s.get("window_duration_seconds") or 0

        if u:
            user_ids.add(str(u))
        if sess:
            session_ids.add(str(sess))
        if dur:
            durations.append(dur)

    return {
        "total_snapshots": len(snapshots),
        "unique_users": list(user_ids),
        "unique_sessions": len(session_ids),
        "mean_window_duration": round(sum(durations) / len(durations), 1) if durations else 0
    }


def run_training_and_evaluation(
    data_path: str,
    model_type: str = "isolation_forest",
    user_id: str = "researcher-01",
    output_dir: str = "ml/artifacts",
    contamination: float = 0.05,
    random_state: int = 42
):
    print("=" * 70)
    print("CYBER DOPPELGÄNGER - ML BASELINE TRAINING & EVALUATION")
    print("=" * 70)

    # 1. Load data
    print(f"\n[1/5] Loading behavioral snapshots from: {data_path}")
    snapshots = load_snapshots_from_jsonl(data_path)
    info = inspect_dataset(snapshots)
    print(f"      Total snapshots found: {info['total_snapshots']}")
    print(f"      Unique users: {info['unique_users'] or 'Unspecified'}")
    print(f"      Sessions: {info['unique_sessions']}")

    if len(snapshots) < 5:
        print("\n[ERROR] INSUFFICIENT DATA:")
        print(f"      Found only {len(snapshots)} snapshots. At least 5 snapshots are required.")
        print("      To collect genuine telemetry, run the Python agent:")
        print("        python agent/main.py --window-seconds 10")
        print("      Then rerun this training script.")
        return False

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 2. Data Split (Group-aware by session to prevent leakage)
    print("\n[2/5] Partitioning data using session-group aware split (75% train / 25% test)...")
    train_snaps, test_snaps, _, _ = group_aware_split(
        snapshots,
        test_size=0.25,
        random_state=random_state
    )
    print(f"      Training partition: {len(train_snaps)} snapshots")
    print(f"      Held-out test partition: {len(test_snaps)} snapshots")

    # 3. Model Training
    print(f"\n[3/5] Training baseline: {model_type.upper()}...")
    if model_type.lower() == "isolation_forest":
        detector = IsolationForestDetector(
            contamination=contamination,
            random_state=random_state,
            model_version="1.0.0"
        )
        detector.fit(train_snaps, user_id=user_id, validation_snapshots=test_snaps)
        artifact_path = out_path / "isolation_forest.joblib"
        detector.save(str(artifact_path))
        print(f"      [SUCCESS] Trained and saved model to: {artifact_path}")
        print(f"      Reference Profile feature count: {len(detector.reference_profile.feature_names)}")
        print(f"      Calibrated Decision Threshold: {detector.threshold:.4f}")

        # 4. Evaluation on test partition
        print("\n[4/5] Evaluating on held-out test partition...")
        test_predictions = [detector.predict_snapshot(s) for s in test_snaps]
        verified_count = sum(1 for p in test_predictions if p["status"] == "VERIFIED")
        uncertain_count = sum(1 for p in test_predictions if p["status"] == "UNCERTAIN")
        deviation_count = sum(1 for p in test_predictions if p["status"] == "DEVIATION")

        print(f"      Test Samples Evaluated: {len(test_snaps)}")
        print(f"      Verified (Consistent): {verified_count} ({verified_count/len(test_snaps):.1%})")
        print(f"      Uncertain (Borderline): {uncertain_count} ({uncertain_count/len(test_snaps):.1%})")
        print(f"      Deviation (Outlier):    {deviation_count} ({deviation_count/len(test_snaps):.1%})")

        eval_report = {
            "model_type": "ISOLATION_FOREST",
            "model_version": "1.0.0",
            "train_samples": len(train_snaps),
            "test_samples": len(test_snaps),
            "threshold": detector.threshold,
            "test_results": {
                "verified": verified_count,
                "uncertain": uncertain_count,
                "deviation": deviation_count
            },
            "evaluation_limitation": (
                "Single-user unsupervised baseline. Full FAR/FRR/EER evaluation "
                "requires second-party or multi-participant benchmark dataset."
            )
        }

    else:
        print("[ERROR] Random Forest requires multi-user labelled data with explicit class labels.")
        return False

    # 5. Export Genuine Results File
    results_path = out_path / "evaluation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    print(f"\n[5/5] Exported genuine evaluation summary to: {results_path}")

    print("\n" + "=" * 70)
    print("BASELINE TRAINING & EVALUATION COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")
    return True


def run_single_prediction(data_path: str = "agent/data/feature_snapshots.jsonl"):
    print("=" * 70)
    print("CYBER DOPPELGÄNGER - SINGLE VERIFICATION PREDICTION")
    print("=" * 70)
    from ml.pipelines.verification_service import VerificationService
    service = VerificationService()
    status = service.get_model_status()
    print(f"Active Engine: {status.get('activeModelType')} (Status: {status.get('status')})")
    
    snapshots = load_snapshots_from_jsonl(data_path)
    if not snapshots:
        print(f"[ERROR] No snapshots found in {data_path} to evaluate.")
        return False

    sample = snapshots[0]
    print(f"Evaluating snapshot 1 of {len(snapshots)} (device: {sample.get('device_id', 'unknown')})...")
    result = service.verify_snapshot(sample)
    
    print("\nVerification Result:")
    print(f"  Status          : {result.get('status')}")
    print(f"  Model Type      : {result.get('modelType')}")
    print(f"  Raw Score       : {result.get('rawScore')}")
    print(f"  Anomaly Score   : {result.get('anomalyScore')}")
    print(f"  Confidence Score: {result.get('confidenceScore')}")
    print(f"  Threshold       : {result.get('threshold')}")
    print(f"  Decision        : {result.get('decision')}")
    print(f"  Reason          : {result.get('reason')}")
    print("=" * 70 + "\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and evaluate Cyber Doppelgänger ML baselines.")
    parser.add_argument(
        "--data",
        type=str,
        default="agent/data/feature_snapshots.jsonl",
        help="Path to JSONL file containing feature snapshots"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["isolation_forest", "random_forest"],
        default="isolation_forest",
        help="Model baseline architecture"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="researcher-01",
        help="Legitimate user reference identifier"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml/artifacts",
        help="Directory to save model artifacts"
    )
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.05,
        help="Isolation Forest contamination factor"
    )
    parser.add_argument(
        "--predict",
        action="store_true",
        help="Run a verification prediction on a feature snapshot"
    )

    args = parser.parse_args()
    if args.predict:
        run_single_prediction(data_path=args.data)
    else:
        run_training_and_evaluation(
            data_path=args.data,
            model_type=args.model_type,
            user_id=args.user_id,
            output_dir=args.output_dir,
            contamination=args.contamination
        )
