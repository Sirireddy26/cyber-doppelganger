package com.cyberdoppelganger.service;

import com.cyberdoppelganger.dto.*;
import com.cyberdoppelganger.entity.*;
import com.cyberdoppelganger.repository.*;
import com.fasterxml.jackson.core.JsonProcessingException;
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

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class AdaptationService {

    private static final Logger log = LoggerFactory.getLogger(AdaptationService.class);

    private final AdaptationEventRepository adaptationEventRepository;
    private final ProfileVersionRepository profileVersionRepository;
    private final ProfileFreezeRecordRepository profileFreezeRecordRepository;
    private final BehaviouralFeatureSnapshotRepository snapshotRepository;
    private final VerificationResultRepository verificationRepository;
    private final AuditService auditService;
    private final ObjectMapper objectMapper;
    private final RestClient restClient;
    private final String mlServiceUrl;
    private final Object adaptationLock = new Object();

    public AdaptationService(
            AdaptationEventRepository adaptationEventRepository,
            ProfileVersionRepository profileVersionRepository,
            ProfileFreezeRecordRepository profileFreezeRecordRepository,
            BehaviouralFeatureSnapshotRepository snapshotRepository,
            VerificationResultRepository verificationRepository,
            AuditService auditService,
            ObjectMapper objectMapper,
            @Value("${ml.service.url:http://localhost:5001}") String mlServiceUrl
    ) {
        this.adaptationEventRepository = adaptationEventRepository;
        this.profileVersionRepository = profileVersionRepository;
        this.profileFreezeRecordRepository = profileFreezeRecordRepository;
        this.snapshotRepository = snapshotRepository;
        this.verificationRepository = verificationRepository;
        this.auditService = auditService;
        this.objectMapper = objectMapper;
        this.mlServiceUrl = mlServiceUrl.replaceAll("/+$", "");
        this.restClient = RestClient.builder().baseUrl(this.mlServiceUrl).build();
    }

    public AdaptationStatusDTO getStatus() {
        try {
            return restClient.get()
                    .uri("/adaptation/status")
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(AdaptationStatusDTO.class);
        } catch (RestClientException e) {
            log.warn("ML Adaptation service is unreachable at {}: {}", mlServiceUrl, e.getMessage());
            AdaptationStatusDTO fallback = new AdaptationStatusDTO();
            fallback.setEngineStatus("SERVICE_UNAVAILABLE");
            fallback.setActiveVersion("UNKNOWN");
            fallback.setIsFrozen(false);
            fallback.setSuspiciousStreak(0);
            fallback.setSampleCount(0);
            Map<String, Object> errMap = new HashMap<>();
            errMap.put("error", "ML service offline. Start with: python ml/service.py");
            fallback.setCandidateBuffer(errMap);
            return fallback;
        }
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getCandidateSummary() {
        try {
            return restClient.get()
                    .uri("/adaptation/candidates")
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException e) {
            log.warn("ML service offline for candidate summary: {}", e.getMessage());
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("current_size", 0);
            fallback.put("error", "Service unavailable");
            return fallback;
        }
    }

    @Transactional(noRollbackFor = {ResponseStatusException.class, RestClientException.class, Exception.class})
    public AdaptationResponseDTO processAdaptation(AdaptationRequestDTO request) {
        synchronized (adaptationLock) {
            return doProcessAdaptation(request);
        }
    }

    private AdaptationResponseDTO doProcessAdaptation(AdaptationRequestDTO request) {
        BehaviouralFeatureSnapshot snapshot = null;
        VerificationResult verificationResult = null;
        Map<String, Object> payloadForML = new HashMap<>();

        if (request.getSnapshotId() != null) {
            snapshot = snapshotRepository.findById(request.getSnapshotId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                            "Feature snapshot #" + request.getSnapshotId() + " not found."));

            payloadForML.put("device_id", snapshot.getDeviceId());
            if (snapshot.getUserId() != null) {
                payloadForML.put("user_id", String.valueOf(snapshot.getUserId()));
            }

            try {
                Map<String, Object> parsedFeatures = objectMapper.readValue(snapshot.getFeaturePayload(), Map.class);
                payloadForML.put("features", parsedFeatures);
            } catch (JsonProcessingException e) {
                throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to parse snapshot feature JSON");
            }
        } else if (request.getFeatures() != null) {
            payloadForML.put("features", request.getFeatures());
            payloadForML.put("device_id", request.getDeviceId() != null ? request.getDeviceId() : "default-device");
            if (request.getUserId() != null) {
                payloadForML.put("user_id", request.getUserId());
            }
        } else {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Must provide either snapshot_id or features payload.");
        }

        if (request.getVerificationResultId() != null) {
            verificationResult = verificationRepository.findById(request.getVerificationResultId()).orElse(null);
            if (verificationResult != null) {
                Map<String, Object> verifMap = new HashMap<>();
                verifMap.put("status", verificationResult.getStatus());
                verifMap.put("rawScore", verificationResult.getRawScore());
                verifMap.put("threshold", verificationResult.getThreshold());
                verifMap.put("anomalyScore", verificationResult.getAnomalyScore());
                verifMap.put("confidenceScore", verificationResult.getConfidenceScore());
                payloadForML.put("verification_result", verifMap);
            }
        }

        // Call ML microservice
        Map<String, Object> mlResponse;
        try {
            byte[] bodyBytes = objectMapper.writeValueAsBytes(payloadForML);
            mlResponse = restClient.post()
                    .uri("/adaptation/evaluate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(bodyBytes)
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException rce) {
            log.error("ML adaptation service unreachable at {}: {}", mlServiceUrl, rce.getMessage());
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    "Adaptation ML microservice is offline at " + mlServiceUrl);
        } catch (JsonProcessingException jpe) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "JSON serialization error: " + jpe.getMessage());
        }

        if (mlResponse == null) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Empty response from ML adaptation engine.");
        }

        // Parse and persist AdaptationEvent
        String decisionState = (String) mlResponse.getOrDefault("decision_state", "INSUFFICIENT_EVIDENCE");
        String priorVersion = (String) mlResponse.getOrDefault("prior_profile_version", "v1.0.0");
        String newVersion = (String) mlResponse.get("new_profile_version");
        Double drift = mlResponse.get("drift_magnitude") != null ? ((Number) mlResponse.get("drift_magnitude")).doubleValue() : null;
        Double velocity = mlResponse.get("velocity") != null ? ((Number) mlResponse.get("velocity")).doubleValue() : null;
        Double stability = mlResponse.get("stability_score") != null ? ((Number) mlResponse.get("stability_score")).doubleValue() : null;
        Integer candCount = mlResponse.get("candidate_count") != null ? ((Number) mlResponse.get("candidate_count")).intValue() : 0;
        Integer suspStreak = mlResponse.get("suspicious_streak") != null ? ((Number) mlResponse.get("suspicious_streak")).intValue() : 0;
        Boolean isFrozen = Boolean.TRUE.equals(mlResponse.get("is_profile_frozen"));
        String reason = (String) mlResponse.getOrDefault("decision_reason", "Adaptation evaluated.");
        String policyVer = (String) mlResponse.getOrDefault("policy_version", "1.0.0");

        String deviceId = snapshot != null ? snapshot.getDeviceId() : (String) payloadForML.get("device_id");
        Long userId = snapshot != null ? snapshot.getUserId() : null;

        AdaptationEvent event = AdaptationEvent.builder()
                .snapshotId(snapshot != null ? snapshot.getId() : null)
                .verificationResultId(verificationResult != null ? verificationResult.getId() : null)
                .userId(userId)
                .deviceId(deviceId != null ? deviceId : "desktop-workstation")
                .decisionState(decisionState)
                .priorProfileVersion(priorVersion)
                .newProfileVersion(newVersion)
                .driftMagnitude(drift)
                .velocity(velocity)
                .stabilityScore(stability)
                .candidateCount(candCount)
                .suspiciousStreak(suspStreak)
                .isProfileFrozen(isFrozen)
                .decisionReason(reason)
                .policyVersion(policyVer)
                .createdAt(Instant.now())
                .build();

        AdaptationEvent savedEvent = adaptationEventRepository.save(event);

        // If a new profile version was activated, record ProfileVersion entity
        if ("SAFE_ADAPTATION".equals(decisionState) && newVersion != null) {
            ProfileVersion newProfile = ProfileVersion.builder()
                    .userId(userId)
                    .deviceId(deviceId != null ? deviceId : "desktop-workstation")
                    .versionTag(newVersion)
                    .parentVersionTag(priorVersion)
                    .sampleCount(candCount)
                    .status("ACTIVE")
                    .reason(reason)
                    .activatedAt(Instant.now())
                    .createdAt(Instant.now())
                    .build();
            profileVersionRepository.save(newProfile);
        }

        // If profile was frozen, record in ProfileFreezeRecord
        if (isFrozen) {
            ProfileFreezeRecord freezeRecord = ProfileFreezeRecord.builder()
                    .userId(userId)
                    .deviceId(deviceId != null ? deviceId : "desktop-workstation")
                    .profileVersion(priorVersion)
                    .isFrozen(true)
                    .freezeReason(reason)
                    .frozenAt(Instant.now())
                    .build();
            profileFreezeRecordRepository.save(freezeRecord);
        }

        // Audit logging
        auditService.record(
                userId,
                "ADAPTATION_" + decisionState,
                "AdaptationEvent",
                String.valueOf(savedEvent.getId()),
                decisionState,
                "reason=" + reason + ";streak=" + suspStreak
        );

        return mapToDTO(savedEvent);
    }

    @Transactional
    public Map<String, Object> freezeProfile(AdaptationActionDTO action) {
        if (action == null || action.getAuthorizedBy() == null || action.getAuthorizedBy().trim().isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,
                    "Security authorization required: 'authorized_by' identity must be provided for profile freeze.");
        }
        try {
            byte[] bodyBytes = objectMapper.writeValueAsBytes(action);
            Map<String, Object> resp = restClient.post()
                    .uri("/adaptation/freeze")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(bodyBytes)
                    .retrieve()
                    .body(Map.class);

            ProfileFreezeRecord record = ProfileFreezeRecord.builder()
                    .deviceId("desktop-workstation")
                    .profileVersion(resp != null ? (String) resp.getOrDefault("active_version", "v1.0.0") : "v1.0.0")
                    .isFrozen(true)
                    .freezeReason(action.getReason() != null ? action.getReason() : "Manual freeze")
                    .frozenAt(Instant.now())
                    .build();
            ProfileFreezeRecord savedRecord = profileFreezeRecordRepository.save(record);

            auditService.record(null, "PROFILE_FREEZE", "ProfileFreezeRecord",
                    String.valueOf(savedRecord.getId()), "FROZEN", "reason=" + action.getReason() + ";authorized_by=" + action.getAuthorizedBy());
            return resp;
        } catch (org.springframework.web.client.HttpStatusCodeException hsce) {
            throw new ResponseStatusException(hsce.getStatusCode(), hsce.getResponseBodyAsString());
        } catch (ResponseStatusException rse) {
            throw rse;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Failed to freeze profile: " + e.getMessage());
        }
    }

    @Transactional
    public Map<String, Object> unfreezeProfile(AdaptationActionDTO action) {
        if (action == null || action.getAuthorizedBy() == null || action.getAuthorizedBy().trim().isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,
                    "Security authorization required: 'authorized_by' identity must be provided for profile unfreeze recovery.");
        }
        try {
            byte[] bodyBytes = objectMapper.writeValueAsBytes(action);
            Map<String, Object> resp = restClient.post()
                    .uri("/adaptation/unfreeze")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(bodyBytes)
                    .retrieve()
                    .body(Map.class);

            Optional<ProfileFreezeRecord> latest = profileFreezeRecordRepository.findFirstByDeviceIdAndIsFrozenTrueOrderByFrozenAtDesc("desktop-workstation");
            latest.ifPresent(rec -> {
                rec.setIsFrozen(false);
                rec.setUnfrozenAt(Instant.now());
                rec.setUnfreezeReason(action.getReason());
                rec.setUnfrozenBy(action.getAuthorizedBy());
                profileFreezeRecordRepository.save(rec);
            });

            auditService.record(null, "PROFILE_UNFREEZE", "ProfileFreezeRecord",
                    "0", "UNFROZEN", "reason=" + action.getReason() + ";authorized_by=" + action.getAuthorizedBy());
            return resp;
        } catch (org.springframework.web.client.HttpStatusCodeException hsce) {
            throw new ResponseStatusException(hsce.getStatusCode(), hsce.getResponseBodyAsString());
        } catch (ResponseStatusException rse) {
            throw rse;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Failed to unfreeze profile: " + e.getMessage());
        }
    }

    @Transactional
    public Map<String, Object> rollbackProfile(AdaptationActionDTO action) {
        if (action == null || action.getTargetVersion() == null || action.getTargetVersion().trim().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "target_version is required for rollback.");
        }
        if (action.getAuthorizedBy() == null || action.getAuthorizedBy().trim().isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,
                    "Security authorization required: 'authorized_by' identity must be provided for profile rollback.");
        }
        try {
            byte[] bodyBytes = objectMapper.writeValueAsBytes(action);
            Map<String, Object> resp = restClient.post()
                    .uri("/adaptation/rollback")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(bodyBytes)
                    .retrieve()
                    .body(Map.class);

            Optional<ProfileFreezeRecord> latest = profileFreezeRecordRepository.findFirstByDeviceIdAndIsFrozenTrueOrderByFrozenAtDesc("desktop-workstation");
            latest.ifPresent(rec -> {
                rec.setIsFrozen(false);
                rec.setUnfrozenAt(Instant.now());
                rec.setUnfreezeReason("Rollback to " + action.getTargetVersion());
                rec.setUnfrozenBy(action.getAuthorizedBy());
                profileFreezeRecordRepository.save(rec);
            });

            auditService.record(null, "PROFILE_ROLLBACK", "ProfileVersion",
                    "0", "ROLLBACK", "target=" + action.getTargetVersion() + ";authorized_by=" + action.getAuthorizedBy());
            return resp;
        } catch (org.springframework.web.client.HttpStatusCodeException hsce) {
            throw new ResponseStatusException(hsce.getStatusCode(), hsce.getResponseBodyAsString());
        } catch (org.springframework.web.client.RestClientResponseException rcre) {
            throw new ResponseStatusException(rcre.getStatusCode(), rcre.getResponseBodyAsString());
        } catch (ResponseStatusException rse) {
            throw rse;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Failed to rollback profile: " + e.getMessage());
        }
    }

    public Page<AdaptationResponseDTO> getAdaptationHistory(Pageable pageable) {
        return adaptationEventRepository.findAllByOrderByCreatedAtDesc(pageable).map(this::mapToDTO);
    }

    private AdaptationResponseDTO mapToDTO(AdaptationEvent event) {
        return AdaptationResponseDTO.builder()
                .id(event.getId())
                .snapshotId(event.getSnapshotId())
                .verificationResultId(event.getVerificationResultId())
                .deviceId(event.getDeviceId())
                .decisionState(event.getDecisionState())
                .priorProfileVersion(event.getPriorProfileVersion())
                .newProfileVersion(event.getNewProfileVersion())
                .driftMagnitude(event.getDriftMagnitude())
                .velocity(event.getVelocity())
                .stabilityScore(event.getStabilityScore())
                .candidateCount(event.getCandidateCount())
                .suspiciousStreak(event.getSuspiciousStreak())
                .isProfileFrozen(event.getIsProfileFrozen())
                .decisionReason(event.getDecisionReason())
                .policyVersion(event.getPolicyVersion())
                .createdAt(event.getCreatedAt())
                .build();
    }
}
