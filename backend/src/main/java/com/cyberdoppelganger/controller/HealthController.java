package com.cyberdoppelganger.controller;

import com.cyberdoppelganger.dto.AdaptationStatusDTO;
import com.cyberdoppelganger.dto.HealthResponseDTO;
import com.cyberdoppelganger.dto.ModelStatusResponseDTO;
import com.cyberdoppelganger.dto.SystemDiagnosticsDTO;
import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.entity.ProfileVersion;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.cyberdoppelganger.repository.ProfileVersionRepository;
import com.cyberdoppelganger.service.AdaptationService;
import com.cyberdoppelganger.service.DatabaseHealthService;
import com.cyberdoppelganger.service.VerificationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api")
public class HealthController {

    private final DatabaseHealthService databaseHealthService;
    private final VerificationService verificationService;
    private final AdaptationService adaptationService;
    private final ProfileVersionRepository profileVersionRepository;
    private final BehaviouralFeatureSnapshotRepository snapshotRepository;

    public HealthController(
            DatabaseHealthService databaseHealthService,
            VerificationService verificationService,
            AdaptationService adaptationService,
            ProfileVersionRepository profileVersionRepository,
            BehaviouralFeatureSnapshotRepository snapshotRepository
    ) {
        this.databaseHealthService = databaseHealthService;
        this.verificationService = verificationService;
        this.adaptationService = adaptationService;
        this.profileVersionRepository = profileVersionRepository;
        this.snapshotRepository = snapshotRepository;
    }

    @GetMapping("/health")
    public ResponseEntity<HealthResponseDTO> getHealth() {
        Map<String, String> dbHealth = databaseHealthService.checkDatabaseHealth();
        String dbStatus = dbHealth.getOrDefault("database", "DOWN");
        String dbType = dbHealth.getOrDefault("database_type", "UNKNOWN");

        HealthResponseDTO response = new HealthResponseDTO(
                "UP",
                "cyber-doppelganger-backend",
                dbStatus,
                dbType
        );
        return ResponseEntity.ok(response);
    }

