package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class SessionFeaturesDTO {

    @JsonProperty("session_duration")
    @NotNull
    @Min(0)
    private Double sessionDuration = 0.0;

    @JsonProperty("active_duration")
    @NotNull
    @Min(0)
    private Double activeDuration = 0.0;

    @JsonProperty("idle_duration")
    @NotNull
    @Min(0)
    private Double idleDuration = 0.0;

    @JsonProperty("active_idle_ratio")
    @NotNull
    @Min(0)
    private Double activeIdleRatio = 0.0;

    @JsonProperty("activity_density")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double activityDensity = 0.0;

    @JsonProperty("keyboard_activity_duration")
    @NotNull
    @Min(0)
    private Double keyboardActivityDuration = 0.0;

    @JsonProperty("mouse_activity_duration")
    @NotNull
    @Min(0)
    private Double mouseActivityDuration = 0.0;

    public SessionFeaturesDTO() {}

    public Double getSessionDuration() { return sessionDuration; }
    public void setSessionDuration(Double sessionDuration) { this.sessionDuration = sessionDuration; }

    public Double getActiveDuration() { return activeDuration; }
    public void setActiveDuration(Double activeDuration) { this.activeDuration = activeDuration; }

    public Double getIdleDuration() { return idleDuration; }
    public void setIdleDuration(Double idleDuration) { this.idleDuration = idleDuration; }

    public Double getActiveIdleRatio() { return activeIdleRatio; }
    public void setActiveIdleRatio(Double activeIdleRatio) { this.activeIdleRatio = activeIdleRatio; }

    public Double getActivityDensity() { return activityDensity; }
    public void setActivityDensity(Double activityDensity) { this.activityDensity = activityDensity; }

    public Double getKeyboardActivityDuration() { return keyboardActivityDuration; }
    public void setKeyboardActivityDuration(Double keyboardActivityDuration) { this.keyboardActivityDuration = keyboardActivityDuration; }

    public Double getMouseActivityDuration() { return mouseActivityDuration; }
    public void setMouseActivityDuration(Double mouseActivityDuration) { this.mouseActivityDuration = mouseActivityDuration; }
}
