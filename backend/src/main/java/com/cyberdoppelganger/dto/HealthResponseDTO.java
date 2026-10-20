package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public class HealthResponseDTO {

    private String status;
    private String service;
    private String database;

    @JsonProperty("database_type")
    private String databaseType;

    private String timestamp;

    public HealthResponseDTO() {
        this.timestamp = Instant.now().toString();
    }

    public HealthResponseDTO(String status, String service, String database, String databaseType) {
        this.status = status;
        this.service = service;
        this.database = database;
        this.databaseType = databaseType;
        this.timestamp = Instant.now().toString();
    }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getService() { return service; }
    public void setService(String service) { this.service = service; }

    public String getDatabase() { return database; }
    public void setDatabase(String database) { this.database = database; }

    public String getDatabaseType() { return databaseType; }
    public void setDatabaseType(String databaseType) { this.databaseType = databaseType; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
}
