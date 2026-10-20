package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class FeatureSnapshotIngestDTO {

    @NotBlank(message = "Timestamp is required")
    private String timestamp;

    @JsonProperty("window_duration_seconds")
    @NotNull(message = "window_duration_seconds is required")
    @Min(value = 1, message = "window_duration_seconds must be at least 1")
    private Integer windowDurationSeconds;

    @JsonProperty("device_id")
    @NotBlank(message = "device_id is required")
    private String deviceId;

    @JsonProperty("user_id")
    private String userId;

    @JsonProperty("schema_version")
    private String schemaVersion = "2.0";

    @Valid
    private KeyboardFeaturesDTO keyboard;

    @Valid
    private MouseFeaturesDTO mouse;

    @Valid
    private SessionFeaturesDTO session;

    @Valid
    private ApplicationFeaturesDTO application;

    public FeatureSnapshotIngestDTO() {}

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public Integer getWindowDurationSeconds() { return windowDurationSeconds; }
    public void setWindowDurationSeconds(Integer windowDurationSeconds) { this.windowDurationSeconds = windowDurationSeconds; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }

    public KeyboardFeaturesDTO getKeyboard() { return keyboard; }
    public void setKeyboard(KeyboardFeaturesDTO keyboard) { this.keyboard = keyboard; }

    public MouseFeaturesDTO getMouse() { return mouse; }
    public void setMouse(MouseFeaturesDTO mouse) { this.mouse = mouse; }

    public SessionFeaturesDTO getSession() { return session; }
    public void setSession(SessionFeaturesDTO session) { this.session = session; }

    public ApplicationFeaturesDTO getApplication() { return application; }
    public void setApplication(ApplicationFeaturesDTO application) { this.application = application; }
}
