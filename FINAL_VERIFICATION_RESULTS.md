# Cyber Doppelgänger — Final End-to-End Verification Report

**Project:** Cyber Doppelgänger: Safe Adaptive Behavioural Identity and Continuous User Verification  
**Evaluation Role:** Senior Cybersecurity Architect, ML Systems Specialist, QA Verification Lead  
**Verification Date:** October 16, 2026  
**Repository Path:** `cyber-doppelganger/`  
**Overall Status:** **VERIFIED FOR LOCAL DEMO**

---

## 1. Overall Status

### **VERIFIED FOR LOCAL DEMO**

The entire end-to-end continuous behavioural verification and safe adaptation pipeline has been rigorously inspected, tested, and validated. All three core subsystems (Python ML microservice, Java Spring Boot backend, and React 19 frontend dashboard) start reliably, communicate accurately, enforce zero-content privacy boundaries, prevent profile poisoning, trigger defensive security freezes upon anomalous streaks, and permit authorized administrative recovery.

A critical transaction propagation defect (`UnexpectedRollbackException` during ML service unavailability) was discovered during testing and resolved with zero regressions.

---

## 2. Services Successfully Started and Their Actual Status

| Subsystem | Port | Technology Stack | Startup Command | Verified Health Endpoint | Actual Runtime Status |
|---|---|---|---|---|---|
| **ML Microservice** | `5001` | Python 3.11, Scikit-Learn, NumPy, Flask | `.\.venv\Scripts\python.exe ml/service.py` | `http://localhost:5001/health` | **HEALTHY / OPERATIONAL** (`"status":"UP", "version":"1.0.0", "adaptation_ready":true`) |
| **Backend API** | `8080` | Java 17, Spring Boot 3.4.4, Spring Security, JPA | `cd backend; .\mvnw.cmd spring-boot:run` | `http://localhost:8080/api/health` | **HEALTHY / OPERATIONAL** (`"status":"UP", "database":"UP", "database_type":"H2"`) |
| **Frontend Dashboard** | `5173` | React 19, TypeScript, Vite 8.3.3, Tailwind v4 | `cd frontend; npm run dev` | `http://localhost:5173/` | **HEALTHY / OPERATIONAL** (`HTTP 200 OK`, Soft Research Lab Pastel Theme) |

All three processes were executed concurrently as background daemons and their communication verified through live REST diagnostics (`GET /api/health/diagnostics`).

---

## 3. Tests Executed, Exact Commands, and Actual Outcomes

Every available test suite in the repository was executed directly. No test results or metrics were fabricated.

### Test Suite 1: Python Desktop Agent Unit & Integration Tests
- **Command:**
  ```powershell
  cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
  .\.venv\Scripts\python.exe -m unittest discover -s agent/tests -p "test_*.py"
  ```
- **Actual Outcome:**
  ```
  Ran 33 tests in 3.570s
  OK
  ```
- **Verified Capabilities:**
  - Keyboard timing extraction (dwell and flight intervals only; zero characters retained).
  - Mouse kinematic calculation (displacement, speed, acceleration, jitter; coordinates discarded).
  - Active/idle session continuity monitoring.
  - Anonymous process context tracking (integer PIDs only; no window titles or URLs).
  - Local JSONL disk buffering and failover replay.

### Test Suite 2: Machine Learning & Safe Adaptation Engine Tests
- **Command:**
  ```powershell
  cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
  .\.venv\Scripts\python.exe -m unittest discover -s ml/tests -p "test_*.py"
  ```
- **Actual Outcome:**
  ```
  Ran 42 tests in 6.376s
  OK
  ```
- **Verified Capabilities:**
  - Isolation Forest model fitting, decision score calculation, and 5th percentile threshold calibration (`0.0327`).
  - Safe Adaptation policy rules: single-observation poisoning prevention, multi-window drift bounding ($\Delta \le 1.8\sigma$, $\nu \le 2.5$).
  - Bounded candidate buffer (capacity: 20, TTL: 3600s).
  - Sudden takeover rejection and automatic freeze streak triggering at streak = 3.
  - Semantic profile version lineage (`v1.0.0` $\to$ `v1.1.0`) and version rollback.

### Test Suite 3: Automated Zero-Content Privacy Boundary Test Suite
- **Command:**
  ```powershell
  cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
  .\.venv\Scripts\python.exe -m unittest tests/test_privacy_boundary.py
  ```
- **Actual Outcome:**
  ```
  Ran 4 tests in 0.479s
  OK
  ```
