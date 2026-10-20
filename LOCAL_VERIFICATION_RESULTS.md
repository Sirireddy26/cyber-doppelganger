# Cyber Doppelgänger — Local Verification Results

**Document Version:** 1.0.0  
**Verification Date:** 2026-10-16  
**Environment:** Windows (PowerShell)  
**Verification Scope:** Local pre-deployment stage verification of Backend, ML Microservice, Database, Frontend, Desktop Agent, Privacy Safeguards, and Adaptation Engine.  
**Final Status:** **VERIFIED FOR LOCAL DEMO**

---

## Executive Summary

The Cyber Doppelgänger platform has undergone thorough empirical verification on the local workstation. All test suites across the Python desktop agent, Python ML microservice, Java Spring Boot backend, and React/TypeScript frontend have executed with **100% pass rates (109/109 tests passing)**. 

All three core runtime services were started, health-checked, and exercised in an integrated end-to-end loop:
- Feature Ingestion &rarr; Privacy Validation &rarr; H2 Persistence &rarr; ML Inference (`/verify`) &rarr; Adaptation Policy &rarr; Profile Freezing / Unfreezing &rarr; Audit Logging.
- The Python desktop behavioural agent's `ApiClient` successfully established communication with the Spring Boot backend (`http://localhost:8080`), passed client-side privacy filtering, and ingested an approved numerical feature snapshot resulting in HTTP 201 Created and immediate downstream ML inference.
- Privacy inspection confirmed **zero transmission, logging, or storage** of raw keystrokes, typed characters, passwords, clipboard contents, screenshots, URLs, or window titles.

---

## 1. Actual Services & Runtime Versions Found

| Component | Technology | Version | Runtime Port | State |
| :--- | :--- | :--- | :--- | :--- |
| **Backend API** | Java Spring Boot | 3.4.4 (Java 17.0.20.1, Tomcat 10.1.39, Hibernate 6.6.11) | `8080` | **HEALTHY / RUNNING** |
| **Database** | In-Memory H2 (PostgreSQL Mode) | 2.3.232 | In-VM (`jdbc:h2:mem:cyber_doppelganger`) | **HEALTHY / RUNNING** |
| **ML Microservice** | Python Flask + Scikit-learn | Python 3.11.9, Flask 3.1.0, Scikit-learn 1.6.1, NumPy 2.2.3 | `5001` | **HEALTHY / RUNNING** |
| **Frontend UI** | React + TypeScript + Vite | React 19.0.0, TypeScript 5.7.2, Vite 8.3.3 | `5173` | **HEALTHY / RUNNING** |
| **Desktop Agent** | Python Telemetry Client | Python 3.11.9 (`agent/main.py`, `agent/communication/api_client.py`) | Outbound client | **VERIFIED & CONNECTED** |

---

## 2. Test Execution Outcomes

All test suites were executed using the repository's documented commands in PowerShell.

### 2.1 Desktop Behavioural Agent Test Suite
- **Command:** `.\.venv\Scripts\python.exe -m unittest discover -s agent/tests -p "test_*.py"`
- **Result:** **33/33 PASSED** in 3.570s (0 failures, 0 errors)
- **Coverage:**
  - `test_keyboard_collector.py`: Interval timing, pause counts, zero text capture.
  - `test_mouse_collector.py`: Kinematics, velocity, acceleration, click counts, zero coordinates.
  - `test_application_collector.py`: Process counts, active load, context switches, zero window titles/URLs.
  - `test_session_collector.py`: Active/idle ratio, continuity tracking.
  - `test_feature_snapshot.py`: Dataclass serialization, schema 2.0 validation.
  - `test_privacy_filter.py`: Rejection of prohibited fields (`typed_text`, `password`, `clipboard`, `screenshot`).
  - `test_api_client.py`: Graceful offline handling, HTTP snapshot transmission.

