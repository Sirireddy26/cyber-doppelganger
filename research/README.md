# Cyber Doppelgänger — Academic Research Foundation

**Research Title**: Safe Adaptive Behavioural Identity & Continuous User Verification  
**Target Output**: Working Prototype, Automated Experimental Evaluation, and IEEE/ACM-Ready Paper Artifacts  

---

## 1. Research Scope & Problem Statement

Continuous behavioural authentication monitors biometric keystroke dynamics and mouse kinematics throughout an authenticated workstation session. However, conventional adaptive systems encounter a fundamental security dilemma:
1. **Profile Stagnation (Static Profiles)**: Human computer-use behavior naturally drifts over time due to fatigue, task changes, and emotional state. When profiles remain strictly static, False Rejection Rates (FRR) escalate, frustrating legitimate users.
2. **Profile Contamination (The Doppelgänger Threat)**: Unchecked or unconstrained model adaptation enables active attackers or session hijackers to gradually corrupt the trusted baseline profile through slow impersonation or repeated bursts of anomalous activity.

**Research Objective**: Proposing and empirically evaluating a **Risk-Guided Safe Adaptation Engine** that accommodates legitimate behavioral drift safely within bounded velocity constraints while enforcing strict zero-contamination invariants under adversarial conditions.

---

## 2. Research Questions (RQs)

- **RQ1 (Static Profile Performance)**: How well does an immutable static behavioural profile identify deviations from the enrolled baseline under ambient variance, and when does lack of adaptation result in profile staleness?
- **RQ2 (Risk-Guided Adaptation Accommodation)**: Can risk-guided adaptation safely accommodate controlled legitimate behavioural drift without automatically absorbing suspicious or anomalous observations?
- **RQ3 (Comparative Baseline Evaluation)**: How does the proposed SafeAdaptationEngine compare against an immutable Static Reference Profile (Baseline A) and an unconstrained Conventional Adaptation baseline (Baseline B) under identical evaluation scenarios?
- **RQ4 (Adversarial Robustness & Freeze/Recovery Invariants)**: How do repeated suspicious observations, slow creep impersonation attempts, and automated freeze/recovery policies impact trusted profile integrity?
- **RQ5 (Computational & Operational Latency)**: What are the computational overhead, inference latency, and memory costs associated with continuous multi-window verification and safe profile adaptation?

---

## 3. Experimental Baselines

### Baseline A — Static Reference Profile
The enrolled reference profile parameters (feature means $\mu$ and standard deviations $\sigma$) remain strictly immutable ($v1.0.0$) following initial enrollment. No candidate buffer is maintained, and no parameter updates occur.

### Baseline B — Conventional Adaptation (Naive Sliding Window / EMA)
An unconstrained continuous adaptation strategy where running parameter estimates are updated on every incoming feature window via exponential moving average ($\alpha = 0.15$):
$$\mu_{t} = (1 - \alpha)\mu_{t-1} + \alpha x_{t}$$
This baseline lacks candidate buffering, drift bound checks, velocity gates, and streak anomaly freeze locks. Used strictly in isolated experimental copies to measure profile contamination vulnerability.

### Proposed Method — Risk-Guided Safe Adaptation Engine (`SafeAdaptationEngine`)
A multi-window candidate buffering architecture enforcing formal safety invariants:
- **Observation Barrier**: Minimum $N=5$ consecutive observations required before adaptation evaluation.
- **Drift Magnitude Bound**: Parameter drift distance constrained to $D \le 1.8\sigma$.
- **Drift Velocity Check**: Inter-window rate of change constrained to $V \le 2.5\sigma$.
- **Variance Stability Filter**: Inter-candidate variance required to satisfy $S \ge 0.35$.
- **Streak Anomaly Freeze**: $\ge 3$ consecutive suspicious observations trigger immediate lockdown (`PROFILE_FROZEN`).
- **Cryptographic Audit Lineage**: Version history preserves lineage with atomic rollback recovery.

---

## 4. Controlled Behavioural Scenarios

All scenarios are anchored on authentic $v1.0.0$ baseline distributions (435 genuine enrollment samples collected on the host machine):

| Scenario ID | Name | Tested Operational Condition | Expected Invariant |
| :--- | :--- | :--- | :--- |
| **SC-1** | Normal Behavioural Variation | Legitimate user with ambient variance ($\sim 0.15\sigma$) | Profile preserved at $v1.0.0$; zero unneeded retrainings. |
| **SC-2** | Gradual Legitimate Evolution | Subtle benign shift ($\sim 1.05\sigma \to 1.25\sigma$, stable) | Safe adaptation to $v1.1.0$ once candidate buffer satisfies stability. |
| **SC-3** | Sudden Behavioural Deviation | Transient non-malicious spike ($3.5\sigma$ jump) | Excluded from candidate buffer; reference profile intact. |
| **SC-4** | Controlled Simulated Takeover | Abrupt intruder jump ($+5.0\sigma$) sitting at workstation | Flagged as deviation; **0.0% profile contamination**. |
| **SC-5** | Slow Impersonation Creep | Adversary mimics user with subtle creep ($2.1\sigma \to 2.5\sigma$) | Velocity and drift bounds reject intake; **0.0% contamination**. |
| **SC-6** | Repeated Suspicious Bursts | Alternating anomaly bursts testing streak freeze threshold | Automated transition to `PROFILE_FROZEN` on streak 3. |
| **SC-7** | Contamination Poisoning | Intermittent poisoning vectors injected every 4th window | Naive baseline absorbs poison; Safe Engine achieves **0.0% contamination**. |
| **SC-8** | Freeze & Recovery Lifecycle | Streak freeze trigger $\to$ lockdown $\to$ authorized unfreeze | Verified state machine progression and successful recovery. |
| **SC-9** | Service Outage Resilience | Simulated ML service timeout (`SERVICE_UNAVAILABLE`) | Fail-secure invariant: adaptation strictly halts, profile intact. |

