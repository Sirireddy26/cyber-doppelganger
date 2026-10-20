-- ====================================================================
-- CYBER DOPPELGÄNGER - PostgreSQL Database Schema (Phase 3)
-- Safe Adaptive Behavioural Identity & Continuous User Verification
-- ====================================================================

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(128) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'ROLE_USER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_user_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);

-- 2. Devices
CREATE TABLE IF NOT EXISTS devices (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_identifier VARCHAR(128) UNIQUE NOT NULL,
    display_name VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_device_identifier ON devices(device_identifier);
CREATE INDEX IF NOT EXISTS idx_device_user_id ON devices(user_id);

-- 3. Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    device_id BIGINT REFERENCES devices(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_session_device_id ON sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_session_status ON sessions(status);

-- 4. Behavioural Feature Snapshots (STRICT PRIVACY: Aggregated Kinematics & Timing Only)
CREATE TABLE IF NOT EXISTS behavioural_feature_snapshots (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(128) NOT NULL,
    session_id BIGINT REFERENCES sessions(id) ON DELETE SET NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_seconds INT NOT NULL,
    schema_version VARCHAR(16) NOT NULL DEFAULT '2.0',
    feature_payload TEXT NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_snapshot_captured_at ON behavioural_feature_snapshots(captured_at);
CREATE INDEX IF NOT EXISTS idx_snapshot_device_id ON behavioural_feature_snapshots(device_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_user_id ON behavioural_feature_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_session_id ON behavioural_feature_snapshots(session_id);

-- 5. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(128),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome VARCHAR(32) NOT NULL,
    safe_metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_actor_user_id ON audit_logs(actor_user_id);

-- 6. Security Events Foundation (Minimal structure for future phases)
CREATE TABLE IF NOT EXISTS security_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(128),
    event_type VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    description VARCHAR(512) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sec_event_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_sec_event_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_sec_event_device_id ON security_events(device_id);

-- 7. Verification Results (Phase 4: ML Verification Evidence)
CREATE TABLE IF NOT EXISTS verification_results (
    id BIGSERIAL PRIMARY KEY,
    snapshot_id BIGINT REFERENCES behavioural_feature_snapshots(id) ON DELETE SET NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(128) NOT NULL,
    model_version VARCHAR(32) NOT NULL,
    model_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    anomaly_score DOUBLE PRECISION,
    raw_score DOUBLE PRECISION,
    threshold DOUBLE PRECISION,
    confidence_score DOUBLE PRECISION,
    decision VARCHAR(64) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verif_snapshot ON verification_results(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_verif_device_user ON verification_results(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_verif_created_at ON verification_results(created_at);

-- ============================================================================
-- 8. PROFILE VERSIONS (Phase 5)
-- ============================================================================
CREATE TABLE IF NOT EXISTS profile_versions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(128) NOT NULL,
    version_tag VARCHAR(64) NOT NULL,
    parent_version_tag VARCHAR(64),
    sample_count INT NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    feature_statistics TEXT,
    reason TEXT,
    activated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_profile_ver_tag ON profile_versions(version_tag);
CREATE INDEX IF NOT EXISTS idx_profile_device_user ON profile_versions(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_profile_created_at ON profile_versions(created_at);

-- ============================================================================
-- 9. ADAPTATION EVENTS (Phase 5)
-- ============================================================================
CREATE TABLE IF NOT EXISTS adaptation_events (
    id BIGSERIAL PRIMARY KEY,
    snapshot_id BIGINT REFERENCES behavioural_feature_snapshots(id) ON DELETE SET NULL,
    verification_result_id BIGINT REFERENCES verification_results(id) ON DELETE SET NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(128) NOT NULL,
    decision_state VARCHAR(32) NOT NULL,
    prior_profile_version VARCHAR(64) NOT NULL,
    new_profile_version VARCHAR(64),
    drift_magnitude DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    stability_score DOUBLE PRECISION,
    candidate_count INT NOT NULL DEFAULT 0,
    suspicious_streak INT NOT NULL DEFAULT 0,
    is_profile_frozen BOOLEAN NOT NULL DEFAULT FALSE,
    decision_reason TEXT NOT NULL,
    policy_version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_adapt_snapshot ON adaptation_events(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_adapt_verif_res ON adaptation_events(verification_result_id);
CREATE INDEX IF NOT EXISTS idx_adapt_decision ON adaptation_events(decision_state);
CREATE INDEX IF NOT EXISTS idx_adapt_created_at ON adaptation_events(created_at);

-- ============================================================================
-- 10. PROFILE FREEZE RECORDS (Phase 5)
-- ============================================================================
CREATE TABLE IF NOT EXISTS profile_freeze_records (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(128) NOT NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    profile_version VARCHAR(64) NOT NULL,
    is_frozen BOOLEAN NOT NULL DEFAULT TRUE,
    freeze_reason TEXT NOT NULL,
    frozen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    unfrozen_at TIMESTAMP WITH TIME ZONE,
    unfreeze_reason TEXT,
    unfrozen_by VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_freeze_device_user ON profile_freeze_records(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_freeze_frozen_at ON profile_freeze_records(frozen_at);
