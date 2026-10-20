package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class MouseFeaturesDTO {

    @JsonProperty("movement_distance")
    @NotNull
    @Min(0)
    private Double movementDistance = 0.0;

    @JsonProperty("mean_mouse_speed")
    @NotNull
    @Min(0)
    private Double meanMouseSpeed = 0.0;

    @JsonProperty("mouse_speed_std")
    @NotNull
    @Min(0)
    private Double mouseSpeedStd = 0.0;

    @JsonProperty("mean_acceleration")
    @NotNull
    @Min(0)
    private Double meanAcceleration = 0.0;

    @JsonProperty("click_count")
    @NotNull
    @Min(0)
    private Integer clickCount = 0;

    @JsonProperty("left_click_count")
    @NotNull
    @Min(0)
    private Integer leftClickCount = 0;

    @JsonProperty("right_click_count")
    @NotNull
    @Min(0)
    private Integer rightClickCount = 0;

    @JsonProperty("middle_click_count")
    @NotNull
    @Min(0)
    private Integer middleClickCount = 0;

    @JsonProperty("mean_click_interval")
    @NotNull
    @Min(0)
    private Double meanClickInterval = 0.0;

    @JsonProperty("click_interval_std")
    @NotNull
    @Min(0)
    private Double clickIntervalStd = 0.0;

    @JsonProperty("scroll_count")
    @NotNull
    @Min(0)
    private Integer scrollCount = 0;

    @JsonProperty("positive_scroll_count")
    @NotNull
    @Min(0)
    private Integer positiveScrollCount = 0;

    @JsonProperty("negative_scroll_count")
    @NotNull
    @Min(0)
    private Integer negativeScrollCount = 0;

    @JsonProperty("mouse_active_duration")
    @NotNull
    @Min(0)
    private Double mouseActiveDuration = 0.0;

    public MouseFeaturesDTO() {}

    public Double getMovementDistance() { return movementDistance; }
    public void setMovementDistance(Double movementDistance) { this.movementDistance = movementDistance; }

    public Double getMeanMouseSpeed() { return meanMouseSpeed; }
    public void setMeanMouseSpeed(Double meanMouseSpeed) { this.meanMouseSpeed = meanMouseSpeed; }

    public Double getMouseSpeedStd() { return mouseSpeedStd; }
    public void setMouseSpeedStd(Double mouseSpeedStd) { this.mouseSpeedStd = mouseSpeedStd; }

    public Double getMeanAcceleration() { return meanAcceleration; }
    public void setMeanAcceleration(Double meanAcceleration) { this.meanAcceleration = meanAcceleration; }

    public Integer getClickCount() { return clickCount; }
    public void setClickCount(Integer clickCount) { this.clickCount = clickCount; }

    public Integer getLeftClickCount() { return leftClickCount; }
    public void setLeftClickCount(Integer leftClickCount) { this.leftClickCount = leftClickCount; }

    public Integer getRightClickCount() { return rightClickCount; }
    public void setRightClickCount(Integer rightClickCount) { this.rightClickCount = rightClickCount; }

    public Integer getMiddleClickCount() { return middleClickCount; }
    public void setMiddleClickCount(Integer middleClickCount) { this.middleClickCount = middleClickCount; }

    public Double getMeanClickInterval() { return meanClickInterval; }
    public void setMeanClickInterval(Double meanClickInterval) { this.meanClickInterval = meanClickInterval; }

    public Double getClickIntervalStd() { return clickIntervalStd; }
    public void setClickIntervalStd(Double clickIntervalStd) { this.clickIntervalStd = clickIntervalStd; }

    public Integer getScrollCount() { return scrollCount; }
    public void setScrollCount(Integer scrollCount) { this.scrollCount = scrollCount; }

    public Integer getPositiveScrollCount() { return positiveScrollCount; }
    public void setPositiveScrollCount(Integer positiveScrollCount) { this.positiveScrollCount = positiveScrollCount; }

    public Integer getNegativeScrollCount() { return negativeScrollCount; }
    public void setNegativeScrollCount(Integer negativeScrollCount) { this.negativeScrollCount = negativeScrollCount; }

    public Double getMouseActiveDuration() { return mouseActiveDuration; }
    public void setMouseActiveDuration(Double mouseActiveDuration) { this.mouseActiveDuration = mouseActiveDuration; }
}
