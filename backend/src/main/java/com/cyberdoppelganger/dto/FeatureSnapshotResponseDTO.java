package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public class FeatureSnapshotResponseDTO {

    private Long id;

    @JsonProperty("device_id")
    private String deviceId;

    @JsonProperty("user_id")
    private Long userId;

    @JsonProperty("session_id")
    private Long sessionId;

    @JsonProperty("captured_at")
    private String capturedAt;

    @JsonProperty("window_duration_seconds")
    private Integer windowDurationSeconds;

    @JsonProperty("schema_version")
    private String schemaVersion;

    @JsonProperty("received_at")
    private String receivedAt;

    private Map<String, Object> features;

    public FeatureSnapshotResponseDTO() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }

    public String getCapturedAt() { return capturedAt; }
    public void setCapturedAt(String capturedAt) { this.capturedAt = capturedAt; }

    public Integer getWindowDurationSeconds() { return windowDurationSeconds; }
    public void setWindowDurationSeconds(Integer windowDurationSeconds) { this.windowDurationSeconds = windowDurationSeconds; }

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }

    public String getReceivedAt() { return receivedAt; }
    public void setReceivedAt(String receivedAt) { this.receivedAt = receivedAt; }

    public Map<String, Object> getFeatures() { return features; }
    public void setFeatures(Map<String, Object> features) { this.features = features; }
}
