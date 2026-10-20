# Cyber Doppelgänger — Architecture Overview
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

## 1. System Architecture Flowchart

```mermaid
flowchart TD
    subgraph Client ["Client Device (Zero Content Collection)"]
        Agent["Desktop Behavioural Agent\n(pynput, psutil, JSONL Buffer)"]
        Sensors["Privacy-Preserving Sensors\n(Keyboard Timing, Mouse Kinematics,\nSession Continuity, App Switches)"]
        Sensors --> Agent
    end

    subgraph BackendLayer ["Backend Services & Storage"]
        API["Spring Boot Backend API (:8080)\n(Security, Validation, Privacy Guards)"]
        DB[("PostgreSQL Database\n(Snapshots, Audits, Verification Results)")]
        Agent -->|"POST /api/agent/features\n(Schema 2.0)"| API
        API -->|"Persist Snapshots & Logs"| DB
    end

    subgraph MLLayer ["Machine Learning Verification Pipeline (:5001)"]
        MLService["Python ML Verification Service\n(HTTP Microservice on Port 5001)"]
        Preprocessor["Feature Preprocessor\n(37 Features, StandardScaler, NaN Guard)"]
        Baseline["Legitimate Reference Profile\n(Statistical Distributions, Zero-Var Guard)"]
        IsoForest["Isolation Forest Baseline\n(Unsupervised Anomaly Detector)"]
        RandForest["Random Forest Baseline\n(Supervised Labelled Evaluation)"]
        
        API -->|"POST /verify"| MLService
        MLService --> Preprocessor
        Preprocessor --> Baseline
        Baseline --> IsoForest
        Baseline --> RandForest
        MLService -->|"Verification Evidence\n(Status, Score, Threshold, Reason)"| API
    end

    subgraph FutureEngine ["Future Adaptation Layer (Phase 5)"]
        Adaptation["Safe Adaptation Engine\n(Contamination-Resistant Profile Learning,\nBaseline Drift Analysis)"]
        DB -.->|"Verification History"| Adaptation
    end

    subgraph FrontendLayer ["Operator Interface"]
        UI["React Dashboard (:5173)\n(Live Verification Monitoring & Metrics)"]
        API --> UI
    end
```

---

## 2. Component Status Matrix

| Component | Status | Responsibilities & Capabilities |
| :--- | :---: | :--- |
| **Desktop Behavioural Agent** | **Implemented (Phase 2)** | Keystroke dwell/flight times, mouse kinematics, session continuity, local JSONL buffering. |
| **Privacy Validation Guard** | **Implemented (Phase 2 & 3)** | Absolute exclusion of raw letters, typed text, passwords, URLs, and screen pixels. |
| **Spring Boot Backend** | **Implemented (Phase 3)** | Ingestion (`/api/agent/features`), retrieval (`/api/behaviour`), JWT auth, audit logging. |
| **PostgreSQL Storage** | **Implemented (Phase 3 & 4)** | Tables for `users`, `devices`, `sessions`, `behavioural_feature_snapshots`, `verification_results`, `audit_logs`. |
| **Feature Preprocessor** | **Implemented (Phase 4)** | 37 approved numerical behavioural features, NaN/Inf rejection, schema 2.0 validation, `StandardScaler`. |
| **Reference Profile** | **Implemented (Phase 4)** | Immutable statistical distributions (mean, std, median, IQR) for legitimate user baselines. |
| **Isolation Forest Detector**| **Implemented (Phase 4)** | 5th-percentile threshold calibration, logistic confidence mapping, `VERIFIED`/`UNCERTAIN`/`DEVIATION`. |
| **Random Forest Baseline**   | **Implemented (Phase 4)** | Supervised baseline with multi-class impostor verification guard and confidence calibration. |
| **ML Microservice**          | **Implemented (Phase 4)** | Zero-dependency HTTP service on port 5001 (`/health`, `/models/status`, `/verify`). |
| **Backend ML Integration**   | **Implemented (Phase 4)** | `POST /api/verification/process`, persistence to `verification_results`, offline resilience. |
| **Safe Adaptation Engine**   | **Planned (Phase 5)** | Contamination-resistant profile evolution and drift learning. (Intentionally omitted in Phase 4). |
| **React Dashboard**          | **Implemented (Phase 1-3)** | Health monitoring, shell layout, and live backend connectivity. |
