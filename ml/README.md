# Cyber Doppelgänger — Machine Learning Verification Pipeline (Phase 4)
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

This module implements the machine learning verification pipeline for Cyber Doppelgänger. It processes privacy-safe behavioural feature snapshots, establishes legitimate-user baseline profiles, detects behavioural anomalies, and produces structured verification evidence for the future `SafeAdaptationEngine`.

---

## 1. Directory Structure

```
ml/
├── anomaly_detection/
│   └── isolation_forest_detector.py  # Isolation Forest anomaly detection baseline
├── models/
│   ├── reference_profile.py          # Legitimate-user reference profile statistics
│   └── random_forest_classifier.py   # Supervised baseline for labelled evaluation
├── preprocessing/
│   └── feature_preprocessor.py       # 37-feature extraction, schema 2.0 validation, scaling
├── evaluation/
│   └── evaluator.py                  # Group-aware data splits, metrics (FAR, FRR, EER, ROC-AUC)
├── pipelines/
│   ├── verification_service.py       # High-level verification engine and lifecycle manager
│   └── verifier.py                   # Legacy baseline verifier (backward compatibility)
├── artifacts/
│   ├── isolation_forest.joblib       # Persisted trained baseline artifact
│   └── evaluation_results.json       # Genuine reproducible evaluation metrics
├── tests/
│   └── test_ml_pipeline.py           # 17 automated unit and smoke tests
├── train_and_evaluate.py             # CLI workflow for model training and evaluation
├── service.py                        # Lightweight zero-dependency HTTP microservice (port 5001)
├── health.py                         # Diagnostic health script
└── README.md                         # This documentation
```

---

## 2. Feature Schema & Preprocessing

The ML pipeline strictly enforces schema version `2.0` and processes **37 approved numerical behavioural features**:

| Domain | Count | Approved Feature Keys |
| :--- | :---: | :--- |
| **Keyboard** | 11 | `total_key_events`, `mean_key_interval`, `median_key_interval`, `key_interval_std`, `minimum_key_interval`, `maximum_key_interval`, `typing_speed`, `pause_count`, `mean_pause_duration`, `longest_pause`, `typing_activity_duration` |
| **Mouse** | 14 | `movement_distance`, `mean_mouse_speed`, `mouse_speed_std`, `mean_acceleration`, `click_count`, `left_click_count`, `right_click_count`, `middle_click_count`, `mean_click_interval`, `click_interval_std`, `scroll_count`, `positive_scroll_count`, `negative_scroll_count`, `mouse_active_duration` |
| **Session** | 7 | `session_duration`, `active_duration`, `idle_duration`, `active_idle_ratio`, `activity_density`, `keyboard_activity_duration`, `mouse_activity_duration` |
| **Application** | 5 | `process_count`, `active_process_count`, `application_switch_count`, `process_activity_count`, `application_activity_duration` |

### Preprocessing Policies:
- **Zero Content Surveillance**: No raw keystrokes, letters, passwords, screen pixels, URLs, or window titles are accepted.
- **NaN / Infinity Rejection**: Any non-finite float triggers immediate rejection with `FeaturePreprocessingError`.
- **Deterministic Ordering**: Feature order is locked and strictly identical between training and inference.
- **Scaling**: Normalized via scikit-learn `StandardScaler` fitted exclusively on training data to prevent data leakage.

---

## 3. Models Implemented

### A. Anomaly Detection Baseline: Isolation Forest (`IsolationForestDetector`)
- **Architecture**: Scikit-learn `IsolationForest` (`n_estimators=100`, `contamination=0.05`, `random_state=42`).
- **Score Convention**:
  - `rawScore`: Model decision function output (positive = nominal user distribution; negative = anomalous).
  - `anomalyScore`: Inverted raw score (`-rawScore`; higher = more anomalous).
  - `confidenceScore`: Calibrated probability via logistic transformation: `1 / (1 + exp(-4 * rawScore))`.
- **Threshold Calibration**:
  - Dynamically calibrated to the 5th percentile of the training reference distribution (or validation set) to bound false rejections.
  - Uncertainty margin of 0.05 around threshold produces three distinct statuses:
    - `VERIFIED`: Score $\ge$ threshold (Normal behaviour consistent with reference profile).
    - `UNCERTAIN`: Threshold - margin $\le$ Score $<$ threshold (Borderline region).
    - `DEVIATION`: Score $<$ threshold - margin (Statistically significant anomaly).

### B. Supervised Baseline: Random Forest Classifier (`RandomForestBaseline`)
- **Architecture**: Scikit-learn `RandomForestClassifier` (`n_estimators=100`, `max_depth=8`, `random_state=42`).
- **Validation Guard**: Requires multi-class labelled data (genuine participant vs impostor/other users). Rejects single-class datasets gracefully without fabricating predictions.
- **Output**: Predicts class probability and calibrated confidence score.

