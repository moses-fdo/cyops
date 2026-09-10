import unittest
from risk_engine import (
    rbi_weighted_cvss,
    asset_risk_weight,
    compute_asset_cr_i,
    compute_overall_cr_i,
    expected_annual_loss,
    total_exposure,
    weakly_crypto,
    quantum_risk_estimate,
    llm_remediate,
    control_impacts_control,
    simulate_control,
    enrich_controls_with_reduction,
    optimize_budget,
    compute_risk_matrix,
)
from controls_library import CONTROLS


class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        self.sample_asset = {
            "asset_id": "TEST_ASSET_1",
            "name": "Test UPI Switch",
            "asset_type": "UPI_SWITCH",
            "criticality": 9,
            "daily_transaction_volume": 5000000,
            "downtime_cost_per_hour": 2500000,
            "crypto_profile": "RSA-2048",
        }
        self.sample_vuln = {
            "vuln_id": "TEST_V_1",
            "asset_id": "TEST_ASSET_1",
            "cve_id": "CVE-2024-0001",
            "cvss_base_score": 8.0,
            "exploit_available": True,
            "days_unpatched": 14,
            "category": "Authentication Bypass",
        }

    def test_rbi_weighted_cvss_bounds(self):
        score = rbi_weighted_cvss(self.sample_vuln, self.sample_asset)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 10.0)

    def test_weakly_crypto(self):
        self.assertTrue(weakly_crypto("RSA-1024"))
        self.assertTrue(weakly_crypto("DES"))
        self.assertTrue(weakly_crypto("3DES"))
        self.assertTrue(weakly_crypto("SHA-1"))
        self.assertFalse(weakly_crypto("RSA-2048"))
        self.assertFalse(weakly_crypto("ECC-224"))
        self.assertFalse(weakly_crypto(None))
        self.assertFalse(weakly_crypto(""))

    def test_quantum_risk_estimate(self):
        weak_asset = {**self.sample_asset, "crypto_profile": "RSA-1024"}
        safe_asset = {**self.sample_asset, "crypto_profile": "RSA-2048"}
        self.assertEqual(quantum_risk_estimate(weak_asset), 1.2)
        self.assertEqual(quantum_risk_estimate(safe_asset), 1.0)

    def test_compute_asset_cr_i(self):
        # Empty vulns -> 100
        self.assertEqual(compute_asset_cr_i(self.sample_asset, []), 100.0)
        # With vuln -> between 0 and 100
        cr_i = compute_asset_cr_i(self.sample_asset, [self.sample_vuln])
        self.assertGreaterEqual(cr_i, 0.0)
        self.assertLessEqual(cr_i, 100.0)

    def test_compute_overall_cr_i_both_signatures(self):
        import data_loader
        data_loader.init_db()
        assets = data_loader.get_assets()
        vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in assets}

        # Signature 1: (assets, vulns_by_asset)
        score1 = compute_overall_cr_i(assets, vulns_by_asset)
        self.assertGreaterEqual(score1, 0.0)
        self.assertLessEqual(score1, 100.0)

        # Signature 2: (vulns_by_asset_dict) with asset_id strings
        score2 = compute_overall_cr_i(vulns_by_asset)
        self.assertAlmostEqual(score1, score2, places=2)

    def test_expected_annual_loss(self):
        eal = expected_annual_loss(self.sample_vuln, self.sample_asset)
        self.assertGreater(eal, 0.0)

    def test_total_exposure(self):
        assets = [self.sample_asset]
        vulns_by_asset = {self.sample_asset["asset_id"]: [self.sample_vuln]}
        exp = total_exposure(assets, vulns_by_asset)
        self.assertGreater(exp, 0.0)
        # Empty case
        self.assertEqual(total_exposure([], {}), 0.0)

    def test_llm_remediate_languages(self):
        res_en = llm_remediate(self.sample_vuln, self.sample_asset, language="en")
        self.assertIn("steps", res_en)
        self.assertGreaterEqual(len(res_en["steps"]), 1)

        res_hi = llm_remediate(self.sample_vuln, self.sample_asset, language="hi")
        self.assertIn("steps", res_hi)
        self.assertGreaterEqual(len(res_hi["steps"]), 1)

    def test_optimize_budget(self):
        assets = [self.sample_asset]
        vulns_by_asset = {self.sample_asset["asset_id"]: [self.sample_vuln]}
        enriched = enrich_controls_with_reduction(list(CONTROLS.values()), assets, vulns_by_asset)

        # ₹1 Crore budget
        budget = 10_000_000
        plan = optimize_budget(enriched, budget, assets, vulns_by_asset)
        self.assertLessEqual(plan["total_cost"], budget)
        self.assertGreaterEqual(plan["total_reduction"], 0.0)
        self.assertGreaterEqual(plan["remaining_budget"], 0.0)

        # 0 budget
        plan_zero = optimize_budget(enriched, 0, assets, vulns_by_asset)
        self.assertEqual(plan_zero["total_cost"], 0.0)
        self.assertEqual(len(plan_zero["controls"]), 0)


if __name__ == "__main__":
    unittest.main()
