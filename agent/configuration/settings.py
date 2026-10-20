"""
Cyber Doppelgänger - Centralized Agent Settings & Configuration
Safe Adaptive Behavioural Identity & Continuous User Verification

Defines runtime configuration with safe defaults and environment variable overrides.
Never stores or handles plaintext credentials or user content.
"""

import os
from dataclasses import dataclass
from pathlib import Path


def _str_to_bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "t")


@dataclass(frozen=True)
class AgentSettings:
    """Central configuration for the desktop behavioural agent."""

    # Agent Identity
    AGENT_NAME: str = "cyber-doppelganger-agent"
    AGENT_VERSION: str = "2.0.0-phase2"
    DEVICE_ID: str = os.getenv("DEVICE_ID", "local-workstation-01")
    USER_ID: str = os.getenv("USER_ID", "default-user")

    # Aggregation & Sampling Windows
    AGGREGATION_WINDOW_SECONDS: int = int(os.getenv("AGENT_WINDOW_SECONDS", os.getenv("AGGREGATION_WINDOW_SECONDS", "60")))
    KEYBOARD_PAUSE_THRESHOLD_SECONDS: float = float(os.getenv("KEYBOARD_PAUSE_THRESHOLD_SECONDS", "1.0"))
    IDLE_THRESHOLD_SECONDS: float = float(os.getenv("IDLE_THRESHOLD_SECONDS", "60.0"))

    # Local Persistence
    LOCAL_SNAPSHOT_STORAGE: bool = _str_to_bool(os.getenv("LOCAL_SNAPSHOT_STORAGE", "true"), default=True)
    SNAPSHOT_STORAGE_PATH: str = os.getenv("SNAPSHOT_STORAGE_PATH", "agent/data/feature_snapshots.jsonl")

    # Backend Communication
    BACKEND_ENABLED: bool = _str_to_bool(os.getenv("BACKEND_ENABLED", "false"), default=False)
    BACKEND_URL: str = os.getenv("BACKEND_URL", os.getenv("BACKEND_API_URL", "http://localhost:8080"))
    HEALTH_ENDPOINT: str = f"{os.getenv('BACKEND_URL', os.getenv('BACKEND_API_URL', 'http://localhost:8080')).rstrip('/')}/api/health"
    FEATURES_ENDPOINT: str = f"{os.getenv('BACKEND_URL', os.getenv('BACKEND_API_URL', 'http://localhost:8080')).rstrip('/')}/api/agent/features"
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("AGENT_REQUEST_TIMEOUT", "3.0"))

    # Logging
    LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO"))

    # Privacy Safeguard Flags (Strictly immutable defaults: all content collection permanently FALSE)
    ALLOW_KEYSTROKE_LOGGING: bool = False
    ALLOW_SCREEN_CAPTURE: bool = False
    ALLOW_CLIPBOARD_INSPECTION: bool = False
    ALLOW_DOCUMENT_READING: bool = False
    ALLOW_BROWSER_URL_TRACKING: bool = False
    ALLOW_WINDOW_TITLE_TRACKING: bool = False


# Global singleton settings instance
settings = AgentSettings()
