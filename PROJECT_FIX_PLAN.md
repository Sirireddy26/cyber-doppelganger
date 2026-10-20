# Cyber Doppelgänger — Quality Fix, Architectural Synchronization & Redesign Plan
**Project:** Cyber Doppelgänger: Safe Adaptive Behavioural Identity and Continuous User Verification  
**Author/Role:** Senior Full-Stack & ML Cybersecurity Engineer, Research Systems Specialist  
**Date:** October 2026  
**Status:** In Progress (Systematic Quality Implementation)

---

## 1. Executive Summary

This fix plan addresses confirmed defects, synchronization gaps, database ambiguities, ML score interpretations, zero-content privacy boundaries, and aesthetic redesign requirements identified across the Cyber Doppelgänger platform. All changes preserve working code and modular architecture across the Spring Boot backend, Python ML microservice, React frontend, and desktop telemetry agent.

---

## 2. Confirmed Defects & Root Cause Analysis

### Defect 1: Trusted Profile Discrepancy (Overview vs. Adaptation Dashboard)
- **Symptom:** The system overview displayed `TRUSTED PROFILE: NONE` while the Safe Adaptation Engine displayed active profile `v1.0.0` with 435 baseline samples.
- **Root Cause:** In `HealthController.java` (`getDiagnostics()`), profile status was solely derived by querying `ProfileVersionRepository.count()`. On application start with fresh H2 in-memory storage (or unseeded database), the database table is empty until an adaptation event writes to it. Meanwhile, the Python ML microservice loaded `v1.0.0` from `ml/artifacts/profile_versions.json`. Consequently, the overview reported `UNINITIALIZED` and `NONE`.
- **Impacted Files:**
  - `backend/src/main/java/com/cyberdoppelganger/controller/HealthController.java`
  - `backend/src/main/java/com/cyberdoppelganger/service/AdaptationService.java`
  - `frontend/src/App.tsx`
- **Fix:** 
  1. Authoritative synchronization: When `HealthController.getDiagnostics()` executes, query `adaptationService.getStatus()`.
  2. If the database repository is unseeded and the ML service confirms an active profile (e.g., `v1.0.0`), automatically synchronize and seed the initial `ProfileVersion` record into the database.
  3. Guarantee that overview, adaptation dashboard, verification engine, and telemetry views reflect identical profile state (`v1.0.0 ACTIVE`).

### Defect 2: Database Indicator Ambiguity (H2 vs. PostgreSQL)
- **Symptom:** Overview showed `H2` (or active DB), while `ModelDiagnostics.tsx` hardcoded `<span className="text-sm font-semibold font-mono text-white">PostgreSQL / H2</span>`.
- **Root Cause:** Hardcoded static label in `ModelDiagnostics.tsx` line 103 instead of binding dynamically to backend `DatabaseHealthService` diagnostic data (`meta.getDatabaseProductName()`).
- **Impacted Files:**
  - `frontend/src/components/telemetry/ModelDiagnostics.tsx`
  - `frontend/src/App.tsx`
  - `backend/src/main/java/com/cyberdoppelganger/service/DatabaseHealthService.java`
- **Fix:**
  1. Bind database badge directly to `diagnostics.database.database_type` and `diagnostics.database.connected`.
  2. Display exact environment context: `H2 (In-Memory Dev DB)` during development and `PostgreSQL (External Relational DB)` in production mode.
  3. If database health check fails, display `DISCONNECTED / ERROR` with clear troubleshooting hints, never a false positive.

### Defect 3: ML Score Interpretation, Directionality & Scientific Honesty
- **Symptom:** Technical labels like raw Isolation Forest decision score could be misunderstood as probability or percentage confidence without mathematical calibration.
- **Root Cause:** Isolation Forest returns `raw_score = model.decision_function(X)` where positive values indicate normal inliers and negative values indicate outliers. Anomaly score is defined as `-raw_score`. A non-calibrated score must not be portrayed as a true Bayesian probability of identity verification.
- **Impacted Files:**
  - `ml/anomaly_detection/isolation_forest_detector.py`
  - `frontend/src/components/telemetry/ModelDiagnostics.tsx`
  - `frontend/src/components/biometrics/BiometricPlayground.tsx`
  - `docs/ARCHITECTURE.md`
