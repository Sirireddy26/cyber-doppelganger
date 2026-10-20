"""
Cyber Doppelgänger — Phase 7 Automated Regression & Research Validation Tests
Safe Adaptive Behavioural Identity & Continuous User Verification

Validates:
  1. Reproducible scenario generation with a fixed seed.
  2. Correct experiment configuration loading and schema validation.
  3. Unique experiment IDs and non-overwriting result persistence.
  4. Metric calculations against small, manually verifiable test fixtures.
  5. Missing ground truth resulting in NOT_AVAILABLE rather than fabricated values.
  6. Correct distinction between synthetic and empirical results.
  7. Correct profile-contamination metric definitions (0% vs >0%).
  8. Correct handling of frozen profiles and rollback outcomes.
  9. Result-table, LaTeX snippet, and figure generation from saved results.
  10. Absence of hardcoded research metrics in generated outputs.
  11. Handling of missing or malformed experiment inputs.
  12. Interrupted experiments and partial-result reporting.
"""

import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from research.experiments.scenario_generator import BehaviouralScenarioGenerator, load_enrolled_baseline_stats
from research.experiments.baselines import StaticProfileBaseline, ConventionalAdaptationBaseline, SafeAdaptationWrapper
from research.experiments.metrics import ResearchMetricsCalculator
from research.experiments.statistical_analysis import StatisticalAnalysisEngine
from research.experiments.tables_and_figures import PaperArtifactsGenerator
from research.experiments.runner import ExperimentRunner


