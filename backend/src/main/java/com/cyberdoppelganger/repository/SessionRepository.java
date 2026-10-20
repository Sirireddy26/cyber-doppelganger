package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SessionRepository extends JpaRepository<Session, Long> {
    List<Session> findByDeviceId(Long deviceId);
    Optional<Session> findTopByDeviceIdAndStatusOrderByStartedAtDesc(Long deviceId, String status);
    List<Session> findByUserIdAndStatus(Long userId, String status);
}
