package com.cyberdoppelganger.service;

import com.cyberdoppelganger.dto.*;
import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.entity.VerificationResult;
import com.cyberdoppelganger.exception.ResourceNotFoundException;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.cyberdoppelganger.repository.VerificationResultRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

import java.util.HashMap;
import java.util.Map;

@Service
public class VerificationService {

    private static final Logger log = LoggerFactory.getLogger(VerificationService.class);

    private final VerificationResultRepository verificationRepository;
    private final BehaviouralFeatureSnapshotRepository snapshotRepository;
    private final AuditService auditService;
    private final ObjectMapper objectMapper;
    private final RestClient restClient;
    private final String mlServiceUrl;

    public VerificationService(
            VerificationResultRepository verificationRepository,
            BehaviouralFeatureSnapshotRepository snapshotRepository,
            AuditService auditService,
            ObjectMapper objectMapper,
            @Value("${ml.service.url:http://localhost:5001}") String mlServiceUrl
    ) {
        this.verificationRepository = verificationRepository;
        this.snapshotRepository = snapshotRepository;
        this.auditService = auditService;
        this.objectMapper = objectMapper;
        this.mlServiceUrl = mlServiceUrl.replaceAll("/+$", "");
        this.restClient = RestClient.builder().baseUrl(this.mlServiceUrl).build();
    }

    public ModelStatusResponseDTO getModelStatus() {
        try {
            return restClient.get()
                    .uri("/models/status")
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(ModelStatusResponseDTO.class);
        } catch (RestClientException e) {
            log.warn("ML Verification service is unreachable at {}: {}", mlServiceUrl, e.getMessage());
            ModelStatusResponseDTO fallback = new ModelStatusResponseDTO();
            fallback.setStatus("SERVICE_UNAVAILABLE");
            fallback.setActiveModelType("UNKNOWN");
            Map<String, Object> iso = new HashMap<>();
            iso.put("available", false);
            iso.put("error", "ML service is not running. Start with: python ml/service.py");
            fallback.setIsolationForest(iso);
            return fallback;
        }
    }

    @Transactional(noRollbackFor = {ResponseStatusException.class, RestClientException.class, Exception.class})
    public VerificationResponseDTO processVerification(VerificationRequestDTO request) {
        if (request.getSnapshotId() == null && request.getSnapshot() == null) {
            throw new IllegalArgumentException("Either snapshot_id or a raw snapshot payload must be provided.");
        }

        Long snapshotId = null;
        Long userId = null;
        String deviceId = "unknown-device";
        Map<String, Object> payloadToSend = new HashMap<>();

        if (request.getSnapshotId() != null) {
            snapshotId = request.getSnapshotId();
            BehaviouralFeatureSnapshot snapshot = snapshotRepository.findById(snapshotId)
                    .orElseThrow(() -> new ResourceNotFoundException("Behavioural snapshot not found with ID: " + request.getSnapshotId()));

            userId = snapshot.getUserId();
            deviceId = snapshot.getDeviceId();

            try {
                JsonNode featuresNode = objectMapper.readTree(snapshot.getFeaturePayload());
                payloadToSend.put("features", featuresNode);
                payloadToSend.put("schema_version", snapshot.getSchemaVersion());
                payloadToSend.put("device_id", snapshot.getDeviceId());
            } catch (Exception e) {
                throw new IllegalStateException("Failed to parse stored snapshot feature payload", e);
            }
        } else {
            FeatureSnapshotIngestDTO raw = request.getSnapshot();
            deviceId = raw.getDeviceId();
            payloadToSend.put("features", raw);
            payloadToSend.put("schema_version", raw.getSchemaVersion());
            payloadToSend.put("device_id", raw.getDeviceId());
        }

        if (request.getPreferredModel() != null) {
            payloadToSend.put("preferredModel", request.getPreferredModel());
        }

        // Call ML verification service
        Map<String, Object> mlResult;
        try {
            String jsonPayload = objectMapper.writeValueAsString(payloadToSend);
            byte[] bytes = jsonPayload.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            mlResult = restClient.post()
                    .uri("/verify")
                    .contentType(MediaType.APPLICATION_JSON)
                    .contentLength(bytes.length)
                    .body(bytes)
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException e) {
            log.error("ML Verification service call failed: {}", e.getMessage());
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "ML Verification service unavailable at " + mlServiceUrl + ". Start with: python ml/service.py", e);
        } catch (Exception e) {
            log.error("Error preparing verification payload: {}", e.getMessage());
            throw new IllegalStateException("Failed to prepare verification payload", e);
        }

        if (mlResult == null) {
            throw new IllegalStateException("Empty response received from ML verification service.");
        }

        String status = (String) mlResult.getOrDefault("status", "UNKNOWN");
        String modelType = (String) mlResult.getOrDefault("modelType", "UNKNOWN");
        String modelVersion = (String) mlResult.getOrDefault("modelVersion", "1.0.0");
        String decision = (String) mlResult.getOrDefault("decision", "UNDETERMINED");
        String reason = (String) mlResult.getOrDefault("reason", "");
        Double anomalyScore = mlResult.get("anomalyScore") != null ? ((Number) mlResult.get("anomalyScore")).doubleValue() : null;
        Double rawScore = mlResult.get("rawScore") != null ? ((Number) mlResult.get("rawScore")).doubleValue() : null;
        Double threshold = mlResult.get("threshold") != null ? ((Number) mlResult.get("threshold")).doubleValue() : null;
        Double confidenceScore = mlResult.get("confidenceScore") != null ? ((Number) mlResult.get("confidenceScore")).doubleValue() : null;

        // Persist VerificationResult entity
        VerificationResult entity = new VerificationResult(
                snapshotId,
                userId,
                deviceId,
                modelVersion,
                modelType,
                status,
                anomalyScore,
                rawScore,
                threshold,
                confidenceScore,
                decision,
                reason
        );

        VerificationResult saved = verificationRepository.save(entity);

        auditService.record(
                userId,
                "VERIFICATION_PROCESSED",
                "VerificationResult",
                String.valueOf(saved.getId()),
                status,
                "model=" + modelType + ";decision=" + decision
        );

        return mapToDTO(saved);
    }

    public Page<VerificationResponseDTO> getResults(Pageable pageable) {
        return verificationRepository.findAllByOrderByCreatedAtDesc(pageable).map(this::mapToDTO);
    }

    public VerificationResponseDTO getResultById(Long id) {
        VerificationResult entity = verificationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Verification result not found with ID: " + id));
        return mapToDTO(entity);
    }

    private VerificationResponseDTO mapToDTO(VerificationResult entity) {
        VerificationResponseDTO dto = new VerificationResponseDTO();
        dto.setId(entity.getId());
        dto.setSnapshotId(entity.getSnapshotId());
        dto.setDeviceId(entity.getDeviceId());
        dto.setUserId(entity.getUserId());
        dto.setStatus(entity.getStatus());
        dto.setModelType(entity.getModelType());
        dto.setModelVersion(entity.getModelVersion());
        dto.setAnomalyScore(entity.getAnomalyScore());
        dto.setRawScore(entity.getRawScore());
        dto.setThreshold(entity.getThreshold());
        dto.setConfidenceScore(entity.getConfidenceScore());
        dto.setDecision(entity.getDecision());
        dto.setReason(entity.getReason());
        dto.setCreatedAt(entity.getCreatedAt());
        return dto;
    }
}