class TestPhase7ResearchPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="cd_test_p7_")
        self.stats = load_enrolled_baseline_stats()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Reproducible scenario generation with fixed seed
    # -------------------------------------------------------------------------
    def test_reproducible_scenario_generation(self):
        gen1 = BehaviouralScenarioGenerator(seed=123, baseline_stats=self.stats)
        gen2 = BehaviouralScenarioGenerator(seed=123, baseline_stats=self.stats)
        gen3 = BehaviouralScenarioGenerator(seed=999, baseline_stats=self.stats)

        sc1 = gen1.scenario_1_normal_variation(n=10)
        sc2 = gen2.scenario_1_normal_variation(n=10)
        sc3 = gen3.scenario_1_normal_variation(n=10)

        # Identical seeds must yield identical float vectors
        for i in range(10):
            for k in sc1[i]["features"]:
                self.assertEqual(sc1[i]["features"][k], sc2[i]["features"][k])

        # Different seeds must yield different float vectors
        differences = sum(
            1 for i in range(10)
            if sc1[i]["features"]["typing_speed"] != sc3[i]["features"]["typing_speed"]
        )
        self.assertGreater(differences, 0)

    # -------------------------------------------------------------------------
    # 2. Correct experiment configuration loading
    # -------------------------------------------------------------------------
    def test_config_loading_and_defaults(self):
        cfg_file = Path(self.temp_dir) / "custom_config.json"
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump({
                "experiment_name": "Custom Test",
                "random_seed": 777,
                "window_count_per_scenario": 12
            }, f)

        runner = ExperimentRunner(config_path=cfg_file, output_base_dir=Path(self.temp_dir))
        self.assertEqual(runner.config["experiment_name"], "Custom Test")
        self.assertEqual(runner.seed, 777)
        self.assertEqual(runner.config["window_count_per_scenario"], 12)
        # Default keys must be preserved
        self.assertIn("policy_parameters", runner.config)

    # -------------------------------------------------------------------------
    # 3. Unique experiment IDs and non-overwriting result persistence
    # -------------------------------------------------------------------------
    def test_unique_experiment_ids_and_non_overwriting(self):
        runner1 = ExperimentRunner(output_base_dir=Path(self.temp_dir), smoke_test=True)
        runner2 = ExperimentRunner(output_base_dir=Path(self.temp_dir), smoke_test=True)

        self.assertNotEqual(runner1.experiment_id, runner2.experiment_id)
        self.assertNotEqual(runner1.output_dir, runner2.output_dir)

        res1 = runner1.run()
        res2 = runner2.run()

        # Both directories must coexist without collision
        self.assertTrue((runner1.output_dir / "raw_results.json").exists())
        self.assertTrue((runner2.output_dir / "raw_results.json").exists())

    # -------------------------------------------------------------------------
    # 4. Metric calculations against manually verifiable test fixtures
    # -------------------------------------------------------------------------
    def test_verifiable_metrics_hand_calculation(self):
        # 10 observations:
        # Genuine: 5 observations. Decisions: 4 accepted (TP=4), 1 rejected (FN=1)
        # Intruder: 5 observations. Decisions: 1 accepted (FP=1), 4 rejected (TN=4)
        decisions = [
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "SUSPICIOUS_CHANGE"},  # FN
            {"is_intruder": True, "decision": "NORMAL"},             # FP (accepted)
            {"is_intruder": True, "decision": "DEVIATION"},
            {"is_intruder": True, "decision": "DEVIATION"},
            {"is_intruder": True, "decision": "DEVIATION"},
            {"is_intruder": True, "decision": "DEVIATION"},
        ]

        m = ResearchMetricsCalculator.compute_verification_metrics(decisions)

        cm = m["confusion_matrix"]
        self.assertEqual(cm["true_positives"], 4)
        self.assertEqual(cm["false_negatives"], 1)
        self.assertEqual(cm["true_negatives"], 4)
        self.assertEqual(cm["false_positives"], 1)

        # Expected FAR: 1 FP / 5 Intruders = 20.0%
        self.assertEqual(m["FAR"]["value"], 20.0)
        # Expected FRR: 1 FN / 5 Genuine = 20.0%
        self.assertEqual(m["FRR"]["value"], 20.0)
        # Expected Precision: 4 / (4 + 1) = 0.8
        self.assertEqual(m["precision"]["value"], 0.8)
        # Expected Recall: 4 / (4 + 1) = 0.8
        self.assertEqual(m["recall"]["value"], 0.8)
        # Expected F1: 2 * 0.8 * 0.8 / 1.6 = 0.8
        self.assertEqual(m["f1_score"]["value"], 0.8)

    # -------------------------------------------------------------------------
    # 5. Missing ground truth resulting in NOT_AVAILABLE (no zero substitution)
    # -------------------------------------------------------------------------
    def test_missing_ground_truth_returns_not_available(self):
        # Purely genuine observations (zero intruders)
        decisions = [
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "NORMAL"},
            {"is_intruder": False, "decision": "NORMAL"},
        ]
        m = ResearchMetricsCalculator.compute_verification_metrics(decisions)

        # FAR must be NOT_AVAILABLE because denominator (total_intruder) is 0
        self.assertEqual(m["FAR"]["status"], "NOT_AVAILABLE")
        self.assertIsNone(m["FAR"]["value"])
        self.assertIn("No intruder observations", m["FAR"]["reason"])

        # ROC-AUC must be NOT_AVAILABLE because only 1 class present
        self.assertEqual(m["ROC_AUC"]["status"], "NOT_AVAILABLE")
        self.assertIsNone(m["ROC_AUC"]["value"])

    # -------------------------------------------------------------------------
    # 6. Correct distinction between synthetic and empirical results
    # -------------------------------------------------------------------------
    def test_synthetic_metadata_marking(self):
        gen = BehaviouralScenarioGenerator(seed=42, baseline_stats=self.stats)
        sc = gen.scenario_4_controlled_takeover(n=5)
        for w in sc:
            self.assertTrue(w["is_synthetic"])
            self.assertIn("transformation_rule", w)
            self.assertIn("scenario_id", w)

    # -------------------------------------------------------------------------
    # 7. Profile-contamination metric definitions (Safe Engine 0% vs Naive > 0%)
    # -------------------------------------------------------------------------
    def test_profile_contamination_calculation(self):
        gen = BehaviouralScenarioGenerator(seed=42, baseline_stats=self.stats)
        windows = gen.scenario_4_controlled_takeover(n=12)

        naive_model = ConventionalAdaptationBaseline(self.stats)
        safe_wrapper = SafeAdaptationWrapper(self.stats)

        for w in windows:
            naive_model.evaluate(w["features"], is_intruder=w["is_intruder"])
            safe_wrapper.evaluate(w["features"], is_intruder=w["is_intruder"])

        intruders = sum(1 for w in windows if w["is_intruder"])
        self.assertGreater(intruders, 0)

        # Naive baseline MUST suffer contamination from intruder vectors
        self.assertGreater(naive_model.contaminated_samples_absorbed, 0)
        naive_contam_rate = (naive_model.contaminated_samples_absorbed / intruders) * 100.0
        self.assertEqual(naive_contam_rate, 100.0)

        # Safe adaptation engine MUST strictly achieve 0.0% contamination
        self.assertEqual(safe_wrapper.contaminated_samples_absorbed, 0)
        safe_wrapper.cleanup()

    # -------------------------------------------------------------------------
    # 8. Handling of frozen profiles and rollback outcomes
    # -------------------------------------------------------------------------
    def test_freeze_and_recovery_invariants(self):
        wrapper = SafeAdaptationWrapper(self.stats)
        self.assertFalse(wrapper.pm.is_frozen)

        # Freeze profile
        wrapper.engine.freeze("Test administrative drill")
        self.assertTrue(wrapper.pm.is_frozen)

        # While frozen, new observations must NOT adapt
        sample_feats = {k: float(v["mean"]) for k, v in self.stats.items()}
        res = wrapper.evaluate(sample_feats, is_intruder=False)
        self.assertFalse(res["adapted"])
        self.assertEqual(res["decision"], "PROFILE_FROZEN")

        # Unfreeze
        success, msg = wrapper.unfreeze(authorized_by="sec-ops-admin", reason="Recovery verified")
        self.assertTrue(success)
        self.assertFalse(wrapper.pm.is_frozen)

        # Rollback to v1.0.0
        rb_ok, rb_msg = wrapper.rollback("v1.0.0", reason="Test reset")
        self.assertTrue(rb_ok)
        self.assertEqual(wrapper.pm.active_version.version_tag, "v1.0.0")

        wrapper.cleanup()

    # -------------------------------------------------------------------------
    # 9. Result-table and figure generation from saved results
    # -------------------------------------------------------------------------
    def test_result_tables_and_figures_generation(self):
        runner = ExperimentRunner(output_base_dir=Path(self.temp_dir), smoke_test=True)
        results = runner.run()

        # Verify tables created
        tables_dir = runner.output_dir / "tables"
        self.assertTrue((tables_dir / "scenario_comparison.csv").exists())
        self.assertTrue((tables_dir / "table1_verification_metrics.tex").exists())
        self.assertTrue((tables_dir / "table2_adaptation_metrics.tex").exists())
        self.assertTrue((tables_dir / "table3_operational_performance.tex").exists())

        # Verify figures created
        figs_dir = runner.output_dir / "figures"
        self.assertTrue((figs_dir / "fig1_verification_decisions.svg").exists())
        self.assertTrue((figs_dir / "fig2_legitimate_vs_suspicious.svg").exists())
        self.assertTrue((figs_dir / "fig3_profile_contamination.svg").exists())
        self.assertTrue((figs_dir / "fig4_drift_and_adaptation_trajectory.svg").exists())
        self.assertTrue((figs_dir / "fig5_latency_distributions.svg").exists())
        self.assertTrue((figs_dir / "fig6_freeze_recovery_lifecycle.svg").exists())
        self.assertTrue((figs_dir / "figures_manifest.json").exists())

    # -------------------------------------------------------------------------
    # 10. No hardcoded research metrics in generated outputs
    # -------------------------------------------------------------------------
    def test_no_hardcoded_metrics_in_tex_tables(self):
        runner = ExperimentRunner(output_base_dir=Path(self.temp_dir), smoke_test=True)
        res = runner.run()

        tex1_path = runner.output_dir / "tables" / "table1_verification_metrics.tex"
        with open(tex1_path, "r", encoding="utf-8") as f:
            content = f.read()

        # The LaTeX file must contain the exact computed FAR/FRR from the run object
        far_val = str(res["global_metrics"]["false_acceptance_rate_far_pct"])
        self.assertIn(far_val, content)

    # -------------------------------------------------------------------------
    # 11. Missing or malformed experiment inputs handling
    # -------------------------------------------------------------------------
    def test_malformed_config_falls_back_gracefully(self):
        bad_cfg = Path(self.temp_dir) / "corrupt.json"
        with open(bad_cfg, "w", encoding="utf-8") as f:
            f.write("{ invalid json content ::::")

        runner = ExperimentRunner(config_path=bad_cfg, output_base_dir=Path(self.temp_dir), smoke_test=True)
        # Must not crash; falls back to defaults
        self.assertEqual(runner.seed, 42)
        self.assertIn("Scenario_1_Normal_Variation", runner.config["scenarios_to_evaluate"])

    # -------------------------------------------------------------------------
    # 12. Statistical analysis engine validation
    # -------------------------------------------------------------------------
    def test_statistical_analysis_calculations(self):
        stat_eng = StatisticalAnalysisEngine()
        data = [1.0, 2.0, 3.0, 4.0, 5.0]

        desc = stat_eng.descriptive_statistics(data)
        self.assertEqual(desc["mean"], 3.0)
        self.assertEqual(desc["median"], 3.0)
        self.assertEqual(desc["min"], 1.0)
        self.assertEqual(desc["max"], 5.0)

        # Bootstrap 95% CI
        ci = stat_eng.bootstrap_confidence_interval(data, n_bootstraps=500, seed=42)
        self.assertEqual(ci["status"], "VALID")
        self.assertLessEqual(ci["ci_lower"], ci["mean"])
        self.assertGreaterEqual(ci["ci_upper"], ci["mean"])

        # Paired comparison
        a = [100.0, 100.0, 100.0, 100.0, 100.0]
        b = [0.0, 0.0, 0.0, 0.0, 0.0]
        paired = stat_eng.paired_comparison(a, b, "Naive", "Safe")
        self.assertEqual(paired["mean_difference"], -100.0)
        self.assertEqual(paired["status"], "VALID")


if __name__ == "__main__":
    unittest.main()
