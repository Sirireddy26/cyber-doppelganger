package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.AdaptationEvent;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AdaptationEventRepository extends JpaRepository<AdaptationEvent, Long> {

    Page<AdaptationEvent> findAllByOrderByCreatedAtDesc(Pageable pageable);

    Page<AdaptationEvent> findByDeviceIdOrderByCreatedAtDesc(String deviceId, Pageable pageable);

    Optional<AdaptationEvent> findFirstByDeviceIdOrderByCreatedAtDesc(String deviceId);
}