- **Verified Capabilities:**
  - Client-side `PrivacyFilter` catches and rejects prohibited fields: `typed_text`, `password`, `clipboard`, `screenshot`, `browser_url`, `command_line`.
  - Backend Spring Boot `PrivacyContentFilter` returns HTTP 400 Privacy Violation.
  - Verifies that sensitive string values (e.g., `CRITICAL_SECRET_CREDENTIAL_DO_NOT_STORE`) are NEVER echoed into error response bodies or logs.

### Test Suite 4: Spring Boot Backend Unit & Integration Tests (Maven Surefire)
- **Command:**
  ```powershell
  cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\backend"
  .\mvnw.cmd test
  ```
- **Initial Run Outcome (ML microservice offline):**
  `Tests run: 30, Failures: 6, Errors: 0, Skipped: 0 (BUILD FAILURE)`
  *Discovery:* Highlighted that backend integration tests required the ML service and exposed a transaction rollback defect in snapshot ingestion.
- **Rerun Outcome (After applying `REQUIRES_NEW` transaction fix & with ML service active):**
  ```
  [INFO] Tests run: 30, Failures: 0, Errors: 0, Skipped: 0
  [INFO] BUILD SUCCESS (Total time: 43.084 s)
  ```
- **Isolated Ingestion Test (ML microservice offline):**
  ```powershell
  .\mvnw.cmd test -Dtest=FeatureIngestionAndRetrievalTests
  ```
  ```
  [INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0
  [INFO] BUILD SUCCESS (Total time: 30.366 s)
  ```

### Test Suite 5: Frontend TypeScript Compilation & Production Bundle
- **Command:**
  ```powershell
  cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\frontend"
  npm run build
  ```
- **Actual Outcome:**
  ```
  vite v8.3.3 building client environment for production...
  transforming...
  ✓ 1903 modules transformed.
  rendering chunks...
  dist/index.html                   1.47 kB │ gzip:  0.86 kB
  dist/assets/index-D6SA92XP.css   29.03 kB │ gzip:  6.61 kB
  dist/assets/index-BPLwLFPM.js   319.62 kB │ gzip: 90.71 kB
  ✓ built in 3.54s (0 errors)
  ```

---

## 4. End-to-End Workflow Evidence

A complete live execution trace was performed across the running stack:

### Step A: Normal Observation Ingestion
- **Request:** Dispatched synthetic Schema 2.0 snapshot (`device_id: "test-eval-device-01"`, timestamp `2026-10-16T06:43:27Z`) with standard kinematic parameters (`mean_key_interval: 0.125s`, `typing_speed: 1.0`, `mean_mouse_speed: 210.0px/s`, `mean_acceleration: 6500.0px/s²`).
- **Backend Log:** `Successfully ingested behavioural snapshot #1 for device [test-eval-device-01] (window: 15s)`.
- **ML Verification Response:**
  - `status: "VERIFIED"`
  - `decision: "NORMAL_BEHAVIOUR"`
  - `raw_score: +0.1344` ($\ge$ threshold `0.0327`)
  - `anomaly_score: -0.1344`
  - `confidence_score: 0.6313`
- **Safe Adaptation Decision:**
  - `decision_state: "NORMAL"`
  - `prior_profile_version: "v1.0.0"`
  - `new_profile_version: null` (trusted baseline unchanged)
  - `drift_magnitude: 0.2068`
  - `suspicious_streak: 0`
  - `is_profile_frozen: false`

### Step B: Database Persistence Verification
Queried persisted entities directly via REST API:
- `GET http://localhost:8080/api/behaviour/1` -> Returned snapshot record with exact timestamp, schema version 2.0, and 37 approved derived features.
- `GET http://localhost:8080/api/verification/1` -> Returned verification result record matching `raw_score: 0.1344`, `threshold: 0.0327`, `decision: "NORMAL_BEHAVIOUR"`.

### Step C: Replay Attack Rejection
Resent identical snapshot (`device_id: "test-eval-device-01"`, timestamp `2026-10-16T06:43:27Z`):
- **HTTP Status:** `400 Bad Request`
- **Error Body:** `{"status":400, "error":"Bad Request", "message":"Duplicate feature snapshot detected for device [test-eval-device-01] at timestamp [2026-10-16T06:43:27Z]. Replay rejected."}`

### Step D: Malformed Input Rejection
- **Malformed JSON Syntax:** Returned `HTTP 400 Bad Request` (`"Invalid JSON payload"`).
- **Missing Required Fields:** Returned `HTTP 400 Bad Request` (`"Validation failed: timestamp: Timestamp is required, deviceId: device_id is required"`).
- **Invalid Timestamp:** Returned `HTTP 400 Bad Request` (`"Invalid ISO-8601 timestamp format: not-a-timestamp"`).
- **Non-Finite Numbers (`"NaN"`, `"Infinity"`):** Returned `HTTP 400 Bad Request` (`"Invalid JSON payload: Non-finite numeric string detected (NaN/Infinity)"`).

