-- ====================================================================
-- CYBER DOPPELGÄNGER - Phase 3 Database Schema Migration (V1)
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
