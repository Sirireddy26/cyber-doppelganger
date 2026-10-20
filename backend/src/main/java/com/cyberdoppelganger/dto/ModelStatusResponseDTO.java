package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public class ModelStatusResponseDTO {

    private String status;

    @JsonProperty("active_model_type")
    @JsonAlias({"active_model_type", "activeModelType"})
    private String activeModelType;

    @JsonProperty("isolation_forest")
    @JsonAlias({"isolation_forest", "isolationForest"})
    private Map<String, Object> isolationForest;

    @JsonProperty("random_forest")
    @JsonAlias({"random_forest", "randomForest"})
    private Map<String, Object> randomForest;

    public ModelStatusResponseDTO() {}

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getActiveModelType() { return activeModelType; }
    public void setActiveModelType(String activeModelType) { this.activeModelType = activeModelType; }

    public Map<String, Object> getIsolationForest() { return isolationForest; }
    public void setIsolationForest(Map<String, Object> isolationForest) { this.isolationForest = isolationForest; }

    public Map<String, Object> getRandomForest() { return randomForest; }
    public void setRandomForest(Map<String, Object> randomForest) { this.randomForest = randomForest; }
}
