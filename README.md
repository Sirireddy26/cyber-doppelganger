# Cyber Doppelgänger

## Overview

Cyber Doppelgänger is a privacy-conscious continuous user verification system that learns behavioural patterns such as typing rhythm, mouse behaviour, and session activity without storing the actual content typed by the user.

It aims to distinguish:
- normal behaviour
- legitimate behavioural evolution
- suspicious behavioural deviation

The core research focus is **safe behavioural adaptation**—ensuring that a user's biometric baseline can safely evolve over time without allowing an attacker to poison or contaminate the behavioural profile.

---

## Architecture

The end-to-end continuous verification pipeline operates as follows:

```
Python Agent
     ↓
Feature Extraction
     ↓
Behavioural Verification
     ↓
Behaviour Change Analysis
     ↓
Safe Adaptation Engine
     ↓
Spring Boot Backend
     ↓
PostgreSQL
     ↓
React Dashboard
```

*(Note: In Phase 1, the core architecture, configuration, interfaces, and health communications are established; live telemetry streaming, behavioral verification, change analysis, and adaptation engines will be fully implemented in subsequent phases).*

---

## Technology Stack

- **Desktop Behavioural Agent**: Python 3.11+, pynput, psutil, pandas, numpy, scikit-learn, requests
- **Backend API**: Java 17+, Spring Boot, Spring Web, Spring Data JPA, Spring Security, Bean Validation, PostgreSQL Driver, Maven
- **Database**: PostgreSQL (with in-memory H2 development fallback)
- **Frontend Dashboard**: React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React
- **Machine Learning**: Python, scikit-learn

---

## Repository Structure

```
cyber-doppelganger/
├── agent/            # Python desktop agent (interfaces, configuration, logging, privacy guard)
├── backend/          # Java 17 + Spring Boot 3.4 REST service (/api/health, security, JPA)
├── database/         # Database migrations, seed scripts, and configuration guides
├── docs/             # Architecture, API specifications, and user documentation
├── frontend/         # React + TypeScript + Vite dashboard
├── ml/               # Machine learning pipelines, anomaly detection & experiments
├── research/         # Research questions, literature review, and academic paper drafts
├── scripts/          # Automation, startup, and end-to-end verification scripts
├── tests/            # Cross-component integration tests
├── .env.example      # Environment variable template with safe defaults
├── .gitignore        # Complete Git exclusion rules
├── LICENSE           # Open-source MIT License
└── README.md         # Master project documentation
```

---

## Development Status

- **Phase 1 — Foundation: COMPLETE**
- **Phase 2 — Privacy-Safe Behavioural Agent: COMPLETE**
- **Phase 3 — Real Backend, PostgreSQL Database & Agent Integration: COMPLETE**
- **Phase 4 — Machine Learning Behavioural Verification Pipeline: COMPLETE**
- **Phase 5 — Safe Adaptation Engine & Continuous Behavioural Profile Evolution: COMPLETE**
- **Phase 6 — End-to-End Integration, Security Hardening, Live Monitoring & Research Evaluation: COMPLETE**

### What Is Currently Implemented:
- [x] **Monorepo Architecture**: Clean separation across `agent/`, `backend/`, `database/`, `docs/`, `frontend/`, `ml/`, `research/`, and `scripts/`.
- [x] **Privacy-Safe Desktop Agent (Phase 2)**: Real-time keyboard timing, coordinate-free mouse kinematics, active/idle session continuity, anonymous process monitoring, and local JSONL disk buffering.
- [x] **Database Architecture & Migrations (Phase 3 & Phase 5)**: PostgreSQL schema and Flyway migrations for `users`, `devices`, `sessions`, `behavioural_feature_snapshots`, `audit_logs`, `security_events`, `verification_results` (V2), and `profile_versions`, `adaptation_events`, `profile_freeze_records` (V3 migration).
- [x] **Feature Ingestion API (Phase 3 & Phase 6)**: `POST /api/agent/features` with schema versioning (`schema_version: "2.0"`), NaN/Inf string validation, replay protection (device + timestamp uniqueness), and automatic chained verification & adaptation evaluation.
- [x] **Behaviour Retrieval API (Phase 3)**: `GET /api/behaviour`, `GET /api/behaviour/{id}`, and `GET /api/behaviour/history` with pagination and DTO mapping.
- [x] **Authentication & Security (Phase 3 & Phase 6)**: BCrypt password hashing, Spring Security, JWT authentication (`POST /api/auth/register`, `POST /api/auth/login`), profile operation authorization enforcement (`authorized_by` required on freeze/unfreeze/rollback), and hardened CORS.
- [x] **ML Behavioural Verification Pipeline (Phase 4)**:
  - 37 approved numerical behavioural features strictly validated against schema 2.0.
  - Zero-content privacy: No raw keystrokes, characters, passwords, URLs, or screen contents.
  - Anomaly detection baseline via Isolation Forest with calibrated decision threshold (0.0327).
  - Supervised baseline via Random Forest with multi-class verification guards.
  - Immutable Reference Profile recording baseline statistics (mean, std, median, IQR).
  - Session-group-aware data split preventing temporal data leakage.
