"""
Cyber Doppelgänger — Phase 7: Statistical Evaluation & Significance Testing
Safe Adaptive Behavioural Identity & Continuous User Verification

Calculates descriptive statistics, bootstrap 95% confidence intervals,
paired significance comparisons (Wilcoxon signed-rank, paired t-test),
and effect sizes (Cohen's d) across reproducible experimental benchmarks.

HONEST SCIENTIFIC REPORTING:
Never manufactures sample counts, p-values, or improvements.
If sample size is insufficient for non-parametric tests, descriptive metrics are reported
with an explicit scientific disclaimer regarding inference boundaries.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats


class StatisticalAnalysisEngine:
    """
    Performs rigorous statistical evaluation across multi-scenario and multi-seed benchmark runs.
    """

    @staticmethod
    def descriptive_statistics(values: List[float]) -> Dict[str, Any]:
        """Calculates sample count, mean, std, median, IQR, min, max."""
        if not values:
            return {
                "n": 0,
                "mean": None,
                "std": None,
                "median": None,
                "iqr": None,
                "min": None,
                "max": None,
                "status": "NOT_AVAILABLE"
            }

        arr = np.array(values, dtype=float)
        q75, q25 = np.percentile(arr, [75, 25])
        return {
            "n": int(len(arr)),
            "mean": float(round(float(np.mean(arr)), 4)),
            "std": float(round(float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0, 4)),
            "median": float(round(float(np.median(arr)), 4)),
            "iqr": float(round(float(q75 - q25), 4)),
            "min": float(round(float(np.min(arr)), 4)),
            "max": float(round(float(np.max(arr)), 4)),
            "status": "VALID"
        }

    @staticmethod
    def bootstrap_confidence_interval(
        values: List[float],
        n_bootstraps: int = 1000,
        ci: float = 0.95,
        seed: int = 42
    ) -> Dict[str, Any]:
        """Calculates non-parametric percentile bootstrap confidence interval."""
        if len(values) < 3:
            return {
                "ci_lower": None,
                "ci_upper": None,
                "confidence_level": ci,
                "status": "NOT_AVAILABLE",
                "reason": "Minimum 3 samples required for bootstrap resampling."
            }

        rng = np.random.RandomState(seed)
        arr = np.array(values, dtype=float)
        boot_means = []

        for _ in range(n_bootstraps):
            sample = rng.choice(arr, size=len(arr), replace=True)
            boot_means.append(float(np.mean(sample)))

        alpha = (1.0 - ci) / 2.0
        lower = float(np.percentile(boot_means, alpha * 100.0))
        upper = float(np.percentile(boot_means, (1.0 - alpha) * 100.0))

        return {
            "mean": float(round(float(np.mean(arr)), 4)),
            "ci_lower": float(round(lower, 4)),
            "ci_upper": float(round(upper, 4)),
            "confidence_level": ci,
            "resamples": n_bootstraps,
            "status": "VALID"
        }

    @staticmethod
    def paired_comparison(
        series_a: List[float],
        series_b: List[float],
        name_a: str = "Baseline",
        name_b: str = "Proposed"
    ) -> Dict[str, Any]:
        """
        Computes paired comparison between two evaluation series on identical test cases.
        Calculates:
          - Mean difference (B - A)
          - Cohen's d effect size
          - Paired t-test (parametric)
          - Wilcoxon signed-rank test (non-parametric)
        """
        if len(series_a) != len(series_b) or len(series_a) < 2:
            return {
                "status": "NOT_AVAILABLE",
                "reason": f"Paired comparison requires identical sample sizes (n >= 2). Found n_a={len(series_a)}, n_b={len(series_b)}."
            }

        arr_a = np.array(series_a, dtype=float)
        arr_b = np.array(series_b, dtype=float)
        diff = arr_b - arr_a
        n = len(diff)

        mean_diff = float(np.mean(diff))
        std_diff = float(np.std(diff, ddof=1)) if n > 1 else 1e-6

        # Cohen's d for paired samples
        cohens_d = float(mean_diff / (std_diff if std_diff > 1e-6 else 1.0))

        # Paired t-test
        try:
            t_stat, p_val_t = stats.ttest_rel(arr_b, arr_a)
            t_res = {
                "t_statistic": float(round(t_stat, 4)),
                "p_value": float(round(p_val_t, 6)),
                "statistically_significant_005": bool(p_val_t < 0.05)
            }
        except Exception as e:
            t_res = {"error": str(e), "p_value": None}

        # Wilcoxon signed-rank test
        try:
            # Check if all differences are zero
            if np.all(diff == 0):
                w_res = {
                    "w_statistic": 0.0,
                    "p_value": 1.0,
                    "statistically_significant_005": False,
                    "note": "All paired differences are identically zero."
                }
            elif n < 5:
                # Scipy wilcoxon requires n >= 5 for reliable p-value without exact calculation
                w_res = {
                    "w_statistic": None,
                    "p_value": None,
                    "status": "NOT_AVAILABLE",
                    "reason": f"Sample size n={n} too small for Wilcoxon signed-rank test (requires n >= 5)."
                }
            else:
                w_stat, p_val_w = stats.wilcoxon(arr_b, arr_a, zero_method="pratt")
                w_res = {
                    "w_statistic": float(round(w_stat, 4)),
                    "p_value": float(round(p_val_w, 6)),
                    "statistically_significant_005": bool(p_val_w < 0.05)
                }
        except Exception as e:
            w_res = {"error": str(e), "p_value": None}

        return {
            "sample_size": n,
            "comparison": f"{name_b} vs {name_a}",
            "mean_difference": float(round(mean_diff, 4)),
            "std_difference": float(round(std_diff, 4)),
            "cohens_d_effect_size": float(round(cohens_d, 4)),
            "paired_t_test": t_res,
            "wilcoxon_signed_rank": w_res,
            "status": "VALID",
            "scientific_disclaimer": "Statistical significance indicates pattern consistency across tested fixtures, not universal security immunity across unobserved attack variants."
        }
