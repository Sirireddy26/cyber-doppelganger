# Cyber Doppelgänger Architecture Specification

**Project**: CYBER DOPPELGÄNGER — Safe Adaptive Behavioural Identity & Continuous User Verification  
**Domain**: Continuous Biometric Authentication, Behavioural Anomaly Detection, Zero-Trust Adaptive Security  

---

## 1. End-to-End System Pipeline

```
  ┌────────────────────────────────────────────────────────┐
  │                    LOCAL COMPUTER                      │
  └───────────────────────────┬────────────────────────────┘
                              │ Physical User Interaction
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │             PYTHON BEHAVIOURAL AGENT                   │
  │    (pynput timing hooks, psutil hardware context)       │
  │    * Zero key logging, Zero screen capture             │
  └───────────────────────────┬────────────────────────────┘
                              │ Raw Millisecond Timings & Velocities
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 FEATURE EXTRACTION                     │
  │  18-Dimensional Kinematics Vector (Dwell, Flight,      │
  │  Latency, Curvature, Velocity, Acceleration, Rates)    │
  └───────────────────────────┬────────────────────────────┘
                              │ Statistical Vector (Privacy Cleared)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                ML VERIFICATION ENGINE                  │
  │  (Isolation Forest, One-Class SVM Anomaly Scoring)     │
  │  Continuous Trust Score [0.0 - 1.0]                    │
  └───────────────────────────┬────────────────────────────┘
                              │ Trust Score + Anomaly Metric
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │               SAFE ADAPTATION ENGINE                   │
  │  Policy Decision Matrix:                               │
  │  TRUSTED -> PASSIVE_MONITOR -> CHALLENGE -> STEP_UP_MFA│
  └───────────────────────────┬────────────────────────────┘
                              │ Telemetry Windows & Decisions
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │               SPRING BOOT REST API                     │
  │  Java 17, Spring Web, Spring Security, JWT, JPA       │
  └───────────────────────────┬────────────────────────────┘
                              │ Persist Audit & State
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │               POSTGRESQL DATABASE                      │
  │  Sessions, Telemetry Windows, Events, Adaptations      │
  └───────────────────────────┬────────────────────────────┘
                              │ REST / WebSockets / Live Polling
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 REACT DASHBOARD                        │
  │  Vite, React 19, TypeScript, Tailwind CSS, Recharts    │
  └────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### A. Python Desktop Agent (`/agent`)
- Runs locally in user space.
- Hooks into low-level keyboard and mouse event queues via `pynput`.
- **Privacy Contract**: Replaces key identifiers with anonymous memory addresses. Only records timestamps for dwell time (key down to key up) and flight time (key up to next key down).
- Intercepts mouse coordinates solely to compute displacement, velocity, acceleration, and curvature.
- Aggregates events into 30-second sliding time windows.

### C. Machine Learning Verification Pipeline (`/ml`)
- Learns baseline biometric profile for the genuine user from 37 approved numerical behavioral features.
- Employs Isolation Forest (calibrated decision threshold 0.0327) and Random Forest multi-class comparison.
- Evaluates individual observation windows producing deterministic verification evidence: `rawScore`, `anomalyScore`, `threshold`, `confidenceScore`, and `decision` (`VERIFIED` vs `DEVIATION`).

### D. Safe Adaptation Engine (`/ml/adaptation`)
- **Strict Decision Separation**: Verification (assessing whether observation matches baseline) is strictly decoupled from Adaptation (deciding whether baseline may safely absorb observation).
- **Candidate Observation Buffer**: Bounded (capacity 20, TTL 3600s), isolated from trusted profile.
- **Multi-Window Gating**: Enforces minimum sample requirements (5 windows), maximum drift magnitude (1.8 sigma), maximum velocity (2.5), and minimum stability score (0.35).
- **Profile Versioning & Atomic Rollback**: Semantic version lineage (`v1.0.0` -> `v1.1.0`), candidate verification before activation, and atomic rollback to prior trusted versions.
- **Defense-in-Depth Freeze**: Anomaly streak threshold (3 consecutive anomalies) immediately transitions profile to `PROFILE_FROZEN`, blocking updates until administrative re-authorization.

### E. Spring Boot Backend API (`/backend`)
- High-throughput Java 17 + Spring Boot 3.4 REST API.
- Replay protection: Rejects duplicate feature snapshots with identical `(deviceId, capturedAt)`.
- Input validation & non-finite filter: Rejects NaN and Infinity numerical strings.
- Chained ingestion pipeline: Ingest Snapshot -> Ingestion Persistence -> ML Verification Service -> Safe Adaptation Engine -> Event & Profile Persistence -> Audit Logging.
- Granular diagnostics: `GET /api/health/diagnostics` and `GET /api/system/diagnostics` inspecting Backend, Database, ML Service, Model Readiness, Profile Readiness, Adaptation Engine, and Agent Telemetry separately.
- Authorization enforcement: Profile modifications (`freeze`, `unfreeze`, `rollback`) require verified `authorized_by` security identity (HTTP 401 Unauthorized if missing).

### F. React Frontend Dashboard (`/frontend`)
- Real-time visualization for user identity trust score, kinematics playground, anomaly distribution, audit logs, and 6-subsystem live diagnostics status ribbon.

---

## 3. Decision Separation: Verification vs Adaptation

| Metric / Stage | Verification Decision | Adaptation Decision |
| :--- | :--- | :--- |
| **Primary Question** | "Does this 15-second window match the active profile?" | "Should this observation update the trusted profile?" |
| **Governing Component** | Isolation Forest / ML Inference Service | Risk-Guided Safe Adaptation Engine |
| **Input Data** | Single 15-second snapshot feature vector | Feature snapshot + verification evidence + candidate buffer history |
| **Decision Space** | `VERIFIED` or `DEVIATION` | `NORMAL`, `SAFE_ADAPTATION`, `SUSPICIOUS_CHANGE`, `PROFILE_FROZEN` |
| **Trust Impact** | Zero profile modification | May promote candidate buffer into new profile version |
| **Security Safeguard** | Calibrated anomaly threshold | Drift bound, velocity check, multi-window buffer, streak freeze |

---

## 4. Privacy Boundary Contract

The architecture enforces a hard privacy boundary across all collectors, APIs, and databases:
- **Permitted Data**: Approved derived statistical features (dwell time mean/std, flight time mean/std, mouse velocity mean/max/std, mouse acceleration, curvature ratio, click rate, pause ratio), window duration, device ID, user ID, schema version, profile version tags.
- **Forbidden Data**: Typed character values, key names, words, passwords, clipboard data, window titles, browser URLs, screenshots, raw pixel buffers, document contents, file paths. Ingestion filters reject payloads containing any forbidden fields with HTTP 400 Bad Request.
