package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.VerificationResult;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VerificationResultRepository extends JpaRepository<VerificationResult, Long> {
    Page<VerificationResult> findAllByOrderByCreatedAtDesc(Pageable pageable);
    List<VerificationResult> findTop50ByOrderByCreatedAtDesc();
    List<VerificationResult> findByDeviceIdOrderByCreatedAtDesc(String deviceId);
    List<VerificationResult> findBySnapshotId(Long snapshotId);
}