- **Fix:**
  1. Replace ambiguous labels with technically precise terms: `Model Decision Score (Raw)` and `Anomaly Score (-raw)`.
  2. Add informative research tooltips detailing:
     - Mathematical formula: `raw_score = decision_function(X)`
     - Normal range: $\ge 0$ (inlier cluster)
     - Decision threshold calibrated from 5th percentile of baseline training data (e.g., `0.0327`).
     - Clarify that anomaly score measures behavioural distance from baseline, not forensic proof of an attacker.

### Defect 4: Excessive Dark Cybersecurity UI vs. Soft Research Lab Aesthetic
- **Symptom:** Excessive dark backgrounds (`bg-slate-950`), neon glows, and illegible uppercase micro-labels created visual clutter rather than a calm, academic laboratory dashboard.
- **Root Cause:** Hardcoded dark Tailwind utility classes throughout the UI without standardized design tokens.
- **Impacted Files:**
  - `frontend/src/index.css`
  - `frontend/src/App.tsx`
  - `frontend/src/components/layout/Navbar.tsx`
  - `frontend/src/components/layout/Footer.tsx`
  - `frontend/src/components/biometrics/BiometricPlayground.tsx`
  - `frontend/src/components/adaptation/AdaptationDashboard.tsx`
  - `frontend/src/components/research/ResearchSimulators.tsx`
  - `frontend/src/components/telemetry/ModelDiagnostics.tsx`
- **Fix:**
  - Implement full Soft Pastel Theme tokens in `index.css`:
    - Base Background: `#F7F5FB`
    - Card Surfaces: `#FFFFFF` with restrained border `#D9E1EC`
    - Soft Lavender: `#EDE7F6`
    - Powder Blue: `#E6F0FA`
    - Soft Mint: `#DDF3E4` (Normal / Healthy)
    - Warm Peach: `#FCE8D5` (Warning / Drift)
    - Dusty Rose: `#F7DFE5` (Anomaly / Frozen)
    - Primary Button Accent: `#8B7AD9`
    - Text Primary: `#263247`
    - Text Secondary: `#64748B`
  - Ensure contrast compliance (WCAG AA), accessible focus rings, and explicit status badges with icons and readable captions (no color-only signals).

### Defect 5: Privacy Boundary Validation for Keystroke & Mouse Ingestion
- **Symptom:** Lack of explicit automated integration test asserting that identifiable user text (passwords, sentences, keystroke character keys) never appears in API payloads, snapshots, audit records, or exports.
- **Impacted Files:**
  - `agent/feature_extractor.py`
  - `backend/src/main/java/com/cyberdoppelganger/dto/FeatureSnapshotDTO.java`
  - `tests/test_privacy_boundary.py` (New test suite)
- **Fix:**
  - Implement automated privacy assertion test passing test strings (`SUPER_SECRET_PASSWORD_99`, `ATTACKER_TEXT`) to verify that only numerical timing aggregations (dwell time, flight time, velocity, jitter) are extracted and stored.

---

## 3. Systematic Implementation Steps

| Step | Phase | Task Description | Verification Criteria |
|---|---|---|---|
| 1 | B | Synchronize Profile Version between Python ML and Spring Boot DB in `HealthController` | `/api/health/diagnostics` reports `ready: true`, `active_version: "v1.0.0"` matching ML service |
| 2 | C | Dynamic Database Health Binding in frontend and PostgreSQL schema validation | `ModelDiagnostics` and `App` display actual active DB type; no hardcoded strings |
| 3 | D | Refine ML Score tooltips, calibration documentation, and score metrics | Clear tooltips explaining `decision_function` and threshold calibration |
| 4 | E | Privacy test suite: Zero-content transmission validation | New automated test proves zero character retention or text leaking |
| 5 | F | Validate Safe Adaptation state transitions (NORMAL, SAFE_ADAPTATION, SUSPICIOUS, FROZEN) | Unit & integration tests verify streak protection & candidate isolation |
| 6 | G | Redesign Frontend with Soft Pastel Palette (`#F7F5FB`, `#FFFFFF`, `#8B7AD9`, etc.) | Clean research laboratory UI with responsive layouts, accessible contrast |
| 7 | H & K | Final documentation: `DEPLOYMENT_GUIDE.md`, `PRIVACY_AND_DATA_HANDLING.md`, `RESEARCH_EXPERIMENT_READINESS.md`, `FINAL_IMPLEMENTATION_AUDIT.md` | Complete guides ready for university demonstration and hosting |
| 8 | I | End-to-end regression validation | Full test pass across Maven backend, Python ML/agent, and Vite build |
