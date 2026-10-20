package com.cyberdoppelganger.exception;

public class PrivacyViolationException extends RuntimeException {

    private final String prohibitedField;

    public PrivacyViolationException(String prohibitedField) {
        super("Privacy Guard Violation: Prohibited content field '" + prohibitedField + "' detected in request payload");
        this.prohibitedField = prohibitedField;
    }

    public String getProhibitedField() {
        return prohibitedField;
    }
}
