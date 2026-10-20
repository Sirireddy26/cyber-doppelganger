# Cyber Doppelgänger — REST API Documentation (Phase 3)
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

All API endpoints strictly follow RESTful conventions, JSON serialization, and privacy-preserving constraints.

---

## 1. Authentication & Public Access Policy

- **Development Policy**: In the local development environment (`SPRING_PROFILES_ACTIVE=dev`), health, authentication, feature ingestion, and behaviour query endpoints are permitted without a pre-existing session to enable seamless desktop agent testing.
- **Production Standard**: User-specific retrieval endpoints are guarded by Bearer JWT tokens. Passwords are never returned in responses and are hashed using BCrypt.

---

## 2. Health & System Status

### `GET /api/health`
Checks application readiness and actively verifies live database connectivity.

- **Access**: Public
- **Response (200 OK - Example)**:
```json
{
  "status": "UP",
  "service": "cyber-doppelganger-backend",
  "database": "UP",
  "timestamp": "2026-10-09T09:17:41.484511200Z",
  "database_type": "H2"
}
```
*(Note: If PostgreSQL is configured, `database_type` returns `"PostgreSQL"`. If database is down, `database` reports `"DOWN"`).*

### `GET /api/health/diagnostics` (or `/api/system/diagnostics`)
Returns comprehensive, uncollapsed multi-subsystem diagnostic readiness for the entire continuous verification pipeline.

- **Access**: Public
- **Response (200 OK - Example)**:
```json
{
  "timestamp": "2026-10-12T17:25:21.088Z",
  "backend": {
    "status": "UP",
    "service": "cyber-doppelganger-backend",
    "version": "1.0.0"
  },
  "database": {
    "status": "UP",
    "database_type": "PostgreSQL",
    "connected": true
  },
  "ml_service": {
    "status": "UP",
    "service_status": "READY",
    "active_model_type": "ISOLATION_FOREST"
  },
  "model_readiness": {
    "ready": true,
    "status": "READY",
    "model_type": "ISOLATION_FOREST",
    "model_version": "1.0.0"
  },
  "trusted_profile": {
    "ready": true,
    "status": "INITIALIZED",
    "total_versions": 1,
    "active_version": "v1.0.0",
    "device_id": "desktop-workstation"
  },
  "adaptation_engine": {
    "ready": true,
    "engine_status": "ACTIVE",
    "is_frozen": false,
    "adaptation_permitted": true,
    "suspicious_streak": 0
  },
  "agent_telemetry": {
    "status": "ACTIVE",
    "last_captured_at": "2026-10-12T17:22:15.340Z",
    "last_device_id": "desktop-workstation"
  },
  "system_summary": {
    "verification_ready": true,
    "adaptation_ready": true,
    "all_systems_operational": true
  }
}
```

---

## 3. User Authentication

### `POST /api/auth/register`
Enrolls a new user with BCrypt password hashing.

