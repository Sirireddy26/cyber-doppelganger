package com.cyberdoppelganger;

import com.cyberdoppelganger.dto.AdaptationActionDTO;
import com.cyberdoppelganger.repository.AdaptationEventRepository;
import com.cyberdoppelganger.repository.ProfileFreezeRecordRepository;
import com.cyberdoppelganger.repository.ProfileVersionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("dev")
public class AdaptationControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private AdaptationEventRepository adaptationEventRepository;

    @Autowired
    private ProfileVersionRepository profileVersionRepository;

    @Autowired
    private ProfileFreezeRecordRepository profileFreezeRecordRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        adaptationEventRepository.deleteAll();
        profileFreezeRecordRepository.deleteAll();
    }

    @Test
    void testGetAdaptationStatusReturnsValidResponse() throws Exception {
        mockMvc.perform(get("/api/adaptation/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.engine_status", notNullValue()));
    }

    @Test
    void testGetAdaptationCandidatesReturnsValidResponse() throws Exception {
        mockMvc.perform(get("/api/adaptation/candidates"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.current_size", notNullValue()));
    }

    @Test
    void testGetAdaptationHistoryEmpty() throws Exception {
        mockMvc.perform(get("/api/adaptation/history"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(0)));
    }

    @Test
    void testProcessAdaptationMissingPayloadFails() throws Exception {
        String emptyPayload = "{}";
        mockMvc.perform(post("/api/adaptation/process")
                .contentType(MediaType.APPLICATION_JSON)
                .content(emptyPayload))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testProcessAdaptationNonExistentSnapshotFails() throws Exception {
        String payload = "{\"snapshot_id\": 999999}";
        mockMvc.perform(post("/api/adaptation/process")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isNotFound());
    }

    @Test
    void testRollbackMissingTargetVersionFails() throws Exception {
        AdaptationActionDTO action = AdaptationActionDTO.builder().reason("Missing target").build();
        mockMvc.perform(post("/api/adaptation/rollback")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(action)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testProcessAdaptationWithDirectFeaturesSucceeds() throws Exception {
        Map<String, Object> request = new HashMap<>();
        Map<String, Object> features = new HashMap<>();
        features.put("mean_key_interval", 120.0);
        features.put("mean_mouse_speed", 250.0);
        request.put("device_id", "test-device-1");
        request.put("user_id", "researcher");
        request.put("features", features);

        // ML service is active on port 5001
        mockMvc.perform(post("/api/adaptation/process")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.decision_state", notNullValue()))
                .andExpect(jsonPath("$.prior_profile_version", notNullValue()));
    }

    @Test
    void testManualFreezeAndUnfreezeCycle() throws Exception {
        AdaptationActionDTO freezeAction = AdaptationActionDTO.builder()
                .reason("Test security freeze")
                .authorizedBy("admin")
                .build();

        mockMvc.perform(post("/api/adaptation/freeze")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(freezeAction)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.is_frozen", is(true)));

        AdaptationActionDTO unfreezeAction = AdaptationActionDTO.builder()
                .reason("Test security recovery")
                .authorizedBy("admin")
                .build();

        mockMvc.perform(post("/api/adaptation/unfreeze")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(unfreezeAction)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.is_frozen", is(false)));
    }
}
