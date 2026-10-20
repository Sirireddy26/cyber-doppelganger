"""
Cyber Doppelgänger - Adaptation Package
Phase 5: Safe Adaptation Engine & Continuous Behavioural Profile Evolution
"""

from ml.adaptation.candidate_buffer import CandidateObservationBuffer, CandidateObservation
from ml.adaptation.adaptation_policy import AdaptationPolicy, AdaptationPolicyConfig
from ml.adaptation.profile_manager import ProfileManager, ProfileVersionRecord
from ml.adaptation.safe_adaptation_engine import SafeAdaptationEngine

__all__ = [
    "CandidateObservationBuffer",
    "CandidateObservation",
    "AdaptationPolicy",
    "AdaptationPolicyConfig",
    "ProfileManager",
    "ProfileVersionRecord",
    "SafeAdaptationEngine"
]
