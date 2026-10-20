package com.cyberdoppelganger.service;

import com.cyberdoppelganger.entity.AuditLog;
import com.cyberdoppelganger.repository.AuditLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuditService {

    private static final Logger logger = LoggerFactory.getLogger(AuditService.class);

    private final AuditLogRepository auditLogRepository;

    public AuditService(AuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void record(Long actorUserId, String action, String entityType, String entityId, String outcome, String safeMetadata) {
        try {
            AuditLog log = new AuditLog(actorUserId, action, entityType, entityId, outcome, safeMetadata);
            auditLogRepository.save(log);
        } catch (Exception e) {
            logger.warn("Failed to persist audit log: {}", e.getMessage());
        }
    }
}
