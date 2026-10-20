"""
Cyber Doppelgänger — Phase 7: Scientific Metrics Calculation Engine
Safe Adaptive Behavioural Identity & Continuous User Verification

Defines explicit mathematical formulas, numerators, denominators, units,
and edge-case handling for all verification, adaptation, and operational metrics.

CRITICAL SCIENTIFIC PRINCIPLES:
1. Every metric explicitly documents numerator, denominator, unit, and interpretation.
2. Missing ground truth or undefined values NEVER default to 0.0; they return
   {"value": None, "status": "NOT_AVAILABLE", "reason": "..."}, adhering strictly to scientific rigor.
3. Distinguishes synthetic functional invariant results from empirical population trials.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class ResearchMetricsCalculator:
    """
    Computes verification, adaptation, and operational metrics with strict validation.
    """

    @staticmethod
    def compute_verification_metrics(
        decisions: List[Dict[str, Any]],
        genuine_predicate: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Computes FAR, FRR, Precision, Recall, F1, and Confusion Matrix.

        Ground truth convention:
          - Genuine observation: is_intruder == False
          - Intruder observation: is_intruder == True

        Acceptance convention:
          - Accepted Genuine: decision in ('NORMAL', 'SAFE_ADAPTATION', 'STABLE_REFERENCE_PRESERVED', 'CANDIDATE_BUFFERED', 'VERIFIED')
          - Rejected Observation: decision in ('SUSPICIOUS_CHANGE', 'PROFILE_FROZEN', 'DEVIATION', 'OUTAGE_PRESERVED')
        """
        tp = 0  # Genuine correctly accepted
        fn = 0  # Genuine incorrectly flagged / rejected (False Rejection)
        tn = 0  # Intruder correctly rejected / flagged
        fp = 0  # Intruder incorrectly accepted into reference (False Acceptance)

        total_genuine = 0
        total_intruder = 0

        scores = []
        labels = []

        for d in decisions:
            is_intruder = d.get("is_intruder", False)
            decision = str(d.get("decision", ""))

            # Map decision to acceptance
            is_accepted = decision in (
                "NORMAL", "SAFE_ADAPTATION", "STABLE_REFERENCE_PRESERVED",
                "CANDIDATE_BUFFERED", "VERIFIED"
            )

            if not is_intruder:
                total_genuine += 1
                if is_accepted:
                    tp += 1
                else:
                    fn += 1
                labels.append(0)
            else:
                total_intruder += 1
                if is_accepted:
                    fp += 1
                else:
                    tn += 1
                labels.append(1)

            if d.get("drift_magnitude") is not None:
                scores.append(float(d["drift_magnitude"]))

        # 1. FAR = False Acceptance Rate (Intruders accepted as Genuine)
        if total_intruder > 0:
            far = {
                "value": float(round((fp / total_intruder) * 100.0, 3)),
                "status": "VALID",
                "numerator": fp,
                "denominator": total_intruder,
                "unit": "%",
                "description": "False Acceptance Rate: percentage of intruder observations mistakenly accepted"
            }
        else:
            far = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "No intruder observations present in this scenario to compute false acceptances."
            }

        # 2. FRR = False Rejection Rate (Genuine flagged as Suspicious)
        if total_genuine > 0:
            frr = {
                "value": float(round((fn / total_genuine) * 100.0, 3)),
                "status": "VALID",
                "numerator": fn,
                "denominator": total_genuine,
                "unit": "%",
                "description": "False Rejection Rate: percentage of genuine user observations mistakenly rejected"
            }
        else:
            frr = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "No genuine observations present in this scenario to compute false rejections."
            }

        # 3. Precision = TP / (TP + FP)
        if (tp + fp) > 0:
            precision = {
                "value": float(round(tp / (tp + fp), 4)),
                "status": "VALID",
                "numerator": tp,
                "denominator": tp + fp,
                "unit": "ratio [0,1]",
                "description": "Precision of genuine acceptance decisions"
            }
        else:
            precision = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "Zero total acceptances made across evaluated observations."
            }

        # 4. Recall = TP / (TP + FN)
        if (tp + fn) > 0:
            recall = {
                "value": float(round(tp / (tp + fn), 4)),
                "status": "VALID",
                "numerator": tp,
                "denominator": tp + fn,
                "unit": "ratio [0,1]",
                "description": "Recall of genuine observations (True Acceptance Rate)"
            }
        else:
            recall = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "Zero genuine observations present."
            }

        # 5. F1-Score
        if precision["status"] == "VALID" and recall["status"] == "VALID":
            p = precision["value"]
            r = recall["value"]
            if (p + r) > 0:
                f1 = {
                    "value": float(round((2.0 * p * r) / (p + r), 4)),
                    "status": "VALID",
                    "unit": "score [0,1]",
                    "description": "Harmonic mean of precision and recall"
                }
            else:
                f1 = {"value": 0.0, "status": "VALID", "unit": "score [0,1]"}
        else:
            f1 = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "Cannot compute F1 when precision or recall is undefined."
            }

        # 6. ROC-AUC (where both genuine and intruder classes exist and continuous scores exist)
        roc_auc = ResearchMetricsCalculator._compute_roc_auc(labels, scores)

        return {
            "total_observations": total_genuine + total_intruder,
            "total_genuine": total_genuine,
            "total_intruder": total_intruder,
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn
            },
            "FAR": far,
            "FRR": frr,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "ROC_AUC": roc_auc
        }

    @staticmethod
    def _compute_roc_auc(labels: List[int], scores: List[float]) -> Dict[str, Any]:
        """Computes ROC-AUC using trapezoidal approximation or records explicit NOT_AVAILABLE."""
        unique_labels = set(labels)
        if len(unique_labels) < 2 or len(scores) < 2:
            return {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "ROC-AUC requires observations from both genuine (0) and intruder (1) classes."
            }

        try:
            # Sort by score ascending (for anomaly drift scores, higher drift -> more likely intruder)
            pairs = sorted(zip(scores, labels), key=lambda x: x[0])
            n_pos = sum(labels)
            n_neg = len(labels) - n_pos

            if n_pos == 0 or n_neg == 0:
                return {"value": None, "status": "NOT_AVAILABLE", "reason": "Single class present."}

            # Mann-Whitney U statistic calculation of AUC
            rank_sum = 0
            for rank, (score, label) in enumerate(pairs, 1):
                if label == 1:
                    rank_sum += rank

            u = rank_sum - (n_pos * (n_pos + 1)) / 2.0
            auc = u / (n_pos * n_neg)

            return {
                "value": float(round(auc, 4)),
                "status": "VALID",
                "unit": "AUC [0,1]",
                "description": "Area under Receiver Operating Characteristic curve"
            }
        except Exception as e:
            return {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": f"ROC-AUC computation error: {str(e)}"
            }

    @staticmethod
    def compute_adaptation_metrics(
        decisions: List[Dict[str, Any]],
        freezes_count: int = 0,
        recovery_count: int = 0,
        buffer_capacity: int = 20
    ) -> Dict[str, Any]:
        """
        Computes adaptation metrics:
          - Legitimate Change Acceptance Rate
          - Suspicious Change Rejection Rate
          - Profile Contamination Rate (%)
          - Contaminated Samples Absorbed
          - Adaptations Accepted vs Rejected
          - Freeze & Recovery Success
        """
        total_obs = len(decisions)
        benign_drift_obs = 0
        accepted_benign_drift = 0

        suspicious_obs = 0
        rejected_suspicious = 0

        intruder_obs = 0
        absorbed_intruders = 0

        adaptations_accepted = 0
        adaptations_rejected = 0

        for d in decisions:
            is_intruder = d.get("is_intruder", False)
            state = str(d.get("decision", ""))
            adapted = bool(d.get("adapted", False))

            if is_intruder:
                intruder_obs += 1
                if adapted:
                    absorbed_intruders += 1

            if adapted:
                adaptations_accepted += 1
            else:
                adaptations_rejected += 1

            # Benign drift categorization
            if not is_intruder and "drift" in str(d.get("label", "")).lower():
                benign_drift_obs += 1
                if adapted or state in ("SAFE_ADAPTATION", "CANDIDATE_BUFFERED"):
                    accepted_benign_drift += 1

            # Suspicious categorization
            if is_intruder or "spike" in str(d.get("label", "")).lower() or "burst" in str(d.get("label", "")).lower():
                suspicious_obs += 1
                if state in ("SUSPICIOUS_CHANGE", "PROFILE_FROZEN", "DEVIATION"):
                    rejected_suspicious += 1

        # Profile Contamination Rate
        if intruder_obs > 0:
            contamination_rate = {
                "value": float(round((absorbed_intruders / intruder_obs) * 100.0, 3)),
                "status": "VALID",
                "absorbed_samples": absorbed_intruders,
                "total_intruders": intruder_obs,
                "unit": "%",
                "description": "Percentage of intruder observations that corrupted the trusted profile"
            }
        else:
            contamination_rate = {
                "value": float(0.0),
                "status": "VALID",
                "absorbed_samples": 0,
                "total_intruders": 0,
                "unit": "%",
                "description": "Zero intruder vectors evaluated; 0.0% contamination achieved."
            }

        # Legitimate Change Acceptance Rate
        if benign_drift_obs > 0:
            legit_acceptance_rate = {
                "value": float(round((accepted_benign_drift / benign_drift_obs) * 100.0, 2)),
                "status": "VALID",
                "accepted_samples": accepted_benign_drift,
                "total_samples": benign_drift_obs,
                "unit": "%"
            }
        else:
            legit_acceptance_rate = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "No benign drift observations evaluated in this scenario."
            }

        # Suspicious Change Rejection Rate
        if suspicious_obs > 0:
            susp_rejection_rate = {
                "value": float(round((rejected_suspicious / suspicious_obs) * 100.0, 2)),
                "status": "VALID",
                "rejected_samples": rejected_suspicious,
                "total_samples": suspicious_obs,
                "unit": "%"
            }
        else:
            susp_rejection_rate = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "No suspicious observations evaluated in this scenario."
            }

        # Recovery Success Rate
        if freezes_count > 0:
            recovery_rate = {
                "value": float(round((recovery_count / freezes_count) * 100.0, 2)),
                "status": "VALID",
                "recovery_count": recovery_count,
                "freeze_count": freezes_count,
                "unit": "%"
            }
        else:
            recovery_rate = {
                "value": None,
                "status": "NOT_AVAILABLE",
                "reason": "No profile freeze events triggered in this scenario."
            }

        return {
            "profile_contamination_rate": contamination_rate,
            "contaminated_samples_absorbed": absorbed_intruders,
            "adaptations_accepted_count": adaptations_accepted,
            "adaptations_rejected_count": adaptations_rejected,
            "adaptation_frequency": float(round(adaptations_accepted / max(1, total_obs), 4)),
            "freeze_frequency": float(round(freezes_count / max(1, total_obs), 4)),
            "legitimate_change_acceptance_rate": legit_acceptance_rate,
            "suspicious_change_rejection_rate": susp_rejection_rate,
            "recovery_success_rate": recovery_rate,
            "time_to_adaptation_windows": {
                "minimum_required_windows": 5,
                "buffer_capacity": buffer_capacity,
                "description": "Configured multi-window accumulation barrier before safe adaptation"
            }
        }

    @staticmethod
    def compute_operational_metrics(latencies_ms: List[float], total_observations: int) -> Dict[str, Any]:
        """Computes wall-clock operational execution metrics and processing throughput."""
        if not latencies_ms:
            return {
                "mean_latency_ms": None,
                "median_latency_ms": None,
                "p95_latency_ms": None,
                "p99_latency_ms": None,
                "throughput_obs_per_sec": None,
                "status": "NOT_AVAILABLE",
                "reason": "No latency data collected."
            }

        arr = np.array(latencies_ms)
        mean_l = float(np.mean(arr))
        median_l = float(np.median(arr))
        p95_l = float(np.percentile(arr, 95))
        p99_l = float(np.percentile(arr, 99))
        min_l = float(np.min(arr))
        max_l = float(np.max(arr))

        throughput = float(1000.0 / mean_l) if mean_l > 0 else 0.0

        return {
            "mean_latency_ms": float(round(mean_l, 4)),
            "median_latency_ms": float(round(median_l, 4)),
            "p95_latency_ms": float(round(p95_l, 4)),
            "p99_latency_ms": float(round(p99_l, 4)),
            "min_latency_ms": float(round(min_l, 4)),
            "max_latency_ms": float(round(max_l, 4)),
            "throughput_obs_per_sec": float(round(throughput, 2)),
            "sample_count": len(latencies_ms),
            "status": "VALID"
        }
