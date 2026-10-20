package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public class AdaptationResponseDTO {

    private Long id;

    @JsonProperty("snapshot_id")
    private Long snapshotId;

    @JsonProperty("verification_result_id")
    private Long verificationResultId;

    @JsonProperty("device_id")
    private String deviceId;

    @JsonProperty("decision_state")
    private String decisionState;

    @JsonProperty("prior_profile_version")
    private String priorProfileVersion;

    @JsonProperty("new_profile_version")
    private String newProfileVersion;

    @JsonProperty("drift_magnitude")
    private Double driftMagnitude;

    @JsonProperty("velocity")
    private Double velocity;

    @JsonProperty("stability_score")
    private Double stabilityScore;

    @JsonProperty("candidate_count")
    private Integer candidateCount;

    @JsonProperty("suspicious_streak")
    private Integer suspiciousStreak;

    @JsonProperty("is_profile_frozen")
    private Boolean isProfileFrozen;

    @JsonProperty("decision_reason")
    private String decisionReason;

    @JsonProperty("policy_version")
    private String policyVersion;

    @JsonProperty("created_at")
    private Instant createdAt;

    public AdaptationResponseDTO() {}

    public AdaptationResponseDTO(Long id, Long snapshotId, Long verificationResultId, String deviceId,
                                 String decisionState, String priorProfileVersion, String newProfileVersion,
                                 Double driftMagnitude, Double velocity, Double stabilityScore,
                                 Integer candidateCount, Integer suspiciousStreak, Boolean isProfileFrozen,
                                 String decisionReason, String policyVersion, Instant createdAt) {
        this.id = id;
        this.snapshotId = snapshotId;
        this.verificationResultId = verificationResultId;
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
        this.createdAt = createdAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public Long getVerificationResultId() { return verificationResultId; }
    public void setVerificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; }

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
        private Long id;
        private Long snapshotId;
        private Long verificationResultId;
        private String deviceId;
        private String decisionState;
        private String priorProfileVersion;
        private String newProfileVersion;
        private Double driftMagnitude;
        private Double velocity;
        private Double stabilityScore;
        private Integer candidateCount;
        private Integer suspiciousStreak;
        private Boolean isProfileFrozen;
        private String decisionReason;
        private String policyVersion;
        private Instant createdAt;

        public Builder id(Long id) { this.id = id; return this; }
        public Builder snapshotId(Long snapshotId) { this.snapshotId = snapshotId; return this; }
        public Builder verificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; return this; }
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

        public AdaptationResponseDTO build() {
            return new AdaptationResponseDTO(id, snapshotId, verificationResultId, deviceId,
                    decisionState, priorProfileVersion, newProfileVersion, driftMagnitude,
                    velocity, stabilityScore, candidateCount, suspiciousStreak, isProfileFrozen,
                    decisionReason, policyVersion, createdAt);
        }
    }
}