- [x] **Safe Adaptation Engine (Phase 5)**:
  - **Explainable Decision States**: `NORMAL`, `SAFE_ADAPTATION`, `SUSPICIOUS_CHANGE`, `PROFILE_FROZEN`, `INSUFFICIENT_EVIDENCE`.
  - **Contamination Resistance**: Defends against single-observation poisoning, sudden takeover, gradual drift poisoning, and buffer poisoning.
  - **Candidate Observation Buffer**: Bounded (capacity 20, TTL 3600s), privacy-safe (37 derived kinematics only), completely isolated from trusted profiles.
  - **Profile Versioning & Rollback**: Semantic version lineage (`v1.0.0` -> `v1.1.0`), candidate validation before promotion, atomic activation, and full historical rollback.
  - **Defense-in-Depth Security Freeze**: Consecutive anomaly streak threshold triggers `PROFILE_FROZEN`, halting all updates until administrative re-authorization.
- [x] **Phase 6 End-to-End Integration & Security Hardening**:
  - **End-to-End Trace**: Ingest Snapshot -> Validate Schema -> Anomaly Inference (Isolation Forest) -> Safe Adaptation Evaluation -> Candidate Buffering / Version Update -> Persistence -> Audit Trail -> Live UI Monitoring.
  - **Replay Protection**: Identical `(deviceId, capturedAt)` combinations rejected with HTTP 400 Bad Request.
  - **Non-Finite Number Filtering**: Rejection of `"NaN"`, `"Infinity"`, `"-Infinity"` values in JSON payloads.
  - **Profile Authorization Guards**: Mandatory non-blank `authorized_by` security identity for `/api/adaptation/freeze`, `/api/adaptation/unfreeze`, and `/api/adaptation/rollback` (returns HTTP 401 Unauthorized otherwise).
  - **Thread-Safe Synchronization**: Concurrency locking on profile update transactions.
  - **Granular Diagnostics Endpoint**: `GET /api/health/diagnostics` and `GET /api/system/diagnostics` reporting separate health states for Backend, Database, ML Microservice, Model Readiness, Trusted Profile, Adaptation Engine, and Agent Telemetry without collapsing into a single misleading status.
  - **Live Monitoring UI**: React 19 dashboard with Phase 6 status badge, 6-subsystem live diagnostic bar, and verified data rendering.
  - **Reproducible Research Evaluation Benchmark**: `ml/experiments/eval_adaptation_scenarios.py` evaluating Scenarios A through G (Normal variation, Gradual drift, Sudden takeover, Poisoning bursts, Slow creep impersonation, Freeze/recovery lifecycle, and Service outage resilience) with reproducible random seed 42, zero data fabrication, and deterministic output saved to `ml/artifacts/phase6_reproducible_evaluation_report.json` and `research/experiments/phase6_adaptation_benchmark_report.md`.
- [x] **Zero Fabrication**: No fake ML metrics, no fake confidence values, and no fabricated research data.

---

## Privacy Principles

By foundational design, the system will **NOT** collect:
- ❌ actual typed characters
- ❌ passwords
- ❌ clipboard contents
- ❌ screenshots
- ❌ screen contents
- ❌ document contents
- ❌ browser contents

Only derived, non-invasive behavioural measurements are used (dwell duration, flight time between keys, mouse velocity, acceleration, and curvature ratios).

---

## Quick Start & Verification

### 1. Build and Test Backend (30 tests)
```powershell
cd backend
.\mvnw.cmd test
```

### 2. Run Backend Locally (Port 8080)
```powershell
cd backend
.\mvnw.cmd spring-boot:run
```

### 3. Run ML Microservice (Port 5001)
```powershell
.\.venv\Scripts\python.exe ml/service.py
```

### 4. Run ML Diagnostics and Test Suite (30 tests)
```powershell
.\.venv\Scripts\python.exe ml/health.py
.\.venv\Scripts\python.exe -m unittest discover -s ml/tests -v
```

### 5. Run Phase 6 Reproducible Research Evaluation Harness (Scenarios A–G)
```powershell
.\.venv\Scripts\python.exe ml/experiments/eval_adaptation_scenarios.py
```

### 6. Run Agent Unit Tests (33 tests)
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s agent/tests
```

### 7. Run and Build Frontend
```powershell
cd frontend
npm run build
npm run dev
```

---

## Total Automated Tests

- **Agent Test Suite**: 33 / 33 tests passed
- **ML Verification & Adaptation Test Suite**: 30 / 30 tests passed
- **Backend Spring Boot & Integration Test Suite**: 30 / 30 tests passed
- **Total Automated Test Count**: **93 / 93 passing tests**

---

## Research Warning

> **"Research claims and performance results will only be reported after reproducible experiments. No fabricated results will be used."**
