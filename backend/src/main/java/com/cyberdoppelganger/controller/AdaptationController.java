package com.cyberdoppelganger.controller;

import com.cyberdoppelganger.dto.*;
import com.cyberdoppelganger.service.AdaptationService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/adaptation")
@CrossOrigin(origins = "*", allowedHeaders = "*")
public class AdaptationController {

    private final AdaptationService adaptationService;

    public AdaptationController(AdaptationService adaptationService) {
        this.adaptationService = adaptationService;
    }

    @GetMapping("/status")
    public ResponseEntity<AdaptationStatusDTO> getStatus() {
        return ResponseEntity.ok(adaptationService.getStatus());
    }

    @GetMapping("/candidates")
    public ResponseEntity<Map<String, Object>> getCandidates() {
        return ResponseEntity.ok(adaptationService.getCandidateSummary());
    }

    @PostMapping("/process")
    public ResponseEntity<AdaptationResponseDTO> processAdaptation(@RequestBody AdaptationRequestDTO request) {
        AdaptationResponseDTO response = adaptationService.processAdaptation(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/history")
    public ResponseEntity<Page<AdaptationResponseDTO>> getHistory(
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable
    ) {
        return ResponseEntity.ok(adaptationService.getAdaptationHistory(pageable));
    }

    @PostMapping("/freeze")
    public ResponseEntity<Map<String, Object>> freezeProfile(@RequestBody(required = false) AdaptationActionDTO action) {
        if (action == null) {
            action = AdaptationActionDTO.builder().reason("Manual freeze from security console").build();
        }
        return ResponseEntity.ok(adaptationService.freezeProfile(action));
    }

    @PostMapping("/unfreeze")
    public ResponseEntity<Map<String, Object>> unfreezeProfile(@RequestBody(required = false) AdaptationActionDTO action) {
        if (action == null) {
            action = AdaptationActionDTO.builder().authorizedBy("admin").reason("Security administrative recovery").build();
        }
        return ResponseEntity.ok(adaptationService.unfreezeProfile(action));
    }

    @PostMapping("/rollback")
    public ResponseEntity<Map<String, Object>> rollbackProfile(@RequestBody AdaptationActionDTO action) {
        return ResponseEntity.ok(adaptationService.rollbackProfile(action));
    }
}
