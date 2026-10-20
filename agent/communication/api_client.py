"""
Cyber Doppelgänger - Backend API Client
Safe Adaptive Behavioural Identity & Continuous User Verification

Handles optional HTTP communication between the local desktop agent and the Spring Boot backend.
Gracefully handles backend unavailability without crashing the monitoring process.
STRICT PRIVACY GUARANTEE: Never transmits user content, credentials, or raw events.
"""

from typing import Dict, Any, Optional
import requests
import json
import logging

from agent.configuration.settings import settings
from agent.features.feature_snapshot import FeatureSnapshot
from agent.privacy.privacy_filter import PrivacyFilter

logger = logging.getLogger("cyber-doppelganger.agent")


class ApiClient:
    """HTTP Client for sending privacy-validated behavioural feature snapshots to backend."""

    def __init__(self, base_url: Optional[str] = None, enabled: Optional[bool] = None):
        self.base_url = (base_url or settings.BACKEND_URL).rstrip("/")
        self.enabled = settings.BACKEND_ENABLED if enabled is None else enabled
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    def check_health(self) -> Dict[str, Any]:
        """
        Queries backend GET /api/health endpoint.
        Returns diagnostic dictionary without throwing exceptions.
        """
        url = f"{self.base_url}/api/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return {
                    "connected": True,
                    "status_code": response.status_code,
                    "data": response.json()
                }
            return {
                "connected": False,
                "status_code": response.status_code,
                "error": f"Unexpected status code {response.status_code}"
            }
        except requests.exceptions.ConnectionError:
            return {
                "connected": False,
                "status_code": None,
                "error": "Connection refused - Backend is not currently reachable."
            }
        except requests.exceptions.Timeout:
            return {
                "connected": False,
                "status_code": None,
                "error": "Health check timed out."
            }
        except Exception as e:
            return {
                "connected": False,
                "status_code": None,
                "error": str(e)
            }

    def send_snapshot(self, snapshot: FeatureSnapshot) -> Dict[str, Any]:
        """
        Validates privacy policy and transmits feature snapshot to POST /api/agent/features.
        
        If BACKEND_ENABLED is False or backend is unreachable, gracefully returns error status
        without throwing an unhandled exception or interrupting monitoring.
        """
        if not self.enabled:
            return {
                "success": False,
                "sent": False,
                "message": "Backend transmission is disabled in agent configuration (BACKEND_ENABLED=False)."
            }

        snapshot_dict = snapshot.to_dict()

        # Enforce privacy check before transmission
        PrivacyFilter.validate_snapshot_dict(snapshot_dict)

        url = f"{self.base_url}/api/agent/features"
        try:
            response = requests.post(
                url,
                json=snapshot_dict,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            if response.status_code in (200, 201, 202):
                data = response.json() if response.content else {}
                snapshot_id = data.get("snapshotId")
                logger.info(f"Successfully transmitted feature snapshot #{snapshot_id} to backend.")
                return {
                    "success": True,
                    "sent": True,
                    "status_code": response.status_code,
                    "snapshot_id": snapshot_id,
                    "data": data
                }
            else:
                logger.warning(f"Backend returned status {response.status_code} on feature ingestion.")
                return {
                    "success": False,
                    "sent": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        except requests.exceptions.ConnectionError:
            logger.info("Backend unavailable (Connection Refused). Snapshot retained in local buffer.")
            return {
                "success": False,
                "sent": False,
                "error": "Backend server is currently offline or unreachable."
            }
        except requests.exceptions.Timeout:
            logger.warning("Backend request timed out. Snapshot retained in local buffer.")
            return {
                "success": False,
                "sent": False,
                "error": "Request timed out."
            }
        except Exception as e:
            logger.warning(f"Failed to transmit feature snapshot: {e}")
            return {
                "success": False,
                "sent": False,
                "error": str(e)
            }


# Backwards compatibility alias
BackendClient = ApiClient
