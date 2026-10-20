# Cyber Doppelgänger — Database Architecture & Schema (Phase 3)
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

This document details the PostgreSQL schema, JPA entity mapping, and database migration architecture for Phase 3.

---

## 1. Relational Schema Architecture

The database model is built around privacy-safe continuous behavioral telemetry, strictly separating user accounts, hardware/application devices, active login sessions, and aggregated feature snapshots.

```
+---------------+       +-----------------+       +-----------------+
|     users     | 1---* |     devices     | 1---* |    sessions     |
+---------------+       +-----------------+       +-----------------+
        |                        |                         |
        |                        |                         |
        +------------------+     |     +-------------------+
                           |     |     |
                           v     v     v
              +-------------------------------------+
              |    behavioural_feature_snapshots    |
              +-------------------------------------+
```

### Table Definitions

#### `users`
Stores enrolled user accounts with BCrypt-hashed credentials.
- `id` (BIGSERIAL PRIMARY KEY)
- `username` (VARCHAR(64) NOT NULL UNIQUE)
- `email` (VARCHAR(255) UNIQUE)
- `password_hash` (VARCHAR(255) NOT NULL) — BCrypt hashed
- `role` (VARCHAR(32) NOT NULL DEFAULT 'ROLE_USER')
- `created_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `updated_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `enabled` (BOOLEAN NOT NULL DEFAULT TRUE)

#### `devices`
Associates telemetry with an application-generated device identifier rather than intrusive hardware fingerprints.
- `id` (BIGSERIAL PRIMARY KEY)
- `user_id` (BIGINT REFERENCES users(id), NULLABLE)
- `device_identifier` (VARCHAR(128) NOT NULL UNIQUE)
- `display_name` (VARCHAR(128))
- `created_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `last_seen_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `enabled` (BOOLEAN NOT NULL DEFAULT TRUE)

#### `sessions`
Represents an active interactive work session.
- `id` (BIGSERIAL PRIMARY KEY)
- `user_id` (BIGINT REFERENCES users(id), NULLABLE)
- `device_id` (BIGINT REFERENCES devices(id), NOT NULL)
- `started_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `ended_at` (TIMESTAMP WITH TIME ZONE NULLABLE)
- `status` (VARCHAR(32) NOT NULL DEFAULT 'ACTIVE')
- `created_at` (TIMESTAMP WITH TIME ZONE NOT NULL)

#### `behavioural_feature_snapshots`
Stores the periodic aggregated, privacy-safe numerical feature representations produced by the desktop agent.
- `id` (BIGSERIAL PRIMARY KEY)
- `user_id` (BIGINT REFERENCES users(id), NULLABLE)
- `device_id` (BIGINT REFERENCES devices(id), NOT NULL)
- `session_id` (BIGINT REFERENCES sessions(id), NULLABLE)
- `captured_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `window_duration_seconds` (INT NOT NULL)
- `schema_version` (VARCHAR(16) NOT NULL)
- `feature_payload` (TEXT / JSONB NOT NULL) — Stored as valid JSON containing ONLY numerical aggregate features
- `received_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- **Indexes**:
  - `idx_snapshot_captured_at` ON `(captured_at)`
  - `idx_snapshot_user_device` ON `(user_id, device_id)`
  - `idx_snapshot_session` ON `(session_id)`

#### `audit_logs`
Records security and data ingestion transactions for accountability.
- `id` (BIGSERIAL PRIMARY KEY)
- `actor_user_id` (BIGINT NULLABLE)
- `action` (VARCHAR(64) NOT NULL)
- `entity_type` (VARCHAR(64) NOT NULL)
- `entity_id` (BIGINT NULLABLE)
- `timestamp` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `outcome` (VARCHAR(32) NOT NULL)
- `safe_metadata` (TEXT NULLABLE)

#### `security_events`
Foundation table for Phase 4 anomaly and security alerts.
- `id` (BIGSERIAL PRIMARY KEY)
- `user_id` (BIGINT NULLABLE)
- `device_id` (BIGINT NULLABLE)
- `event_type` (VARCHAR(64) NOT NULL)
- `severity` (VARCHAR(32) NOT NULL)
- `description` (TEXT NOT NULL)
- `status` (VARCHAR(32) NOT NULL DEFAULT 'OPEN')
- `created_at` (TIMESTAMP WITH TIME ZONE NOT NULL)

---

## 2. Environment Variables & Credentials

Database credentials are parameterized using standard environment variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DB_HOST` | PostgreSQL hostname | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `cyber_doppelganger` |
| `DB_USERNAME` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `your_secure_password` |
| `SPRING_PROFILES_ACTIVE` | Active Spring profile | `postgres` (or `dev` for H2) |

---

## 3. Database Setup & Migration

### Setting Up Local PostgreSQL
1. Start PostgreSQL (e.g., via PostgreSQL service or container):
   ```powershell
   # If running native Windows service:
   net start postgresql-x64-16
   ```
2. Create the target database:
   ```sql
   CREATE DATABASE cyber_doppelganger;
   ```
3. Run migrations:
   - Migrations are automatically applied by Flyway on Spring Boot startup via:
     `backend/src/main/resources/db/migration/V1__initial_schema.sql`
   - Alternatively, you can run `database/schema.sql` manually using `psql`:
     ```powershell
     psql -U postgres -d cyber_doppelganger -f database/schema.sql
     ```

### Development Profile Fallback
When PostgreSQL is not installed or unreachable, Spring Boot defaults to `SPRING_PROFILES_ACTIVE=dev`, utilizing an in-memory H2 database running in PostgreSQL compatibility mode (`MODE=PostgreSQL`).
The health endpoint `GET /api/health` dynamically tests and reports the actual database engine status (`"database_type": "H2"` or `"PostgreSQL"`).
