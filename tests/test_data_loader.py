import unittest
import tempfile
import os
import sqlite3
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

    def test_get_assets_filtered(self):
        # Test business unit filter
        payments_assets = data_loader.get_assets(business_unit="Payments")
        for a in payments_assets:
            self.assertEqual(a["business_unit"], "Payments")

        # Test asset type filter
        switch_assets = data_loader.get_assets(asset_type="UPI_SWITCH")
        for a in switch_assets:
            self.assertEqual(a["asset_type"], "UPI_SWITCH")

    def test_get_asset_by_id(self):
        asset = data_loader.get_asset("UPI_SWITCH_001")
        self.assertIsNotNone(asset)
        self.assertEqual(asset["asset_id"], "UPI_SWITCH_001")
        self.assertEqual(asset["asset_type"], "UPI_SWITCH")

    def test_get_vulnerabilities(self):
        all_vulns = data_loader.get_vulnerabilities()
        self.assertGreaterEqual(len(all_vulns), 17)

        # By asset_id
        switch_vulns = data_loader.get_vulnerabilities("UPI_SWITCH_001")
        self.assertGreaterEqual(len(switch_vulns), 1)
        for v in switch_vulns:
            self.assertEqual(v["asset_id"], "UPI_SWITCH_001")

        # By category
        auth_vulns = data_loader.get_vulnerabilities(category="Authentication Bypass")
        for v in auth_vulns:
            self.assertEqual(v["category"], "Authentication Bypass")

    def test_get_rbi_mapping(self):
        mapping = data_loader.get_rbi_mapping("UPI_SWITCH", "Authentication Bypass")
        self.assertIsNotNone(mapping)
        self.assertIn("rbi_clause", mapping)
        self.assertEqual(mapping["rbi_clause"], "RBI/2023-24/105.A.3")
        # Original UPI dataset has no NPCI/SEBI clause for this mapping
        self.assertFalse(mapping["nci_clause"])
        self.assertFalse(mapping["sebi_clause"])

    def test_get_all_rbi_mappings(self):
        mappings = data_loader.get_all_rbi_mappings()
        self.assertGreaterEqual(len(mappings), 17)
        # Verify all have required regulatory fields
        for m in mappings:
            self.assertIn("asset_type", m)
            self.assertIn("category", m)
            self.assertIn("rbi_clause", m)

    def test_get_incidents(self):
        incidents = data_loader.get_incidents()
        self.assertGreaterEqual(len(incidents), 1)

        # Test filtering by asset_id
        if incidents:
            asset_id = incidents[0]["asset_id"]
            filtered = data_loader.get_incidents(asset_id)
            for i in filtered:
                self.assertEqual(i["asset_id"], asset_id)

    def test_get_compliance_stats(self):
        stats = data_loader.get_compliance_stats()
        self.assertIn("total_mappings", stats)
        self.assertIn("rbi_mapped", stats)
        self.assertIn("npci_mapped", stats)
        self.assertIn("sebi_mapped", stats)
        self.assertIn("coverage_percentage", stats)
        self.assertGreaterEqual(stats["rbi_mapped"], 17)
        self.assertGreaterEqual(stats["coverage_percentage"], 90.0)

    def test_get_incident_stats(self):
        stats = data_loader.get_incident_stats()
        self.assertIn("total_incidents", stats)
        self.assertIn("total_loss_inr", stats)
        self.assertIn("total_downtime_hours", stats)
        self.assertIn("avg_loss_per_incident_inr", stats)
        self.assertGreaterEqual(stats["total_loss_inr"], 0)

    def test_get_controls(self):
        controls = data_loader.get_controls()
        self.assertGreaterEqual(len(controls), 5)

    def test_validate_data_pass(self):
        """Test that current dataset passes validation."""
        validation = data_loader.validate_data()
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(validation["error_count"], 0)
        self.assertIn("summary", validation)
        self.assertGreaterEqual(validation["summary"]["assets_count"], 10)
        self.assertGreaterEqual(validation["summary"]["vulnerabilities_count"], 17)

    def test_database_foreign_key_constraint(self):
        """Test that SQLite schema enforces Foreign Key integrity."""
        test_conn = sqlite3.connect(":memory:")
        test_conn.execute("PRAGMA foreign_keys = ON;")
        with open(data_loader.SCHEMA_PATH, encoding="utf-8") as f:
            test_conn.executescript(f.read())

        # Attempting to insert an orphaned vulnerability should raise IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            test_conn.execute(
                "INSERT INTO vulnerabilities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("V_FAIL", "NON_EXISTENT_ASSET", "CVE-2024-0001", 8.0, 1, 10, "SQL Injection", "API", "Test vuln")
            )

    def test_database_check_constraints(self):
        """Test that SQLite schema enforces CHECK constraints (criticality, CVSS)."""
        test_conn = sqlite3.connect(":memory:")
        with open(data_loader.SCHEMA_PATH, encoding="utf-8") as f:
            test_conn.executescript(f.read())

        # Criticality > 10 should fail CHECK constraint
        with self.assertRaises(sqlite3.IntegrityError):
            test_conn.execute(
                "INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("TEST_FAIL", "Invalid Asset", "CBS_SERVER", "Test Unit", 15, 1000, 1000000, 50000, "[]", "RSA-2048")
            )

        # Negative CVSS should fail CHECK constraint
        with self.assertRaises(sqlite3.IntegrityError):
            test_conn.execute(
                "INSERT INTO vulnerabilities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("V_FAIL_2", "TEST_ASSET", "CVE-2024-0001", -1.0, 1, 10, "SQL Injection", "API", "Test vuln")
            )

    def test_validate_data_integrity(self):
        """Test that Python validation layer detects anomalies."""
        test_conn = sqlite3.connect(":memory:")
        test_conn.row_factory = sqlite3.Row
        # Create tables without constraints to simulate raw dirty data import
        test_conn.execute("CREATE TABLE assets (asset_id TEXT, name TEXT, asset_type TEXT, business_unit TEXT, criticality INT, daily_transaction_volume INT, replacement_cost INT, downtime_cost_per_hour INT, user_segments TEXT, crypto_profile TEXT)")
        test_conn.execute("CREATE TABLE vulnerabilities (vuln_id TEXT, asset_id TEXT, cve_id TEXT, cvss_base_score REAL, exploit_available INT, days_unpatched INT, category TEXT, affected_component TEXT, description TEXT)")
        test_conn.execute("CREATE TABLE incidents (incident_id TEXT, asset_id TEXT, incident_type TEXT, financial_loss_inr INT, downtime_hours INT, incident_date DATE, description TEXT)")
        test_conn.execute("CREATE TABLE rbi_mappings (mapping_id TEXT, asset_type TEXT, category TEXT, rbi_clause TEXT, nci_clause TEXT, sebi_clause TEXT, description TEXT)")

        # Insert asset and orphaned vulnerability
        test_conn.execute("INSERT INTO assets VALUES ('A1', 'Asset 1', 'UPI_SWITCH', 'Payments', 5, 1000, 1000, 500, '[]', 'RSA-2048')")
        test_conn.execute("INSERT INTO vulnerabilities VALUES ('V1', 'NON_EXISTENT', 'CVE-1', 8.0, 1, 5, 'SQL Injection', 'API', 'desc')")
        test_conn.commit()

        validation = data_loader.validate_data(test_conn)
        self.assertEqual(validation["status"], "FAIL")
        self.assertTrue(any("non-existent asset" in e for e in validation["errors"]))

    def test_safe_type_casting(self):
        """Test safe type conversion functions."""
        self.assertEqual(data_loader._safe_int("10"), 10)
        self.assertEqual(data_loader._safe_int("10.7"), 10)
        self.assertEqual(data_loader._safe_int("invalid", 99), 99)
        self.assertEqual(data_loader._safe_int(None, 5), 5)

        self.assertEqual(data_loader._safe_float("7.5"), 7.5)
        self.assertEqual(data_loader._safe_float("invalid", 1.5), 1.5)

        self.assertEqual(data_loader._safe_bool("true"), 1)
        self.assertEqual(data_loader._safe_bool("1"), 1)
        self.assertEqual(data_loader._safe_bool("yes"), 1)
        self.assertEqual(data_loader._safe_bool("false"), 0)
        self.assertEqual(data_loader._safe_bool("0"), 0)
        self.assertEqual(data_loader._safe_bool(True), 1)
        self.assertEqual(data_loader._safe_bool(False), 0)

    def test_export_compliance_report_json(self):
        """Test compliance report export to JSON format."""
        import json
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            result = data_loader.export_compliance_report(
                output_dir=tmpdir,
                formats=["json"],
                conn=data_loader.get_connection()
            )

            self.assertEqual(result["status"], "SUCCESS")
            self.assertEqual(len(result["files_generated"]), 1)
            self.assertTrue(result["files_generated"][0].endswith("compliance_report.json"))

            # Verify JSON content
            with open(result["files_generated"][0], "r", encoding="utf-8") as f:
                report = json.load(f)

            self.assertIn("report_metadata", report)
            self.assertIn("executive_summary", report)
            self.assertIn("vulnerability_compliance_details", report)
            self.assertIn("asset_compliance_summary", report)

            # Verify summary counts
            summary = report["executive_summary"]
            self.assertGreaterEqual(summary["total_vulnerabilities"], 17)
            self.assertGreaterEqual(summary["compliance_coverage"]["coverage_percentage"], 90.0)

    def test_export_compliance_report_csv(self):
        """Test compliance report export to CSV format."""
        import csv
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = data_loader.export_compliance_report(
                output_dir=tmpdir,
                formats=["csv"],
                conn=data_loader.get_connection()
            )

            self.assertEqual(result["status"], "SUCCESS")
            self.assertGreaterEqual(len(result["files_generated"]), 1)
            self.assertTrue(any("compliance_report.csv" in f for f in result["files_generated"]))

            # Verify CSV content
            csv_file = next(f for f in result["files_generated"] if "compliance_report.csv" in f)
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self.assertGreaterEqual(len(rows), 17)
            # Check required columns
            self.assertIn("vuln_id", rows[0])
            self.assertIn("asset_id", rows[0])
            self.assertIn("rbi_clause", rows[0])
            self.assertIn("compliance_status", rows[0])

    def test_export_compliance_report_both_formats(self):
        """Test compliance report export to both JSON and CSV."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = data_loader.export_compliance_report(
                output_dir=tmpdir,
                formats=["json", "csv"],
                conn=data_loader.get_connection()
            )

            self.assertEqual(result["status"], "SUCCESS")
            self.assertGreaterEqual(len(result["files_generated"]), 2)

            # Verify both formats present
            files = result["files_generated"]
            self.assertTrue(any("compliance_report.json" in f for f in files))
            self.assertTrue(any("compliance_report.csv" in f for f in files))

    def test_export_compliance_report_coverage_metrics(self):
        """Test that compliance report includes accurate regulatory coverage."""
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = data_loader.export_compliance_report(
                output_dir=tmpdir,
                formats=["json"],
                conn=data_loader.get_connection()
            )

            with open(result["files_generated"][0], "r", encoding="utf-8") as f:
                report = json.load(f)

            coverage = report["executive_summary"]["regulatory_framework_coverage"]

            # Original UPI dataset: all 17 vulns map to an RBI clause -> 100% RBI
            self.assertEqual(coverage["rbi"]["covered"], 17)
            self.assertEqual(coverage["rbi"]["percentage"], 100.0)

            # NPCI field: 3 vulns carry an NCI clause (CBS, WEB, DB privilege escalation)
            self.assertEqual(coverage["npci"]["covered"], 3)

            # SEBI field: 1 vuln carries an SEBI clause (UPI data exposure)
            self.assertEqual(coverage["sebi"]["covered"], 1)

    def test_export_compliance_report_asset_summary(self):
        """Test per-asset compliance summary generation."""
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = data_loader.export_compliance_report(
                output_dir=tmpdir,
                formats=["json"],
                conn=data_loader.get_connection()
            )

            with open(result["files_generated"][0], "r", encoding="utf-8") as f:
                report = json.load(f)

            asset_summary = report["asset_compliance_summary"]

            # Should have all 10 assets
            self.assertGreaterEqual(len(asset_summary), 10)

            # Each asset should have required fields
            for asset_id, summary in asset_summary.items():
                self.assertIn("asset_name", summary)
                self.assertIn("asset_type", summary)
                self.assertIn("total_vulnerabilities", summary)
                self.assertIn("mapped", summary)
                self.assertIn("gaps", summary)
                self.assertIn("coverage_percentage", summary)

    def test_verify_compliance_consistency_structure(self):
        """Cross-verification returns a consistent report shape."""
        report = data_loader.verify_compliance_consistency()
        self.assertIn("pass", report)
        self.assertIn("checks", report)
        self.assertIn("summary", report)
        self.assertIsInstance(report["checks"], list)
        self.assertGreaterEqual(len(report["checks"]), 4)
        # Summary totals add up
        s = report["summary"]
        self.assertEqual(s["total_checks"], len(report["checks"]))
        self.assertEqual(s["passed"] + s["failed"], s["total_checks"])

    def test_verify_compliance_consistency_all_pass(self):
        """All consistency checks pass against the live data layer."""
        report = data_loader.verify_compliance_consistency()
        self.assertTrue(report["pass"], f"Checks failed: {report['checks']}")
        for check in report["checks"]:
            self.assertTrue(check["pass"], f"Check '{check['name']}' failed: {check}")

    def test_verify_compliance_consistency_stats_match_db(self):
        """get_compliance_stats() matches the raw rbi_mappings query."""
        report = data_loader.verify_compliance_consistency()
        check = next(c for c in report["checks"] if c["name"] == "compliance_stats_vs_db")
        self.assertTrue(check["pass"])
        self.assertEqual(check["expected"], check["actual"])

    def test_verify_compliance_consistency_vulns_mapped(self):
        """Every vulnerability resolves to an (asset_type, category) mapping."""
        report = data_loader.verify_compliance_consistency()
        check = next(c for c in report["checks"] if c["name"] == "per_vuln_mapping_coverage")
        self.assertTrue(check["pass"])
        self.assertEqual(check["total_vulns"], check["mapped_vulns"])
        self.assertEqual(check["unmapped_vulns"], [])

    def test_verify_compliance_consistency_risk_matrix_agrees(self):
        """Risk engine coverage matches the data_loader coverage percentage."""
        report = data_loader.verify_compliance_consistency()
        check = next(c for c in report["checks"] if c["name"] == "risk_matrix_vs_data_loader")
        self.assertTrue(check["pass"])
        self.assertAlmostEqual(check["risk_engine_coverage"],
                               check["data_loader_coverage"], delta=1.0)

    def test_verify_compliance_consistency_export_agrees(self):
        """Export report coverage matches live data-layer stats."""
        report = data_loader.verify_compliance_consistency()
        check = next(c for c in report["checks"] if c["name"] == "export_report_vs_live")
        self.assertTrue(check["pass"])
        self.assertEqual(check["report_covered"], check["live_rbi_mapped"])

    def test_load_judge_demo_scenario_structure(self):
        """Test the before/after breach simulation returns expected sections."""
        scenario = data_loader.load_judge_demo_scenario(conn=data_loader.get_connection())

        # Top-level sections
        self.assertIn("scenario", scenario)
        self.assertIn("breach", scenario)
        self.assertIn("before", scenario)
        self.assertIn("after", scenario)
        self.assertIn("delta", scenario)
        self.assertIn("narrative", scenario)

        # Before metrics
        before = scenario["before"]
        self.assertIn("overall_cr_i", before)
        self.assertIn("total_exposure_inr", before)
        self.assertGreaterEqual(before["assets_count"], 10)
        self.assertGreaterEqual(before["vulnerabilities_count"], 17)
        self.assertGreaterEqual(before["total_exposure_inr"], 0)

        # Breach details
        breach = scenario["breach"]
        self.assertIn("asset_id", breach)
        self.assertIn("realized_single_loss_inr", breach)
        self.assertGreaterEqual(breach["realized_single_loss_inr"], 0)
        self.assertIn("rbi_clause", breach["peak_vulnerability"])

        # After metrics
        after = scenario["after"]
        self.assertGreaterEqual(after["control_plan_reduction_inr"], 0)
        self.assertLessEqual(after["control_plan_reduction_pct"], 100.0)
        self.assertIn("recommended_controls", after)

    def test_load_judge_demo_scenario_narrative(self):
        """Test scenario includes a non-empty judge-facing narrative."""
        scenario = data_loader.load_judge_demo_scenario(conn=data_loader.get_connection())
        self.assertTrue(len(scenario["narrative"]) > 100)

    def test_load_judge_demo_scenario_breach_target_override(self):
        """Test caller can override the breach asset."""
        scenario = data_loader.load_judge_demo_scenario(
            conn=data_loader.get_connection(),
            breach_asset_id="UPI_SWITCH_001",
        )
        self.assertEqual(scenario["breach"]["asset_id"], "UPI_SWITCH_001")
        self.assertEqual(scenario["breach"]["asset_name"], "NPCI UPI Switch")
        # Narrative refers to the breached asset by name
        self.assertIn("NPCI UPI Switch", scenario["narrative"])

    def test_load_judge_demo_scenario_top_risk_sorted(self):
        """Test top-risk assets are sorted descending by EAL."""
        scenario = data_loader.load_judge_demo_scenario(conn=data_loader.get_connection())
        top = scenario["before"]["top_risk_assets"]
        self.assertGreaterEqual(len(top), 3)
        eals = [t["ean_eal_inr"] for t in top]
        self.assertEqual(eals, sorted(eals, reverse=True))

    def test_export_demo_scenario_markdown(self):
        """Test markdown export writes a file and returns content."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "DEMO_SCENARIO_REPORT.md")
            scenario = data_loader.load_judge_demo_scenario(conn=data_loader.get_connection())
            content = data_loader.export_demo_scenario_markdown(scenario, path=out)

            self.assertTrue(os.path.exists(out))
            self.assertGreater(len(content), 200)
            # Content should mention the before/after framing
            self.assertIn("Before/After", content)
            self.assertIn("Breach", content)
            # Top-risk asset table should be present
            self.assertIn("Top 5 Assets", content)

    # --- Phase 2.4: CSV Upload Pre-flight Validator Tests ---

    def test_validate_csv_upload_assets_valid(self):
        """Test valid assets CSV passes validation."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "assets.csv")
            # Write a valid assets CSV
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "asset_id", "name", "asset_type", "business_unit", "criticality",
                    "daily_transaction_volume", "replacement_cost", "downtime_cost_per_hour",
                    "user_segments", "crypto_profile",
                ])
                writer.writerow([
                    "TEST_001", "Test Asset", "WEB_BANKING_PORTAL", "Online Banking", "5",
                    "100000", "5000000", "100000", '["retail"]', "RSA-2048",
                ])

            result = data_loader.validate_csv_upload(csv_path, "assets", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["row_count"], 1)
            self.assertEqual(result["errors"], [])

    def test_validate_csv_upload_assets_missing_column(self):
        """Test assets CSV missing required column fails."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "assets.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "asset_id", "name", "asset_type", "business_unit",  # missing criticality, etc.
                ])
                writer.writerow(["TEST_001", "Test Asset", "WEB_BANKING_PORTAL", "Online Banking"])

            result = data_loader.validate_csv_upload(csv_path, "assets", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Missing required columns" in e for e in result["errors"]))

    def test_validate_csv_upload_assets_invalid_criticality(self):
        """Test assets CSV with out-of-range criticality fails."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "assets.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "asset_id", "name", "asset_type", "business_unit", "criticality",
                    "daily_transaction_volume", "replacement_cost", "downtime_cost_per_hour",
                    "user_segments", "crypto_profile",
                ])
                writer.writerow([
                    "TEST_001", "Test Asset", "WEB_BANKING_PORTAL", "Online Banking", "15",  # > 10
                    "100000", "5000000", "100000", '["retail"]', "RSA-2048",
                ])

            result = data_loader.validate_csv_upload(csv_path, "assets", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("below minimum" in e or "above maximum" in e for e in result["errors"]))

    def test_validate_csv_upload_vulnerabilities_valid(self):
        """Test valid vulnerabilities CSV passes validation."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "vulns.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "vuln_id", "asset_id", "cve_id", "cvss_base_score", "exploit_available",
                    "days_unpatched", "category", "affected_component", "description",
                ])
                writer.writerow([
                    "V_TEST_001", "UPI_SWITCH_001", "CVE-2024-0001", "7.5", "true",
                    "10", "SQL Injection", "API", "Test vulnerability",
                ])

            result = data_loader.validate_csv_upload(csv_path, "vulnerabilities", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["row_count"], 1)

    def test_validate_csv_upload_vulnerabilities_fk_violation(self):
        """Test vulnerabilities CSV with non-existent asset_id fails."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "vulns.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "vuln_id", "asset_id", "cve_id", "cvss_base_score", "exploit_available",
                    "days_unpatched", "category", "affected_component", "description",
                ])
                writer.writerow([
                    "V_TEST_001", "NON_EXISTENT_ASSET", "CVE-2024-0001", "7.5", "true",
                    "10", "SQL Injection", "API", "Test vulnerability",
                ])

            result = data_loader.validate_csv_upload(csv_path, "vulnerabilities", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("non-existent asset_id" in e for e in result["errors"]))

    def test_validate_csv_upload_vulnerabilities_invalid_cvss(self):
        """Test vulnerabilities CSV with out-of-range CVSS fails."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "vulns.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "vuln_id", "asset_id", "cve_id", "cvss_base_score", "exploit_available",
                    "days_unpatched", "category", "affected_component", "description",
                ])
                writer.writerow([
                    "V_TEST_001", "UPI_SWITCH_001", "CVE-2024-0001", "11.0", "true",  # > 10
                    "10", "SQL Injection", "API", "Test vulnerability",
                ])

            result = data_loader.validate_csv_upload(csv_path, "vulnerabilities", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("above maximum" in e for e in result["errors"]))

    def test_validate_csv_upload_incidents_valid(self):
        """Test valid incidents CSV passes validation."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "incidents.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "incident_id", "asset_id", "incident_type", "financial_loss_inr",
                    "downtime_hours", "incident_date", "description",
                ])
                writer.writerow([
                    "INC_TEST_001", "UPI_SWITCH_001", "Fraud", "1000000",
                    "2", "2024-01-15", "Test incident",
                ])

            result = data_loader.validate_csv_upload(csv_path, "incidents", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["row_count"], 1)

    def test_validate_csv_upload_rbi_mappings_valid(self):
        """Test valid rbi_mappings CSV passes validation."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "mappings.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "mapping_id", "asset_type", "category", "rbi_clause", "nci_clause",
                    "sebi_clause", "description",
                ])
                writer.writerow([
                    "RMAP_TEST", "TEST_TYPE", "Test Category", "RBI/TEST", "NPCI/TEST",
                    "SEBI/TEST", "Test mapping",
                ])

            result = data_loader.validate_csv_upload(csv_path, "rbi_mappings", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["row_count"], 1)

    def test_validate_csv_upload_unknown_table(self):
        """Test unknown table name fails."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "unknown.csv")
            with open(csv_path, "w") as f:
                f.write("a,b\n1,2\n")

            result = data_loader.validate_csv_upload(csv_path, "unknown_table", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Unknown table" in e for e in result["errors"]))

    def test_validate_csv_upload_missing_file(self):
        """Test missing file fails."""
        result = data_loader.validate_csv_upload("/nonexistent/path.csv", "assets", conn=data_loader.get_connection())
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("File not found" in e for e in result["errors"]))

    def test_validate_csv_upload_assets_duplicate_id(self):
        """Test duplicate asset_ids in CSV fails."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "assets.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "asset_id", "name", "asset_type", "business_unit", "criticality",
                    "daily_transaction_volume", "replacement_cost", "downtime_cost_per_hour",
                    "user_segments", "crypto_profile",
                ])
                writer.writerow(["TEST_001", "Asset 1", "WEB_BANKING_PORTAL", "Online", "5", "1000", "1000", "100", '["retail"]', "RSA-2048"])
                writer.writerow(["TEST_001", "Asset 2", "WEB_BANKING_PORTAL", "Online", "5", "1000", "1000", "100", '["retail"]', "RSA-2048"])

            result = data_loader.validate_csv_upload(csv_path, "assets", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Duplicate asset_ids" in e for e in result["errors"]))

    def test_validate_csv_upload_extra_columns_warning(self):
        """Test extra columns produce warning but not error."""
        import tempfile
        import os
        import csv

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "assets.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "asset_id", "name", "asset_type", "business_unit", "criticality",
                    "daily_transaction_volume", "replacement_cost", "downtime_cost_per_hour",
                    "user_segments", "crypto_profile", "extra_col",
                ])
                writer.writerow(["TEST_001", "Asset 1", "WEB_BANKING_PORTAL", "Online", "5", "1000", "1000", "100", '["retail"]', "RSA-2048", "extra_val"])

            result = data_loader.validate_csv_upload(csv_path, "assets", conn=data_loader.get_connection())
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(any("Extra columns" in w for w in result["warnings"]))

    # --- Phase 2.5: Multi-Institution Banking Profiles Tests ---

    def test_load_banking_profile_payment_bank(self):
        """Test loading Payment Bank profile."""
        import tempfile
        result = data_loader.load_banking_profile("payment_bank", db_path=":memory:")

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["profile_name"], "payment_bank")
        self.assertGreaterEqual(result["assets_count"], 4)
        self.assertGreaterEqual(result["vulnerabilities_count"], 4)
        self.assertGreater(result["total_exposure_inr"], 0)
        self.assertGreater(result["overall_cr_i"], 0)

    def test_load_banking_profile_small_finance_bank(self):
        """Test loading Small Finance Bank profile."""
        result = data_loader.load_banking_profile("small_finance_bank", db_path=":memory:")

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["profile_name"], "small_finance_bank")
        self.assertGreaterEqual(result["assets_count"], 6)
        self.assertGreaterEqual(result["vulnerabilities_count"], 7)

    def test_load_banking_profile_coop_bank(self):
        """Test loading Co-operative Bank profile (legacy weak crypto)."""
        result = data_loader.load_banking_profile("coop_bank", db_path=":memory:")

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["profile_name"], "coop_bank")
        # Co-op has weak crypto, so CR-I should be lower than other profiles for similar assets
        self.assertLessEqual(result["overall_cr_i"], 50.0)

    def test_load_banking_profile_unknown(self):
        """Test loading unknown profile fails."""
        result = data_loader.load_banking_profile("unknown_bank", db_path=":memory:")

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Unknown profile", result.get("error", ""))

    def test_load_banking_profile_replaces_data(self):
        """Test loading a profile replaces existing data."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")

            # Load first profile
            result1 = data_loader.load_banking_profile("payment_bank", db_path=db_path)
            count1 = result1["assets_count"]

            # Load different profile
            result2 = data_loader.load_banking_profile("small_finance_bank", db_path=db_path)
            count2 = result2["assets_count"]

            # Second profile should have different asset count
            self.assertNotEqual(count1, count2)
            self.assertEqual(result2["assets_count"], 7)

    def test_get_available_profiles(self):
        """Test getting list of available profiles."""
        profiles = data_loader.get_available_profiles()

        self.assertGreaterEqual(len(profiles), 3)
        profile_ids = [p["id"] for p in profiles]
        self.assertIn("payment_bank", profile_ids)
        self.assertIn("small_finance_bank", profile_ids)
        self.assertIn("coop_bank", profile_ids)

        # Each profile should have id, name, description
        for p in profiles:
            self.assertIn("id", p)
            self.assertIn("name", p)
            self.assertIn("description", p)

    def test_banking_profiles_have_quantum_risk(self):
        """Test that coop_bank profile has weak crypto for quantum risk multiplier."""
        import tempfile
        import risk_engine as re

        # Load coop_bank into an isolated temp-file DB so we can inspect its assets.
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "coop.db")
            data_loader.load_banking_profile("coop_bank", db_path=db_path)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            assets = data_loader._rows(conn.execute("SELECT * FROM assets").fetchall())
            conn.close()

            # Coop should have RSA-1024 or MD5 (weak crypto)
            weak_crypto_assets = [a for a in assets if re.weakly_crypto(a.get("crypto_profile", ""))]

            self.assertGreater(len(weak_crypto_assets), 0,
                               "Coop bank should have weak crypto assets for quantum risk demo")

    def test_payment_bank_profile_metrics(self):
        """Test Payment Bank profile produces reasonable metrics."""
        result = data_loader.load_banking_profile("payment_bank", db_path=":memory:")

        # Payment bank should have:
        # - 5 assets
        # - ~5 vulnerabilities
        # - 1 incident
        # - Positive total exposure
        # - CR-I between 0 and 100
        self.assertEqual(result["assets_count"], 5)
        self.assertEqual(result["vulnerabilities_count"], 5)
        self.assertEqual(result["incidents_count"], 1)
        self.assertGreater(result["total_exposure_inr"], 0)
        self.assertGreaterEqual(result["overall_cr_i"], 0)
        self.assertLessEqual(result["overall_cr_i"], 100)

    def test_banking_profiles_scenario_generation(self):
        """Test that breach demo works with loaded banking profiles."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            report_path = os.path.join(tmpdir, "DEMO_SCENARIO_REPORT.md")

            # Load payment bank profile
            data_loader.load_banking_profile("payment_bank", db_path=db_path)
            conn = data_loader.get_connection(db_path)

            # Generate breach scenario (with report path inside temp dir to avoid locks)
            scenario = data_loader.load_judge_demo_scenario(conn=conn)
            data_loader.export_demo_scenario_markdown(scenario, path=report_path, conn=conn)

            # Close connection and disable WAL to release all file handles (Windows requirement)
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.close()

            self.assertIn("before", scenario)
            self.assertIn("breach", scenario)
            self.assertIn("after", scenario)
            self.assertEqual(scenario["before"]["assets_count"], 5)


if __name__ == "__main__":
    unittest.main()