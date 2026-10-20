package com.cyberdoppelganger.util;

import com.cyberdoppelganger.exception.PrivacyViolationException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

import java.util.Iterator;
import java.util.Map;
import java.util.Set;

@Component
public class PrivacyContentFilter {

    private static final Set<String> FORBIDDEN_FIELDS = Set.of(
            "typed_text", "keystrokes", "clipboard_content", "screenshot",
            "screen_image", "screen_content", "pixel_data", "frame",
            "browser_url", "url", "history", "document_content", "document_name",
            "window_title", "window_text", "password", "passphrase", "secret",
            "char", "character", "key_name", "key_char", "text", "raw_keys",
            "clipboard", "terminal_command", "command_line"
    );

    private final ObjectMapper objectMapper;

    public PrivacyContentFilter(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * Recursively verifies that a JSON payload contains no forbidden content fields
     * and contains only finite numbers.
     *
     * @param jsonString raw or serialized JSON string
     * @throws PrivacyViolationException if a forbidden content field is detected
     * @throws IllegalArgumentException if non-finite numeric values are found
     */
    public void validateRawJson(String jsonString) {
        if (jsonString == null || jsonString.isBlank()) {
            return;
        }

        try {
            JsonNode root = objectMapper.readTree(jsonString);
            checkNodeRecursively(root);
        } catch (PrivacyViolationException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid JSON payload: " + e.getMessage());
        }
    }

    private void checkNodeRecursively(JsonNode node) {
        if (node.isObject()) {
            Iterator<Map.Entry<String, JsonNode>> fields = node.fields();
            while (fields.hasNext()) {
                Map.Entry<String, JsonNode> entry = fields.next();
                String keyName = entry.getKey().toLowerCase().trim();

                // Check for exact match or substring in forbidden keywords
                if (FORBIDDEN_FIELDS.contains(keyName) ||
                        keyName.contains("password") ||
                        keyName.contains("screenshot") ||
                        keyName.contains("clipboard") ||
                        keyName.contains("typed_text")) {
                    throw new PrivacyViolationException(entry.getKey());
                }

                // Check string values that might represent forbidden single character logs
                if (entry.getValue().isTextual() && ("key".equals(keyName) || "char".equals(keyName))) {
                    throw new PrivacyViolationException(entry.getKey());
                }

                checkNodeRecursively(entry.getValue());
            }
        } else if (node.isArray()) {
            for (JsonNode child : node) {
                checkNodeRecursively(child);
            }
        } else if (node.isTextual()) {
            String text = node.asText().trim().toLowerCase();
            if ("nan".equals(text) || "infinity".equals(text) || "-infinity".equals(text) || "+infinity".equals(text)) {
                throw new IllegalArgumentException("Non-finite numeric string detected (NaN/Infinity)");
            }
        } else if (node.isDouble() || node.isFloat()) {
            double val = node.asDouble();
            if (Double.isNaN(val) || Double.isInfinite(val)) {
                throw new IllegalArgumentException("Non-finite numeric value detected (NaN/Infinity)");
            }
        }
    }
}
