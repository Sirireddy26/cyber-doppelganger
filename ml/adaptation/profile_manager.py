"""
Cyber Doppelgänger - Reference Profile Version Manager
Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution

Maintains versioned reference profiles, manages atomic profile evolution,
supports rollback to previous trusted versions, and enforces the security freeze state.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json
from pathlib import Path
import copy
import logging
import numpy as np

logger = logging.getLogger("cyber-doppelganger.adaptation.profile")


class ProfileVersionRecord:
    """Represents a frozen, immutable snapshot of a trusted reference profile version."""

    def __init__(
        self,
        version_tag: str,
        parent_version_tag: Optional[str],
        user_id: str,
        sample_count: int,
        feature_means: Dict[str, float],
        feature_stds: Dict[str, float],
        created_at: Optional[str] = None,
        status: str = "ACTIVE",
        reason: str = "Initial baseline enrollment"
    ):
        self.version_tag = version_tag
        self.parent_version_tag = parent_version_tag
        self.user_id = user_id
        self.sample_count = sample_count
        self.feature_means = {k: float(v) for k, v in feature_means.items()}
        self.feature_stds = {k: float(v) for k, v in feature_stds.items()}
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.status = status  # ACTIVE, ARCHIVED, ROLLED_BACK
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_tag": self.version_tag,
            "parent_version_tag": self.parent_version_tag,
            "user_id": self.user_id,
            "sample_count": self.sample_count,
            "feature_count": len(self.feature_means),
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds,
            "created_at": self.created_at,
            "status": self.status,
            "reason": self.reason
        }


class ProfileManager:
    """
    Manages the lifecycle of trusted behavioural reference profiles,
    including versioning, candidate generation, atomic activation, and rollback.
    """

    def __init__(
        self,
        user_id: str = "default-user",
        storage_path: str = "ml/artifacts/profile_versions.json"
    ):
        self.user_id = user_id
        self.storage_path = Path(storage_path)
        self.version_history: List[ProfileVersionRecord] = []
        self.active_version: Optional[ProfileVersionRecord] = None
        self.is_frozen: bool = False
        self.freeze_reason: Optional[str] = None
        self.frozen_at: Optional[str] = None
        self.suspicious_streak: int = 0
        self.last_adaptation_timestamp: Optional[datetime] = None

        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        """Loads version history from disk if present."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records = data.get("versions", [])
                    for r in records:
                        rec = ProfileVersionRecord(
                            version_tag=r["version_tag"],
                            parent_version_tag=r.get("parent_version_tag"),
                            user_id=r.get("user_id", self.user_id),
                            sample_count=r.get("sample_count", 0),
                            feature_means=r.get("feature_means", {}),
                            feature_stds=r.get("feature_stds", {}),
                            created_at=r.get("created_at"),
                            status=r.get("status", "ARCHIVED"),
                            reason=r.get("reason", "Loaded from storage")
                        )
                        self.version_history.append(rec)

                    self.is_frozen = bool(data.get("is_frozen", False))
                    self.freeze_reason = data.get("freeze_reason")
                    self.frozen_at = data.get("frozen_at")

                    # Find active version
                    for rec in reversed(self.version_history):
                        if rec.status == "ACTIVE":
                            self.active_version = rec
                            break
                    if not self.active_version and self.version_history:
                        self.active_version = self.version_history[-1]
                        self.active_version.status = "ACTIVE"
            except Exception as e:
                logger.error(f"Failed to load profile versions from {self.storage_path}: {e}")

    def initialize_from_reference_profile(
        self,
        feature_means: Dict[str, float],
        feature_stds: Dict[str, float],
        sample_count: int = 100,
        version_tag: str = "v1.0.0"
    ) -> ProfileVersionRecord:
        """Initializes the baseline v1.0.0 from an existing fitted ReferenceProfile."""
        if self.active_version is not None:
            return self.active_version

        record = ProfileVersionRecord(
            version_tag=version_tag,
            parent_version_tag=None,
            user_id=self.user_id,
            sample_count=sample_count,
            feature_means=feature_means,
            feature_stds=feature_stds,
            status="ACTIVE",
            reason="Initial baseline enrollment"
        )
        self.version_history.append(record)
        self.active_version = record
        self._save_to_disk()
        logger.info(f"Initialized active trusted reference profile {version_tag} with {len(feature_means)} features.")
        return record

    def build_candidate_version(
        self,
        candidate_observations: List[Any],
        learning_rate: float = 0.15
    ) -> Tuple[Optional[ProfileVersionRecord], str]:
        """
        Builds a candidate profile version by smoothly blending candidate
        observations with the current active profile (learning rate alpha).
        Does NOT modify the active profile.
        """
        if self.active_version is None:
            return None, "Cannot adapt: no active trusted profile exists."

        if self.is_frozen:
            return None, "Cannot build candidate: profile is locked in FROZEN state."

        if not candidate_observations:
            return None, "Cannot build candidate: observation buffer is empty."

        # Compute empirical means and stds from candidate observations
        candidate_matrix = {}
        for obs in candidate_observations:
            for k, v in obs.features.items():
                if k not in candidate_matrix:
                    candidate_matrix[k] = []
                candidate_matrix[k].append(v)

        cand_means = {k: float(np.mean(vals)) for k, vals in candidate_matrix.items()}
        cand_stds = {k: float(np.std(vals)) for k, vals in candidate_matrix.items()}

        # Next version tag: e.g. v1.0.0 -> v1.1.0 -> v1.2.0
        current_tag = self.active_version.version_tag
        try:
            parts = current_tag.lstrip("v").split(".")
            major, minor = int(parts[0]), int(parts[1]) + 1
            next_tag = f"v{major}.{minor}.0"
        except Exception:
            next_tag = f"{current_tag}-adapted-{len(self.version_history)+1}"

        # Exponential moving average blending
        alpha = max(0.01, min(0.35, learning_rate))
        blended_means = {}
        blended_stds = {}

        for k, curr_mean in self.active_version.feature_means.items():
            if k in cand_means:
                new_mean = (1.0 - alpha) * curr_mean + alpha * cand_means[k]
                blended_means[k] = round(float(new_mean), 6)
            else:
                blended_means[k] = curr_mean

        for k, curr_std in self.active_version.feature_stds.items():
            if k in cand_stds:
                new_std = (1.0 - alpha) * curr_std + alpha * max(0.001, cand_stds[k])
                blended_stds[k] = round(float(new_std), 6)
            else:
                blended_stds[k] = curr_std

        # Validation of candidate values
        for k, v in blended_means.items():
            if not np.isfinite(v):
                return None, f"Candidate validation failed: non-finite float in feature '{k}'."

        candidate_record = ProfileVersionRecord(
            version_tag=next_tag,
            parent_version_tag=self.active_version.version_tag,
            user_id=self.user_id,
            sample_count=self.active_version.sample_count + len(candidate_observations),
            feature_means=blended_means,
            feature_stds=blended_stds,
            status="CANDIDATE",
            reason=f"Safe adaptation from {len(candidate_observations)} verified observations"
        )
        return candidate_record, "Candidate version generated and validated successfully."

    def activate_candidate_version(self, candidate: ProfileVersionRecord) -> bool:
        """
        Atomically archives the current active version and activates the candidate.
        Preserves complete version history for rollback.
        """
        if self.is_frozen:
            logger.warning("Attempted to activate candidate on a frozen profile. Rejected.")
            return False

        if self.active_version:
            self.active_version.status = "ARCHIVED"

        candidate.status = "ACTIVE"
        candidate.created_at = datetime.now(timezone.utc).isoformat()
        self.version_history.append(candidate)
        self.active_version = candidate
        self.last_adaptation_timestamp = datetime.now(timezone.utc)
        self.suspicious_streak = 0
        self._save_to_disk()
        logger.info(f"Successfully activated new trusted profile version: {candidate.version_tag}")
        return True

    def rollback_to_version(self, target_version_tag: str, reason: str = "Authorized security rollback") -> Tuple[bool, str]:
        """
        Rolls back the active profile to an earlier trusted version in the registry.
        Never deletes history.
        """
        target = None
        for rec in self.version_history:
            if rec.version_tag == target_version_tag:
                target = rec
                break

        if not target:
            return False, f"Version '{target_version_tag}' not found in profile registry."

        if target == self.active_version:
            # If target is already the active version, re-assert and reset baseline state
            self.active_version.status = "ACTIVE"
            self.is_frozen = False
            self.freeze_reason = None
            self.frozen_at = None
            self.suspicious_streak = 0
            self._save_to_disk()
            logger.info(f"Profile active version '{target_version_tag}' re-asserted and reset to baseline.")
            return True, f"Profile active version '{target_version_tag}' re-asserted and reset to baseline."

        if self.active_version:
            self.active_version.status = "ROLLED_BACK"

        # Create new rollback version node preserving explicit lineage
        parts = self.active_version.version_tag.lstrip("v").split(".") if self.active_version else ["1", "0", "0"]
        try:
            major = int(parts[0]) + 1
            rollback_tag = f"v{major}.0.0-rollback-to-{target.version_tag}"
        except Exception:
            rollback_tag = f"v-rollback-{target.version_tag}"

        rollback_record = ProfileVersionRecord(
            version_tag=rollback_tag,
            parent_version_tag=self.active_version.version_tag if self.active_version else None,
            user_id=self.user_id,
            sample_count=target.sample_count,
            feature_means=copy.deepcopy(target.feature_means),
            feature_stds=copy.deepcopy(target.feature_stds),
            status="ACTIVE",
            reason=f"Rollback to {target.version_tag}: {reason}"
        )
        self.version_history.append(rollback_record)
        self.active_version = rollback_record
        self.is_frozen = False
        self.freeze_reason = None
        self.frozen_at = None
        self.suspicious_streak = 0
        self._save_to_disk()
        logger.info(f"Profile safely rolled back to {target_version_tag} as new active version {rollback_tag}")
        return True, f"Profile safely rolled back to {target_version_tag} as new active version {rollback_tag}."

    def freeze(self, reason: str) -> None:
        """Locks adaptation. Rejects all future updates until explicit recovery."""
        self.is_frozen = True
        self.freeze_reason = reason
        self.frozen_at = datetime.now(timezone.utc).isoformat()
        self._save_to_disk()
        logger.warning(f"Profile adaptation FROZEN: {reason}")

    def unfreeze(self, authorized_by: str, reason: str) -> Tuple[bool, str]:
        """Unfreezes the profile following authorized review."""
        if not self.is_frozen:
            return False, "Profile is not currently frozen."

        self.is_frozen = False
        prev_reason = self.freeze_reason
        self.freeze_reason = None
        self.frozen_at = None
        self.suspicious_streak = 0
        self._save_to_disk()
        logger.info(f"Profile adaptation UNFROZEN by {authorized_by}. Reason: {reason} (Prior freeze: {prev_reason})")
        return True, f"Profile adaptation successfully unfrozen by {authorized_by}."

    def _save_to_disk(self) -> None:
        """Persists profile version history and state to local JSON file."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "user_id": self.user_id,
                "is_frozen": self.is_frozen,
                "freeze_reason": self.freeze_reason,
                "frozen_at": self.frozen_at,
                "suspicious_streak": self.suspicious_streak,
                "versions": [rec.to_dict() for rec in self.version_history]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist profile versions to {self.storage_path}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Returns non-sensitive metadata for adaptation monitoring."""
        return {
            "active_version": self.active_version.version_tag if self.active_version else "NONE",
            "is_frozen": self.is_frozen,
            "freeze_reason": self.freeze_reason,
            "frozen_at": self.frozen_at,
            "suspicious_streak": self.suspicious_streak,
            "sample_count": self.active_version.sample_count if self.active_version else 0,
            "total_versions": len(self.version_history),
            "versions_summary": [
                {
                    "version_tag": v.version_tag,
                    "status": v.status,
                    "sample_count": v.sample_count,
                    "created_at": v.created_at,
                    "reason": v.reason
                }
                for v in self.version_history
            ]
        }
