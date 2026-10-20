# Cyber Doppelgänger — Spring Boot Backend (Phase 3)
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

This service provides the production-grade REST API, Spring Security authentication, PostgreSQL persistence, and privacy-preserving behavioral feature ingestion for the continuous user verification system.

---

## 1. Architecture & Layered Packages

The backend strictly follows a layered architecture with separation of concerns:

```
com.cyberdoppelganger
├── config/         # Spring Security, CORS, WebMvc, Jackson configurations
├── controller/     # REST Controllers
│   ├── HealthController.java           # GET /api/health
│   ├── AuthController.java             # POST /api/auth/register, /api/auth/login
│   ├── FeatureIngestionController.java # POST /api/agent/features
│   └── BehaviourController.java        # GET /api/behaviour, /api/behaviour/{id}, /history
├── service/        # Business logic services
│   ├── AuthService.java                # User registration, BCrypt, JWT issuance
│   ├── FeatureIngestionService.java    # Privacy validation, device mapping, snapshot persistence
│   ├── BehaviourRetrievalService.java  # Paged snapshot queries, history queries
│   ├── DatabaseHealthService.java      # Active JDBC connection verification
│   └── AuditService.java               # Safe asynchronous audit logging
├── repository/     # Spring Data JPA Repositories
│   ├── UserRepository.java
│   ├── DeviceRepository.java
│   ├── SessionRepository.java
│   ├── BehaviouralFeatureSnapshotRepository.java
│   ├── AuditLogRepository.java
│   └── SecurityEventRepository.java
├── entity/         # JPA Entities
│   ├── User.java, Device.java, Session.java
│   ├── BehaviouralFeatureSnapshot.java, AuditLog.java, SecurityEvent.java
├── dto/            # Data Transfer Objects (Strictly decoupled from JPA entities)
│   ├── FeatureSnapshotIngestDTO.java, KeyboardFeaturesDTO.java, MouseFeaturesDTO.java...
│   ├── FeatureIngestResponseDTO.java, FeatureSnapshotResponseDTO.java...
│   ├── RegisterRequestDTO.java, LoginRequestDTO.java, AuthResponseDTO.java...
├── security/       # JWT token provider, Bearer auth filter, password encoding
├── exception/      # Centralized GlobalExceptionHandler & custom exceptions
└── util/           # PrivacyContentFilter (Strict JSON inspection against surveillance fields)
```

---

## 2. Configuration & Environment Variables

No credentials or secrets are hardcoded. All settings are externalized:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SERVER_PORT` | HTTP server port | `8080` |
| `SPRING_PROFILES_ACTIVE` | Active profile (`dev` or `postgres`) | `dev` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | PostgreSQL database | `cyber_doppelganger` |
| `DB_USERNAME` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `JWT_SECRET` | 256-bit HMAC signing key | Standard default for local dev |
| `JWT_EXPIRATION_MS` | Token lifespan (ms) | `86400000` (24 hours) |

### Profiles
- **`dev` (Default)**: In-memory H2 database running in PostgreSQL compatibility mode. Allows immediate verification and testing without external dependencies.
- **`postgres`**: Production-ready connection to persistent PostgreSQL using the environment credentials above.

---

## 3. Building and Testing

```powershell
# Run the automated test suite (11 unit and MockMvc integration tests)
.\mvnw.cmd clean test

# Run application locally on port 8080
.\mvnw.cmd spring-boot:run

