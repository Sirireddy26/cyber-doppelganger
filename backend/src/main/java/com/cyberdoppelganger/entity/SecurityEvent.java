package com.cyberdoppelganger.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "security_events", indexes = {
    @Index(name = "idx_sec_event_created_at", columnList = "created_at"),
    @Index(name = "idx_sec_event_user_id", columnList = "user_id"),
    @Index(name = "idx_sec_event_device_id", columnList = "device_id")
})
public class SecurityEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "device_id", length = 128)
    private String deviceId;

    @Column(name = "event_type", nullable = false, length = 64)
    private String eventType;

    @Column(nullable = false, length = 32)
    private String severity = "MEDIUM";

    @Column(nullable = false, length = 512)
    private String description;

    @Column(nullable = false, length = 32)
    private String status = "NEW";

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt = Instant.now();

    public SecurityEvent() {}

    public SecurityEvent(Long userId, String deviceId, String eventType, String severity, String description, String status) {
        this.userId = userId;
        this.deviceId = deviceId;
        this.eventType = eventType;
        this.severity = (severity != null) ? severity : "MEDIUM";
        this.description = description;
        this.status = (status != null) ? status : "NEW";
        this.createdAt = Instant.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }

    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
