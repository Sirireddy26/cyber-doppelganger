package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.SecurityEvent;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SecurityEventRepository extends JpaRepository<SecurityEvent, Long> {
    Page<SecurityEvent> findAllByOrderByCreatedAtDesc(Pageable pageable);
    List<SecurityEvent> findByUserIdOrderByCreatedAtDesc(Long userId);
    List<SecurityEvent> findByDeviceIdOrderByCreatedAtDesc(String deviceId);
}