### 2.2 Machine Learning & Adaptation Engine Test Suite
- **Command:** `.\.venv\Scripts\python.exe -m unittest discover -s ml/tests -p "test_*.py"`
- **Result:** **42/42 PASSED** in 6.376s (0 failures, 0 errors)
- **Coverage:**
  - `test_service.py`: Flask `/health`, `/verify`, `/models`, and `/privacy-policy` endpoints.
  - `test_feature_extractor.py`: 12-dimensional canonical feature vector extraction.
  - `test_isolation_forest.py`: Decision boundary, score normalization, anomaly thresholding.
  - `test_adaptation_engine.py`: Candidate buffering, drift velocity, freeze trigger, rollback.
  - `test_candidate_buffer.py`: FIFO queue, TTL eviction, duplicate rejection.
  - `test_profile_versioning.py`: Profile freezing, streak tracking, rollback integrity.

### 2.3 Privacy Boundary Verification Suite
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_privacy_boundary.py`
- **Result:** **4/4 PASSED** in 0.479s (0 failures, 0 errors)
- **Coverage:**
  - `test_agent_sanitizer_enforcement`: Asserts agent-side filtering prevents prohibited fields.
  - `test_backend_privacy_filter_rejection`: Asserts backend rejects tainted payloads with HTTP 400.
  - `test_ml_service_privacy_filter_rejection`: Asserts ML service refuses non-numerical features.
  - `test_end_to_end_privacy_preservation`: Validates clean schema 2.0 numerical payload ingestion.

### 2.4 Spring Boot Backend Test Suite
- **Command:** `.\mvnw.cmd test`
- **Result:** **30/30 PASSED** in 48.699s (`BUILD SUCCESS`, 0 failures, 0 errors)
- **Coverage:**
  - `AdaptationControllerTests`: Status, candidate summary, freeze/unfreeze, rollback (7 tests).
  - `AuthServiceTests`: Password hashing (BCrypt), user registration, credential verification (3 tests).
  - `EndToEndPipelineIntegrationTests`: Multi-snapshot pipeline, replay rejection, adaptation workflow (6 tests).
  - `FeatureIngestionAndRetrievalTests`: Snapshot ingestion, bean validation, pagination, privacy filter (6 tests).
  - `SecurityAndAuthTests`: JWT authentication, protected endpoint authorization (4 tests).
  - `VerificationControllerTests`: Single snapshot verification, model status, paging (4 tests).

### 2.5 Frontend Production Build
- **Command:** `npm run build` (in `frontend/`)
- **Result:** **SUCCESS** in 3.54s (1,903 modules transformed, 0 errors)

---

## 3. Service Startup & Health Verification

All three runtime services were started concurrently and validated via live HTTP requests:

1. **Python ML Service** (`http://127.0.0.1:5001`)
   - **Command:** `.\.venv\Scripts\python.exe ml/service.py`
   - **Health Endpoint:** `GET http://127.0.0.1:5001/health`
   - **Response (HTTP 200):**
     ```json
     {
       "status": "healthy",
       "service": "cyber-doppelganger-ml",
       "version": "1.0.0",
       "models_loaded": {
         "isolation_forest": true,
         "random_forest": false
       }
     }
     ```

2. **Java Spring Boot Backend** (`http://localhost:8080`)
   - **Command:** `.\mvnw.cmd spring-boot:run`
   - **Health Endpoint:** `GET http://localhost:8080/api/health`
   - **Response (HTTP 200):**
     ```json
     {
       "status": "UP",
       "service": "cyber-doppelganger-backend",
       "database": "UP",
       "database_type": "H2",
       "timestamp": "2026-10-16T09:21:27.886156Z"
     }
     ```

3. **React Vite Frontend** (`http://localhost:5173`)
   - **Command:** `npm run dev`
   - **HTTP Check:** `GET http://localhost:5173/` returned **HTTP 200 OK** (HTML entry point with `<div id="root">` rendered).

---

## 4. End-to-End Pipeline & Adaptation Lifecycle Verification

A live telemetry ingestion cycle was performed against the active backend and downstream ML service:

### 4.1 Inlier Observation (Normal Verification)
- **Action:** Ingested standard baseline snapshot (schema 2.0).
- **ML Evaluation:** `raw_score: +0.1344` &ge; `threshold: +0.0327`.
- **Decision:** `status: VERIFIED`, `decision: BENIGN_ACTIVITY`.
- **Adaptation Engine:** `decision_state: INLIER_OBSERVATION`, added to candidate buffer.
- **Profile:** Remains active at `v1.0.0`.

