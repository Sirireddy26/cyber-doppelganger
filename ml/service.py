"""
Cyber Doppelgänger - Internal ML Verification & Safe Adaptation Microservice
Safe Adaptive Behavioural Identity & Continuous User Verification

Provides a zero-dependency, lightweight internal HTTP interface (default port 5001)
for the Spring Boot backend to query behavioral verification and safe profile adaptation.
Endpoints:
- GET  /health
- GET  /models/status
- POST /verify
- GET  /adaptation/status
- GET  /adaptation/candidates
- POST /adaptation/evaluate
- POST /adaptation/freeze
- POST /adaptation/unfreeze
- POST /adaptation/rollback
"""

import sys
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.pipelines.verification_service import VerificationService
from ml.preprocessing.feature_preprocessor import FeaturePreprocessingError
from ml.adaptation.safe_adaptation_engine import SafeAdaptationEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [cyber-doppelganger.ml.service]: %(message)s"
)
logger = logging.getLogger("cyber-doppelganger.ml.service")

# Global Service instances
verification_engine = VerificationService()
adaptation_engine = SafeAdaptationEngine(verification_service=verification_engine)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class MLVerificationRequestHandler(BaseHTTPRequestHandler):

    def _send_json(self, status_code: int, data: dict):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _parse_body(self) -> dict:
        """Parses JSON request body supporting chunked and standard Content-Length."""
        if self.headers.get("Transfer-Encoding", "").lower() == "chunked":
            chunks = []
            while True:
                line = self.rfile.readline().strip()
                if not line:
                    break
                chunk_len = int(line, 16)
                if chunk_len == 0:
                    self.rfile.readline()
                    break
                chunks.append(self.rfile.read(chunk_len))
                self.rfile.readline()
            body = b"".join(chunks).decode("utf-8")
        else:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        if not body or body.strip() == "":
            body = "{}"
        return json.loads(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/health":
            self._send_json(200, {
                "status": "UP",
                "service": "cyber-doppelganger-ml-verifier",
                "version": "1.0.0",
                "adaptation_ready": True
            })
        elif path in ("/models/status", "/api/models/status"):
            status_data = verification_engine.get_model_status()
            self._send_json(200, status_data)
        elif path in ("/adaptation/status", "/api/adaptation/status"):
            status_data = adaptation_engine.get_status()
            self._send_json(200, status_data)
        elif path in ("/adaptation/candidates", "/api/adaptation/candidates"):
            candidates_data = adaptation_engine.buffer.get_summary()
            self._send_json(200, candidates_data)
        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            payload = self._parse_body()
        except Exception as e:
            self._send_json(400, {"error": "Invalid JSON", "message": str(e)})
            return

        if path in ("/verify", "/api/verification/process"):
            snapshot = payload.get("snapshot") or payload.get("features") or payload
            preferred_model = payload.get("preferredModel")
            try:
                result = verification_engine.verify_snapshot(snapshot, preferred_model=preferred_model)
                self._send_json(200, result)
            except FeaturePreprocessingError as pe:
                self._send_json(400, {
                    "status": "REJECTED",
                    "error": "Preprocessing Error",
                    "message": str(pe)
                })
            except Exception as ex:
                logger.error(f"Error during verification: {ex}", exc_info=True)
                self._send_json(500, {
                    "status": "ERROR",
                    "error": "Internal Verification Error",
                    "message": "An error occurred during feature scoring."
                })

        elif path in ("/adaptation/evaluate", "/api/adaptation/process"):
            snapshot = payload.get("snapshot") or payload.get("features") or payload
            verification_result = payload.get("verification_result") or payload.get("verificationResult")
            device_id = payload.get("device_id") or payload.get("deviceId") or "default-device"
            user_id = payload.get("user_id") or payload.get("userId")

            try:
                result = adaptation_engine.evaluate_observation(
                    snapshot_dict=snapshot,
                    verification_result=verification_result,
                    device_id=device_id,
                    user_id=user_id
                )
                self._send_json(200, result)
            except FeaturePreprocessingError as pe:
                self._send_json(400, {
                    "decision_state": "INSUFFICIENT_EVIDENCE",
                    "error": "Validation Error",
                    "message": str(pe)
                })
            except Exception as ex:
                logger.error(f"Error during adaptation evaluation: {ex}", exc_info=True)
                self._send_json(500, {
                    "decision_state": "INSUFFICIENT_EVIDENCE",
                    "error": "Internal Adaptation Error",
                    "message": str(ex)
                })

        elif path in ("/adaptation/freeze", "/api/adaptation/freeze"):
            reason = payload.get("reason", "Manual administrator security freeze")
            result = adaptation_engine.freeze(reason=reason)
            result["success"] = True
            result["is_frozen"] = True
            self._send_json(200, result)

        elif path in ("/adaptation/unfreeze", "/api/adaptation/unfreeze"):
            authorized_by = payload.get("authorized_by") or payload.get("authorizedBy") or "admin"
            reason = payload.get("reason", "Security clearance re-activation")
            success, message = adaptation_engine.unfreeze(authorized_by=authorized_by, reason=reason)
            st = adaptation_engine.get_status()
            self._send_json(200 if success else 400, {
                "success": success,
                "is_frozen": False if success else st["is_frozen"],
                "message": message,
                "status": st
            })

        elif path in ("/adaptation/rollback", "/api/adaptation/rollback"):
            target_version = payload.get("target_version") or payload.get("targetVersion")
            reason = payload.get("reason", "Rollback to previous trusted version")
            if not target_version:
                self._send_json(400, {"success": False, "error": "target_version is required"})
                return
            success, message = adaptation_engine.rollback(target_version=target_version, reason=reason)
            if success:
                self._send_json(200, {"success": True, "message": message, "status": adaptation_engine.get_status()})
            else:
                self._send_json(400, {"success": False, "message": message, "status": adaptation_engine.get_status()})

        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")


def run_service(host: str = "127.0.0.1", port: int = 5001):
    server_address = (host, port)
    httpd = ThreadingSimpleServer(server_address, MLVerificationRequestHandler)
    print(f"Cyber Doppelgänger ML Verification & Safe Adaptation Service running on http://{host}:{port}", flush=True)
    logger.info(f"Service initialized on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ML Service...", flush=True)
        httpd.shutdown()


if __name__ == "__main__":
    port = int(os.environ.get("ML_SERVICE_PORT", 5001))
    host = os.environ.get("ML_SERVICE_HOST", "127.0.0.1")
    run_service(host=host, port=port)
