import unittest
import data_loader


class TestDataLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_loader.init_db()

    def test_get_assets(self):
        assets = data_loader.get_assets()
        self.assertGreaterEqual(len(assets), 10)
        # Check asset fields
        first = assets[0]
        self.assertIn("asset_id", first)
        self.assertIn("name", first)
        self.assertIn("criticality", first)
        self.assertIn("daily_transaction_volume", first)

    def test_get_asset_by_id(self):
        asset = data_loader.get_asset("UPI_SWITCH_001")
        self.assertIsNotNone(asset)
        self.assertEqual(asset["asset_id"], "UPI_SWITCH_001")
        self.assertEqual(asset["asset_type"], "UPI_SWITCH")

    def test_get_vulnerabilities(self):
        all_vulns = data_loader.get_vulnerabilities()
        self.assertGreaterEqual(len(all_vulns), 17)

        # By asset_id
        upi_vulns = data_loader.get_vulnerabilities("UPI_SWITCH_001")
        self.assertGreaterEqual(len(upi_vulns), 1)
        for v in upi_vulns:
            self.assertEqual(v["asset_id"], "UPI_SWITCH_001")

    def test_get_rbi_mapping(self):
        mapping = data_loader.get_rbi_mapping("UPI_SWITCH", "Authentication Bypass")
        self.assertIsNotNone(mapping)
        self.assertIn("rbi_clause", mapping)
        self.assertEqual(mapping["rbi_clause"], "RBI/2023-24/105.A.3")

    def test_get_incidents(self):
        incidents = data_loader.get_incidents()
        self.assertGreaterEqual(len(incidents), 1)

    def test_get_controls(self):
        controls = data_loader.get_controls()
        self.assertGreaterEqual(len(controls), 5)


if __name__ == "__main__":
    unittest.main()
