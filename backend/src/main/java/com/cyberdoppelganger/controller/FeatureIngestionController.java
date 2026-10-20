package com.cyberdoppelganger.controller;

import com.cyberdoppelganger.dto.FeatureIngestResponseDTO;
import com.cyberdoppelganger.dto.FeatureSnapshotIngestDTO;
import com.cyberdoppelganger.exception.ValidationException;
import com.cyberdoppelganger.service.FeatureIngestionService;
import com.cyberdoppelganger.util.PrivacyContentFilter;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class FeatureIngestionController {

    private final FeatureIngestionService featureIngestionService;
    private final PrivacyContentFilter privacyContentFilter;
    private final ObjectMapper objectMapper;
    private final Validator validator;

    public FeatureIngestionController(
            FeatureIngestionService featureIngestionService,
            PrivacyContentFilter privacyContentFilter,
            ObjectMapper objectMapper,
            Validator validator
    ) {
        this.featureIngestionService = featureIngestionService;
        this.privacyContentFilter = privacyContentFilter;
        this.objectMapper = objectMapper;
        this.validator = validator;
    }

    @PostMapping("/agent/features")
    public ResponseEntity<FeatureIngestResponseDTO> ingestFeatures(@RequestBody String rawPayload) {
        if (rawPayload == null || rawPayload.isBlank()) {
            throw new ValidationException("Request body must not be empty");
        }

        // 1. Strict Privacy Filter check on raw JSON string
        privacyContentFilter.validateRawJson(rawPayload);

        // 2. Deserialize to DTO
        FeatureSnapshotIngestDTO dto;
        try {
            dto = objectMapper.readValue(rawPayload, FeatureSnapshotIngestDTO.class);
        } catch (Exception e) {
            throw new ValidationException("Malformed JSON payload: " + e.getMessage());
        }

        // 3. Perform Bean Validation
        Set<ConstraintViolation<FeatureSnapshotIngestDTO>> violations = validator.validate(dto);
        if (!violations.isEmpty()) {
            String errorMsg = violations.stream()
                    .map(v -> v.getPropertyPath() + ": " + v.getMessage())
                    .collect(Collectors.joining(", "));
            throw new ValidationException("Validation failed: " + errorMsg);
        }

        // 4. Ingest and persist
        FeatureIngestResponseDTO response = featureIngestionService.ingestSnapshot(dto, rawPayload);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
