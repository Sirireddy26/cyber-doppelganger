"""
Cyber Doppelgänger - Phase 1 Integration Smoke Test
Verifies that the Spring Boot backend /api/health endpoint is reachable.
"""

import unittest
import requests

class TestHealthIntegration(unittest.TestCase):

    def test_backend_health_endpoint(self):
        url = "http://localhost:8080/api/health"
        try:
            response = requests.get(url, timeout=3.0)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get("status"), "UP")
            self.assertEqual(data.get("service"), "cyber-doppelganger-backend")
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server is not running on localhost:8080. Start backend to run this test.")

if __name__ == "__main__":
    unittest.main()
