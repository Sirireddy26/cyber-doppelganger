package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "profile_versions")
public class ProfileVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", nullable = false, length = 128)
    private String deviceId;

    @Column(name = "version_tag", nullable = false, length = 64)
    private String versionTag;

    @Column(name = "parent_version_tag", length = 64)
    private String parentVersionTag;

    @Column(name = "sample_count", nullable = false)
    private Integer sampleCount;

    @Column(name = "status", nullable = false, length = 32)
    private String status;

    @Column(name = "feature_statistics", columnDefinition = "TEXT")
    private String featureStatistics;

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;

    @Column(name = "activated_at")
    private Instant activatedAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public ProfileVersion() {}

    public ProfileVersion(Long userId, String deviceId, String versionTag, String parentVersionTag,
                          Integer sampleCount, String status, String featureStatistics,
                          String reason, Instant activatedAt, Instant createdAt) {
        this.userId = userId;
        this.deviceId = deviceId;
        this.versionTag = versionTag;
        this.parentVersionTag = parentVersionTag;
        this.sampleCount = sampleCount;
        this.status = status;
        this.featureStatistics = featureStatistics;
        this.reason = reason;
        this.activatedAt = activatedAt;
        this.createdAt = createdAt != null ? createdAt : Instant.now();
    }

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = Instant.now();
        }
        if (sampleCount == null) {
            sampleCount = 0;
        }
        if (status == null) {
            status = "ACTIVE";
        }
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getVersionTag() { return versionTag; }
    public void setVersionTag(String versionTag) { this.versionTag = versionTag; }

    public String getParentVersionTag() { return parentVersionTag; }
    public void setParentVersionTag(String parentVersionTag) { this.parentVersionTag = parentVersionTag; }

    public Integer getSampleCount() { return sampleCount; }
    public void setSampleCount(Integer sampleCount) { this.sampleCount = sampleCount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getFeatureStatistics() { return featureStatistics; }
    public void setFeatureStatistics(String featureStatistics) { this.featureStatistics = featureStatistics; }

    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }

    public Instant getActivatedAt() { return activatedAt; }
    public void setActivatedAt(Instant activatedAt) { this.activatedAt = activatedAt; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private Long userId;
        private String deviceId;
        private String versionTag;
        private String parentVersionTag;
        private Integer sampleCount = 0;
        private String status = "ACTIVE";
        private String featureStatistics;
        private String reason;
        private Instant activatedAt;
        private Instant createdAt;

        public Builder userId(Long userId) { this.userId = userId; return this; }
        public Builder deviceId(String deviceId) { this.deviceId = deviceId; return this; }
        public Builder versionTag(String versionTag) { this.versionTag = versionTag; return this; }
        public Builder parentVersionTag(String parentVersionTag) { this.parentVersionTag = parentVersionTag; return this; }
        public Builder sampleCount(Integer sampleCount) { this.sampleCount = sampleCount; return this; }
        public Builder status(String status) { this.status = status; return this; }
        public Builder featureStatistics(String featureStatistics) { this.featureStatistics = featureStatistics; return this; }
        public Builder reason(String reason) { this.reason = reason; return this; }
        public Builder activatedAt(Instant activatedAt) { this.activatedAt = activatedAt; return this; }
        public Builder createdAt(Instant createdAt) { this.createdAt = createdAt; return this; }

        public ProfileVersion build() {
            return new ProfileVersion(userId, deviceId, versionTag, parentVersionTag, sampleCount,
                    status, featureStatistics, reason, activatedAt, createdAt);
        }
    }
}