---

## 5. Adaptation, Freeze, Recovery, and Rollback Findings

### A. Impostor Takeover & Freeze Triggering
Dispatched a sequence of high-deviation synthetic observations (`mean_key_interval: 25.5s`, `mouse_speed: 8500.0px/s`, `acceleration: 95000.0px/s²`):
1. **Observation 1:** `raw_score: -0.2157 < 0.0327` $\to$ `DEVIATION` $\to$ `decision_state: SUSPICIOUS_CHANGE`, `suspicious_streak: 1`, `is_frozen: false`.
2. **Observation 2:** `raw_score: -0.2157` $\to$ `DEVIATION` $\to$ `decision_state: SUSPICIOUS_CHANGE`, `suspicious_streak: 2`, `is_frozen: false`.
3. **Observation 3:** `raw_score: -0.2157` $\to$ `DEVIATION` $\to$ `decision_state: PROFILE_FROZEN`, `suspicious_streak: 3`, `is_frozen: true`.
4. **Observation 4 (Post-Freeze):** Profile remained frozen. `decision_reason: "Profile is FROZEN (Suspicious anomaly streak reached threshold (3).). Updates blocked until authorized recovery."` Candidate buffer flushed. Trusted profile preserved at `v1.0.0`.

### B. Authorization Security Enforcement
- **Unauthorized Unfreeze (`/api/adaptation/unfreeze` without `authorized_by`):**
  - **HTTP Status:** `401 Unauthorized`
  - **Message:** `"Security authorization required: 'authorized_by' identity must be provided for profile unfreeze recovery."`
- **Unauthorized Rollback (`/api/adaptation/rollback` without `authorized_by`):**
  - **HTTP Status:** `401 Unauthorized`
  - **Message:** `"Security authorization required: 'authorized_by' identity must be provided for profile rollback."`
- **Rollback Missing `target_version`:**
  - **HTTP Status:** `400 Bad Request` (`"target_version is required for rollback."`)

### C. Authorized Recovery and Rollback
- **Authorized Unfreeze (`authorized_by: "SecOps Admin"`):**
  - Returned `HTTP 200 OK`: `is_frozen: false`, `engine_status: "ACTIVE"`, `suspicious_streak: 0`.
  - Stored audit log in `audit_logs` table (`event_type: "PROFILE_UNFREEZE"`).
- **Authorized Rollback (`authorized_by: "SecOps Lead"`, `target_version: "v1.0.0"`):**
  - Returned `HTTP 200 OK`: `"Profile active version 'v1.0.0' re-asserted and reset to baseline."`
  - Stored audit log in `audit_logs` table (`event_type: "PROFILE_ROLLBACK"`).

---

## 6. Privacy and Security Findings

### Confirmed Privacy Boundaries
1. **Hardware / OS Hook Level:**
   - Keystrokes: `KeyboardCollector._on_press(key)` captures exclusively `time.monotonic()` and never touches `key.char`, `key.name`, or any text representation.
   - Mouse: `MouseCollector` captures delta displacements ($\Delta x, \Delta y$), calculates scalar distance and speed, and immediately discards $(x, y)$ coordinate positions.
   - Applications: `ApplicationCollector` compares integer process IDs (PIDs) and never queries window titles, terminal text, browser URLs, or file names.
2. **Network Transmission Level:**
   - Both client-side `PrivacyFilter` and backend `PrivacyContentFilter` recursively scan payloads for forbidden keys (`typed_text`, `char`, `password`, `clipboard`, `screenshot`, `browser_url`, etc.).
   - If any forbidden key is detected, client aborts with `PrivacyViolationError` and backend aborts with HTTP 400.
3. **Logging & Error Boundaries:**
   - Exception handlers log only the prohibited field name (e.g., `prohibited field [typed_text]`), never the submitted value.

### What Remains Unverified
- **Kernel-Level Keyloggers:** While application-level software filters strictly discard keystroke text, kernel-level or hypervisor-level surveillance running outside the application cannot be prevented by this software.
- **Physical Shoulder Surfing:** Non-biometric physical observation of the user's screen or keyboard is outside the technical threat model.

---

## 7. Database and Model Consistency Findings

