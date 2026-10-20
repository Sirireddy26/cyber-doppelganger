package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "adaptation_events")
public class AdaptationEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "snapshot_id")
    private Long snapshotId;

    @Column(name = "verification_result_id")
    private Long verificationResultId;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", nullable = false, length = 128)
    private String deviceId;

    @Column(name = "decision_state", nullable = false, length = 32)
    private String decisionState;

    @Column(name = "prior_profile_version", nullable = false, length = 64)
    private String priorProfileVersion;

    @Column(name = "new_profile_version", length = 64)
    private String newProfileVersion;

    @Column(name = "drift_magnitude")
    private Double driftMagnitude;

    @Column(name = "velocity")
    private Double velocity;

    @Column(name = "stability_score")
    private Double stabilityScore;

    @Column(name = "candidate_count", nullable = false)
    private Integer candidateCount;

    @Column(name = "suspicious_streak", nullable = false)
    private Integer suspiciousStreak;

    @Column(name = "is_profile_frozen", nullable = false)
    private Boolean isProfileFrozen;

    @Column(name = "decision_reason", nullable = false, columnDefinition = "TEXT")
    private String decisionReason;

    @Column(name = "policy_version", nullable = false, length = 32)
    private String policyVersion;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public AdaptationEvent() {}

    public AdaptationEvent(Long snapshotId, Long verificationResultId, Long userId,
                           String deviceId, String decisionState, String priorProfileVersion,
                           String newProfileVersion, Double driftMagnitude, Double velocity,
                           Double stabilityScore, Integer candidateCount, Integer suspiciousStreak,
                           Boolean isProfileFrozen, String decisionReason, String policyVersion,
                           Instant createdAt) {
        this.snapshotId = snapshotId;
        this.verificationResultId = verificationResultId;
        this.userId = userId;
        this.deviceId = deviceId;
        this.decisionState = decisionState;
        this.priorProfileVersion = priorProfileVersion;
        this.newProfileVersion = newProfileVersion;
        this.driftMagnitude = driftMagnitude;
        this.velocity = velocity;
        this.stabilityScore = stabilityScore;
        this.candidateCount = candidateCount;
        this.suspiciousStreak = suspiciousStreak;
        this.isProfileFrozen = isProfileFrozen;
        this.decisionReason = decisionReason;
        this.policyVersion = policyVersion;
        this.createdAt = createdAt != null ? createdAt : Instant.now();
    }

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = Instant.now();
        }
        if (candidateCount == null) {
            candidateCount = 0;
        }
        if (suspiciousStreak == null) {
            suspiciousStreak = 0;
        }
        if (isProfileFrozen == null) {
            isProfileFrozen = false;
        }
        if (policyVersion == null) {
            policyVersion = "1.0.0";
        }
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public Long getVerificationResultId() { return verificationResultId; }
    public void setVerificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getDecisionState() { return decisionState; }
    public void setDecisionState(String decisionState) { this.decisionState = decisionState; }

    public String getPriorProfileVersion() { return priorProfileVersion; }
    public void setPriorProfileVersion(String priorProfileVersion) { this.priorProfileVersion = priorProfileVersion; }

    public String getNewProfileVersion() { return newProfileVersion; }
    public void setNewProfileVersion(String newProfileVersion) { this.newProfileVersion = newProfileVersion; }

    public Double getDriftMagnitude() { return driftMagnitude; }
    public void setDriftMagnitude(Double driftMagnitude) { this.driftMagnitude = driftMagnitude; }

    public Double getVelocity() { return velocity; }
    public void setVelocity(Double velocity) { this.velocity = velocity; }

    public Double getStabilityScore() { return stabilityScore; }
    public void setStabilityScore(Double stabilityScore) { this.stabilityScore = stabilityScore; }

    public Integer getCandidateCount() { return candidateCount; }
    public void setCandidateCount(Integer candidateCount) { this.candidateCount = candidateCount; }

    public Integer getSuspiciousStreak() { return suspiciousStreak; }
    public void setSuspiciousStreak(Integer suspiciousStreak) { this.suspiciousStreak = suspiciousStreak; }

    public Boolean getIsProfileFrozen() { return isProfileFrozen; }
    public void setIsProfileFrozen(Boolean isProfileFrozen) { this.isProfileFrozen = isProfileFrozen; }

    public String getDecisionReason() { return decisionReason; }
    public void setDecisionReason(String decisionReason) { this.decisionReason = decisionReason; }

    public String getPolicyVersion() { return policyVersion; }
    public void setPolicyVersion(String policyVersion) { this.policyVersion = policyVersion; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private Long snapshotId;
        private Long verificationResultId;
        private Long userId;
        private String deviceId;
        private String decisionState;
        private String priorProfileVersion;
        private String newProfileVersion;
        private Double driftMagnitude;
        private Double velocity;
        private Double stabilityScore;
        private Integer candidateCount = 0;
        private Integer suspiciousStreak = 0;
        private Boolean isProfileFrozen = false;
        private String decisionReason;
        private String policyVersion = "1.0.0";
        private Instant createdAt;

        public Builder snapshotId(Long snapshotId) { this.snapshotId = snapshotId; return this; }
        public Builder verificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; return this; }
        public Builder userId(Long userId) { this.userId = userId; return this; }
        public Builder deviceId(String deviceId) { this.deviceId = deviceId; return this; }
        public Builder decisionState(String decisionState) { this.decisionState = decisionState; return this; }
        public Builder priorProfileVersion(String priorProfileVersion) { this.priorProfileVersion = priorProfileVersion; return this; }
        public Builder newProfileVersion(String newProfileVersion) { this.newProfileVersion = newProfileVersion; return this; }
        public Builder driftMagnitude(Double driftMagnitude) { this.driftMagnitude = driftMagnitude; return this; }
        public Builder velocity(Double velocity) { this.velocity = velocity; return this; }
        public Builder stabilityScore(Double stabilityScore) { this.stabilityScore = stabilityScore; return this; }
        public Builder candidateCount(Integer candidateCount) { this.candidateCount = candidateCount; return this; }
        public Builder suspiciousStreak(Integer suspiciousStreak) { this.suspiciousStreak = suspiciousStreak; return this; }
        public Builder isProfileFrozen(Boolean isProfileFrozen) { this.isProfileFrozen = isProfileFrozen; return this; }
        public Builder decisionReason(String decisionReason) { this.decisionReason = decisionReason; return this; }
        public Builder policyVersion(String policyVersion) { this.policyVersion = policyVersion; return this; }
        public Builder createdAt(Instant createdAt) { this.createdAt = createdAt; return this; }

        public AdaptationEvent build() {
            return new AdaptationEvent(snapshotId, verificationResultId, userId, deviceId, decisionState,
                    priorProfileVersion, newProfileVersion, driftMagnitude, velocity, stabilityScore,
                    candidateCount, suspiciousStreak, isProfileFrozen, decisionReason, policyVersion, createdAt);
        }
    }
}
