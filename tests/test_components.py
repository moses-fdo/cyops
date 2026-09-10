import unittest
import os
import data_loader
from components.widgets import inr, inr_indian
from components.executive_view import compliance_pct, risk_badge
from components.sih_features import load_demo_scenario, reset_full_portfolio, generate_sih_summary
from risk_engine import compute_risk_matrix


class TestComponents(unittest.TestCase):

    def setUp(self):
        data_loader.init_db()
        self.assets = data_loader.get_assets()
        self.vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in self.assets}
        self.risk_matrix = compute_risk_matrix(self.assets, self.vulns_by_asset)

    def test_inr_formatting(self):
        self.assertEqual(inr(0), "₹0")
        self.assertEqual(inr(500), "₹500")
        self.assertEqual(inr(1000), "₹1,000")
        self.assertEqual(inr(25000), "₹25,000")
        self.assertEqual(inr(100000), "₹1,00,000")
        self.assertEqual(inr(10000000), "₹1,00,00,000")
        self.assertEqual(inr(42000000000), "₹42,00,00,00,000")
        self.assertEqual(inr(-50000), "-₹50,000")
        self.assertEqual(inr(None), "₹0")

    def test_compliance_pct(self):
        pct = compliance_pct(self.risk_matrix)
        self.assertGreaterEqual(pct, 0.0)
        self.assertLessEqual(pct, 100.0)
        self.assertEqual(compliance_pct([]), 100.0)

    def test_risk_badge(self):
        self.assertIn("CRITICAL", risk_badge(15000000))
        self.assertIn("HIGH", risk_badge(6000000))
        self.assertIn("MEDIUM", risk_badge(2000000))
        self.assertIn("LOW", risk_badge(600000))
        self.assertIn("MINIMAL", risk_badge(100000))

    def test_sih_features_demo_and_reset(self):
        session = {
            "assets": list(self.assets),
            "vulns_by_asset": dict(self.vulns_by_asset),
            "risk_matrix": list(self.risk_matrix),
            "audit_log": [],
        }
        # Load demo scenario
        load_demo_scenario(session)
        self.assertEqual(len(session["assets"]), 5)

        # Generate summary
        generate_sih_summary(session)
        self.assertTrue(os.path.exists("SIH_Submission.md"))

        # Reset full portfolio
        reset_full_portfolio(session)
        self.assertEqual(len(session["assets"]), 10)


if __name__ == "__main__":
    unittest.main()
