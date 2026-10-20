package com.cyberdoppelganger.controller;

import com.cyberdoppelganger.dto.ModelStatusResponseDTO;
import com.cyberdoppelganger.dto.VerificationRequestDTO;
import com.cyberdoppelganger.dto.VerificationResponseDTO;
import com.cyberdoppelganger.service.VerificationService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class VerificationController {

    private final VerificationService verificationService;

    public VerificationController(VerificationService verificationService) {
        this.verificationService = verificationService;
    }

    @PostMapping("/verification/process")
    public ResponseEntity<VerificationResponseDTO> processVerification(@RequestBody VerificationRequestDTO request) {
        VerificationResponseDTO result = verificationService.processVerification(request);
        return ResponseEntity.status(HttpStatus.OK).body(result);
    }

    @GetMapping("/verification")
    public ResponseEntity<Page<VerificationResponseDTO>> getVerificationResults(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        int boundedSize = Math.min(Math.max(size, 1), 100);
        int boundedPage = Math.max(page, 0);
        Page<VerificationResponseDTO> results = verificationService.getResults(PageRequest.of(boundedPage, boundedSize));
        return ResponseEntity.ok(results);
    }

    @GetMapping("/verification/{id}")
    public ResponseEntity<VerificationResponseDTO> getVerificationResultById(@PathVariable Long id) {
        VerificationResponseDTO result = verificationService.getResultById(id);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/models/status")
    public ResponseEntity<ModelStatusResponseDTO> getModelStatus() {
        ModelStatusResponseDTO status = verificationService.getModelStatus();
        return ResponseEntity.ok(status);
    }
}
