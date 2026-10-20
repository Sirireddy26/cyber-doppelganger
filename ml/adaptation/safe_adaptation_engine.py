"""
Cyber Doppelgänger - Safe Adaptation Engine
Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution

Core coordinator orchestrating verification evidence, bounded candidate buffering,
drift velocity analysis, contamination prevention, and versioned profile evolution.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import logging

from ml.preprocessing.feature_preprocessor import FeaturePreprocessor, FeaturePreprocessingError
from ml.adaptation.candidate_buffer import CandidateObservationBuffer, CandidateObservation
from ml.adaptation.adaptation_policy import AdaptationPolicy, AdaptationPolicyConfig
from ml.adaptation.profile_manager import ProfileManager, ProfileVersionRecord
from ml.pipelines.verification_service import VerificationService

logger = logging.getLogger("cyber-doppelganger.adaptation.engine")


class SafeAdaptationEngine:
    """
    Orchestrates the safe, contamination-resistant evolution of behavioural reference profiles.
    Distinguishes legitimate evolutionary change from malicious contamination.
    """

    def __init__(
        self,
        config: Optional[AdaptationPolicyConfig] = None,
        verification_service: Optional[VerificationService] = None,
        profile_manager: Optional[ProfileManager] = None
    ):
        self.config = config or AdaptationPolicyConfig()
        self.policy = AdaptationPolicy(self.config)
        self.buffer = CandidateObservationBuffer(max_capacity=self.config.max_capacity)
        self.verifier = verification_service or VerificationService()
        self.profile_manager = profile_manager or ProfileManager()
        self.preprocessor = FeaturePreprocessor()
        self._previous_features: Optional[Dict[str, float]] = None

        self._ensure_baseline_initialized()

    def _ensure_baseline_initialized(self) -> None:
        """Ensures v1.0.0 is initialized from the active trained Isolation Forest artifact."""
        if self.profile_manager.active_version is None:
            status = self.verifier.get_model_status()
            iso_info = status.get("isolationForest", {})
            if iso_info.get("available") and self.verifier.iso_detector and self.verifier.iso_detector.reference_profile:
                ref = self.verifier.iso_detector.reference_profile
                self.profile_manager.initialize_from_reference_profile(
                    feature_means=ref.feature_means,
                    feature_stds=ref.feature_stds,
                    sample_count=ref.sample_count,
                    version_tag="v1.0.0"
                )

    def evaluate_observation(
        self,
        snapshot_dict: Dict[str, Any],
        verification_result: Optional[Dict[str, Any]] = None,
        device_id: str = "default-device",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a single behavioural feature snapshot through the Safe Adaptation Engine.
        Returns explainable adaptation decision dictionary.
        """
        snapshot_id = snapshot_dict.get("id") or snapshot_dict.get("snapshot_id") or snapshot_dict.get("snapshotId")
        u_id = user_id or snapshot_dict.get("user_id") or snapshot_dict.get("userId") or "default-user"
        d_id = device_id or snapshot_dict.get("device_id") or snapshot_dict.get("deviceId") or "default-device"

        # 1. Validation & Preprocessing (NaN/Inf check, privacy filter, schema 2.0)
        try:
            if hasattr(self.preprocessor, "extract_feature_dict"):
                flat_features = self.preprocessor.extract_feature_dict(snapshot_dict)
            else:
                vec = self.preprocessor.extract_feature_vector(snapshot_dict)
                flat_features = {k: float(vec[idx]) for idx, k in enumerate(self.preprocessor.feature_names)}
        except FeaturePreprocessingError as pe:
            return {
                "decision_state": "INSUFFICIENT_EVIDENCE",
                "prior_profile_version": self.profile_manager.active_version.version_tag if self.profile_manager.active_version else "NONE",
                "new_profile_version": None,
                "is_profile_frozen": self.profile_manager.is_frozen,
                "candidate_count": self.buffer.size(),
                "suspicious_streak": self.profile_manager.suspicious_streak,
                "drift_magnitude": 0.0,
                "velocity": 0.0,
                "stability_score": 1.0,
                "decision_reason": f"Input validation rejected snapshot: {pe}",
                "policy_version": self.config.policy_version,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # 2. Check frozen profile state immediately
        if self.profile_manager.is_frozen:
            return {
                "decision_state": "PROFILE_FROZEN",
                "prior_profile_version": self.profile_manager.active_version.version_tag if self.profile_manager.active_version else "NONE",
                "new_profile_version": None,
                "is_profile_frozen": True,
                "candidate_count": self.buffer.size(),
                "suspicious_streak": self.profile_manager.suspicious_streak,
                "drift_magnitude": 0.0,
                "velocity": 0.0,
                "stability_score": 1.0,
                "decision_reason": f"Profile is FROZEN ({self.profile_manager.freeze_reason}). Updates blocked until authorized recovery.",
                "policy_version": self.config.policy_version,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # 3. Ensure Phase 4 Verification is available
        if verification_result is None:
            verification_result = self.verifier.verify_snapshot(snapshot_dict)

        verif_status = verification_result.get("status", "UNCERTAIN")
        raw_score = float(verification_result.get("rawScore") or verification_result.get("raw_score") or 0.0)
        threshold = float(verification_result.get("threshold") or 0.0)
        anomaly_score = float(verification_result.get("anomalyScore") or verification_result.get("anomaly_score") or 0.0)
        conf_score = float(verification_result.get("confidenceScore") or verification_result.get("confidence_score") or 0.5)

        if verif_status == "MODEL_NOT_READY":
            return {
                "decision_state": "INSUFFICIENT_EVIDENCE",
                "prior_profile_version": "NONE",
                "new_profile_version": None,
                "is_profile_frozen": False,
                "candidate_count": 0,
                "suspicious_streak": 0,
                "drift_magnitude": 0.0,
                "velocity": 0.0,
                "stability_score": 1.0,
                "decision_reason": "ML verification model is not ready. Baseline enrollment required.",
                "policy_version": self.config.policy_version,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        self._ensure_baseline_initialized()
        active_rec = self.profile_manager.active_version

        # 4. Compute Metrics (Drift Magnitude, Velocity, Stability)
        ref_means = active_rec.feature_means if active_rec else {}
        ref_stds = active_rec.feature_stds if active_rec else {}

        drift_mag = self.policy.compute_drift_magnitude(flat_features, ref_means, ref_stds)
        velocity = self.policy.compute_velocity(flat_features, self._previous_features, ref_stds)
        self._previous_features = flat_features

        # Cooldown calculation
        now = datetime.now(timezone.utc)
        if self.profile_manager.last_adaptation_timestamp:
            elapsed_sec = (now - self.profile_manager.last_adaptation_timestamp).total_seconds()
        else:
            elapsed_sec = 999999.0

        # Create candidate observation wrapper
        candidate_obs = CandidateObservation(
            snapshot_id=snapshot_id,
            device_id=d_id,
            user_id=u_id,
            features=flat_features,
            raw_score=raw_score,
            anomaly_score=anomaly_score,
            confidence_score=conf_score
        )

        # Pre-compute stability across buffer + current candidate
        temp_features_list = list(self.preprocessor.feature_names)
        stability_score, _ = self.buffer.compute_stability(temp_features_list)

        # 5. Evaluate Adaptation Policy
        decision_state, reason = self.policy.evaluate(
            verification_status=verif_status,
            raw_score=raw_score,
            threshold=threshold,
            candidate_count=self.buffer.size() + 1,
            drift_magnitude=drift_mag,
            velocity=velocity,
            stability_score=stability_score,
            suspicious_streak=self.profile_manager.suspicious_streak,
            is_frozen=self.profile_manager.is_frozen,
            seconds_since_last_adaptation=elapsed_sec
        )

        prior_version = active_rec.version_tag if active_rec else "NONE"
        new_version = None

        # 6. Apply State Effects
        if decision_state == "NORMAL":
            self.profile_manager.suspicious_streak = 0
            # Under normal conditions, trusted profile is unchanged

        elif decision_state == "SUSPICIOUS_CHANGE":
            self.profile_manager.suspicious_streak += 1
            # Evict contaminated observations from candidate buffer
            self.buffer.clear()
            if self.profile_manager.suspicious_streak >= self.config.max_suspicious_streak:
                self.profile_manager.freeze(
                    f"Suspicious anomaly streak reached threshold ({self.profile_manager.suspicious_streak})."
                )
                decision_state = "PROFILE_FROZEN"
                reason = f"Profile automatically FROZEN due to repeated suspicious anomalies (streak: {self.profile_manager.suspicious_streak})."

        elif decision_state == "PROFILE_FROZEN":
            self.buffer.clear()

        elif decision_state == "INSUFFICIENT_EVIDENCE":
            # Add observation to candidate buffer for continued observation
            self.buffer.add(candidate_obs, is_frozen=self.profile_manager.is_frozen)

        elif decision_state == "SAFE_ADAPTATION":
            # All safety gates passed! Build and activate candidate profile version
            self.buffer.add(candidate_obs, is_frozen=self.profile_manager.is_frozen)
            candidates = self.buffer.get_observations()
            candidate_rec, msg = self.profile_manager.build_candidate_version(candidates)
            if candidate_rec:
                activated = self.profile_manager.activate_candidate_version(candidate_rec)
                if activated:
                    new_version = candidate_rec.version_tag
                    self.buffer.clear()
                    reason = f"Safe adaptation executed: activated {new_version} from {len(candidates)} stable observations."
                else:
                    decision_state = "INSUFFICIENT_EVIDENCE"
                    reason = "Candidate version activation failed."
            else:
                decision_state = "INSUFFICIENT_EVIDENCE"
                reason = f"Candidate profile build failed: {msg}"

        return {
            "decision_state": decision_state,
            "prior_profile_version": prior_version,
            "new_profile_version": new_version,
            "is_profile_frozen": self.profile_manager.is_frozen,
            "candidate_count": self.buffer.size(),
            "suspicious_streak": self.profile_manager.suspicious_streak,
            "drift_magnitude": drift_mag,
            "velocity": velocity,
            "stability_score": stability_score,
            "decision_reason": reason,
            "policy_version": self.config.policy_version,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status of the adaptation engine."""
        pm_status = self.profile_manager.get_status()
        buf_summary = self.buffer.get_summary()
        return {
            "engine_status": "FROZEN" if pm_status["is_frozen"] else "ACTIVE",
            "active_version": pm_status["active_version"],
            "is_frozen": pm_status["is_frozen"],
            "freeze_reason": pm_status["freeze_reason"],
            "frozen_at": pm_status["frozen_at"],
            "suspicious_streak": pm_status["suspicious_streak"],
            "sample_count": pm_status["sample_count"],
            "candidate_buffer": buf_summary,
            "policy_config": self.config.to_dict(),
            "versions_summary": pm_status["versions_summary"]
        }

    def freeze(self, reason: str = "Manual security freeze") -> Dict[str, Any]:
        self.profile_manager.freeze(reason)
        self.buffer.clear()
        return self.get_status()

    def unfreeze(self, authorized_by: str = "security-admin", reason: str = "Security clearance recovery") -> Tuple[bool, str]:
        success, msg = self.profile_manager.unfreeze(authorized_by=authorized_by, reason=reason)
        if success:
            self.buffer.clear()
        return success, msg

    def rollback(self, target_version: str, reason: str = "Security incident rollback") -> Tuple[bool, str]:
        success, msg = self.profile_manager.rollback_to_version(target_version, reason=reason)
        if success:
            self.buffer.clear()
        return success, msg
