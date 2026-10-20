"""
Cyber Doppelgänger - Privacy Filter & Verification Guard
Safe Adaptive Behavioural Identity & Continuous User Verification

Enforces strict non-collection rules ensuring zero capture of typed text,
individual keys, passwords, clipboard, screen captures, URLs, or documents.
"""

from typing import Dict, Any, Set, List
import math
import logging

logger = logging.getLogger("cyber-doppelganger.agent")


class PrivacyViolationError(Exception):
    """Raised when an attempt to include prohibited or sensitive content is detected."""
    pass


class PrivacyFilter:
    """
    Enforces privacy boundaries and verifies that feature snapshots
    contain strictly aggregated, privacy-safe, non-content metadata.
    """

    # Prohibited field names that must NEVER appear anywhere in snapshots or event streams
    PROHIBITED_FIELDS: Set[str] = {
        "char", "character", "key", "key_name", "key_char", "text", "typed_text",
        "typed_chars", "keystroke_content", "raw_keys", "word", "words", "sentence",
        "password", "passphrase", "secret", "token", "credential",
        "clipboard", "clipboard_content", "clipboard_text",
        "screenshot", "screen_image", "screen_content", "pixel_data", "frame",
        "window_title", "window_text", "document_content", "document_name", "file_content",
        "browser_url", "url", "history", "search_query", "message", "message_content",
        "email_content", "chat_message", "terminal_command", "command_line"
    }

    @classmethod
    def validate_snapshot_dict(cls, snapshot_data: Dict[str, Any]) -> bool:
        """
        Validates that a feature snapshot dictionary contains NO forbidden fields
        and contains exclusively valid, finite numerical data or authorized metadata.
        
        Raises PrivacyViolationError if any forbidden field is detected.
        NEVER logs the sensitive value itself.
        """
        cls._recursive_check_forbidden(snapshot_data, path="")
        cls._check_numerical_integrity(snapshot_data)
        return True

    @classmethod
    def _recursive_check_forbidden(cls, obj: Any, path: str = "") -> None:
        """Recursively inspects dictionary keys and object attributes for prohibited terms."""
        if isinstance(obj, dict):
            for key, val in obj.items():
                current_path = f"{path}.{key}" if path else key
                # Check key name in lower case
                norm_key = str(key).lower().strip()
                if norm_key in cls.PROHIBITED_FIELDS or any(p in norm_key for p in ["password", "clipboard", "screenshot", "typed_text"]):
                    # Note: Log only the field name, NEVER the value!
                    logger.warning(f"Privacy validation failed: Prohibited field name detected: '{key}'")
                    raise PrivacyViolationError(
                        f"Privacy Guard Violation: Prohibited field '{key}' detected at path '{current_path}'"
                    )
                
                # Check if val is string and might contain forbidden content representations
                if isinstance(val, str) and norm_key in ("key", "char", "character", "letter"):
                    logger.warning(f"Privacy validation failed: Prohibited content key detected: '{key}'")
                    raise PrivacyViolationError(
                        f"Privacy Guard Violation: Prohibited content key '{key}' detected"
                    )

                cls._recursive_check_forbidden(val, current_path)

        elif isinstance(obj, (list, tuple)):
            for idx, item in enumerate(obj):
                cls._recursive_check_forbidden(item, f"{path}[{idx}]")

    @classmethod
    def _check_numerical_integrity(cls, snapshot_data: Dict[str, Any]) -> None:
        """
        Ensures all numerical values inside feature sections are finite (no NaN, no Inf).
        """
        feature_sections = ["keyboard", "mouse", "session", "application"]
        for section in feature_sections:
            sec_dict = snapshot_data.get(section)
            if isinstance(sec_dict, dict):
                for feat_name, val in sec_dict.items():
                    if val is not None and isinstance(val, (int, float)):
                        if math.isnan(val) or math.isinf(val):
                            logger.warning(f"Numerical integrity error: Non-finite value in feature '{section}.{feat_name}'")
                            raise ValueError(
                                f"Feature '{section}.{feat_name}' has non-finite value: {val}"
                            )

    @classmethod
    def sanitize_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Validates that an event dictionary does not contain prohibited content."""
        for field in cls.PROHIBITED_FIELDS:
            if field in event:
                logger.warning(f"Privacy validation rejected raw event containing field: '{field}'")
                raise PrivacyViolationError(
                    f"Privacy Guard Violation: Prohibited field '{field}' detected in event stream!"
                )
        return event

    @classmethod
    def is_feature_vector_compliant(cls, vector: Dict[str, Any]) -> bool:
        """Verifies that all extracted features are strictly numerical/statistical or None."""
        for key, val in vector.items():
            if val is not None and not isinstance(val, (int, float)):
                logger.warning(f"Privacy compliance check failed: Non-numerical feature '{key}'")
                raise PrivacyViolationError(
                    f"Privacy Guard Violation: Non-numerical feature '{key}' found with type {type(val)}."
                )
        return True


# Backward-compatible alias
PrivacyGuard = PrivacyFilter
