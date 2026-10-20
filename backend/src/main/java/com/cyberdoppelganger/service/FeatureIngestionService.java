package com.cyberdoppelganger.service;

import com.cyberdoppelganger.dto.*;
import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.entity.Device;
import com.cyberdoppelganger.entity.Session;
import com.cyberdoppelganger.entity.User;
import com.cyberdoppelganger.exception.ValidationException;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.cyberdoppelganger.repository.DeviceRepository;
import com.cyberdoppelganger.repository.SessionRepository;
import com.cyberdoppelganger.repository.UserRepository;
import com.cyberdoppelganger.util.PrivacyContentFilter;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class FeatureIngestionService {

    private static final Logger logger = LoggerFactory.getLogger(FeatureIngestionService.class);

    private final BehaviouralFeatureSnapshotRepository snapshotRepository;
    private final DeviceRepository deviceRepository;
    private final SessionRepository sessionRepository;
    private final UserRepository userRepository;
    private final AuditService auditService;
    private final PrivacyContentFilter privacyContentFilter;
    private final ObjectMapper objectMapper;
    private final VerificationService verificationService;
    private final AdaptationService adaptationService;

    public FeatureIngestionService(
            BehaviouralFeatureSnapshotRepository snapshotRepository,
            DeviceRepository deviceRepository,
            SessionRepository sessionRepository,
            UserRepository userRepository,
            AuditService auditService,
            PrivacyContentFilter privacyContentFilter,
            ObjectMapper objectMapper,
            VerificationService verificationService,
            AdaptationService adaptationService
    ) {
        this.snapshotRepository = snapshotRepository;
        this.deviceRepository = deviceRepository;
        this.sessionRepository = sessionRepository;
        this.userRepository = userRepository;
        this.auditService = auditService;
        this.privacyContentFilter = privacyContentFilter;
        this.objectMapper = objectMapper;
        this.verificationService = verificationService;
        this.adaptationService = adaptationService;
    }

    @Transactional
    public FeatureIngestResponseDTO ingestSnapshot(FeatureSnapshotIngestDTO dto, String rawJsonPayload) {
        // 1. Strict Privacy Filter Validation on raw incoming JSON
        if (rawJsonPayload != null) {
            privacyContentFilter.validateRawJson(rawJsonPayload);
        }

        // 2. Validate timestamp
        Instant capturedAt;
        try {
            capturedAt = Instant.parse(dto.getTimestamp());
        } catch (Exception e) {
            throw new ValidationException("Invalid ISO-8601 timestamp format: " + dto.getTimestamp());
        }

        // 3. Validate window duration
        if (dto.getWindowDurationSeconds() == null || dto.getWindowDurationSeconds() <= 0) {
            throw new ValidationException("window_duration_seconds must be a positive integer greater than 0");
        }

        // 4. Device Management: Find or auto-register device
        String deviceIdentifier = dto.getDeviceId().trim();
        if (deviceIdentifier.isBlank()) {
            throw new ValidationException("device_id must not be blank");
        }

        // 4b. Replay / Duplicate snapshot protection
        if (snapshotRepository.existsByDeviceIdAndCapturedAt(deviceIdentifier, capturedAt)) {
            throw new ValidationException("Duplicate feature snapshot detected for device [" + deviceIdentifier + "] at timestamp [" + capturedAt + "]. Replay rejected.");
        }

        Device device = deviceRepository.findByDeviceIdentifier(deviceIdentifier)
                .orElseGet(() -> {
                    logger.info("Registering new device with identifier: [{}]", deviceIdentifier);
                    Device newDev = new Device(deviceIdentifier, null, "Desktop Agent Device");
                    return deviceRepository.save(newDev);
                });
        device.setLastSeenAt(Instant.now());
        deviceRepository.save(device);

        // 5. User association if valid user_id passed
        Long resolvedUserId = null;
        if (dto.getUserId() != null && !dto.getUserId().isBlank() && !"default-user".equalsIgnoreCase(dto.getUserId().trim())) {
            try {
                Long uid = Long.parseLong(dto.getUserId().trim());
                Optional<User> uOpt = userRepository.findById(uid);
                if (uOpt.isPresent()) {
                    resolvedUserId = uid;
                    if (device.getUser() == null) {
                        device.setUser(uOpt.get());
                        deviceRepository.save(device);
                    }
                }
            } catch (NumberFormatException ignored) {
                // Non-numeric username search
                Optional<User> uOpt = userRepository.findByUsername(dto.getUserId().trim());
                if (uOpt.isPresent()) {
                    resolvedUserId = uOpt.get().getId();
                }
            }
        }

        // 6. Session lookup or association
        Long resolvedSessionId = null;
        Optional<Session> activeSession = sessionRepository.findTopByDeviceIdAndStatusOrderByStartedAtDesc(
                device.getId(), "ACTIVE");
        if (activeSession.isPresent()) {
            resolvedSessionId = activeSession.get().getId();
        }

        // 7. Serialize feature payload cleanly
        Map<String, Object> featureMap = new LinkedHashMap<>();
        if (dto.getKeyboard() != null) featureMap.put("keyboard", dto.getKeyboard());
        if (dto.getMouse() != null) featureMap.put("mouse", dto.getMouse());
        if (dto.getSession() != null) featureMap.put("session", dto.getSession());
        if (dto.getApplication() != null) featureMap.put("application", dto.getApplication());

        String serializedPayload;
        try {
            serializedPayload = objectMapper.writeValueAsString(featureMap);
        } catch (Exception e) {
            throw new ValidationException("Failed to serialize feature payload: " + e.getMessage());
        }

        // 8. Persist BehaviouralFeatureSnapshot
        BehaviouralFeatureSnapshot snapshot = new BehaviouralFeatureSnapshot(
                resolvedUserId,
                deviceIdentifier,
                resolvedSessionId,
                capturedAt,
                dto.getWindowDurationSeconds(),
                dto.getSchemaVersion(),
                serializedPayload
        );
        BehaviouralFeatureSnapshot saved = snapshotRepository.save(snapshot);

        // 9. Record safe audit log
        auditService.record(
                resolvedUserId,
                "FEATURE_SNAPSHOT_INGESTED",
                "SNAPSHOT",
                saved.getId().toString(),
                "SUCCESS",
                "{\"device_id\":\"" + deviceIdentifier + "\",\"window_seconds\":" + dto.getWindowDurationSeconds() + "}"
        );

        logger.info("Successfully ingested behavioural snapshot #{} for device [{}] (window: {}s)",
                saved.getId(), deviceIdentifier, dto.getWindowDurationSeconds());

        // 10. Automatic Phase 6 Pipeline: Trigger ML Verification & Adaptation if ML service is online
        VerificationResponseDTO verifDto = null;
        AdaptationResponseDTO adaptDto = null;
        String processingErr = null;

        try {
            VerificationRequestDTO vReq = new VerificationRequestDTO();
            vReq.setSnapshotId(saved.getId());
            vReq.setPreferredModel("ISOLATION_FOREST");
            verifDto = verificationService.processVerification(vReq);

            AdaptationRequestDTO aReq = new AdaptationRequestDTO();
            aReq.setSnapshotId(saved.getId());
            aReq.setVerificationResultId(verifDto.getId());
            aReq.setDeviceId(deviceIdentifier);
            if (resolvedUserId != null) {
                aReq.setUserId(String.valueOf(resolvedUserId));
            }
            adaptDto = adaptationService.processAdaptation(aReq);
        } catch (Exception e) {
            logger.warn("Automatic downstream ML verification/adaptation deferred for snapshot #{}: {}",
                    saved.getId(), e.getMessage());
            processingErr = e.getMessage();
        }

        FeatureIngestResponseDTO response = new FeatureIngestResponseDTO(
                "accepted",
                saved.getId().toString(),
                saved.getReceivedAt().toString(),
                verifDto,
                adaptDto
        );
        response.setProcessingError(processingErr);

        return response;
    }
}

