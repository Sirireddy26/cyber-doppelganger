package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.BehaviouralFeatureSnapshot;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface BehaviouralFeatureSnapshotRepository extends JpaRepository<BehaviouralFeatureSnapshot, Long> {
    Page<BehaviouralFeatureSnapshot> findAllByOrderByCapturedAtDesc(Pageable pageable);
    Page<BehaviouralFeatureSnapshot> findByDeviceIdOrderByCapturedAtDesc(String deviceId, Pageable pageable);
    Page<BehaviouralFeatureSnapshot> findByUserIdOrderByCapturedAtDesc(Long userId, Pageable pageable);
    Optional<BehaviouralFeatureSnapshot> findTopByDeviceIdOrderByCapturedAtDesc(String deviceId);
    Optional<BehaviouralFeatureSnapshot> findTopByOrderByCapturedAtDesc();
    boolean existsByDeviceIdAndCapturedAt(String deviceId, java.time.Instant capturedAt);
}
