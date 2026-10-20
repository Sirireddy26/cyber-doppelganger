package com.cyberdoppelganger.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AdaptationActionDTO {

    @JsonProperty("reason")
    private String reason;

    @JsonProperty("authorized_by")
    private String authorizedBy;

    @JsonProperty("target_version")
    private String targetVersion;

    public AdaptationActionDTO() {}

    public AdaptationActionDTO(String reason, String authorizedBy, String targetVersion) {
        this.reason = reason;
        this.authorizedBy = authorizedBy;
        this.targetVersion = targetVersion;
    }

    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }

    public String getAuthorizedBy() { return authorizedBy; }
    public void setAuthorizedBy(String authorizedBy) { this.authorizedBy = authorizedBy; }

    public String getTargetVersion() { return targetVersion; }
    public void setTargetVersion(String targetVersion) { this.targetVersion = targetVersion; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private String reason;
        private String authorizedBy;
        private String targetVersion;

        public Builder reason(String reason) { this.reason = reason; return this; }
        public Builder authorizedBy(String authorizedBy) { this.authorizedBy = authorizedBy; return this; }
        public Builder targetVersion(String targetVersion) { this.targetVersion = targetVersion; return this; }

        public AdaptationActionDTO build() {
            return new AdaptationActionDTO(reason, authorizedBy, targetVersion);
        }
    }
}
