-- Flyway Migration V3: Safe Adaptation Engine & Profile Evolution
-- Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution

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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_profile_ver_tag ON profile_versions(version_tag);
CREATE INDEX IF NOT EXISTS idx_profile_device_user ON profile_versions(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_profile_created_at ON profile_versions(created_at);

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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_adapt_snapshot ON adaptation_events(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_adapt_verif_res ON adaptation_events(verification_result_id);
CREATE INDEX IF NOT EXISTS idx_adapt_decision ON adaptation_events(decision_state);
CREATE INDEX IF NOT EXISTS idx_adapt_created_at ON adaptation_events(created_at);

CREATE TABLE IF NOT EXISTS profile_freeze_records (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(128) NOT NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    profile_version VARCHAR(64) NOT NULL,
    is_frozen BOOLEAN NOT NULL DEFAULT TRUE,
    freeze_reason TEXT NOT NULL,
    frozen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    unfrozen_at TIMESTAMP WITH TIME ZONE,
    unfreeze_reason TEXT,
    unfrozen_by VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_freeze_device_user ON profile_freeze_records(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_freeze_frozen_at ON profile_freeze_records(frozen_at);
