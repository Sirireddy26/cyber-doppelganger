package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class KeyboardFeaturesDTO {

    @JsonProperty("total_key_events")
    @NotNull
    @Min(0)
    private Integer totalKeyEvents = 0;

    @JsonProperty("mean_key_interval")
    @NotNull
    @Min(0)
    private Double meanKeyInterval = 0.0;

    @JsonProperty("median_key_interval")
    @NotNull
    @Min(0)
    private Double medianKeyInterval = 0.0;

    @JsonProperty("key_interval_std")
    @NotNull
    @Min(0)
    private Double keyIntervalStd = 0.0;

    @JsonProperty("minimum_key_interval")
    @NotNull
    @Min(0)
    private Double minimumKeyInterval = 0.0;

    @JsonProperty("maximum_key_interval")
    @NotNull
    @Min(0)
    private Double maximumKeyInterval = 0.0;

    @JsonProperty("typing_speed")
    @NotNull
    @Min(0)
    private Double typingSpeed = 0.0;

    @JsonProperty("pause_count")
    @NotNull
    @Min(0)
    private Integer pauseCount = 0;

    @JsonProperty("mean_pause_duration")
    @NotNull
    @Min(0)
    private Double meanPauseDuration = 0.0;

    @JsonProperty("longest_pause")
    @NotNull
    @Min(0)
    private Double longestPause = 0.0;

    @JsonProperty("typing_activity_duration")
    @NotNull
    @Min(0)
    private Double typingActivityDuration = 0.0;

    public KeyboardFeaturesDTO() {}

    public Integer getTotalKeyEvents() { return totalKeyEvents; }
    public void setTotalKeyEvents(Integer totalKeyEvents) { this.totalKeyEvents = totalKeyEvents; }

    public Double getMeanKeyInterval() { return meanKeyInterval; }
    public void setMeanKeyInterval(Double meanKeyInterval) { this.meanKeyInterval = meanKeyInterval; }

    public Double getMedianKeyInterval() { return medianKeyInterval; }
    public void setMedianKeyInterval(Double medianKeyInterval) { this.medianKeyInterval = medianKeyInterval; }

    public Double getKeyIntervalStd() { return keyIntervalStd; }
    public void setKeyIntervalStd(Double keyIntervalStd) { this.keyIntervalStd = keyIntervalStd; }

    public Double getMinimumKeyInterval() { return minimumKeyInterval; }
    public void setMinimumKeyInterval(Double minimumKeyInterval) { this.minimumKeyInterval = minimumKeyInterval; }

    public Double getMaximumKeyInterval() { return maximumKeyInterval; }
    public void setMaximumKeyInterval(Double maximumKeyInterval) { this.maximumKeyInterval = maximumKeyInterval; }

    public Double getTypingSpeed() { return typingSpeed; }
    public void setTypingSpeed(Double typingSpeed) { this.typingSpeed = typingSpeed; }

    public Integer getPauseCount() { return pauseCount; }
    public void setPauseCount(Integer pauseCount) { this.pauseCount = pauseCount; }

    public Double getMeanPauseDuration() { return meanPauseDuration; }
    public void setMeanPauseDuration(Double meanPauseDuration) { this.meanPauseDuration = meanPauseDuration; }

    public Double getLongestPause() { return longestPause; }
    public void setLongestPause(Double longestPause) { this.longestPause = longestPause; }

    public Double getTypingActivityDuration() { return typingActivityDuration; }
    public void setTypingActivityDuration(Double typingActivityDuration) { this.typingActivityDuration = typingActivityDuration; }
}