1. **Active Database:**
   - Profile `dev` is active.
   - Engine: **H2 (In-Memory Dev DB)** with PostgreSQL compatibility mode (`jdbc:h2:mem:cyber_doppelganger;MODE=PostgreSQL`).
   - Dynamic inspection: `DatabaseHealthService` inspects live metadata via `connection.getMetaData().getDatabaseProductName()` returning `"H2"`. Both `App.tsx` and `ModelDiagnostics.tsx` dynamically display `H2 (In-Memory Dev DB)`.
2. **Profile Version Synchronization:**
   - The ML service loads `v1.0.0` (435 samples, 37 features) from `ml/artifacts/profile_versions.json`.
   - `HealthController.java` synchronizes the ML service baseline into the backend repository, guaranteeing 100% agreement (`v1.0.0 ACTIVE`) between overview badges, diagnostics cards, and adaptation tables.
3. **ML Scoring & Calibration:**
   - **Model Decision Score (Raw):** Direct output of Scikit-Learn `decision_function(X)`. Range: positive for normal inliers, negative for outliers.
   - **Anomaly Score:** Defined as `-raw_score`.
   - **Decision Threshold:** Calibrated at `0.0327` (5th percentile of normal baseline training data).
   - **Confidence Score:** Evaluated via logistic calibration `1.0 / (1.0 + exp(-raw_score * 4.0))`. It measures behavioral congruence with the profile ($[0.0, 1.0]$) and is **not** a Bayesian posterior probability of identity.
4. **Data Separation:**
   - `train_and_evaluate.py` partitions training and testing data using `GroupShuffleSplit` on `session_id` (80% train, 20% test, seed 42), strictly preventing temporal autocorrelation leakage between adjacent observation windows.

---

## 8. Bugs Discovered and Fixes Made

### Defect 1: Ingestion Crash (`UnexpectedRollbackException`) When ML Microservice is Offline
- **What Was Broken:** If the ML service on port 5001 was offline or temporarily restarting, incoming agent snapshot submissions (`POST /api/agent/features`) crashed with HTTP 500 Internal Server Error, discarding the snapshot rather than persisting it.
- **Root Cause:** In `FeatureIngestionService.java`, the outer method `ingestSnapshot` was annotated `@Transactional`. When it called `verificationService.processVerification` (also `@Transactional` with default propagation `REQUIRED`), connection failure to the ML microservice threw an unchecked `RestClientException`. This marked the active physical transaction as `rollback-only`. When `FeatureIngestionService` caught the exception to gracefully store the snapshot, the outer commit failed with Spring's `UnexpectedRollbackException`.
- **Applied Fix:**
  - Modified `VerificationService.java` to specify `@Transactional(propagation = Propagation.REQUIRES_NEW)`.
  - Modified `AdaptationService.java` to specify `@Transactional(propagation = Propagation.REQUIRES_NEW)`.
  - Updated `VerificationService.java` to throw `ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, ...)` on `RestClientException`.
- **Verification Evidence:**
  - Ran `.\mvnw.cmd test -Dtest=FeatureIngestionAndRetrievalTests` with ML service offline: passed 6/6 tests with `BUILD SUCCESS`.
  - Dispatched live snapshot with ML service offline: returned `HTTP 201 Created` with `status: "accepted"`, snapshot persisted with ID, and `processing_error` populated.

---

## 9. Tests That Failed or Could Not Be Completed

### Automated Headless Browser Visual Inspection
- **Attempted Action:** Invoked browser subagent to execute Playwright-driven visual inspection of `http://localhost:5173`.
- **Reason for Incompletion:** The Playwright automated driver download encountered an HTTP 404 error from the CDN (`https://playwright.azureedge.net/builds/driver/playwright-1.57.0-win32_x64.zip`), preventing headless browser launch.
- **Mitigation & Alternative Verification:**
  - Validated frontend via TypeScript compilation and Vite production build (`npm run build`), which transformed 1,903 modules cleanly with 0 errors.
  - Verified Vite dev server directly via HTTP web request (`http://localhost:5173/`), confirming HTTP 200 OK and proper serving of HTML, Tailwind CSS, and React modules.

---

## 10. Remaining Risks and Next Recommended Actions

1. **In-Memory H2 Ephemeral Storage:**
   - *Risk:* In development mode, terminating the backend process resets all stored snapshots and verification records.
   - *Recommendation:* For persistent research data collection across multi-day trials, start the backend with `SPRING_PROFILES_ACTIVE=postgres` against a live PostgreSQL 15+ instance as documented in `DEPLOYMENT_GUIDE.md`.
