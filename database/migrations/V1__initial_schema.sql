-- ====================================================================
-- CYBER DOPPELGÄNGER - PostgreSQL Database Schema
-- Safe Adaptive Behavioural Identity & Continuous User Verification
-- ====================================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'ROLE_USER',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Biometric Behavioral Profiles
CREATE TABLE IF NOT EXISTS biometric_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    profile_status VARCHAR(30) DEFAULT 'CALIBRATING', -- CALIBRATING, ACTIVE, RETRAINING
    baseline_samples_count INT DEFAULT 0,
    model_version VARCHAR(50) DEFAULT 'v1.0.0-isoforest',
    baseline_confidence DOUBLE PRECISION DEFAULT 0.0,
    last_trained_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Verification Sessions (Continuous Authentication Sessions)
CREATE TABLE IF NOT EXISTS verification_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(64) NOT NULL,
    status VARCHAR(30) DEFAULT 'AUTHENTICATED', -- AUTHENTICATED, UNDER_REVIEW, CHALLENGED, TERMINATED
    current_trust_score DOUBLE PRECISION DEFAULT 1.0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- 4. Derived Behavioural Telemetry Windows (STRICT PRIVACY: NO CONTENT)
CREATE TABLE IF NOT EXISTS behavioural_telemetry_windows (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) REFERENCES verification_sessions(session_id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    window_duration_seconds INT DEFAULT 30,
    
    -- Keystroke Timing Metrics (milliseconds)
    dwell_mean_ms DOUBLE PRECISION NOT NULL,
    dwell_std_ms DOUBLE PRECISION NOT NULL,
    dwell_median_ms DOUBLE PRECISION NOT NULL,
    flight_mean_ms DOUBLE PRECISION NOT NULL,
    flight_std_ms DOUBLE PRECISION NOT NULL,
    press_latency_mean_ms DOUBLE PRECISION NOT NULL,
    press_latency_std_ms DOUBLE PRECISION NOT NULL,
    
    -- Mouse Kinematics
    mouse_velocity_mean DOUBLE PRECISION NOT NULL,
    mouse_velocity_max DOUBLE PRECISION NOT NULL,
    mouse_velocity_std DOUBLE PRECISION NOT NULL,
    mouse_accel_mean DOUBLE PRECISION NOT NULL,
    mouse_accel_std DOUBLE PRECISION NOT NULL,
    click_duration_mean_ms DOUBLE PRECISION NOT NULL,
    click_duration_std_ms DOUBLE PRECISION NOT NULL,
    
    -- Rates & Activity Counts
    keystroke_rate_hz DOUBLE PRECISION NOT NULL,
    mouse_event_rate_hz DOUBLE PRECISION NOT NULL,
    total_events INT NOT NULL,
    
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Verification Assessment Events
CREATE TABLE IF NOT EXISTS verification_events (
    id BIGSERIAL PRIMARY KEY,
    telemetry_window_id BIGINT REFERENCES behavioural_telemetry_windows(id) ON DELETE CASCADE,
    session_id VARCHAR(64) REFERENCES verification_sessions(session_id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    trust_score DOUBLE PRECISION NOT NULL,
    anomaly_score DOUBLE PRECISION NOT NULL,
    adaptation_decision VARCHAR(30) NOT NULL, -- TRUSTED, PASSIVE_MONITOR, REVERIFY_CHALLENGE, STEP_UP_MFA
    decision_reason TEXT,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Safe Adaptation Engine Action Ledger
CREATE TABLE IF NOT EXISTS adaptation_actions (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT REFERENCES verification_events(id) ON DELETE CASCADE,
    session_id VARCHAR(64) REFERENCES verification_sessions(session_id) ON DELETE CASCADE,
    action_type VARCHAR(40) NOT NULL, -- NONE, PASSIVE_CAPTCHA, BIOMETRIC_REAUTH, STEP_UP_MFA, SESSION_LOCK
    status VARCHAR(20) DEFAULT 'DISPATCHED', -- DISPATCHED, COMPLETED, FAILED, TIMED_OUT
    action_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    performed_by VARCHAR(50) DEFAULT 'SYSTEM',
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high-throughput continuous stream processing
CREATE INDEX IF NOT EXISTS idx_telemetry_session ON behavioural_telemetry_windows(session_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_recorded_at ON behavioural_telemetry_windows(recorded_at);
CREATE INDEX IF NOT EXISTS idx_verification_events_session ON verification_events(session_id);
CREATE INDEX IF NOT EXISTS idx_verification_events_user ON verification_events(user_id);
