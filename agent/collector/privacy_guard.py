"""
Cyber Doppelgänger - Privacy Guard Layer
Enforces non-collection rules for user safety and ethical research compliance.
"""

from typing import Any, Dict

class PrivacyViolationError(Exception):
    """Raised when an attempt to record prohibited content is detected."""
    pass

class PrivacyGuard:
    PROHIBITED_KEYS = {
        "char", "character", "key_char", "text", "password", 
        "clipboard", "screenshot", "screen_image", "window_content", 
        "browser_url", "document_text", "message"
    }

    @classmethod
    def sanitize_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates that an event dictionary contains ONLY permitted timing and kinematics metrics.
        Raises PrivacyViolationError if any prohibited content key is detected.
        """
        for prohibited in cls.PROHIBITED_KEYS:
            if prohibited in event:
                raise PrivacyViolationError(
                    f"Privacy Violation: Prohibited field '{prohibited}' detected in event stream!"
                )
        return event

    @classmethod
    def verify_feature_vector(cls, features: Dict[str, float]) -> bool:
        """
        Verifies that feature vector consists only of aggregate numbers (timing, velocity, etc.).
        """
        for k, v in features.items():
            if not isinstance(v, (int, float)):
                raise PrivacyViolationError(
                    f"Privacy Violation: Feature '{k}' has non-numerical value ({type(v)}). Only statistical kinematics allowed."
                )
        return True
