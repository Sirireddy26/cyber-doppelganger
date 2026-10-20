package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public class AdaptationRequestDTO {

    @JsonProperty("snapshot_id")
    private Long snapshotId;

    @JsonProperty("verification_result_id")
    private Long verificationResultId;

    @JsonProperty("device_id")
    private String deviceId;

    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("features")
    private Map<String, Object> features;

    public AdaptationRequestDTO() {}

    public AdaptationRequestDTO(Long snapshotId, Long verificationResultId, String deviceId,
                                String userId, Map<String, Object> features) {
        this.snapshotId = snapshotId;
        this.verificationResultId = verificationResultId;
        this.deviceId = deviceId;
        this.userId = userId;
        this.features = features;
    }

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public Long getVerificationResultId() { return verificationResultId; }
    public void setVerificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public Map<String, Object> getFeatures() { return features; }
    public void setFeatures(Map<String, Object> features) { this.features = features; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private Long snapshotId;
        private Long verificationResultId;
        private String deviceId;
        private String userId;
        private Map<String, Object> features;

        public Builder snapshotId(Long snapshotId) { this.snapshotId = snapshotId; return this; }
        public Builder verificationResultId(Long verificationResultId) { this.verificationResultId = verificationResultId; return this; }
        public Builder deviceId(String deviceId) { this.deviceId = deviceId; return this; }
        public Builder userId(String userId) { this.userId = userId; return this; }
        public Builder features(Map<String, Object> features) { this.features = features; return this; }

        public AdaptationRequestDTO build() {
            return new AdaptationRequestDTO(snapshotId, verificationResultId, deviceId, userId, features);
        }
    }
}
