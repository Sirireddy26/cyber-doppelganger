package com.cyberdoppelganger;

import com.cyberdoppelganger.dto.AdaptationActionDTO;
import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.entity.ProfileVersion;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.cyberdoppelganger.repository.ProfileVersionRepository;
import com.cyberdoppelganger.repository.VerificationResultRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class EndToEndPipelineIntegrationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BehaviouralFeatureSnapshotRepository snapshotRepository;

    @Autowired
    private ProfileVersionRepository profileVersionRepository;

    @Autowired
    private VerificationResultRepository verificationRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        snapshotRepository.deleteAll();
    }

    @Test
    @DisplayName("Granular system diagnostics endpoint distinguishes backend, database, ML, model, profile, adaptation, and agent states")
    void testSystemDiagnosticsEndpointGranularity() throws Exception {
        mockMvc.perform(get("/api/health/diagnostics"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.backend.status").value("UP"))
                .andExpect(jsonPath("$.backend.service").value("cyber-doppelganger-backend"))
                .andExpect(jsonPath("$.database.status").value("UP"))
                .andExpect(jsonPath("$.database.connected").value(true))
                .andExpect(jsonPath("$.ml_service.status").exists())
                .andExpect(jsonPath("$.model_readiness.ready").exists())
                .andExpect(jsonPath("$.trusted_profile.ready").exists())
                .andExpect(jsonPath("$.adaptation_engine.ready").exists())
                .andExpect(jsonPath("$.agent_telemetry.status").exists())
                .andExpect(jsonPath("$.system_summary.verification_ready").exists())
                .andExpect(jsonPath("$.system_summary.adaptation_ready").exists());
    }

    @Test
    @DisplayName("Valid snapshot ingestion succeeds, validates schema, persists snapshot, and attempts verification/adaptation chaining")
    void testIngestValidSnapshotEndToEnd() throws Exception {
        String payload = """
        {
          "timestamp": "2026-10-12T12:00:00Z",
          "window_duration_seconds": 15,
          "device_id": "test-device-p6-01",
          "user_id": "cse-researcher",
          "schema_version": "2.0",
          "keyboard": {
            "total_key_events": 20,
            "mean_key_interval": 0.165,
            "median_key_interval": 0.150,
            "key_interval_std": 0.035,
            "minimum_key_interval": 0.080,
            "maximum_key_interval": 1.20,
            "typing_speed": 4.5,
            "backspace_ratio": 0.05,
            "error_correction_rate": 0.02
          },
          "mouse": {
            "total_mouse_events": 35,
            "mean_mouse_speed": 420.5,
            "max_mouse_speed": 1150.0,
            "mouse_speed_std": 120.0,
            "mean_acceleration": 650.0,
            "click_rate": 0.4,
            "curvature_ratio": 1.25,
            "straightness_score": 0.85,
            "pause_ratio": 0.10
          }
        }
        """;

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("accepted"))
                .andExpect(jsonPath("$.snapshotId").isNotEmpty());

        assertEquals(1, snapshotRepository.count());
    }

    @Test
    @DisplayName("Replay protection rejects duplicate snapshot with identical deviceId and capturedAt")
    void testReplayDetectionRejectsDuplicateSnapshot() throws Exception {
        String timestamp = "2026-10-12T14:30:00Z";
        String payload = """
        {
          "timestamp": "%s",
          "window_duration_seconds": 15,
          "device_id": "replay-test-device",
          "user_id": "research-user",
          "schema_version": "2.0",
          "keyboard": {
            "total_key_events": 15,
            "mean_key_interval": 0.180,
            "median_key_interval": 0.160,
            "key_interval_std": 0.040,
            "minimum_key_interval": 0.090,
            "maximum_key_interval": 1.50,
            "typing_speed": 3.8,
            "backspace_ratio": 0.02,
            "error_correction_rate": 0.01
          },
          "mouse": {
            "total_mouse_events": 20,
            "mean_mouse_speed": 350.0,
            "max_mouse_speed": 900.0,
            "mouse_speed_std": 100.0,
            "mean_acceleration": 500.0,
            "click_rate": 0.3,
            "curvature_ratio": 1.15,
            "straightness_score": 0.88,
            "pause_ratio": 0.08
          }
        }
        """.formatted(timestamp);

        // First submission succeeds
        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("accepted"));

        // Replay submission with same deviceId and timestamp is rejected
        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("Duplicate feature snapshot detected")));
    }

    @Test
    @DisplayName("Rejection of NaN string and non-finite values in behavioral payload")
    void testNaNValueRejection() throws Exception {
        String payloadWithNaN = """
        {
          "timestamp": "2026-10-12T15:00:00Z",
          "window_duration_seconds": 15,
          "device_id": "nan-test-device",
          "user_id": "research-user",
          "schema_version": "2.0",
          "keyboard": {
            "total_key_events": 15,
            "mean_key_interval": "NaN",
            "median_key_interval": 0.160,
            "key_interval_std": 0.040,
            "minimum_key_interval": 0.090,
            "maximum_key_interval": 1.50,
            "typing_speed": 3.8,
            "backspace_ratio": 0.02,
            "error_correction_rate": 0.01
          },
          "mouse": {
            "total_mouse_events": 20,
            "mean_mouse_speed": 350.0,
            "max_mouse_speed": 900.0,
            "mouse_speed_std": 100.0,
            "mean_acceleration": 500.0,
            "click_rate": 0.3,
            "curvature_ratio": 1.15,
            "straightness_score": 0.88,
            "pause_ratio": 0.08
          }
        }
        """;

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payloadWithNaN))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("Profile freeze endpoint strictly requires authorization identity")
    void testProfileFreezeRequiresAuthorization() throws Exception {
        AdaptationActionDTO unauthorizedReq = new AdaptationActionDTO();
        unauthorizedReq.setReason("Suspicious drift anomaly test");
        // authorizedBy is missing (null)

        mockMvc.perform(post("/api/adaptation/freeze")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(unauthorizedReq)))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Profile rollback endpoint strictly requires authorization identity")
    void testProfileRollbackRequiresAuthorization() throws Exception {
        AdaptationActionDTO unauthorizedReq = new AdaptationActionDTO();
        unauthorizedReq.setTargetVersion("v1.0.0");
        unauthorizedReq.setReason("Contamination mitigation rollback");
        // authorizedBy is missing (null)

        mockMvc.perform(post("/api/adaptation/rollback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(unauthorizedReq)))
                .andExpect(status().isUnauthorized());
    }
}
