"""
Cyber Doppelgänger - Desktop Behavioural Agent Configuration
Privacy-First Continuous User Verification
"""

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class PrivacyPolicy:
    """Strict privacy guarantees enforced at architectural level"""
    ALLOW_KEYSTROKE_CONTENT: bool = False
    ALLOW_PASSWORDS: bool = False
    ALLOW_MESSAGES: bool = False
    ALLOW_CLIPBOARD: bool = False
    ALLOW_SCREENSHOTS: bool = False
    ALLOW_SCREEN_CONTENTS: bool = False
    ALLOW_DOCUMENT_CONTENTS: bool = False
    ALLOW_BROWSER_CONTENTS: bool = False
    ONLY_DERIVED_BEHAVIOURAL_FEATURES: bool = True

@dataclass
class AgentConfig:
    # Service identity
    AGENT_VERSION: str = "1.0.0-phase1"
    DEVICE_ID: str = os.getenv("DEVICE_ID", "local-workstation-01")
    USER_ID: str = os.getenv("USER_ID", "default-user")
    
    # Backend API configuration
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8080/api")
    HEALTH_ENDPOINT: str = f"{BACKEND_API_URL}/health"
    TELEMETRY_ENDPOINT: str = f"{BACKEND_API_URL}/telemetry"
    
    # Behavioural sampling window (in seconds)
    FEATURE_WINDOW_SECONDS: int = 30
    MIN_KEYSTROKE_EVENTS_PER_WINDOW: int = 10
    MIN_MOUSE_EVENTS_PER_WINDOW: int = 20
    
    # Privacy policy attached
    PRIVACY: PrivacyPolicy = PrivacyPolicy()

config = AgentConfig()
