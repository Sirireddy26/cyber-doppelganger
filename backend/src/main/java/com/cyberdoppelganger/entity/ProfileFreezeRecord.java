package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "profile_freeze_records")
public class ProfileFreezeRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", nullable = false, length = 128)
    private String deviceId;

    @Column(name = "profile_version", nullable = false, length = 64)
    private String profileVersion;

    @Column(name = "is_frozen", nullable = false)
    private Boolean isFrozen;

    @Column(name = "freeze_reason", nullable = false, columnDefinition = "TEXT")
    private String freezeReason;

    @Column(name = "frozen_at", nullable = false)
    private Instant frozenAt;

    @Column(name = "unfrozen_at")
    private Instant unfrozenAt;

    @Column(name = "unfreeze_reason", columnDefinition = "TEXT")
    private String unfreezeReason;

    @Column(name = "unfrozen_by", length = 64)
    private String unfrozenBy;

    public ProfileFreezeRecord() {}

    public ProfileFreezeRecord(Long userId, String deviceId, String profileVersion, Boolean isFrozen,
                               String freezeReason, Instant frozenAt, Instant unfrozenAt,
                               String unfreezeReason, String unfrozenBy) {
        this.userId = userId;
        this.deviceId = deviceId;
        this.profileVersion = profileVersion;
        this.isFrozen = isFrozen;
        this.freezeReason = freezeReason;
        this.frozenAt = frozenAt != null ? frozenAt : Instant.now();
        this.unfrozenAt = unfrozenAt;
        this.unfreezeReason = unfreezeReason;
        this.unfrozenBy = unfrozenBy;
    }

    @PrePersist
    protected void onCreate() {
        if (frozenAt == null) {
            frozenAt = Instant.now();
        }
        if (isFrozen == null) {
            isFrozen = true;
        }
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getProfileVersion() { return profileVersion; }
    public void setProfileVersion(String profileVersion) { this.profileVersion = profileVersion; }

    public Boolean getIsFrozen() { return isFrozen; }
    public void setIsFrozen(Boolean isFrozen) { this.isFrozen = isFrozen; }

    public String getFreezeReason() { return freezeReason; }
    public void setFreezeReason(String freezeReason) { this.freezeReason = freezeReason; }

    public Instant getFrozenAt() { return frozenAt; }
    public void setFrozenAt(Instant frozenAt) { this.frozenAt = frozenAt; }

    public Instant getUnfrozenAt() { return unfrozenAt; }
    public void setUnfrozenAt(Instant unfrozenAt) { this.unfrozenAt = unfrozenAt; }

    public String getUnfreezeReason() { return unfreezeReason; }
    public void setUnfreezeReason(String unfreezeReason) { this.unfreezeReason = unfreezeReason; }

    public String getUnfrozenBy() { return unfrozenBy; }
    public void setUnfrozenBy(String unfrozenBy) { this.unfrozenBy = unfrozenBy; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private Long userId;
        private String deviceId;
        private String profileVersion;
        private Boolean isFrozen = true;
        private String freezeReason;
        private Instant frozenAt;
        private Instant unfrozenAt;
        private String unfreezeReason;
        private String unfrozenBy;

        public Builder userId(Long userId) { this.userId = userId; return this; }
        public Builder deviceId(String deviceId) { this.deviceId = deviceId; return this; }
        public Builder profileVersion(String profileVersion) { this.profileVersion = profileVersion; return this; }
        public Builder isFrozen(Boolean isFrozen) { this.isFrozen = isFrozen; return this; }
        public Builder freezeReason(String freezeReason) { this.freezeReason = freezeReason; return this; }
        public Builder frozenAt(Instant frozenAt) { this.frozenAt = frozenAt; return this; }
        public Builder unfrozenAt(Instant unfrozenAt) { this.unfrozenAt = unfrozenAt; return this; }
        public Builder unfreezeReason(String unfreezeReason) { this.unfreezeReason = unfreezeReason; return this; }
        public Builder unfrozenBy(String unfrozenBy) { this.unfrozenBy = unfrozenBy; return this; }

        public ProfileFreezeRecord build() {
            return new ProfileFreezeRecord(userId, deviceId, profileVersion, isFrozen, freezeReason,
                    frozenAt, unfrozenAt, unfreezeReason, unfrozenBy);
        }
    }
}