### C. Reference Profile (`ReferenceProfile`)
- Stores immutable distribution metrics calculated from legitimate training data:
  - Sample count
  - Feature means, standard deviations, medians, and IQRs
  - Zero-variance feature detection
  - Model and schema versions
- Serves as an immutable reference during Phase 4 (no automatic online drift adaptation; adaptation belongs to Phase 5).

---

## 4. Preventing Data Leakage

In behavioural biometrics, consecutive 15-second windows are autocorrelated. A random row split leaks session dynamics between train and test sets.

- **Group-Aware Splitting**: `evaluator.group_aware_split()` groups snapshots by `session_id` or collection date.
- **Isolated Normalization**: `StandardScaler` is fitted strictly on the training partition and applied to test partitions.
- **Threshold Freezing**: Decision threshold is calibrated exclusively on the training/validation partition and never tuned against the final test set.

---

## 5. Genuine Experimental Evaluation Results

Training and evaluation were performed on 294 genuine desktop behavioural snapshots (`agent/data/feature_snapshots.jsonl`):

```
Dataset Summary:
- Total genuine snapshots available: 294
- Training partition (first sessions): 225 samples
- Test partition (held-out sessions):   69 samples
- Features used:                     37 numerical features
- Model Version:                     1.0.0

Isolation Forest Calibration:
- Baseline Threshold (5th percentile): 0.0594
- Test Partition Results:
  * VERIFIED   : 65 / 69 (94.20%)
  * UNCERTAIN  :  2 / 69 ( 2.90%)
  * DEVIATION  :  2 / 69 ( 2.90%)

Evaluation Limitations:
The dataset currently consists of a single participant's natural sessions.
While the model accurately validates 94.2% of legitimate held-out activity,
metrics requiring impostor labels (ROC-AUC, FAR, FRR, EER) cannot be computed
without multi-participant benchmark datasets. Synthetic impostor numbers are
NOT presented as real research results.
```

---

## 6. How to Run

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Inspect Training Data & Train Models
```powershell
# Train Isolation Forest on genuine snapshots and evaluate held-out set
python ml/train_and_evaluate.py --data agent/data/feature_snapshots.jsonl --model iso_forest

# View dataset statistics and summary without training
python ml/train_and_evaluate.py --data agent/data/feature_snapshots.jsonl --summary
```

### Run Diagnostics Health Script
```powershell
python ml/health.py
```

### Run Automated Unit Tests (30 tests: 17 ML + 13 Adaptation)
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s ml/tests -v
```

### Run the ML Microservice (Port 5001)
```powershell
.\.venv\Scripts\python.exe ml/service.py
```

### Run Phase 5 Research Evaluation Harness
```powershell
.\.venv\Scripts\python.exe ml/experiments/eval_adaptation_scenarios.py
```

---

## 7. Phase 5 — Safe Adaptation Engine & Continuous Profile Evolution

Phase 5 introduces continuous behavioural identity evolution designed to answer:
> **How can a continuous biometric verification system accommodate legitimate human behavioural evolution while preventing suspicious observations from contaminating its trusted reference profile?**

### Core Components (`ml/adaptation/`):
1. **`candidate_buffer.py` (`CandidateObservationBuffer`)**:
   - Bounded FIFO observation queue (`capacity=20`, `ttl=3600s`).
   - Strictly isolated from active reference statistics.
   - Calculates candidate variance stability ($\sigma^2$) across observation windows.
2. **`adaptation_policy.py` (`AdaptationPolicy`)**:
   - Evaluates multi-dimensional evidence: verification score, drift magnitude, inter-window velocity, stability, and anomaly streaks.
   - Outputs one of five mutually exclusive states:
     - `NORMAL`: Legitimately conforming to baseline.
     - `SAFE_ADAPTATION`: Sufficient stable evidence passes all safety gates.
     - `SUSPICIOUS_CHANGE`: Flagged as deviation / anomalous.
     - `PROFILE_FROZEN`: Locked due to consecutive anomaly streak threshold.
     - `INSUFFICIENT_EVIDENCE`: Awaiting multi-window evidence or model ready.
3. **`profile_manager.py` (`ProfileManager`)**:
   - Manages versioned reference profiles (`v1.0.0` -> `v1.1.0`).
   - Pre-activation schema and numerical sanity validation.
   - Rollback capability to restore previous trusted baseline.
   - Automatic security freeze state machine.
4. **`safe_adaptation_engine.py` (`SafeAdaptationEngine`)**:
   - Central coordinator orchestrating Phase 4 anomaly detection with candidate buffer and profile manager.

---

## 8. Zero Fabrication Policy
All metrics reported in `artifacts/evaluation_results.json` and `artifacts/adaptation_evaluation_results.json` reflect genuine mathematical computations on recorded sessions and controlled functional stress testbeds. When multi-participant ground truth is absent, explicit limitations are documented rather than inventing artificial benchmark numbers.
