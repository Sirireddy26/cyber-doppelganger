package com.cyberdoppelganger.controller;

import com.cyberdoppelganger.dto.FeatureSnapshotResponseDTO;
import com.cyberdoppelganger.service.BehaviourRetrievalService;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/behaviour")
public class BehaviourController {

    private final BehaviourRetrievalService retrievalService;

    public BehaviourController(BehaviourRetrievalService retrievalService) {
        this.retrievalService = retrievalService;
    }

    @GetMapping
    public ResponseEntity<Page<FeatureSnapshotResponseDTO>> getSnapshots(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Page<FeatureSnapshotResponseDTO> result = retrievalService.getSnapshots(page, size);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<FeatureSnapshotResponseDTO> getSnapshotById(@PathVariable Long id) {
        FeatureSnapshotResponseDTO result = retrievalService.getSnapshotById(id);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/history")
    public ResponseEntity<Page<FeatureSnapshotResponseDTO>> getHistory(
            @RequestParam(required = false) String deviceId,
            @RequestParam(required = false) Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        Page<FeatureSnapshotResponseDTO> result = retrievalService.getHistory(deviceId, userId, page, size);
        return ResponseEntity.ok(result);
    }
}