### 4.2 Outlier Observation (Suspicious Verification)
- **Action:** Ingested anomalous snapshot with atypical inter-key timing and extreme cursor velocity.
- **ML Evaluation:** `raw_score: -0.1081` < `threshold: +0.0327`.
- **Decision:** `status: DEVIATION`, `decision: ANOMALOUS_BEHAVIOUR`.
- **Adaptation Engine:** `decision_state: SUSPICIOUS_CHANGE`, rejected from buffer to prevent poisoning, `suspicious_streak: 1`.

### 4.3 Profile Freezing & Anomaly Streak Threshold
- **Action:** Ingested 3 consecutive anomalous observations.
- **Outcome:** `suspicious_streak` reached configured threshold (`3`).
- **Policy Trigger:** Engine automatically entered `FROZEN` status:
  - `is_frozen: true`
  - `freeze_reason: "Suspicious anomaly streak reached threshold (3)."`
  - Candidate buffer was immediately flushed (`current_size: 0`).
  - Silent profile adaptation was completely locked down.

### 4.4 Recovery, Unfreeze & Rollback
- **Unauthorized Unfreeze Attempt:** Anonymous request to `/api/adaptation/unfreeze` without authorization parameters rejected with HTTP 400.
- **Authorized Administrative Unfreeze:**
  - Sent `POST /api/adaptation/unfreeze` with `{"authorized_by": "admin", "reason": "Local verification unfreeze test"}`.
  - Returned HTTP 200: `engine_status: "ACTIVE"`, `is_frozen: false`, `suspicious_streak: 0`.
- **Rollback Validation:** Verified `/api/adaptation/rollback` endpoint accepts authorized target profile version and restores prior baseline state.

### 4.5 Robustness & Replay Attack Defense
- **Replay Protection:** Submitting a duplicate snapshot with identical `(device_id, captured_at)` was rejected immediately by the backend with **HTTP 400 Bad Request** (`Duplicate feature snapshot detected`).
- **Malformed Payload Handling:** Payloads with missing mandatory fields, invalid ISO-8601 timestamps, or `NaN`/`Infinity` float values were rejected with **HTTP 400 Bad Request**.

---

## 5. Desktop Behavioural Agent Connection Verification

The desktop agent was executed against the running backend using its native `ApiClient` and feature dataclasses:

- **Health Check:** `ApiClient.check_health()` successfully reached `http://localhost:8080/api/health` and verified backend status `UP`.
- **Telemetry Transmission:**
  - Constructed a full `FeatureSnapshot` with `KeyboardFeatures`, `MouseFeatures`, `SessionFeatures`, and `ApplicationFeatures`.
  - Client-side `PrivacyFilter.validate_snapshot_dict()` confirmed zero prohibited fields.
  - Snapshot transmitted to `POST /api/agent/features`.
  - Backend response: **HTTP 201 Created** with `snapshot_id: "1"`, `processing_error: null`, and populated ML verification/adaptation blocks.

---

## 6. Privacy & Security Findings

Inspection of actual transmitted payloads and stored database records was conducted:

1. **Inspection of Stored Database Record (`GET /api/behaviour/1`):**
   ```json
   {
     "id": 1,
     "device_id": "desktop-agent-workstation-01",
     "schema_version": "2.0",
     "features": {
       "keyboard": {
         "total_key_events": 45,
         "mean_key_interval": 0.182,
         "median_key_interval": 0.165,
         "key_interval_std": 0.045,
         "minimum_key_interval": 0.08,
         "maximum_key_interval": 0.45,
         "typing_speed": 3.8,
         "pause_count": 2,
         "mean_pause_duration": 1.2,
         "longest_pause": 1.8,
         "typing_activity_duration": 28.5
       },
       "mouse": {
         "movement_distance": 1240.5,
         "mean_mouse_speed": 185.2,
         "mouse_speed_std": 45.0,
         "mean_acceleration": 95.0,
         "click_count": 8,
         "left_click_count": 6,
         "right_click_count": 2,
         "scroll_count": 4,
         "mouse_active_duration": 22.0
       },
       "session": {
         "session_duration": 60.0,
         "active_duration": 48.0,
         "idle_duration": 12.0,
         "active_idle_ratio": 4.0,
         "activity_density": 0.8
       },
       "application": {
         "process_count": 18,
         "active_process_count": 5,
         "application_switch_count": 3,
         "process_activity_count": 12,
         "application_activity_duration": 48.0
       }
     }
   }
   ```
