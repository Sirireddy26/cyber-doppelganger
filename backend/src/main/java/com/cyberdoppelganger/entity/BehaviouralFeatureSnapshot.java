package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "behavioural_feature_snapshots", indexes = {
    @Index(name = "idx_snapshot_captured_at", columnList = "captured_at"),
    @Index(name = "idx_snapshot_device_id", columnList = "device_id"),
    @Index(name = "idx_snapshot_user_id", columnList = "user_id"),
    @Index(name = "idx_snapshot_session_id", columnList = "session_id")
})
public class BehaviouralFeatureSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", nullable = false, length = 128)
    private String deviceId;

    @Column(name = "session_id")
    private Long sessionId;

    @Column(name = "captured_at", nullable = false)
    private Instant capturedAt;

    @Column(name = "window_duration_seconds", nullable = false)
    private Integer windowDurationSeconds;

    @Column(name = "schema_version", nullable = false, length = 16)
    private String schemaVersion = "2.0";

    @Column(name = "feature_payload", nullable = false, columnDefinition = "TEXT")
    private String featurePayload;

    @Column(name = "received_at", nullable = false, updatable = false)
    private Instant receivedAt = Instant.now();

    public BehaviouralFeatureSnapshot() {}

    public BehaviouralFeatureSnapshot(
            Long userId,
            String deviceId,
            Long sessionId,
            Instant capturedAt,
            Integer windowDurationSeconds,
            String schemaVersion,
            String featurePayload
    ) {
        this.userId = userId;
        this.deviceId = deviceId;
        this.sessionId = sessionId;
        this.capturedAt = capturedAt;
        this.windowDurationSeconds = windowDurationSeconds;
        this.schemaVersion = (schemaVersion != null && !schemaVersion.isBlank()) ? schemaVersion : "2.0";
        this.featurePayload = featurePayload;
        this.receivedAt = Instant.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }

    public Instant getCapturedAt() { return capturedAt; }
    public void setCapturedAt(Instant capturedAt) { this.capturedAt = capturedAt; }

    public Integer getWindowDurationSeconds() { return windowDurationSeconds; }
    public void setWindowDurationSeconds(Integer windowDurationSeconds) { this.windowDurationSeconds = windowDurationSeconds; }

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }

    public String getFeaturePayload() { return featurePayload; }
    public void setFeaturePayload(String featurePayload) { this.featurePayload = featurePayload; }

    public Instant getReceivedAt() { return receivedAt; }
    public void setReceivedAt(Instant receivedAt) { this.receivedAt = receivedAt; }
}
