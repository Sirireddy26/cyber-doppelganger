package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class ApplicationFeaturesDTO {

    @JsonProperty("process_count")
    @NotNull
    @Min(0)
    private Integer processCount = 0;

    @JsonProperty("active_process_count")
    @NotNull
    @Min(0)
    private Integer activeProcessCount = 0;

    @JsonProperty("application_switch_count")
    @NotNull
    @Min(0)
    private Integer applicationSwitchCount = 0;

    @JsonProperty("process_activity_count")
    @NotNull
    @Min(0)
    private Integer processActivityCount = 0;

    @JsonProperty("application_activity_duration")
    @NotNull
    @Min(0)
    private Double applicationActivityDuration = 0.0;

    public ApplicationFeaturesDTO() {}

    public Integer getProcessCount() { return processCount; }
    public void setProcessCount(Integer processCount) { this.processCount = processCount; }

    public Integer getActiveProcessCount() { return activeProcessCount; }
    public void setActiveProcessCount(Integer activeProcessCount) { this.activeProcessCount = activeProcessCount; }

    public Integer getApplicationSwitchCount() { return applicationSwitchCount; }
    public void setApplicationSwitchCount(Integer applicationSwitchCount) { this.applicationSwitchCount = applicationSwitchCount; }

    public Integer getProcessActivityCount() { return processActivityCount; }
    public void setProcessActivityCount(Integer processActivityCount) { this.processActivityCount = processActivityCount; }

    public Double getApplicationActivityDuration() { return applicationActivityDuration; }
    public void setApplicationActivityDuration(Double applicationActivityDuration) { this.applicationActivityDuration = applicationActivityDuration; }
}
