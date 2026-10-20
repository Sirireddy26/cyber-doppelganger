package com.cyberdoppelganger.repository;

import com.cyberdoppelganger.entity.ProfileFreezeRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ProfileFreezeRecordRepository extends JpaRepository<ProfileFreezeRecord, Long> {

    Optional<ProfileFreezeRecord> findFirstByDeviceIdAndIsFrozenTrueOrderByFrozenAtDesc(String deviceId);

    Page<ProfileFreezeRecord> findByDeviceIdOrderByFrozenAtDesc(String deviceId, Pageable pageable);
}
