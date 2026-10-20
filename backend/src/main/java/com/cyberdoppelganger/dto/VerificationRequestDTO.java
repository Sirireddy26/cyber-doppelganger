package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class VerificationRequestDTO {

    @JsonProperty("snapshot_id")
    private Long snapshotId;

    @JsonProperty("preferred_model")
    private String preferredModel;

    @JsonProperty("snapshot")
    private FeatureSnapshotIngestDTO snapshot;

    public VerificationRequestDTO() {}

    public Long getSnapshotId() { return snapshotId; }
    public void setSnapshotId(Long snapshotId) { this.snapshotId = snapshotId; }

    public String getPreferredModel() { return preferredModel; }
    public void setPreferredModel(String preferredModel) { this.preferredModel = preferredModel; }

    public FeatureSnapshotIngestDTO getSnapshot() { return snapshot; }
    public void setSnapshot(FeatureSnapshotIngestDTO snapshot) { this.snapshot = snapshot; }
}