2. **Prohibited Content Verification:**
   - **Typed Characters / Passwords:** ZERO keystroke characters, scan codes, or key names captured or stored.
   - **Clipboard Data:** ZERO clipboard text or buffers captured or stored.
   - **Screenshots & Coordinates:** ZERO screen buffers or coordinate trails captured or stored (only aggregate pixel distance and speeds).
   - **URLs & Window Titles:** ZERO document titles, window titles, or URLs tracked (only anonymized process counts and context switch counts).
3. **Secrets Audit:**
   - Repository contains only `.env.example` templates; no live production secrets, database credentials, or JWT private keys are checked into source control.
   - `application.yml` uses environment variable injection with safe local development defaults.

---

## 7. Issues Identified & Resolved During Verification

1. **Transaction Rollback on External Service Failures:**
   - **Issue:** If the ML service was unreachable during feature ingestion, `VerificationService` threw `RestClientException`, marking the active Spring transaction as `rollback-only`. The outer transaction in `FeatureIngestionService` then threw `UnexpectedRollbackException` when attempting to return HTTP 201.
   - **Root Cause:** Spring's `@Transactional` rollback-on-exception defaults intercepted the runtime exception before the calling service could catch and handle it gracefully.
   - **Resolution:** Updated `@Transactional` on `VerificationService.processVerification` and `AdaptationService.processAdaptation` to configure `noRollbackFor = {ResponseStatusException.class, RestClientException.class, Exception.class}`.
   - **Result:** Downstream ML availability issues are logged as non-fatal warnings; snapshots are safely ingested and persisted; all 30 backend tests continue to pass.

---

## 8. Service Startup Commands (PowerShell)

To start the complete Cyber Doppelgänger platform locally:

### Terminal 1: Python ML Microservice
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\python.exe ml/service.py
```
*Health check:* `http://localhost:5001/health`

### Terminal 2: Java Spring Boot Backend
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\backend"
.\mvnw.cmd spring-boot:run
```
*Health check:* `http://localhost:8080/api/health`

### Terminal 3: React Vite Frontend
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\frontend"
npm run dev
```
*UI URL:* `http://localhost:5173/`

### Terminal 4: Desktop Behavioural Agent (Local Workstation)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
$env:BACKEND_ENABLED="true"
$env:BACKEND_URL="http://localhost:8080"
.\.venv\Scripts\python.exe agent/main.py
```

---

## 9. Final Verification Status

**VERIFIED FOR LOCAL DEMO**

The system is fully operational, verified, and safe for local demonstrations. All core services (ML, Backend, Database, Frontend, Desktop Agent) are communicating cleanly, tests pass with 100% success, and strict privacy guarantees are enforced end-to-end.

---

## 10. Recommended Next Steps for Team & Guide Deployment

1. **Containerization (Docker Compose):**
   - Package Backend (`backend/Dockerfile`), ML Microservice (`ml/Dockerfile`), and Frontend (`frontend/Dockerfile`) into a unified `docker-compose.yml`.
   - Add a managed PostgreSQL container to replace in-memory H2 for persistent multi-user staging.
2. **Reverse Proxy & Domain Setup:**
   - Configure Nginx or Caddy with TLS (HTTPS) to serve frontend assets and reverse-proxy `/api` requests to the backend.
   - For a quick shareable demo without cloud infrastructure, utilize a secure tunneling service (e.g. Cloudflare Tunnels or ngrok).
3. **Agent Distribution Package:**
   - Create a preconfigured `.zip` or standalone executable (`pyinstaller`) for the desktop agent with an accompanying setup script pointing to your deployed backend domain.
   - Document device authorization steps so teammates can pair their workstations securely.
