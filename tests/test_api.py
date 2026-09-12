"""
test_api.py - Unit tests for FastAPI REST Service in CyberLens 2.0
"""

import unittest
from fastapi.testclient import TestClient
from api import app

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_list_assets(self):
        response = self.client.get("/assets")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreater(len(response.json()), 0)

    def test_get_asset_by_id(self):
        response = self.client.get("/assets/CBS_SERVER_001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["asset_id"], "CBS_SERVER_001")

    def test_get_asset_not_found(self):
        response = self.client.get("/assets/NONEXISTENT")
        self.assertEqual(response.status_code, 404)

    def test_list_vulnerabilities(self):
        response = self.client.get("/vulnerabilities")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_calculate_cri(self):
        response = self.client.post("/calculate/cr-i", json={})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cr_i", data)
        self.assertGreaterEqual(data["cr_i"], 0)
        self.assertLessEqual(data["cr_i"], 100)

    def test_calculate_eal(self):
        vulns_resp = self.client.get("/vulnerabilities")
        vuln_id = vulns_resp.json()[0]["vuln_id"]

        response = self.client.post("/calculate/eal", json={"vuln_id": vuln_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("eal_inr", data)

    def test_calculate_eal_not_found(self):
        response = self.client.post("/calculate/eal", json={"vuln_id": "VULN-9999"})
        self.assertEqual(response.status_code, 404)

    def test_calculate_total_exposure(self):
        response = self.client.post("/calculate/total-exposure", json={})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_exposure_inr", data)
        self.assertGreater(data["total_exposure_inr"], 0)

    def test_optimize_budget(self):
        response = self.client.post("/optimize/budget", json={"budget_inr": 5000000})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("controls", data)

    def test_llm_remediate(self):
        vulns_resp = self.client.get("/vulnerabilities")
        vuln_id = vulns_resp.json()[0]["vuln_id"]

        response = self.client.post("/llm/remediate", json={"vuln_id": vuln_id, "language": "en"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("remediation_steps", data)
        self.assertIsInstance(data["remediation_steps"], list)

    def test_translate_endpoint(self):
        response = self.client.post("/translate", json={"text": "Cyber Resilience Index", "target_lang": "hi"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("translated_text", data)

    def test_translate_endpoint_invalid_lang(self):
        response = self.client.post("/translate", json={"text": "Hello", "target_lang": "invalid_lang_code"})
        self.assertEqual(response.status_code, 400)

    def test_ai_summary_endpoint(self):
        response = self.client.post("/ai/summary", json={"lang": "en"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary_markdown", data)

if __name__ == "__main__":
    unittest.main()