    @GetMapping({"/health/diagnostics", "/system/diagnostics"})
    public ResponseEntity<SystemDiagnosticsDTO> getDiagnostics() {
        SystemDiagnosticsDTO diagnostics = new SystemDiagnosticsDTO();

        // 1. Backend
        Map<String, Object> backend = new LinkedHashMap<>();
        backend.put("status", "UP");
        backend.put("service", "cyber-doppelganger-backend");
        backend.put("version", "1.0.0");
        diagnostics.setBackend(backend);

        // 2. Database
        Map<String, String> dbHealth = databaseHealthService.checkDatabaseHealth();
        String dbStatus = dbHealth.getOrDefault("database", "DOWN");
        String dbType = dbHealth.getOrDefault("database_type", "UNKNOWN");
        boolean dbUp = "UP".equalsIgnoreCase(dbStatus);

        Map<String, Object> database = new LinkedHashMap<>();
        database.put("status", dbStatus);
        database.put("database_type", dbType);
        database.put("connected", dbUp);
        diagnostics.setDatabase(database);

        // 3. ML Service & Model Readiness
        ModelStatusResponseDTO modelStatus = verificationService.getModelStatus();
        boolean mlUp = modelStatus != null && !"SERVICE_UNAVAILABLE".equalsIgnoreCase(modelStatus.getStatus());

        Map<String, Object> mlService = new LinkedHashMap<>();
        mlService.put("status", mlUp ? "UP" : "DOWN");
        mlService.put("service_status", modelStatus != null ? modelStatus.getStatus() : "UNKNOWN");
        mlService.put("active_model_type", modelStatus != null ? modelStatus.getActiveModelType() : "UNKNOWN");
        diagnostics.setMlService(mlService);

        boolean modelReady = false;
        String modelVersion = "UNKNOWN";
        if (mlUp && modelStatus != null && modelStatus.getIsolationForest() != null) {
            Object avail = modelStatus.getIsolationForest().get("available");
            modelReady = Boolean.TRUE.equals(avail);
            Object ver = modelStatus.getIsolationForest().get("version");
            if (ver != null) {
                modelVersion = ver.toString();
            }
        }

        Map<String, Object> modelReadiness = new LinkedHashMap<>();
        modelReadiness.put("ready", modelReady);
        modelReadiness.put("status", modelReady ? "READY" : "NOT_READY");
        modelReadiness.put("model_type", modelStatus != null ? modelStatus.getActiveModelType() : "UNKNOWN");
        modelReadiness.put("model_version", modelVersion);
        diagnostics.setModelReadiness(modelReadiness);

        // 4. Adaptation Engine Readiness
        AdaptationStatusDTO adaptationStatus = adaptationService.getStatus();
        boolean adaptOnline = adaptationStatus != null && !"SERVICE_UNAVAILABLE".equalsIgnoreCase(adaptationStatus.getEngineStatus());
        boolean isFrozen = adaptationStatus != null && Boolean.TRUE.equals(adaptationStatus.getIsFrozen());
        boolean adaptationPermitted = adaptOnline && !isFrozen;

        Map<String, Object> adaptationEngine = new LinkedHashMap<>();
        adaptationEngine.put("ready", adaptOnline);
        adaptationEngine.put("engine_status", adaptationStatus != null ? adaptationStatus.getEngineStatus() : "UNKNOWN");
        adaptationEngine.put("is_frozen", isFrozen);
        adaptationEngine.put("adaptation_permitted", adaptationPermitted);
        adaptationEngine.put("suspicious_streak", adaptationStatus != null ? adaptationStatus.getSuspiciousStreak() : 0);
        diagnostics.setAdaptationEngine(adaptationEngine);

        // 5. Trusted Profile Readiness (Synchronized with ML Authoritative Engine)
        long versionCount = 0;
        Optional<ProfileVersion> activeProfileOpt = Optional.empty();
        try {
            versionCount = profileVersionRepository.count();
            activeProfileOpt = profileVersionRepository.findTop10ByOrderByCreatedAtDesc().stream()
                    .filter(pv -> "ACTIVE".equalsIgnoreCase(pv.getStatus()))
                    .findFirst();
        } catch (Exception ignored) {
        }

        // If DB has no active profile version record but ML service reports a valid active baseline version (e.g. v1.0.0),
        // automatically seed and synchronize the baseline profile to ensure consistency between ML and DB.
        String activeVersion = activeProfileOpt.map(ProfileVersion::getVersionTag).orElse(null);
        String deviceId = activeProfileOpt.map(ProfileVersion::getDeviceId).orElse("desktop-workstation");
        if (activeVersion == null && adaptationStatus != null && adaptationStatus.getActiveVersion() != null
                && !"NONE".equalsIgnoreCase(adaptationStatus.getActiveVersion())
                && !"UNKNOWN".equalsIgnoreCase(adaptationStatus.getActiveVersion())) {
            activeVersion = adaptationStatus.getActiveVersion();
            try {
                ProfileVersion baselineProfile = ProfileVersion.builder()
                        .deviceId(deviceId)
                        .versionTag(activeVersion)
                        .parentVersionTag(null)
                        .sampleCount(adaptationStatus.getSampleCount() != null ? adaptationStatus.getSampleCount() : 435)
                        .status("ACTIVE")
                        .reason("Baseline profile synchronized from ML engine")
                        .activatedAt(java.time.Instant.now())
                        .createdAt(java.time.Instant.now())
                        .build();
                profileVersionRepository.save(baselineProfile);
                versionCount = Math.max(1, versionCount + 1);
            } catch (Exception ignored) {
            }
        }

        boolean profileReady = activeVersion != null && !"NONE".equalsIgnoreCase(activeVersion) && !"UNKNOWN".equalsIgnoreCase(activeVersion);
        String profileStatus;
        if (!adaptOnline) {
            profileStatus = "SERVICE_UNAVAILABLE";
        } else if (!profileReady) {
            profileStatus = "NO_PROFILE";
        } else if (isFrozen) {
            profileStatus = "PROFILE_FROZEN";
        } else {
            profileStatus = "PROFILE_ACTIVE";
        }

        Map<String, Object> trustedProfile = new LinkedHashMap<>();
        trustedProfile.put("ready", profileReady);
        trustedProfile.put("status", profileStatus);
        trustedProfile.put("total_versions", versionCount > 0 ? versionCount : (profileReady ? 1 : 0));
        trustedProfile.put("active_version", profileReady ? activeVersion : "NONE");
        trustedProfile.put("device_id", deviceId);
        diagnostics.setTrustedProfile(trustedProfile);

        // 6. Agent Telemetry
        Optional<BehaviouralFeatureSnapshot> latestSnapshot = Optional.empty();
        try {
            latestSnapshot = snapshotRepository.findTopByOrderByCapturedAtDesc();
        } catch (Exception ignored) {
        }

        Map<String, Object> agentTelemetry = new LinkedHashMap<>();
        agentTelemetry.put("status", latestSnapshot.isPresent() ? "ACTIVE" : "NO_DATA");
        agentTelemetry.put("last_captured_at", latestSnapshot.map(s -> s.getCapturedAt().toString()).orElse(null));
        agentTelemetry.put("last_device_id", latestSnapshot.map(BehaviouralFeatureSnapshot::getDeviceId).orElse(null));
        diagnostics.setAgentTelemetry(agentTelemetry);

        // 7. System Summary (Separating Running, Model Loaded, Profile Initialized, Verification Ready, Adaptation Ready)
        boolean verificationReady = dbUp && mlUp && modelReady;
        boolean adaptationReady = verificationReady && profileReady && adaptationPermitted;

        Map<String, Object> systemSummary = new LinkedHashMap<>();
        systemSummary.put("verification_ready", verificationReady);
        systemSummary.put("adaptation_ready", adaptationReady);
        systemSummary.put("all_systems_operational", verificationReady && adaptationReady && latestSnapshot.isPresent());
        diagnostics.setSystemSummary(systemSummary);

        return ResponseEntity.ok(diagnostics);
    }
}
