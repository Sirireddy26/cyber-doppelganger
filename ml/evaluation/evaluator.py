"""
Cyber Doppelgänger - Model Evaluation & Benchmark Metrics
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates rigorous biometric verification metrics:
- Precision, Recall, F1-score, Confusion Matrix
- False Acceptance Rate (FAR), False Rejection Rate (FRR)
- Equal Error Rate (EER) and ROC-AUC
Enforces group-aware splits (by session) to prevent temporal data leakage.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
import logging

logger = logging.getLogger("cyber-doppelganger.ml")


def group_aware_split(
    snapshots: List[Dict[str, Any]],
    labels: Optional[List[int]] = None,
    group_key: str = "session_id",
    test_size: float = 0.25,
    random_state: int = 42
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Optional[List[int]], Optional[List[int]]]:
    """
    Performs group-aware split based on session identifiers to prevent temporal data leakage.
    Adjacent snapshots from the same interactive session are kept together in either train or test.
    """
    rng = np.random.default_rng(random_state)
    
    # Extract unique sessions (or pseudo-sessions based on time grouping if missing)
    groups: Dict[str, List[int]] = {}
    for idx, s in enumerate(snapshots):
        grp = s.get(group_key) or s.get("sessionId") or f"group_{(idx // 5)}"
        groups.setdefault(str(grp), []).append(idx)

    group_keys = list(groups.keys())
    rng.shuffle(group_keys)

    n_test_groups = max(1, int(len(group_keys) * test_size))
    test_group_keys = set(group_keys[:n_test_groups])
    train_group_keys = set(group_keys[n_test_groups:])

    train_indices = [i for k in train_group_keys for i in groups[k]]
    test_indices = [i for k in test_group_keys for i in groups[k]]

    train_snaps = [snapshots[i] for i in train_indices]
    test_snaps = [snapshots[i] for i in test_indices]

    train_labels = [labels[i] for i in train_indices] if labels is not None else None
    test_labels = [labels[i] for i in test_indices] if labels is not None else None

    return train_snaps, test_snaps, train_labels, test_labels


class ModelEvaluator:
    """
    Evaluates binary behavioral verification models.
    Convention:
    - 1 = Genuine / Legitimate User
    - 0 = Impostor / Other User
    """

    @staticmethod
    def calculate_eer(y_true: np.ndarray, y_scores: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculates Equal Error Rate (EER) and the operating threshold where FAR == FRR.
        Returns (eer, threshold) or (None, None) if computation is not mathematically possible.
        """
        unique_labels = np.unique(y_true)
        if len(unique_labels) < 2:
            return None, None

        # fpr = FAR (False Acceptance of impostors)
        # fnr = FRR (False Rejection of genuine users) = 1 - tpr
        fpr, tpr, thresholds = roc_curve(y_true, y_scores, pos_label=1)
        fnr = 1.0 - tpr

        # Find point where |FPR - FNR| is minimized
        abs_diffs = np.abs(fpr - fnr)
        min_idx = np.argmin(abs_diffs)
        eer = float((fpr[min_idx] + fnr[min_idx]) / 2.0)
        opt_threshold = float(thresholds[min_idx]) if min_idx < len(thresholds) else 0.5
        return round(eer, 4), round(opt_threshold, 4)

    @staticmethod
    def evaluate_predictions(
        y_true: List[int],
        y_pred: List[int],
        y_scores: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates complete evaluation metrics.
        Returns structured dictionary.
        """
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)

        unique_labels = np.unique(y_true_arr)
        if len(unique_labels) < 2:
            return {
                "status": "UNAVAILABLE",
                "reason": f"Evaluation requires both genuine and impostor samples. Only class {unique_labels.tolist()} present.",
                "sample_count": len(y_true),
                "metrics": None
            }

        cm = confusion_matrix(y_true_arr, y_pred_arr, labels=[0, 1])
        tn, fp, fn, tp = [int(v) for v in cm.ravel()]

        # Biometric metrics:
        # FAR = False Acceptance Rate = FP / (FP + TN) [Impostors wrongly accepted]
        # FRR = False Rejection Rate = FN / (FN + TP) [Genuines wrongly rejected]
        far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        frr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
        rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
        f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

        roc_auc = None
        eer = None
        opt_thresh = None

        if y_scores is not None and len(y_scores) == len(y_true):
            y_scores_arr = np.array(y_scores)
            try:
                roc_auc = float(roc_auc_score(y_true_arr, y_scores_arr))
                roc_auc = round(roc_auc, 4)
            except Exception as e:
                logger.warning(f"Could not compute ROC-AUC: {e}")

            eer, opt_thresh = ModelEvaluator.calculate_eer(y_true_arr, y_scores_arr)

        return {
            "status": "SUCCESS",
            "sample_count": len(y_true),
            "genuine_count": int(np.sum(y_true_arr == 1)),
            "impostor_count": int(np.sum(y_true_arr == 0)),
            "confusion_matrix": {
                "true_negatives_impostor_blocked": tn,
                "false_positives_impostor_accepted": fp,
                "false_negatives_genuine_blocked": fn,
                "true_positives_genuine_accepted": tp
            },
            "metrics": {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "false_acceptance_rate": round(far, 4),
                "false_rejection_rate": round(frr, 4),
                "roc_auc": roc_auc,
                "equal_error_rate": eer,
                "optimal_eer_threshold": opt_thresh
            }
        }
