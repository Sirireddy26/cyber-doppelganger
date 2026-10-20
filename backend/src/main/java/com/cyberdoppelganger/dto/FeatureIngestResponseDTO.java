package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class FeatureIngestResponseDTO {

    private String status;

    @JsonProperty("snapshotId")
    private String snapshotId;

    @JsonProperty("receivedAt")
    private String receivedAt;

    @JsonProperty("verification")
    private VerificationResponseDTO verification;

    @JsonProperty("adaptation")
    private AdaptationResponseDTO adaptation;

    @JsonProperty("processing_error")
    private String processingError;

    public FeatureIngestResponseDTO() {}

    public FeatureIngestResponseDTO(String status, String snapshotId, String receivedAt) {
        this.status = status;
        this.snapshotId = snapshotId;
        this.receivedAt = receivedAt;
    }

    public FeatureIngestResponseDTO(String status, String snapshotId, String receivedAt,
                                   VerificationResponseDTO verification, AdaptationResponseDTO adaptation) {
        this.status = status;
        this.snapshotId = snapshotId;
        this.receivedAt = receivedAt;
        this.verification = verification;
        this.adaptation = adaptation;
    }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getSnapshotId() { return snapshotId; }
    public void setSnapshotId(String snapshotId) { this.snapshotId = snapshotId; }

    public String getReceivedAt() { return receivedAt; }
    public void setReceivedAt(String receivedAt) { this.receivedAt = receivedAt; }

    public VerificationResponseDTO getVerification() { return verification; }
    public void setVerification(VerificationResponseDTO verification) { this.verification = verification; }

    public AdaptationResponseDTO getAdaptation() { return adaptation; }
    public void setAdaptation(AdaptationResponseDTO adaptation) { this.adaptation = adaptation; }

    public String getProcessingError() { return processingError; }
    public void setProcessingError(String processingError) { this.processingError = processingError; }
}