# Run with PostgreSQL profile
$env:SPRING_PROFILES_ACTIVE="postgres"
.\mvnw.cmd spring-boot:run
```

---

## 4. Endpoints Implemented in Phase 3

### Health Check
- `GET /api/health` — Returns status (`UP`/`DOWN`), verifies real database connection, and reports `database_type`.

### Authentication
- `POST /api/auth/register` — Registers new account, hashes password with BCrypt, returns JWT.
- `POST /api/auth/login` — Validates credentials and returns JWT Bearer token.

### Feature Ingestion
- `POST /api/agent/features` — Validates schema version (`"2.0"`), rejects negative durations, rejects NaN/Inf, filters out prohibited surveillance fields (`typed_text`, `keystrokes`, `screenshot`, etc.), and persists snapshot to database (HTTP 201 Created).

### Behaviour Retrieval
- `GET /api/behaviour` — Paginated history of persisted snapshots in reverse chronological order.
- `GET /api/behaviour/{id}` — Retrieves single snapshot by ID.
- `GET /api/behaviour/history` — Quick retrieval of recent snapshots.

---

## 5. Endpoints Implemented in Phase 4 (ML Verification)

### ML Model Readiness Status
- `GET /api/models/status` — Checks ML microservice availability on port 5001, returning active model type, threshold, baseline sample count, and readiness status (`READY`, `MODEL_NOT_READY`, or `SERVICE_UNAVAILABLE`).

### Behavioural Verification Processing
- `POST /api/verification/process` — Verifies a behavioural feature snapshot against the active reference profile.
  - **Request Body (By Snapshot ID)**:
    ```json
    { "snapshot_id": 1 }
    ```
  - **Response (200 OK - Example)**:
    ```json
    {
      "id": 1,
      "snapshot_id": 1,
      "status": "VERIFIED",
      "model_type": "ISOLATION_FOREST",
      "anomaly_score": -0.0423,
      "raw_score": 0.0423,
      "threshold": 0.0594,
      "confidence_score": 0.5422,
      "model_version": "1.0.0",
      "decision": "NORMAL_BEHAVIOUR",
      "reason": "Feature vector consistent with reference profile (score: +0.0423 >= 0.0594).",
      "created_at": "2026-10-09T10:04:12.185Z"
    }
    ```
  - **Resilience**: If the ML service is offline, returns HTTP 503 `SERVICE_UNAVAILABLE` rather than fabricating predictions.

### Verification Results Retrieval
- `GET /api/verification` — Paginated historical list of verification decisions.
- `GET /api/verification/{id}` — Retrieves a specific verification result by ID.

---

## 6. Endpoints Implemented in Phase 5 (Safe Adaptation Engine)

### Current Adaptation Engine Status
- `GET /api/adaptation/status` — Retrieves engine state (`ACTIVE`, `FROZEN`, `SERVICE_UNAVAILABLE`), current active profile version (`v1.0.0`), freeze reason/timestamp, suspicious streak, candidate buffer metrics, and policy parameters.

### Candidate Buffer Summary
- `GET /api/adaptation/candidates` — Retrieves size, capacity, stability score, and observation count in the isolated candidate buffer.

### Adaptation Evaluation
- `POST /api/adaptation/process` — Submits a snapshot for Safe Adaptation evaluation.
  - **Request Body (By Snapshot ID or Direct Features)**:
    ```json
    { "snapshot_id": 1 }
    ```
  - **Response (200 OK - Example)**:
    ```json
    {
      "id": 1,
      "snapshot_id": 1,
      "device_id": "desktop-workstation",
      "decision_state": "NORMAL",
      "prior_profile_version": "v1.0.0",
      "new_profile_version": null,
      "drift_magnitude": 0.42,
      "velocity": 0.31,
      "stability_score": 0.88,
      "candidate_count": 0,
      "suspicious_streak": 0,
      "is_profile_frozen": false,
      "decision_reason": "Observation conforms to trusted reference profile.",
      "policy_version": "1.0.0",
      "created_at": "2026-10-10T14:24:28.120Z"
    }
    ```

### Adaptation Audit History
- `GET /api/adaptation/history` — Paginated history of adaptation decisions in reverse chronological order.

### Security Freeze & Recovery
- `POST /api/adaptation/freeze` — Halts all profile evolution immediately to contain suspected contamination.
  - Body: `{ "reason": "Suspected session takeover" }`
- `POST /api/adaptation/unfreeze` — Authorized administrative unfreeze restoring active adaptation.
  - Body: `{ "authorized_by": "sec-admin", "reason": "Verified legitimate user identity" }`
- `POST /api/adaptation/rollback` — Restores previous trusted version tag.
  - Body: `{ "target_version": "v1.0.0", "reason": "Incident response baseline rollback" }`

---

## 7. Database Migration V3 (Phase 5)
- `profile_versions`: Stores semantic profile versions (`version_tag`, `parent_version_tag`, `sample_count`, `feature_statistics`, `status`, `reason`).
- `adaptation_events`: Stores full audit trail of adaptation decisions (`decision_state`, `drift_magnitude`, `velocity`, `stability_score`, `candidate_count`, `suspicious_streak`).
- `profile_freeze_records`: Stores operational freeze and unfreeze event history.

---

## 8. Security & Privacy Guarantees
- **Password Security**: Passwords hashed with BCrypt. Passwords never appear in logs or responses.
- **Payload Sanitization**: `PrivacyContentFilter` recursively inspects incoming payloads and throws `PrivacyViolationException` (HTTP 400) if any prohibited field is present.
- **Error Safety**: `GlobalExceptionHandler` ensures stack traces, database credentials, and raw inputs are never exposed in error responses.
- **Candidate Isolation**: Candidate observations are buffered separately and cannot contaminate reference profiles without multi-window verification.