- **Request Body (Example)**:
```json
{
  "username": "researcher01",
  "email": "researcher@example.org",
  "password": "SecurePassword123!"
}
```
- **Response (201 Created - Example)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "Bearer",
  "username": "researcher01",
  "role": "ROLE_USER"
}
```

### `POST /api/auth/login`
Authenticates user and returns JWT token.

- **Request Body (Example)**:
```json
{
  "username": "researcher01",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK - Example)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "Bearer",
  "username": "researcher01",
  "role": "ROLE_USER"
}
```

---

## 4. Behavioural Feature Ingestion

### `POST /api/agent/features`
Receives privacy-validated numerical feature snapshots from the desktop behavioural agent.

- **Validation Rules**:
  - Validates `schema_version` (supported: `"2.0"`).
  - Validates non-negative numerical fields.
  - Rejects NaN, Infinity, and non-finite floating points.
  - Rejects requests containing forbidden content fields (`typed_text`, `keystrokes`, `clipboard_content`, `screenshot`, `browser_url`, `document_content`, etc.).
  - Maximum request body size: 2MB.

- **Request Body (Example)**:
```json
{
  "timestamp": "2026-10-09T09:17:41.484511Z",
  "window_duration_seconds": 15,
  "device_id": "desktop-workstation-win11",
  "user_id": "researcher01",
  "schema_version": "2.0",
  "keyboard": {
    "total_key_events": 42,
    "mean_key_interval": 0.145,
    "median_key_interval": 0.138,
    "key_interval_std": 0.032,
    "minimum_key_interval": 0.045,
    "maximum_key_interval": 0.450,
    "typing_speed": 4.8,
    "pause_count": 1,
    "mean_pause_duration": 1.2,
    "longest_pause": 1.2,
    "typing_activity_duration": 8.75
  },
  "mouse": {
    "movement_distance": 960.5,
    "mean_mouse_speed": 124.5,
    "mouse_speed_std": 45.2,
    "mean_acceleration": 210.0,
    "click_count": 7,
    "left_click_count": 5,
    "right_click_count": 2,
    "middle_click_count": 0,
    "mean_click_interval": 1.25,
    "click_interval_std": 0.34,
    "scroll_count": 2,
    "positive_scroll_count": 2,
    "negative_scroll_count": 0,
    "mouse_active_duration": 6.2
  },
  "session": {
    "session_duration": 60.0,
    "active_duration": 12.5,
    "idle_duration": 2.5,
    "active_idle_ratio": 5.0,
    "activity_density": 0.833,
    "keyboard_activity_duration": 8.75,
    "mouse_activity_duration": 6.2
  },
  "application": {
    "process_count": 88,
    "active_process_count": 4,
    "application_switch_count": 1,
    "process_activity_count": 10,
    "application_activity_duration": 15.0
  }
}
```

- **Response (201 Created - Example)**:
```json
{
  "status": "accepted",
  "snapshotId": "2",
  "receivedAt": "2026-10-09T09:17:41.522558Z"
}
```

- **Rejection Responses (400 Bad Request - Example)**:
```json
{
  "timestamp": "2026-10-09T09:17:41.522558Z",
  "status": 400,
  "error": "Privacy Violation",
  "message": "Snapshot payload contains prohibited surveillance field: 'typed_text'",
  "path": "/api/agent/features"
}
```

---

## 5. Behavioural Data Retrieval

### `GET /api/behaviour`
Retrieves paginated historical snapshots in descending chronological order.

- **Query Parameters**:
  - `page` (integer, default: `0`)
  - `size` (integer, default: `20`, max: `100`)
- **Response (200 OK - Example)**:
```json
{
  "content": [
    {
      "id": 2,
      "device_id": "desktop-workstation-win11",
      "user_id": null,
      "session_id": null,
      "captured_at": "2026-10-09T09:17:41.484511Z",
      "window_duration_seconds": 15,
      "schema_version": "2.0",
      "features": { ... },
      "received_at": "2026-10-09T09:17:41.522558Z"
    }
  ],
  "page": {
    "size": 10,
    "number": 0,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### `GET /api/behaviour/{id}`
Retrieves a single persisted snapshot by ID.

- **Response (200 OK - Example)**: Same structure as single snapshot element above.
- **Response (404 Not Found)** if ID does not exist.

### `GET /api/behaviour/history`
Retrieves the most recent snapshots (default limit: 50, maximum: 200).

---

## 6. Behavioural Verification API (Phase 4)

### `GET /api/models/status`
Retrieves the active ML model readiness status, baseline threshold, and sample metrics.

- **Access**: Public in dev / Authenticated
- **Response (200 OK - Example)**:
```json
{
  "status": "READY",
  "active_model_type": "ISOLATION_FOREST",
  "isolation_forest": {
    "available": true,
    "version": "1.0.0",
    "threshold": 0.0594,
    "sample_count": 225
  },
  "random_forest": {
    "available": false,
    "version": null,
    "threshold": null
  }
}
```

### `POST /api/verification/process`
Submits a behavioural snapshot for verification by the active ML baseline.

- **Request Body Options**:
  1. By Snapshot ID:
  ```json
  {
    "snapshot_id": 1,
    "preferred_model": "ISOLATION_FOREST"
  }
  ```
  2. With Inline Features:
  ```json
  {
    "features": {
      "keyboard": { ... },
      "mouse": { ... },
      "session": { ... },
      "application": { ... }
    }
  }
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

- **Offline ML Service Fallback (503 Service Unavailable)**:
```json
{
  "status": 503,
  "error": "ML Service Unavailable",
  "message": "Behavioural verification ML service is offline at http://localhost:5001"
}
```

### `GET /api/verification`
Retrieves a paginated list of historical verification decisions.

- **Query Parameters**:
  - `page` (integer, default: `0`)
  - `size` (integer, default: `20`)
- **Response (200 OK)**: Standard Spring Data Page DTO of verification results.

### `GET /api/verification/{id}`
Retrieves a single verification result by database ID.

---

## 7. Safe Adaptation Engine API (Phase 5)

### `GET /api/adaptation/status`
Returns the operational state of the Safe Adaptation Engine, active reference profile version, freeze state, candidate buffer status, and policy bounds.

- **Access**: Public
- **Response (200 OK - Example)**:
```json
{
  "engine_status": "ACTIVE",
  "active_version": "v1.0.0",
  "is_frozen": false,
  "freeze_reason": null,
  "frozen_at": null,
  "suspicious_streak": 0,
  "sample_count": 435,
  "candidate_buffer": {
    "current_size": 2,
    "max_capacity": 20,
    "min_required": 5,
    "is_full": false,
    "stability_score": 0.82
  },
  "policy_config": {
    "min_observations": 5,
    "max_drift_magnitude": 1.8,
    "max_velocity": 2.5,
    "min_stability": 0.35,
    "max_suspicious_streak": 3,
    "cooldown_seconds": 60.0,
    "policy_version": "1.0.0"
  }
}
```

### `GET /api/adaptation/candidates`
Returns the status and contents summary of the isolated candidate buffer.

### `POST /api/adaptation/process`
Evaluates a behavioural observation snapshot against the safe adaptation policy.

- **Request Body (Example)**:
```json
{
  "snapshot_id": 1,
  "device_id": "desktop-workstation"
}
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
  "drift_magnitude": 0.35,
  "velocity": 0.22,
  "stability_score": 0.91,
  "candidate_count": 0,
  "suspicious_streak": 0,
  "is_profile_frozen": false,
  "decision_reason": "Observation conforms to trusted reference profile.",
  "policy_version": "1.0.0",
  "created_at": "2026-10-12T10:30:15.120Z"
}
```

### `GET /api/adaptation/history`
Returns a paginated audit trail of adaptation decisions.

### `POST /api/adaptation/freeze`
Freezes profile updates immediately upon suspected security anomalies. Strictly requires `authorized_by` security identity in Phase 6 (returns HTTP 401 Unauthorized if missing).
- **Request Body**:
```json
{
  "authorized_by": "sec-ops-admin",
  "reason": "Suspected session takeover or poisoning attempt"
}
```

### `POST /api/adaptation/unfreeze`
Restores active profile evolution through authorized administrative recovery. Strictly requires `authorized_by` security identity (returns HTTP 401 Unauthorized if missing).
- **Request Body**:
```json
{
  "authorized_by": "sec-ops-admin",
  "reason": "Legitimate user confirmed via out-of-band verification"
}
```

### `POST /api/adaptation/rollback`
Rolls back the active reference profile to a specified previous trusted version tag. Strictly requires `authorized_by` and `target_version` (returns HTTP 401 Unauthorized if unauthorized, 400 Bad Request if target version is omitted).
- **Request Body**:
```json
{
  "authorized_by": "sec-ops-admin",
  "target_version": "v1.0.0",
  "reason": "Reverting to baseline after anomalous deviation"
```

---

## 8. Privacy & Security Guarantees
- **Zero Content Surveillance**: No raw keystrokes, letters, words, passwords, or URLs are accepted or stored.
- **Audit Logging**: Every ingestion, verification, adaptation, and security action writes an immutable audit record to `audit_logs` without storing sensitive metadata.
- **Candidate Buffer Isolation**: Candidate observations are strictly decoupled from active reference profiles until multi-window stability and safety criteria pass.
- **Fail-Safe Processing**: Transient network failures or ML service restarts do not cause the backend or agent to crash.

