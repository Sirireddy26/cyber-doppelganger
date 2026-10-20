# Cyber Doppelgänger — Experiment Workflow & Baseline Benchmarking
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

This document describes the reproducible experimental methodology, group-aware data split strategy, baseline algorithms, and evaluation protocol established in Phase 4.

---

## 1. Experimental Objectives

1. **Baseline Behavioral Characterization**: Fit an anomaly detection model (Isolation Forest) on genuine desktop user activity without storing sensitive keystroke or content data.
2. **Temporal Independence**: Prevent data leakage arising from consecutive time-series snapshots through session-group-aware partitioning.
3. **Threshold Calibration**: Determine an empirical decision boundary balancing False Acceptance and False Rejection on legitimate behavior.
4. **Transparent Limitation Reporting**: Explicitly document what metrics are mathematically supportable given the current single-user dataset, strictly refusing to fabricate impostor benchmarks.

---

## 2. Experimental Data Collection

- **Dataset Source**: `agent/data/feature_snapshots.jsonl`
- **Total Valid Snapshots**: 294 snapshots (each spanning a 15-second aggregation window).
- **Behavioral Modalities**:
  - Keyboard cadence: 11 numerical features (e.g., dwell intervals, flight latencies, typing speed).
  - Mouse kinematics: 14 numerical features (e.g., movement distance, speed, acceleration, click latencies).
  - Session continuity: 7 numerical features (e.g., active/idle ratio, activity density).
  - Application focus: 5 numerical features (e.g., process switches, active diversity).
- **Privacy Enforcement**: Pre-write sanitization rejected all content-level fields (keystroke characters, passwords, clipboard contents, screenshots, and URLs).

---

## 3. Data Partitioning Strategy

Because consecutive 15-second windows exhibit temporal autocorrelation, random cross-validation or random train-test splitting introduces significant optimistic data leakage.

### Session-Group-Aware Partitioning:
- **Partitioning Algorithm**: Snapshots are grouped by session boundaries (`session_id`) or chronological recording dates (`captured_at`).
- **Training Set**: 225 snapshots (76.5% of total dataset; chronological early sessions).
- **Test Set**: 69 snapshots (23.5% of total dataset; chronological held-out sessions).
- **Scaling Isolation**: `StandardScaler` parameters (mean $\mu$, variance $\sigma^2$) are fitted exclusively on the 225 training samples and transformed onto the 69 test samples.

---

## 4. Models & Threshold Calibration

### A. Isolation Forest Detector
- **Hyperparameters**: `n_estimators=100`, `contamination=0.05`, `random_state=42`.
- **Threshold Calibration**: The threshold $\tau$ is chosen as the 5th percentile of the training decision scores:
  $$\tau = 0.0594$$
- **Decision Rule**:
  - $\text{score} \ge \tau \implies \text{VERIFIED}$ (Legitimate activity conforming to baseline)
  - $\tau - 0.05 \le \text{score} < \tau \implies \text{UNCERTAIN}$ (Marginal boundary region)
  - $\text{score} < \tau - 0.05 \implies \text{DEVIATION}$ (Anomalous deviation)

### B. Random Forest Supervised Baseline
- **Hyperparameters**: `n_estimators=100`, `max_depth=8`, `random_state=42`.
- **Precondition**: Multi-class participant dataset (genuine vs impostor). In single-class mode, the pipeline safely documents `MODEL_NOT_READY` for supervised classification rather than generating misleading predictions.

---

## 5. Experimental Results

The results from the held-out evaluation on 69 genuine test snapshots (`ml/artifacts/evaluation_results.json`):

| Metric / Outcome | Value | Interpretation |
| :--- | :---: | :--- |
| **Training Samples** | 225 | Legitimate user enrollment baseline |
| **Test Samples** | 69 | Chronological held-out evaluation |
| **Calibrated Threshold** | `+0.0594` | 5th-percentile empirical boundary |
| **Verified Test Samples** | 65 (94.20%) | Consistent with legitimate user baseline |
| **Uncertain Samples** | 2 (2.90%) | Borderline variance during user transitions |
| **Deviation Samples** | 2 (2.90%) | Rare behavioral anomaly / transient pause |

---

## 6. Scientific Limitations & Future Directions

1. **Single-Participant Dataset**:
   The current operational dataset consists of natural interaction telemetry from one legitimate participant. Therefore, metrics that require labelled negative (impostor) classes—such as **ROC-AUC**, **False Acceptance Rate (FAR)**, and **Equal Error Rate (EER)**—cannot be computed without introducing arbitrary assumptions.
2. **Zero Fabrication**:
   In strict accordance with scientific ethics, synthetic impostor data was NOT mixed into the test set to invent artificial FAR/EER numbers.
3. **Transition to Phase 5**:
   Phase 4 establishes the static baseline and anomalous deviation detection. Phase 5 will implement the `SafeAdaptationEngine` to distinguish between gradual benign drift (which should safely evolve the baseline) and rapid malicious intrusion.
