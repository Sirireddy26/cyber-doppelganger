package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.ProfileVersion;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProfileVersionRepository extends JpaRepository<ProfileVersion, Long> {

    Optional<ProfileVersion> findFirstByDeviceIdOrderByCreatedAtDesc(String deviceId);

    Optional<ProfileVersion> findFirstByDeviceIdAndStatus(String deviceId, String status);

    Optional<ProfileVersion> findByDeviceIdAndVersionTag(String deviceId, String versionTag);

    Page<ProfileVersion> findByDeviceIdOrderByCreatedAtDesc(String deviceId, Pageable pageable);

    List<ProfileVersion> findTop10ByOrderByCreatedAtDesc();
}
