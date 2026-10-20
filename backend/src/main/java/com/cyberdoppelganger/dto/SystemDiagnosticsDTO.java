package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.Map;

public class SystemDiagnosticsDTO {

    private String timestamp;
    private Map<String, Object> backend;
    private Map<String, Object> database;

    @JsonProperty("ml_service")
    private Map<String, Object> mlService;

    @JsonProperty("model_readiness")
    private Map<String, Object> modelReadiness;

    @JsonProperty("trusted_profile")
    private Map<String, Object> trustedProfile;

    @JsonProperty("adaptation_engine")
    private Map<String, Object> adaptationEngine;

    @JsonProperty("agent_telemetry")
    private Map<String, Object> agentTelemetry;

    @JsonProperty("system_summary")
    private Map<String, Object> systemSummary;

    public SystemDiagnosticsDTO() {
        this.timestamp = Instant.now().toString();
    }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public Map<String, Object> getBackend() { return backend; }
    public void setBackend(Map<String, Object> backend) { this.backend = backend; }

    public Map<String, Object> getDatabase() { return database; }
    public void setDatabase(Map<String, Object> database) { this.database = database; }

    public Map<String, Object> getMlService() { return mlService; }
    public void setMlService(Map<String, Object> mlService) { this.mlService = mlService; }

    public Map<String, Object> getModelReadiness() { return modelReadiness; }
    public void setModelReadiness(Map<String, Object> modelReadiness) { this.modelReadiness = modelReadiness; }

    public Map<String, Object> getTrustedProfile() { return trustedProfile; }
    public void setTrustedProfile(Map<String, Object> trustedProfile) { this.trustedProfile = trustedProfile; }

    public Map<String, Object> getAdaptationEngine() { return adaptationEngine; }
    public void setAdaptationEngine(Map<String, Object> adaptationEngine) { this.adaptationEngine = adaptationEngine; }

    public Map<String, Object> getAgentTelemetry() { return agentTelemetry; }
    public void setAgentTelemetry(Map<String, Object> agentTelemetry) { this.agentTelemetry = agentTelemetry; }

    public Map<String, Object> getSystemSummary() { return systemSummary; }
    public void setSystemSummary(Map<String, Object> systemSummary) { this.systemSummary = systemSummary; }
}
