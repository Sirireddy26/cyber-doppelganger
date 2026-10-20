package com.cyberdoppelganger;

import com.cyberdoppelganger.repository.BehaviouralFeatureSnapshotRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class FeatureIngestionAndRetrievalTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BehaviouralFeatureSnapshotRepository snapshotRepository;

    @BeforeEach
    void setUp() {
        snapshotRepository.deleteAll();
    }

    @Test
    void testHealthEndpointReturnsStatusAndDatabase() throws Exception {
        mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.service").value("cyber-doppelganger-backend"))
                .andExpect(jsonPath("$.database").value("UP"))
                .andExpect(jsonPath("$.database_type").isNotEmpty());
    }

    @Test
    void testValidFeatureSnapshotIngestionSucceedsAndPersists() throws Exception {
        String validPayload = """
        {
          "timestamp": "2026-10-09T08:41:37.120607Z",
          "window_duration_seconds": 15,
          "device_id": "test-workstation-01",
          "user_id": "default-user",
          "schema_version": "2.0",
          "keyboard": {
            "total_key_events": 25,
            "mean_key_interval": 0.185,
            "median_key_interval": 0.175,
            "key_interval_std": 0.042,
            "minimum_key_interval": 0.092,
            "maximum_key_interval": 2.45,
            "typing_speed": 4.8,
            "pause_count": 1,
            "mean_pause_duration": 1.82,
            "longest_pause": 2.45,
            "typing_activity_duration": 10.0
          },
          "mouse": {
            "movement_distance": 1579.8,
            "mean_mouse_speed": 233.7,
            "mouse_speed_std": 491.0,
            "mean_acceleration": 6908.5,
            "click_count": 1,
            "left_click_count": 1,
            "right_click_count": 0,
            "middle_click_count": 0,
            "mean_click_interval": 0.0,
            "click_interval_std": 0.0,
            "scroll_count": 0,
            "positive_scroll_count": 0,
            "negative_scroll_count": 0,
            "mouse_active_duration": 12.5
          },
          "session": {
            "session_duration": 15.0,
            "active_duration": 12.5,
            "idle_duration": 2.5,
            "active_idle_ratio": 5.0,
            "activity_density": 0.833,
            "keyboard_activity_duration": 10.0,
            "mouse_activity_duration": 12.5
          },
          "application": {
            "process_count": 315,
            "active_process_count": 312,
            "application_switch_count": 1,
            "process_activity_count": 4,
            "application_activity_duration": 12.5
          }
        }
        """;

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(validPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("accepted"))
                .andExpect(jsonPath("$.snapshotId").isNotEmpty())
                .andExpect(jsonPath("$.receivedAt").isNotEmpty());

        assertEquals(1, snapshotRepository.count());
    }

    @Test
    void testForbiddenContentFieldRejectedAndNotPersisted() throws Exception {
        String violationPayload = """
        {
          "timestamp": "2026-10-09T08:41:37.120607Z",
          "window_duration_seconds": 15,
          "device_id": "test-workstation-01",
          "typed_text": "SensitivePassword123"
        }
        """;

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(violationPayload))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Privacy Violation"))
                // Ensure sensitive payload is NEVER leaked in response message
                .andExpect(jsonPath("$.message").value(not(containsString("SensitivePassword123"))));

        assertEquals(0, snapshotRepository.count());
    }

    @Test
    void testNegativeWindowDurationRejected() throws Exception {
        String invalidPayload = """
        {
          "timestamp": "2026-10-09T08:41:37.120607Z",
          "window_duration_seconds": -5,
          "device_id": "test-workstation-01"
        }
        """;

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidPayload))
                .andExpect(status().isBadRequest());

        assertEquals(0, snapshotRepository.count());
    }

    @Test
    void testMalformedJsonRejected() throws Exception {
        String malformedJson = "{ timestamp: invalid, window_duration_seconds: ";

        mockMvc.perform(post("/api/agent/features")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(malformedJson))
                .andExpect(status().isBadRequest());

        assertEquals(0, snapshotRepository.count());
    }

    @Test
    void testRetrieveSnapshotsAndPagination() throws Exception {
        // Ingest 2 snapshots
        String payload1 = """
        {"timestamp":"2026-10-09T08:00:00Z","window_duration_seconds":15,"device_id":"dev-1"}
        """;
        String payload2 = """
        {"timestamp":"2026-10-09T08:00:15Z","window_duration_seconds":15,"device_id":"dev-1"}
        """;

        mockMvc.perform(post("/api/agent/features").contentType(MediaType.APPLICATION_JSON).content(payload1))
                .andExpect(status().isCreated());
        mockMvc.perform(post("/api/agent/features").contentType(MediaType.APPLICATION_JSON).content(payload2))
                .andExpect(status().isCreated());

        // Get list
        mockMvc.perform(get("/api/behaviour?page=0&size=10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.page.totalElements").value(2))
                .andExpect(jsonPath("$.content", hasSize(2)));

        // Get single by existing id
        Long firstId = snapshotRepository.findAll().get(0).getId();
        mockMvc.perform(get("/api/behaviour/" + firstId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(firstId))
                .andExpect(jsonPath("$.device_id").value("dev-1"));

        // Get non-existing id -> 404
        mockMvc.perform(get("/api/behaviour/999999"))
                .andExpect(status().isNotFound());
    }
}