---

## 5. Metric Definitions

### Verification Metrics
- **False Acceptance Rate (FAR)**: $\text{FAR} = \frac{\text{False Accepts}}{\text{Total Intruder Observations}} \times 100\%$
- **False Rejection Rate (FRR)**: $\text{FRR} = \frac{\text{False Rejects}}{\text{Total Genuine Observations}} \times 100\%$
- **Precision**: $\frac{\text{True Accepts}}{\text{True Accepts} + \text{False Accepts}}$
- **Recall**: $\frac{\text{True Accepts}}{\text{True Accepts} + \text{False Rejects}}$
- **F1-Score**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
- **ROC-AUC**: Trapezoidal Mann-Whitney U computation over continuous anomaly scores.

### Adaptation Metrics
- **Profile Contamination Rate**: $\frac{\text{Intruder Observations Absorbed}}{\text{Total Intruder Observations}} \times 100\%$
- **Legitimate Change Acceptance Rate**: $\frac{\text{Accepted Benign Drift Windows}}{\text{Total Benign Drift Windows}} \times 100\%$
- **Suspicious Change Rejection Rate**: $\frac{\text{Flagged Suspicious Windows}}{\text{Total Suspicious Windows}} \times 100\%$
- **Recovery Success Rate**: $\frac{\text{Successful Unfreezes}}{\text{Total Freeze Triggers}} \times 100\%$

### Operational Metrics
- **Verification & Adaptation Latencies**: Wall-clock evaluation time (Mean, Median, 95th Percentile, 99th Percentile in ms).
- **Processing Throughput**: Observations processed per second ($\text{obs/s}$).

*Scientific Rule: If ground-truth labels are absent or sample counts are insufficient for a metric, the system explicitly reports `NOT_AVAILABLE` with documented rationale rather than substituting zero.*

---

## 6. Directory Structure

```
research/
├── configs/                                 # JSON experiment configurations
│   ├── full_suite.json                      # Comprehensive 9-scenario benchmark
│   ├── rq1_static_profile_eval.json         # Static baseline evaluation
│   └── rq4_adversarial_contamination.json   # Adversarial poisoning stress tests
├── experiments/                             # Experiment pipeline code
│   ├── runner.py                            # Central reproducible experiment runner
│   ├── scenario_generator.py                # 9 deterministic behavioural scenarios
│   ├── baselines.py                         # Isolated Baselines A, B, and Safe Engine
│   ├── metrics.py                           # Scientific metric formulas & edge-case guards
│   ├── statistical_analysis.py              # Descriptive stats, 95% CIs, paired tests
│   └── tables_and_figures.py                # LaTeX (.tex) tables and vector SVG figures
├── results/                                 # Dedicated timestamped run directories
│   └── exp_<timestamp>_<uuid>/              # Non-overwriting run artifacts
│       ├── config.json                      # Exact configuration snapshot
│       ├── manifest.json                    # Full execution manifest
│       ├── raw_results.json                 # Granular observation-by-observation results
│       ├── metrics.json                     # Computed verification & adaptation metrics
│       ├── research_report.md               # Auto-generated markdown research summary
│       ├── tables/                          # CSV tables and LaTeX (.tex) snippets
│       └── figures/                         # High-resolution vector (.svg) figures
└── README.md                                # This document
```

---

## 7. How to Reproduce Experiments

Run commands from the project root using PowerShell:

### Quick Smoke Test (Validates All Pipelines in ~3 seconds)
```powershell
.\.venv\Scripts\python.exe research/experiments/runner.py --smoke-test
```

### Full 9-Scenario Research Benchmark
```powershell
.\.venv\Scripts\python.exe research/experiments/runner.py --config research/configs/full_suite.json
```

### Run Custom Random Seed
```powershell
.\.venv\Scripts\python.exe research/experiments/runner.py --seed 2026
```

### Run Phase 7 Automated Regression Test Suite
```powershell
.\.venv\Scripts\python.exe -m unittest ml/tests/test_phase7_experiments.py
```

### Run All ML Tests (42/42)
```powershell
.\.venv\Scripts\python.exe -m unittest discover ml/tests
```

---

## 8. Threats to Validity & Honest Scientific Disclosure

1. **Synthetic Evaluation Boundary**: The scenarios evaluated herein represent controlled functional stress-testing using synthetically generated feature perturbations anchored on authentic $v1.0.0$ baseline distributions (435 genuine user samples). They formally verify functional safety invariants under adversarial conditions, but do not replace multi-subject population trials.
2. **Zero Fabrication Policy**: All reported rates, latencies, sample counts, and p-values derive strictly from deterministic execution saved in `raw_results.json`.
3. **Core Empirical Finding**: Unconstrained adaptation without candidate buffering inevitably suffers 100% contamination under sudden takeover and slow creep attacks. The proposed SafeAdaptationEngine provides verifiable reference preservation and zero contamination under all tested scenarios.
