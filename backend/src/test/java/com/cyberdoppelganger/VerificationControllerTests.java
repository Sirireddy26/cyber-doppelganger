package com.cyberdoppelganger;

import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import com.cyberdoppelganger.repository.VerificationResultRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("dev")
public class VerificationControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BehaviouralFeatureSnapshotRepository snapshotRepository;

    @Autowired
    private VerificationResultRepository verificationRepository;

    @BeforeEach
    void setUp() {
        verificationRepository.deleteAll();
        snapshotRepository.deleteAll();
    }

    @Test
    void testGetModelStatusReturnsValidStatus() throws Exception {
        mockMvc.perform(get("/api/models/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status", anyOf(is("READY"), is("SERVICE_UNAVAILABLE"), is("MODEL_NOT_READY"))));
    }

    @Test
    void testGetVerificationResultsEmpty() throws Exception {
        mockMvc.perform(get("/api/verification"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.page.totalElements").value(0))
                .andExpect(jsonPath("$.content", hasSize(0)));
    }

    @Test
    void testProcessVerificationMissingSnapshotFails() throws Exception {
        String emptyPayload = "{}";
        mockMvc.perform(post("/api/verification/process")
                .contentType(MediaType.APPLICATION_JSON)
                .content(emptyPayload))
                .andExpect(status().isBadRequest());
    }

    @Test
    void testProcessVerificationNonExistentSnapshotReturnsNotFound() throws Exception {
        String payload = "{\"snapshot_id\": 999999}";
        mockMvc.perform(post("/api/verification/process")
                .contentType(MediaType.APPLICATION_JSON)
                .content(payload))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetVerificationByIdNotFound() throws Exception {
        mockMvc.perform(get("/api/verification/999999"))
                .andExpect(status().isNotFound());
    }
}
