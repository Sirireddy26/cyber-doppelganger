package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class AdaptationStatusDTO {

    @JsonProperty("engine_status")
    private String engineStatus;

    @JsonProperty("active_version")
    private String activeVersion;

    @JsonProperty("is_frozen")
    private Boolean isFrozen;

    @JsonProperty("freeze_reason")
    private String freezeReason;

    @JsonProperty("frozen_at")
    private String frozenAt;

    @JsonProperty("suspicious_streak")
    private Integer suspiciousStreak;

    @JsonProperty("sample_count")
    private Integer sampleCount;

    @JsonProperty("candidate_buffer")
    private Map<String, Object> candidateBuffer;

    @JsonProperty("policy_config")
    private Map<String, Object> policyConfig;

    @JsonProperty("versions_summary")
    private List<Map<String, Object>> versionsSummary;

    public AdaptationStatusDTO() {}

    public AdaptationStatusDTO(String engineStatus, String activeVersion, Boolean isFrozen,
                               String freezeReason, String frozenAt, Integer suspiciousStreak,
                               Integer sampleCount, Map<String, Object> candidateBuffer,
                               Map<String, Object> policyConfig, List<Map<String, Object>> versionsSummary) {
        this.engineStatus = engineStatus;
        this.activeVersion = activeVersion;
        this.isFrozen = isFrozen;
        this.freezeReason = freezeReason;
        this.frozenAt = frozenAt;
        this.suspiciousStreak = suspiciousStreak;
        this.sampleCount = sampleCount;
        this.candidateBuffer = candidateBuffer;
        this.policyConfig = policyConfig;
        this.versionsSummary = versionsSummary;
    }

    public String getEngineStatus() { return engineStatus; }
    public void setEngineStatus(String engineStatus) { this.engineStatus = engineStatus; }

    public String getActiveVersion() { return activeVersion; }
    public void setActiveVersion(String activeVersion) { this.activeVersion = activeVersion; }

    public Boolean getIsFrozen() { return isFrozen; }
    public void setIsFrozen(Boolean isFrozen) { this.isFrozen = isFrozen; }

    public String getFreezeReason() { return freezeReason; }
    public void setFreezeReason(String freezeReason) { this.freezeReason = freezeReason; }

    public String getFrozenAt() { return frozenAt; }
    public void setFrozenAt(String frozenAt) { this.frozenAt = frozenAt; }

    public Integer getSuspiciousStreak() { return suspiciousStreak; }
    public void setSuspiciousStreak(Integer suspiciousStreak) { this.suspiciousStreak = suspiciousStreak; }

    public Integer getSampleCount() { return sampleCount; }
    public void setSampleCount(Integer sampleCount) { this.sampleCount = sampleCount; }

    public Map<String, Object> getCandidateBuffer() { return candidateBuffer; }
    public void setCandidateBuffer(Map<String, Object> candidateBuffer) { this.candidateBuffer = candidateBuffer; }

    public Map<String, Object> getPolicyConfig() { return policyConfig; }
    public void setPolicyConfig(Map<String, Object> policyConfig) { this.policyConfig = policyConfig; }

    public List<Map<String, Object>> getVersionsSummary() { return versionsSummary; }
    public void setVersionsSummary(List<Map<String, Object>> versionsSummary) { this.versionsSummary = versionsSummary; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private String engineStatus;
        private String activeVersion;
        private Boolean isFrozen;
        private String freezeReason;
        private String frozenAt;
        private Integer suspiciousStreak;
        private Integer sampleCount;
        private Map<String, Object> candidateBuffer;
        private Map<String, Object> policyConfig;
        private List<Map<String, Object>> versionsSummary;

        public Builder engineStatus(String engineStatus) { this.engineStatus = engineStatus; return this; }
        public Builder activeVersion(String activeVersion) { this.activeVersion = activeVersion; return this; }
        public Builder isFrozen(Boolean isFrozen) { this.isFrozen = isFrozen; return this; }
        public Builder freezeReason(String freezeReason) { this.freezeReason = freezeReason; return this; }
        public Builder frozenAt(String frozenAt) { this.frozenAt = frozenAt; return this; }
        public Builder suspiciousStreak(Integer suspiciousStreak) { this.suspiciousStreak = suspiciousStreak; return this; }
        public Builder sampleCount(Integer sampleCount) { this.sampleCount = sampleCount; return this; }
        public Builder candidateBuffer(Map<String, Object> candidateBuffer) { this.candidateBuffer = candidateBuffer; return this; }
        public Builder policyConfig(Map<String, Object> policyConfig) { this.policyConfig = policyConfig; return this; }
        public Builder versionsSummary(List<Map<String, Object>> versionsSummary) { this.versionsSummary = versionsSummary; return this; }

        public AdaptationStatusDTO build() {
            return new AdaptationStatusDTO(engineStatus, activeVersion, isFrozen, freezeReason,
                    frozenAt, suspiciousStreak, sampleCount, candidateBuffer, policyConfig, versionsSummary);
        }
    }
}
