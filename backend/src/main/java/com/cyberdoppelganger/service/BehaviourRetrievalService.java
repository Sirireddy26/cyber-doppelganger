package com.cyberdoppelganger.service;

import com.cyberdoppelganger.dto.FeatureSnapshotResponseDTO;
import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.exception.ResourceNotFoundException;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.Map;

@Service
@Transactional(readOnly = true)
public class BehaviourRetrievalService {

    private final BehaviouralFeatureSnapshotRepository snapshotRepository;
    private final ObjectMapper objectMapper;

    public BehaviourRetrievalService(
            BehaviouralFeatureSnapshotRepository snapshotRepository,
            ObjectMapper objectMapper
    ) {
        this.snapshotRepository = snapshotRepository;
        this.objectMapper = objectMapper;
    }

    public Page<FeatureSnapshotResponseDTO> getSnapshots(int page, int size) {
        int safePage = Math.max(0, page);
        int safeSize = Math.min(100, Math.max(1, size));
        Pageable pageable = PageRequest.of(safePage, safeSize);

        Page<BehaviouralFeatureSnapshot> entityPage = snapshotRepository.findAllByOrderByCapturedAtDesc(pageable);
        return entityPage.map(this::mapToDTO);
    }

    public FeatureSnapshotResponseDTO getSnapshotById(Long id) {
        BehaviouralFeatureSnapshot snapshot = snapshotRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Behavioural snapshot with id " + id + " not found"));
        return mapToDTO(snapshot);
    }

    public Page<FeatureSnapshotResponseDTO> getHistory(String deviceId, Long userId, int page, int size) {
        int safePage = Math.max(0, page);
        int safeSize = Math.min(100, Math.max(1, size));
        Pageable pageable = PageRequest.of(safePage, safeSize);

        Page<BehaviouralFeatureSnapshot> entityPage;
        if (deviceId != null && !deviceId.isBlank()) {
            entityPage = snapshotRepository.findByDeviceIdOrderByCapturedAtDesc(deviceId.trim(), pageable);
        } else if (userId != null) {
            entityPage = snapshotRepository.findByUserIdOrderByCapturedAtDesc(userId, pageable);
        } else {
            entityPage = snapshotRepository.findAllByOrderByCapturedAtDesc(pageable);
        }

        return entityPage.map(this::mapToDTO);
    }

    private FeatureSnapshotResponseDTO mapToDTO(BehaviouralFeatureSnapshot entity) {
        FeatureSnapshotResponseDTO dto = new FeatureSnapshotResponseDTO();
        dto.setId(entity.getId());
        dto.setDeviceId(entity.getDeviceId());
        dto.setUserId(entity.getUserId());
        dto.setSessionId(entity.getSessionId());
        dto.setCapturedAt(entity.getCapturedAt() != null ? entity.getCapturedAt().toString() : null);
        dto.setWindowDurationSeconds(entity.getWindowDurationSeconds());
        dto.setSchemaVersion(entity.getSchemaVersion());
        dto.setReceivedAt(entity.getReceivedAt() != null ? entity.getReceivedAt().toString() : null);

        Map<String, Object> featureMap = Collections.emptyMap();
        if (entity.getFeaturePayload() != null && !entity.getFeaturePayload().isBlank()) {
            try {
                featureMap = objectMapper.readValue(entity.getFeaturePayload(), new TypeReference<Map<String, Object>>() {});
            } catch (Exception ignored) {}
        }
        dto.setFeatures(featureMap);

        return dto;
    }
}