2. **ML Microservice Network Loopback Boundary:**
   - *Risk:* Port 5001 has no API key authentication and listens on loopback (`127.0.0.1`).
   - *Recommendation:* Keep port 5001 unexposed to public ingress. If deployed across separate containers, enforce mutual TLS (mTLS) or an API gateway token filter.
3. **Rate Limiting:**
   - *Risk:* An adversarial client could flood `/api/agent/features` with high-frequency snapshots.
   - *Recommendation:* Implement rate-limiting middleware (e.g. Bucket4j or NGINX `limit_req`) restricting submissions to 1 snapshot per 10 seconds per device.

---

## 11. Exact PowerShell Commands for Starting the Application

Open separate Windows PowerShell terminal windows:

### Terminal 1: Start Python ML Microservice (Port 5001)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\Activate.ps1
python ml/service.py
```
*Expected log:* `Cyber Doppelgänger ML Verification & Safe Adaptation Service running on http://127.0.0.1:5001`

### Terminal 2: Start Spring Boot Backend (Port 8080)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\backend"
.\mvnw.cmd spring-boot:run
```
*Expected log:* `Started CyberDoppelgangerBackendApplication in ~15 seconds`

### Terminal 3: Start React Frontend Dashboard (Port 5173)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\frontend"
npm run dev
```
*Expected log:* `VITE v8.3.3 ready in ... Local: http://localhost:5173/`

### Clean Demonstration Reset Command (Run before demonstration)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\python.exe -c "from ml.adaptation.profile_version_manager import ProfileVersionManager; pvm = ProfileVersionManager('ml/artifacts/profile_versions.json'); pvm.unfreeze('admin', 'Pre-demo reset'); print('Reset complete. Profile active at v1.0.0.')"
```

---

## 12. Manual Demonstration Checklist

Follow this step-by-step checklist during live university or committee demonstrations:

- [ ] **Step 1: Launch Services**
  - Start Terminal 1 (ML), Terminal 2 (Backend), Terminal 3 (Frontend).
  - Open `http://localhost:5173` in Google Chrome or Microsoft Edge.
- [ ] **Step 2: Verify System Overview Bar**
  - Confirm **Soft Research Lab** pastel theme is active (light lavender `#F7F5FB`, white cards).
  - Backend status: **ONLINE** (green pill).
  - Database status: **H2 (In-Memory Dev DB)** (green pill).
  - ML Model: **ONLINE (ISOLATION_FOREST)** (green pill).
  - Trusted Profile: **v1.0.0 (ACTIVE)** (green pill).
  - Adaptation Engine: **ACTIVE** (green pill).
- [ ] **Step 3: Biometric Playground Exploration**
  - Click on the **Biometric Playground** tab.
  - Type sample text into the typing cadence area.
  - Move the mouse across the cursor trajectory canvas.
  - Hover over the kinematic gauges (Dwell Time, Flight Time, Cursor Speed, Acceleration, Jitter, Trajectory Curvature) to show educational tooltips.
  - Click **Verify Interaction Window** and observe the Isolation Forest decision score ($+0.1344 \ge 0.0327 \to \text{NORMAL}$).
- [ ] **Step 4: Adaptation Engine & Freeze Demonstration**
  - Click on the **Research Simulators** tab.
  - Select **Scenario 4: Controlled Session Hijacking / Takeover**.
  - Click **Execute Simulation**.
  - Show the 3 consecutive anomalous observations ($\Delta > 1.8\sigma$).
  - Switch to the **Adaptation Dashboard** tab:
    - Point out that the engine transitioned to **PROFILE_FROZEN**.
    - Show that candidate buffer was automatically flushed to prevent contamination.
    - Point out that active version remains pinned to `v1.0.0`.
- [ ] **Step 5: Administrative Security Recovery Drill**
  - On the **Adaptation Dashboard**, locate the **Administrative Emergency Override** card.
  - Attempt to click **Unfreeze** without an authorized identity to demonstrate that unauthorized actions are blocked.
  - Enter `SecOps Admin` as the authorized identity and provide reason `Demo unfreeze drill`.
  - Click **Authorize Profile Recovery**.
  - Confirm the engine immediately returns to **ACTIVE** with streak reset to 0.
- [ ] **Step 6: Model Diagnostics & Scientific Transparency**
  - Click on the **Model Diagnostics** tab.
  - Review the Isolation Forest hyperparameter card (`n_estimators: 100`, `contamination: 0.05`).
  - Show the **Score Calibration & Decision Boundary** research callout explaining the difference between raw decision function outputs and true Bayesian probabilities.
  - Review the feature importance distribution across keyboard and mouse kinematics.
