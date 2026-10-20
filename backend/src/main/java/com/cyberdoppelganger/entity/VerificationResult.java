package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "verification_results", indexes = {
    @Index(name = "idx_verif_snapshot", columnList = "snapshot_id"),
    @Index(name = "idx_verif_device_user", columnList = "device_id, user_id"),
    @Index(name = "idx_verif_created_at", columnList = "created_at")
})
public class VerificationResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "snapshot_id")
    private Long snapshotId;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", nullable = false, length = 128)
    private String deviceId;

    @Column(name = "model_version", nullable = false, length = 32)
    private String modelVersion;

    @Column(name = "model_type", nullable = false, length = 32)
    private String modelType;

    @Column(name = "status", nullable = false, length = 32)
    private String status;

    @Column(name = "anomaly_score")
    private Double anomalyScore;

    @Column(name = "raw_score")
    private Double rawScore;

    @Column(name = "threshold")
    private Double threshold;

    @Column(name = "confidence_score")
    private Double confidenceScore;

    @Column(name = "decision", nullable = false, length = 64)
    private String decision;

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    public VerificationResult() {}

    public VerificationResult(
            Long snapshotId,
            Long userId,
            String deviceId,
            String modelVersion,
            String modelType,
            String status,
            Double anomalyScore,
            Double rawScore,
            Double threshold,
            Double confidenceScore,
            String decision,
            String reason
    ) {
        this.snapshotId = snapshotId;
        this.userId = userId;
        this.deviceId = deviceId;
        this.modelVersion = modelVersion;
        this.modelType = modelType;
        this.status = status;
        this.anomalyScore = anomalyScore;
        this.rawScore = rawScore;
        this.threshold = threshold;
        this.confidenceScore = confidenceScore;
        this.decision = decision;
        this.reason = reason;
        this.createdAt = Instant.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getModelVersion() { return modelVersion; }
    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public String getModelType() { return modelType; }
    public void setModelType(String modelType) { this.modelType = modelType; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

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
