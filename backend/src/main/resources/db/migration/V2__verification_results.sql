-- Flyway Migration V2: Verification Results Table
-- Phase 4: Machine Learning Behavioural Verification Pipeline

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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_verif_snapshot ON verification_results(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_verif_device_user ON verification_results(device_id, user_id);
CREATE INDEX IF NOT EXISTS idx_verif_created_at ON verification_results(created_at);
