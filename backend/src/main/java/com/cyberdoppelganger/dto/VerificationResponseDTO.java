package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public class VerificationResponseDTO {

    private Long id;

    @JsonProperty("snapshot_id")
    private Long snapshotId;

    @JsonProperty("device_id")
    private String deviceId;

    @JsonProperty("user_id")
    private Long userId;

    private String status;

    @JsonProperty("model_type")
    private String modelType;

    @JsonProperty("model_version")
    private String modelVersion;

    @JsonProperty("anomaly_score")
    private Double anomalyScore;

    @JsonProperty("raw_score")
    private Double rawScore;

    private Double threshold;

    @JsonProperty("confidence_score")
    private Double confidenceScore;

    private String decision;
    private String reason;

    @JsonProperty("created_at")
    private Instant createdAt;

    public VerificationResponseDTO() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getModelType() { return modelType; }
    public void setModelType(String modelType) { this.modelType = modelType; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public Double getAnomalyScore() { return anomalyScore; }
    public void setAnomalyScore(Double anomalyScore) { this.anomalyScore = anomalyScore; }

    public Double getRawScore() { return rawScore; }
    public void setRawScore(Double rawScore) { this.rawScore = rawScore; }

    public Double getThreshold() { return threshold; }
    public void setThreshold(Double threshold) { this.threshold = threshold; }

    public Double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(Double confidenceScore) { this.confidenceScore = confidenceScore; }

    public String getDecision() { return decision; }
    public void setDecision(String decision) { this.decision = decision; }

    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
