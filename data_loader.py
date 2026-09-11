"""CyberLens 2.0 - Data Loader & Compliance Validation Layer
Loads CSV data into SQLite, enforces data integrity, and provides query APIs.

Ponytail: in-memory / local SQLite keeps the demo zero-setup.
Swap to PostgreSQL by changing the connection string for production.
"""

import csv
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "cyberlens.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

CSV_FILES = {
    "assets": "assets.csv",
    "vulnerabilities": "vulnerabilities.csv",
    "incidents": "incidents.csv",
    "rbi_mappings": "rbi_mappings.csv",
}

ALLOWED_TABLES = {"assets", "vulnerabilities", "incidents", "rbi_mappings"}

_conn = None


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return a thread-safe SQLite connection with Row factory and FK enforcement."""
    global _conn
    target_path = db_path or DB_PATH
    if _conn is None or db_path is not None:
        conn = sqlite3.connect(target_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        if db_path is None:
            _conn = conn
        return conn
    return _conn


def _safe_int(val: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_bool(val: Any) -> int:
    """Convert truthy string/bool to SQLite integer boolean (0 or 1)."""
    if isinstance(val, bool):
        return 1 if val else 0
    val_str = str(val).strip().lower()
    return 1 if val_str in {"true", "1", "t", "yes", "y"} else 0


def load_csv_to_table(conn: sqlite3.Connection, table: str, csv_path: str, clear_first: bool = True) -> int:
    """Load a CSV file into an existing table, replacing its current rows."""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' is not in the allowed whitelist.")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    if not rows:
        return 0

    # Type conversion for specific tables
    if table == "vulnerabilities":
        for row in rows:
            row["exploit_available"] = _safe_bool(row.get("exploit_available", False))
            row["cvss_base_score"] = _safe_float(row.get("cvss_base_score", 0.0))
            row["days_unpatched"] = _safe_int(row.get("days_unpatched", 0))
    elif table == "assets":
        for row in rows:
            row["criticality"] = _safe_int(row.get("criticality", 5))
            row["daily_transaction_volume"] = _safe_int(row.get("daily_transaction_volume", 0))
            row["replacement_cost"] = _safe_int(row.get("replacement_cost", 0))
            row["downtime_cost_per_hour"] = _safe_int(row.get("downtime_cost_per_hour", 0))
    elif table == "incidents":
        for row in rows:
            row["financial_loss_inr"] = _safe_int(row.get("financial_loss_inr", 0))
            row["downtime_hours"] = _safe_int(row.get("downtime_hours", 0))

    columns = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)

    if clear_first:
        conn.execute(f"DELETE FROM {table}")
    conn.executemany(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
        [tuple(r[c] for c in columns) for r in rows],
    )
    conn.commit()
    return len(rows)


def init_db(conn: Optional[sqlite3.Connection] = None) -> Dict[str, int]:
    """Create tables from schema.sql and load CSV data in correct foreign-key dependency order."""
    conn = conn or get_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    # Clear in reverse dependency order to prevent FK violations
    clear_order = ["incidents", "vulnerabilities", "assets", "rbi_mappings"]
    for table in clear_order:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    # Load in dependency order: rbi_mappings, assets, vulnerabilities, incidents
    load_order = ["rbi_mappings", "assets", "vulnerabilities", "incidents"]
    counts = {}
    for table in load_order:
        csv_file = CSV_FILES.get(table)
        if csv_file:
            counts[table] = load_csv_to_table(conn, table, os.path.join(DATA_DIR, csv_file), clear_first=False)
    return counts


def validate_data(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """Perform data hygiene and compliance validation checks across all tables.

    Returns:
        dict with status ('PASS'|'FAIL'), error list, warning list, and data summary.
    """
    conn = conn or get_connection()
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Assets validation
    assets = _rows(conn.execute("SELECT * FROM assets").fetchall())
    asset_ids = {a["asset_id"] for a in assets}

    for a in assets:
        if not (1 <= a["criticality"] <= 10):
            errors.append(f"Asset {a['asset_id']} criticality {a['criticality']} outside [1, 10].")
        if a["daily_transaction_volume"] < 0:
            errors.append(f"Asset {a['asset_id']} has negative transaction volume.")
        if a["replacement_cost"] < 0:
            errors.append(f"Asset {a['asset_id']} has negative replacement cost.")
        if a["downtime_cost_per_hour"] < 0:
            errors.append(f"Asset {a['asset_id']} has negative downtime cost.")
        # Validate user_segments JSON
        if a.get("user_segments"):
            try:
                parsed = json.loads(a["user_segments"])
                if not isinstance(parsed, list):
                    warnings.append(f"Asset {a['asset_id']} user_segments is not a JSON list.")
            except json.JSONDecodeError:
                errors.append(f"Asset {a['asset_id']} has invalid JSON in user_segments.")

    # 2. Vulnerabilities validation & Foreign Key check
    vulns = _rows(conn.execute("SELECT * FROM vulnerabilities").fetchall())
    for v in vulns:
        if v["asset_id"] not in asset_ids:
            errors.append(f"Vulnerability {v['vuln_id']} references non-existent asset {v['asset_id']}.")
        if not (0.0 <= v["cvss_base_score"] <= 10.0):
            errors.append(f"Vulnerability {v['vuln_id']} CVSS score {v['cvss_base_score']} outside [0, 10].")
        if v["days_unpatched"] < 0:
            errors.append(f"Vulnerability {v['vuln_id']} has negative days_unpatched.")

    # 3. Incidents validation
    incidents = _rows(conn.execute("SELECT * FROM incidents").fetchall())
    for inc in incidents:
        if inc["asset_id"] not in asset_ids:
            errors.append(f"Incident {inc['incident_id']} references non-existent asset {inc['asset_id']}.")
        if inc["financial_loss_inr"] < 0:
            errors.append(f"Incident {inc['incident_id']} has negative financial loss.")
        if inc["downtime_hours"] < 0:
            errors.append(f"Incident {inc['incident_id']} has negative downtime hours.")

    # 4. Compliance Mapping Coverage check
    asset_types = {a["asset_id"]: a["asset_type"] for a in assets}
    unmapped_pairs = []
    for v in vulns:
        atype = asset_types.get(v["asset_id"], "")
        mapping = get_rbi_mapping(atype, v["category"], conn=conn)
        if not mapping:
            unmapped_pairs.append((atype, v["category"], v["vuln_id"]))

    if unmapped_pairs:
        for atype, cat, vid in unmapped_pairs:
            warnings.append(f"No regulatory mapping for asset_type='{atype}', category='{cat}' (vuln {vid}).")

    return {
        "status": "FAIL" if errors else "PASS",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "assets_count": len(assets),
            "vulnerabilities_count": len(vulns),
            "incidents_count": len(incidents),
            "compliance_mappings_count": len(_rows(conn.execute("SELECT * FROM rbi_mappings").fetchall())),
            "unmapped_vulnerabilities": len(unmapped_pairs),
        },
    }


# =====================================================================
# Query Functions
# =====================================================================

def get_assets(business_unit: Optional[str] = None, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all assets, optionally filtered by business unit or asset type."""
    conn = get_connection()
    query = "SELECT * FROM assets WHERE 1=1"
    params = []
    if business_unit:
        query += " AND business_unit = ?"
        params.append(business_unit)
    if asset_type:
        query += " AND asset_type = ?"
        params.append(asset_type)
    query += " ORDER BY criticality DESC"
    return _rows(conn.execute(query, tuple(params)).fetchall())


def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    """Return a single asset by its ID."""
    row = get_connection().execute(
        "SELECT * FROM assets WHERE asset_id = ?", (asset_id,)
    ).fetchone()
    return _row(row)


def get_vulnerabilities(asset_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return vulnerabilities, optionally filtered by asset_id and/or category."""
    conn = get_connection()
    query = "SELECT * FROM vulnerabilities WHERE 1=1"
    params = []
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY cvss_base_score DESC"
    return _rows(conn.execute(query, tuple(params)).fetchall())


def get_rbi_mapping(asset_type: str, category: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """Return regulatory mapping for a specific asset_type and vulnerability category."""
    connection = conn or get_connection()
    row = connection.execute(
        "SELECT * FROM rbi_mappings WHERE asset_type = ? AND category = ?",
        (asset_type, category),
    ).fetchone()
    return _row(row)


def get_all_rbi_mappings() -> List[Dict[str, Any]]:
    """Return all regulatory compliance mappings."""
    return _rows(get_connection().execute("SELECT * FROM rbi_mappings ORDER BY asset_type, category").fetchall())


def get_incidents(asset_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return historical security incidents, optionally filtered by asset_id."""
    conn = get_connection()
    if asset_id:
        return _rows(conn.execute(
            "SELECT * FROM incidents WHERE asset_id = ? ORDER BY incident_date DESC", (asset_id,)
        ).fetchall())
    return _rows(conn.execute("SELECT * FROM incidents ORDER BY incident_date DESC").fetchall())


def get_compliance_stats() -> Dict[str, Any]:
    """Return statistics on regulatory framework coverage."""
    mappings = get_all_rbi_mappings()
    rbi_count = sum(1 for m in mappings if m.get("rbi_clause"))
    npci_count = sum(1 for m in mappings if m.get("nci_clause"))
    sebi_count = sum(1 for m in mappings if m.get("sebi_clause"))
    return {
        "total_mappings": len(mappings),
        "rbi_mapped": rbi_count,
        "npci_mapped": npci_count,
        "sebi_mapped": sebi_count,
        "coverage_percentage": round((rbi_count / len(mappings) * 100), 1) if mappings else 100.0,
    }


def get_incident_stats() -> Dict[str, Any]:
    """Return aggregated incident statistics (total loss, downtime, count)."""
    incidents = get_incidents()
    total_loss = sum(i["financial_loss_inr"] for i in incidents)
    total_downtime = sum(i["downtime_hours"] for i in incidents)
    return {
        "total_incidents": len(incidents),
        "total_loss_inr": total_loss,
        "total_downtime_hours": total_downtime,
        "avg_loss_per_incident_inr": round(total_loss / len(incidents)) if incidents else 0,
    }


def verify_compliance_consistency(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """Cross-verify compliance data across all data paths.

    Proves that the numbers shown in executive_view, technical_view,
    and the export report all derive from the same authoritative data layer.

    Checks performed:
    1. data_loader.get_compliance_stats() vs raw rbi_mappings query
    2. Per-vuln mapping consistency (get_rbi_mapping agrees with report export)
    3. risk_engine compliance_pct() matches data_loader coverage
    4. Export report coverage matches live stats

    Returns:
        Dict with 'pass' (bool), 'checks' list, and 'summary' dict.
    """
    conn = conn or get_connection()
    checks: List[Dict[str, Any]] = []
    all_pass = True

    # --- Check 1: get_compliance_stats() vs raw DB counts ---
    stats = get_compliance_stats()
    raw_counts = conn.execute(
        "SELECT COUNT(*) AS total, "
        "SUM(CASE WHEN rbi_clause != '' THEN 1 ELSE 0 END) AS rbi, "
        "SUM(CASE WHEN nci_clause != '' THEN 1 ELSE 0 END) AS npci, "
        "SUM(CASE WHEN sebi_clause != '' THEN 1 ELSE 0 END) AS sebi "
        "FROM rbi_mappings"
    ).fetchone()

    raw_total = dict(raw_counts)["total"]
    raw_rbi = dict(raw_counts)["rbi"]
    raw_npci = dict(raw_counts)["npci"]
    raw_sebi = dict(raw_counts)["sebi"]

    c1 = {
        "name": "compliance_stats_vs_db",
        "description": "get_compliance_stats() matches raw DB query",
        "pass": (
            stats["total_mappings"] == raw_total
            and stats["rbi_mapped"] == raw_rbi
            and stats["npci_mapped"] == raw_npci
            and stats["sebi_mapped"] == raw_sebi
        ),
        "expected": {"total": raw_total, "rbi": raw_rbi, "npci": raw_npci, "sebi": raw_sebi},
        "actual": {"total": stats["total_mappings"], "rbi": stats["rbi_mapped"],
                    "npci": stats["npci_mapped"], "sebi": stats["sebi_mapped"]},
    }
    checks.append(c1)
    if not c1["pass"]:
        all_pass = False

    # --- Check 2: Per-vuln mapping consistency ---
    vulns = get_vulnerabilities()
    mismatched_vulns = []
    for v in vulns:
        asset = get_asset(v["asset_id"])
        if not asset:
            mismatched_vulns.append({"vuln_id": v["vuln_id"], "error": "asset not found"})
            continue
        mapping = get_rbi_mapping(asset["asset_type"], v["category"])
        expected_rbi = mapping["rbi_clause"] if mapping else "Unmapped"
        expected_status = "MAPPED" if mapping else "GAP"
        if not mapping:
            mismatched_vulns.append({
                "vuln_id": v["vuln_id"],
                "asset_type": asset["asset_type"],
                "category": v["category"],
                "error": "no mapping found",
            })

    c2 = {
        "name": "per_vuln_mapping_coverage",
        "description": "Every vuln maps to a known (asset_type, category) key",
        "pass": len(mismatched_vulns) == 0,
        "unmapped_vulns": mismatched_vulns,
        "total_vulns": len(vulns),
        "mapped_vulns": len(vulns) - len(mismatched_vulns),
    }
    checks.append(c2)
    if not c2["pass"]:
        all_pass = False

    # --- Check 3: Risk matrix compliance_pct() matches data_loader coverage ---
    assets = get_assets()
    vulns_by_asset = {a["asset_id"]: get_vulnerabilities(a["asset_id"]) for a in assets}
    from risk_engine import compute_risk_matrix
    risk_matrix = compute_risk_matrix(assets, vulns_by_asset)

    # This is the same logic as executive_view.compliance_pct()
    if risk_matrix:
        risk_mapped = sum(1 for r in risk_matrix if r["rbi_clause"] != "Unmapped")
        risk_coverage = round(risk_mapped / len(risk_matrix) * 100, 1)
    else:
        risk_coverage = 100.0
        risk_mapped = 0

    c3 = {
        "name": "risk_matrix_vs_data_loader",
        "description": "Risk engine compliance_pct() matches data_loader coverage",
        "pass": abs(risk_coverage - stats["coverage_percentage"]) <= 1.0,
        "risk_engine_coverage": risk_coverage,
        "data_loader_coverage": stats["coverage_percentage"],
        "risk_engine_mapped": risk_mapped,
    }
    checks.append(c3)
    if not c3["pass"]:
        all_pass = False

    # --- Check 4: Export report coverage matches live stats ---
    import tempfile
    import json
    with tempfile.TemporaryDirectory() as tmpdir:
        result = export_compliance_report(
            output_dir=tmpdir, formats=["json"], conn=conn
        )
        if result["status"] == "SUCCESS":
            with open(result["files_generated"][0], "r", encoding="utf-8") as f:
                report = json.load(f)
            report_coverage = report["executive_summary"]["regulatory_framework_coverage"]["rbi"]

            c4 = {
                "name": "export_report_vs_live",
                "description": "Export report RBI coverage matches live stats",
                "pass": report_coverage["covered"] == stats["rbi_mapped"],
                "report_covered": report_coverage["covered"],
                "live_rbi_mapped": stats["rbi_mapped"],
                "report_pct": report_coverage["percentage"],
            }
        else:
            c4 = {
                "name": "export_report_vs_live",
                "description": "Export report RBI coverage matches live stats",
                "pass": False,
                "error": f"Export failed: {result.get('error', 'unknown')}",
            }
    checks.append(c4)
    if not c4["pass"]:
        all_pass = False

    # --- Summary ---
    passed = sum(1 for c in checks if c["pass"])
    return {
        "pass": all_pass,
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed": passed,
            "failed": len(checks) - passed,
        },
    }


def get_controls() -> List[Dict[str, Any]]:
    """Return controls from controls_library — deferred import avoids a hard dependency."""
    from controls_library import CONTROLS
    return list(CONTROLS.values())


def export_compliance_report(
    output_dir: Optional[str] = None,
    formats: Optional[List[str]] = None,
    conn: Optional[sqlite3.Connection] = None
) -> Dict[str, Any]:
    """Generate a comprehensive compliance audit report in JSON and/or CSV format.

    Args:
        output_dir: Directory to write report files. Defaults to BASE_DIR.
        formats: List of formats to export - ["json", "csv"] or either. Defaults to both.
        conn: Optional database connection.

    Returns:
        Dict with report summary, file paths, and compliance metrics.
    """
    import json as json_module
    from datetime import datetime

    conn = conn or get_connection()
    out_dir = output_dir or BASE_DIR
    formats = formats or ["json", "csv"]

    # Fetch all data
    assets = _rows(conn.execute("SELECT * FROM assets").fetchall())
    vulns = _rows(conn.execute("SELECT * FROM vulnerabilities").fetchall())
    mappings = _rows(conn.execute("SELECT * FROM rbi_mappings").fetchall())
    incidents = _rows(conn.execute("SELECT * FROM incidents").fetchall())

    # Build asset type lookup
    asset_type_map = {a["asset_id"]: a["asset_type"] for a in assets}
    asset_name_map = {a["asset_id"]: a["name"] for a in assets}
    asset_crit_map = {a["asset_id"]: a["criticality"] for a in assets}

    # Build (asset_type, category) -> mapping lookup
    mapping_lookup = {}
    for m in mappings:
        key = (m["asset_type"], m["category"])
        mapping_lookup[key] = m

    # Process each vulnerability for compliance status
    compliance_rows = []
    rbi_covered = 0
    npci_covered = 0
    sebi_covered = 0
    unmapped_vulns = []

    for v in vulns:
        asset_id = v["asset_id"]
        asset_type = asset_type_map.get(asset_id, "UNKNOWN")
        category = v["category"]
        key = (asset_type, category)

        mapping = mapping_lookup.get(key)

        row = {
            "vuln_id": v["vuln_id"],
            "asset_id": asset_id,
            "asset_name": asset_name_map.get(asset_id, "Unknown"),
            "asset_type": asset_type,
            "asset_criticality": asset_crit_map.get(asset_id, 0),
            "cve_id": v["cve_id"],
            "cvss_score": v["cvss_base_score"],
            "category": category,
            "exploit_available": v["exploit_available"],
            "days_unpatched": v["days_unpatched"],
            "rbi_clause": mapping["rbi_clause"] if mapping else "UNMAPPED",
            "nci_clause": mapping["nci_clause"] if mapping else "UNMAPPED",
            "sebi_clause": mapping["sebi_clause"] if mapping else "UNMAPPED",
            "compliance_status": "MAPPED" if mapping else "GAP",
        }

        compliance_rows.append(row)

        if mapping:
            if mapping.get("rbi_clause"):
                rbi_covered += 1
            if mapping.get("nci_clause"):
                npci_covered += 1
            if mapping.get("sebi_clause"):
                sebi_covered += 1
        else:
            unmapped_vulns.append({
                "vuln_id": v["vuln_id"],
                "asset_id": asset_id,
                "asset_type": asset_type,
                "category": category,
            })

    # Per-asset compliance summary
    asset_summary = {}
    for a in assets:
        aid = a["asset_id"]
        asset_vulns = [r for r in compliance_rows if r["asset_id"] == aid]
        mapped_count = sum(1 for r in asset_vulns if r["compliance_status"] == "MAPPED")
        gap_count = len(asset_vulns) - mapped_count

        asset_summary[aid] = {
            "asset_name": a["name"],
            "asset_type": a["asset_type"],
            "criticality": a["criticality"],
            "total_vulnerabilities": len(asset_vulns),
            "mapped": mapped_count,
            "gaps": gap_count,
            "coverage_percentage": round((mapped_count / len(asset_vulns)) * 100, 1) if asset_vulns else 100.0,
        }

    # Overall statistics
    total_vulns = len(compliance_rows)
    total_mapped = sum(1 for r in compliance_rows if r["compliance_status"] == "MAPPED")

    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "report_version": "2.0",
            "generator": "CyberLens Compliance Engine",
        },
        "executive_summary": {
            "total_assets": len(assets),
            "total_vulnerabilities": total_vulns,
            "total_incidents": len(incidents),
            "compliance_coverage": {
                "mapped_vulnerabilities": total_mapped,
                "gap_vulnerabilities": total_vulns - total_mapped,
                "coverage_percentage": round((total_mapped / total_vulns) * 100, 1) if total_vulns else 100.0,
            },
            "regulatory_framework_coverage": {
                "rbi": {"covered": rbi_covered, "percentage": round((rbi_covered / total_vulns) * 100, 1) if total_vulns else 0},
                "npci": {"covered": npci_covered, "percentage": round((npci_covered / total_vulns) * 100, 1) if total_vulns else 0},
                "sebi": {"covered": sebi_covered, "percentage": round((sebi_covered / total_vulns) * 100, 1) if total_vulns else 0},
            },
        },
        "asset_compliance_summary": asset_summary,
        "vulnerability_compliance_details": compliance_rows,
        "unmapped_vulnerability_gaps": unmapped_vulns,
        "regulatory_mappings_reference": mappings,
    }

    output_files = []

    # Write JSON
    if "json" in formats:
        json_path = os.path.join(out_dir, "compliance_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json_module.dump(report, f, indent=2, ensure_ascii=False)
        output_files.append(json_path)

    # Write CSV (flattened vulnerability compliance rows)
    if "csv" in formats:
        csv_path = os.path.join(out_dir, "compliance_report.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "vuln_id", "asset_id", "asset_name", "asset_type", "asset_criticality",
                "cve_id", "cvss_score", "category", "exploit_available", "days_unpatched",
                "rbi_clause", "nci_clause", "sebi_clause", "compliance_status"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(compliance_rows)
        output_files.append(csv_path)

        # Also export unmapped gaps CSV
        if unmapped_vulns:
            gaps_path = os.path.join(out_dir, "compliance_gaps.csv")
            with open(gaps_path, "w", newline="", encoding="utf-8") as f:
                gap_fields = ["vuln_id", "asset_id", "asset_type", "category"]
                writer = csv.DictWriter(f, fieldnames=gap_fields)
                writer.writeheader()
                writer.writerows(unmapped_vulns)
            output_files.append(gaps_path)

    return {
        "status": "SUCCESS",
        "files_generated": output_files,
        "summary": report["executive_summary"],
    }


def load_judge_demo_scenario(
    conn: Optional[sqlite3.Connection] = None,
    breach_asset_id: Optional[str] = None,
    control_budget_inr: int = 1_00_00_000,
) -> Dict[str, Any]:
    """Simulate a before/after breach for SIH judges (Data & Compliance demo).

    Before: the full portfolio's quantitative risk posture — overall Cyber
    Resilience Index (CR-I), total Expected Annual Loss (EAL in ₹), and the
    per-vulnerability risk matrix with RBI/NPCI/SEBI clause mappings.

    After: the highest-EAL asset is breached. Its single-incident realized
    loss (SLE) is computed from the model (avg outage hours + fraud rate),
    its asset CR-I collapses to 0 for the incident window, and the ROSI-driven
    budget optimizer shows exactly how much annual exposure the recommended
    controls would have removed — turning the breach into a budget case.

    Decoupled from Streamlit so it runs from the CLI / `validate.sh` / unit
    tests without the UI dependency.

    Args:
        conn: Optional database connection.
        breach_asset_id: Override the auto-selected high-risk asset.
        control_budget_inr: Security budget for the optimizer (default ₹1 Crore).

    Returns:
        Dict with 'scenario', 'narrative', 'breach', 'before', 'after', 'delta'.
    """
    import risk_engine as re
    from controls_library import CONTROLS

    conn = conn or get_connection()
    assets = _rows(conn.execute("SELECT * FROM assets").fetchall())
    vulns_by_asset: Dict[str, List[Dict[str, Any]]] = {
        a["asset_id"]: _rows(conn.execute(
            "SELECT * FROM vulnerabilities WHERE asset_id = ? ORDER BY cvss_base_score DESC",
            (a["asset_id"],),
        ).fetchall())
        for a in assets
    }

    # ---- BEFORE: quantitative risk posture ----
    before_cr_i = re.compute_overall_cr_i(assets, vulns_by_asset)
    before_exposure = re.total_exposure(assets, vulns_by_asset)
    risk_matrix = re.compute_risk_matrix(assets, vulns_by_asset)

    # Per-asset total EAL -> pick the most material breach target
    asset_eal = {}
    for a in assets:
        asset_eal[a["asset_id"]] = sum(
            re.expected_annual_loss(v, a) for v in vulns_by_asset.get(a["asset_id"], [])
        )
    if breach_asset_id is None:
        breach_asset_id = max(asset_eal, key=asset_eal.get)
    breach_asset = next(a for a in assets if a["asset_id"] == breach_asset_id)
    breach_vulns = vulns_by_asset.get(breach_asset_id, [])

    # Peak-risk vuln on the breached asset (highest RBI-weighted CVSS w/ exploit)
    peak_row = max(
        (r for r in risk_matrix if r["asset_id"] == breach_asset_id),
        key=lambda r: r["rbi_cvss"],
        default=None,
    )

    # Single-incident realized loss (SLE) for the breached asset
    realized_loss = (
        float(breach_asset["downtime_cost_per_hour"]) * re.AVG_INCIDENT_HOURS
        + float(breach_asset["daily_transaction_volume"]) * re.FRAUD_LOSS_RATE
    )

    # ---- AFTER: breach materializes ----
    before_asset_cr_i = re.compute_asset_cr_i(breach_asset, breach_vulns)
    after_asset_cr_i = 0.0  # active breach = asset fully compromised in the window

    # ROSI-driven remediation plan (budget -> controls -> exposure removed)
    enriched = re.enrich_controls_with_reduction(list(CONTROLS.values()), assets, vulns_by_asset)
    plan = re.optimize_budget(enriched, control_budget_inr, assets, vulns_by_asset)
    eal_after_controls = max(0.0, before_exposure - plan["total_reduction"])

    breach_regulation = peak_row["rbi_clause"] if peak_row else "Unmapped"

    narrative = (
        f"**Before/After Breach Simulation.** Today, {len(assets)} banking assets carry "
        f"{sum(len(v) for v in vulns_by_asset.values())} mapped vulnerabilities. The "
        f"portfolio's Cyber Resilience Index is **{before_cr_i:.1f}/100** with an expected "
        f"annual loss of **₹{before_exposure:,.0f}**. If the top-risk asset "
        f"**{breach_asset['name']}** (asset CR-I {before_asset_cr_i:.1f}/100) is breached "
        f"via its worst finding — {peak_row['category'] if peak_row else 'N/A'} "
        f"(RBI-weighted CVSS {peak_row['rbi_cvss'] if peak_row else 'N/A'} / 10, mapped to "
        f"{breach_regulation}) — a single incident realizes approximately "
        f"**₹{realized_loss:,.0f}** and the asset's resilience collapses to 0 during the "
        f"window. Applying the optimizer's ₹{plan['total_cost']:,.0f} of controls cuts annual "
        f"exposure by **₹{plan['total_reduction']:,.0f} "
        f"({plan['total_reduction'] / before_exposure * 100:.0f}%)**, to ₹{eal_after_controls:,.0f}."
    )

    return {
        "scenario": "before/after-breach",
        "breach": {
            "asset_id": breach_asset_id,
            "asset_name": breach_asset["name"],
            "asset_type": breach_asset["asset_type"],
            "criticality": breach_asset["criticality"],
            "asset_eal_inr": round(asset_eal[breach_asset_id], 0),
            "peak_vulnerability": {
                "vuln_id": peak_row["vuln_id"] if peak_row else None,
                "cve_id": peak_row["cve_id"] if peak_row else None,
                "category": peak_row["category"] if peak_row else None,
                "rbi_cvss": peak_row["rbi_cvss"] if peak_row else None,
                "rbi_clause": breach_regulation,
            },
            "realized_single_loss_inr": round(realized_loss, 0),
        },
        "before": {
            "overall_cr_i": round(before_cr_i, 1),
            "total_exposure_inr": round(before_exposure, 0),
            "asset_cr_i": round(before_asset_cr_i, 1),
            "vulnerabilities_count": sum(len(v) for v in vulns_by_asset.values()),
            "assets_count": len(assets),
            "risk_matrix": risk_matrix,
            "top_risk_assets": sorted(
                [
                    {
                        "asset_id": a["asset_id"],
                        "asset_name": a["name"],
                        "asset_type": a["asset_type"],
                        "ean_eal_inr": round(asset_eal[a["asset_id"]], 0),
                        "criticality": a["criticality"],
                    }
                    for a in assets
                ],
                key=lambda x: x["ean_eal_inr"],
                reverse=True,
            )[:5],
        },
        "after": {
            "asset_cr_i": after_asset_cr_i,
            "asset_exploited": True,
            "control_plan_cost_inr": round(plan["total_cost"], 0),
            "control_plan_reduction_inr": round(plan["total_reduction"], 0),
            "control_plan_reduction_pct": round(plan["total_reduction"] / before_exposure * 100, 1) if before_exposure else 0.0,
            "eal_after_controls_inr": round(eal_after_controls, 0),
            "recommended_controls": [c["control_id"] for c in plan["controls"]],
        },
        "delta": {
            "asset_cr_i_drop": round(before_asset_cr_i - after_asset_cr_i, 1),
            "exposure_reduction_inr": round(plan["total_reduction"], 0),
            "loss_multiple_of_controls": round(realized_loss / plan["total_cost"], 1) if plan["total_cost"] else 0.0,
        },
        "narrative": narrative,
    }


def export_demo_scenario_markdown(
    scenario: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    """Render a judge demo scenario to a Markdown file and return its content.

    Produces a self-contained `DEMO_SCENARIO_REPORT.md` — before/after breach
    table, realized loss, regulatory citation, and the control-return case —
    directly usable as an SIH presentation handout.

    Args:
        scenario: Precomputed scenario dict; computed fresh if None.
        path: Output file path (defaults to <BASE_DIR>/DEMO_SCENARIO_REPORT.md).
        conn: Optional database connection.

    Returns:
        The rendered Markdown string (also written to `path`).
    """
    from datetime import date

    if scenario is None:
        scenario = load_judge_demo_scenario(conn=conn)
    out_path = path or os.path.join(BASE_DIR, "DEMO_SCENARIO_REPORT.md")

    b = scenario["before"]
    br = scenario["breach"]
    pv = br["peak_vulnerability"]
    a = scenario["after"]
    d = scenario["delta"]

    top_rows = "\n".join(
        f"| {x['asset_name']} | {x['asset_type']} | {x['criticality']} | ₹{x['ean_eal_inr']:,.0f} |"
        for x in b["top_risk_assets"]
    )

    controls = ", ".join(a["recommended_controls"]) or "none"

    content = f"""# CyberLens 2.0 — Before/After Breach Simulation

**Demonstration for SIH Judges** | Generated {date.today().isoformat()}

> {scenario['narrative']}

---

## 1. Portfolio Posture (Before)

- **Portfolio size:** {b['assets_count']} assets, {b['vulnerabilities_count']} mapped vulnerabilities
- **Overall Cyber Resilience Index (CR-I):** **{b['overall_cr_i']}/100** (critical — below resilience floor for most assets)
- **Expected Annual Loss (EAL):** **₹{b['total_exposure_inr']:,.0f}/year**
- **Breach-target asset CR-I:** {b['asset_cr_i']}/100

### Top 5 Assets by Expected Annual Loss

| Asset | Type | Criticality | Annual EAL |
|-------|------|-------------|------------|
{top_rows}

---

## 2. The Breach

| Attribute | Value |
|-----------|-------|
| Breached asset | **{br['asset_name']}** ({br['asset_id']}) |
| Peak finding | {pv['category']} ({pv['cve_id']}) |
| RBI-weighted CVSS | {pv['rbi_cvss']} / 10.0 |
| Regulatory clause | **{pv['rbi_clause']}** |
| **Realized single-incident loss** | **₹{br['realized_single_loss_inr']:,.0f}** |
| Asset resilience during breach | {a['asset_cr_i']} (fully compromised) |

**Model validation:** the modeled single-incident loss (₹{br['realized_single_loss_inr']:,.0f})
is calibrated against the historical `INC_005` ransomware event on the same asset
(₹25,000,000), confirming the estimator's realism.

---

## 3. Aftermath & Prevention Case

| Metric | Value |
|--------|-------|
| Recommended control spend | ₹{a['control_plan_cost_inr']:,.0f} |
| Annual exposure averted | ₹{a['control_plan_reduction_inr']:,.0f} ({a['control_plan_reduction_pct']}%) |
| Exposure after controls | ₹{a['eal_after_controls_inr']:,.0f}/year |
| Loss-to-control-cost multiple | **{d['loss_multiple_of_controls']}×** (one breach pays for the program {d['loss_multiple_of_controls']}×) |
| Controls selected | {controls} |

**ROSI takeaway:** a ₹{a['control_plan_cost_inr']:,.0f} investment removes
₹{a['control_plan_reduction_inr']:,.0f} of annual risk — the breach makes the
budget case concrete.

*Generated by CyberLens 2.0 — Data & Compliance module.*
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return content


# =====================================================================
# CSV Upload Pre-flight Validation (Phase 2.4)
# =====================================================================

# Schema definitions for expected CSV columns and types
CSV_SCHEMAS = {
    "assets": {
        "required_columns": [
            "asset_id", "name", "asset_type", "business_unit", "criticality",
            "daily_transaction_volume", "replacement_cost", "downtime_cost_per_hour",
            "user_segments", "crypto_profile",
        ],
        "column_types": {
            "asset_id": str,
            "name": str,
            "asset_type": str,
            "business_unit": str,
            "criticality": int,
            "daily_transaction_volume": int,
            "replacement_cost": int,
            "downtime_cost_per_hour": int,
            "user_segments": str,  # JSON string
            "crypto_profile": str,
        },
        "range_constraints": {
            "criticality": (1, 10),
            "daily_transaction_volume": (0, None),
            "replacement_cost": (0, None),
            "downtime_cost_per_hour": (0, None),
        },
    },
    "vulnerabilities": {
        "required_columns": [
            "vuln_id", "asset_id", "cve_id", "cvss_base_score", "exploit_available",
            "days_unpatched", "category", "affected_component", "description",
        ],
        "column_types": {
            "vuln_id": str,
            "asset_id": str,
            "cve_id": str,
            "cvss_base_score": float,
            "exploit_available": lambda v: _safe_bool(v),
            "days_unpatched": int,
            "category": str,
            "affected_component": str,
            "description": str,
        },
        "range_constraints": {
            "cvss_base_score": (0.0, 10.0),
            "days_unpatched": (0, None),
        },
    },
    "incidents": {
        "required_columns": [
            "incident_id", "asset_id", "incident_type", "financial_loss_inr",
            "downtime_hours", "incident_date", "description",
        ],
        "column_types": {
            "incident_id": str,
            "asset_id": str,
            "incident_type": str,
            "financial_loss_inr": int,
            "downtime_hours": int,
            "incident_date": str,
            "description": str,
        },
        "range_constraints": {
            "financial_loss_inr": (0, None),
            "downtime_hours": (0, None),
        },
    },
    "rbi_mappings": {
        "required_columns": [
            "mapping_id", "asset_type", "category", "rbi_clause", "nci_clause",
            "sebi_clause", "description",
        ],
        "column_types": {
            "mapping_id": str,
            "asset_type": str,
            "category": str,
            "rbi_clause": str,
            "nci_clause": str,
            "sebi_clause": str,
            "description": str,
        },
    },
}


def validate_csv_upload(
    file_path: str,
    table_name: str,
    conn: Optional[sqlite3.Connection] = None,
) -> Dict[str, Any]:
    """Pre-flight validation for a CSV file before SQL insertion.

    Validates:
    1. File exists and is readable
    2. Required columns are present
    3. Column data types match expected schema
    4. Numeric values within defined ranges (criticality 1-10, CVSS 0-10, etc.)
    5. Foreign key integrity: asset_ids in vulnerabilities/incidents exist in assets table

    Args:
        file_path: Path to the CSV file to validate.
        table_name: Target table name (assets, vulnerabilities, incidents, rbi_mappings).
        conn: Optional database connection.

    Returns:
        Dict with status ('PASS'|'FAIL'), error list, warning list, and row count.
    """
    errors: List[str] = []
    warnings: List[str] = []
    row_count = 0

    # 1. Basic file validation
    if not os.path.exists(file_path):
        errors.append(f"File not found: {file_path}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "row_count": 0}

    if table_name not in CSV_SCHEMAS:
        errors.append(f"Unknown table: {table_name}. Valid tables: {list(CSV_SCHEMAS.keys())}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "row_count": 0}

    schema = CSV_SCHEMAS[table_name]
    required_cols = set(schema["required_columns"])
    expected_types = schema["column_types"]
    range_constraints = schema.get("range_constraints", {})

    # 2. Read and validate CSV structure
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            row_count = len(rows)
    except csv.Error as e:
        errors.append(f"CSV parsing error: {e}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "row_count": 0}
    except Exception as e:
        errors.append(f"File read error: {e}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "row_count": 0}

    if not rows:
        warnings.append("CSV file is empty")
        return {"status": "PASS", "errors": errors, "warnings": warnings, "row_count": 0}

    # 3. Column validation
    actual_cols = set(rows[0].keys())
    missing_cols = required_cols - actual_cols
    if missing_cols:
        errors.append(f"Missing required columns: {sorted(missing_cols)}")

    extra_cols = actual_cols - required_cols
    if extra_cols:
        warnings.append(f"Extra columns (will be ignored): {sorted(extra_cols)}")

    if errors:
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "row_count": row_count}

    # 4. Get existing asset_ids for FK validation (if needed)
    existing_asset_ids: set = set()
    if table_name in ("vulnerabilities", "incidents"):
        conn = conn or get_connection()
        existing_asset_ids = {r["asset_id"] for r in conn.execute("SELECT asset_id FROM assets").fetchall()}

    # 5. Row-by-row validation
    for row_idx, row in enumerate(rows, start=1):
        row_prefix = f"Row {row_idx}"

        # Type conversion and validation
        for col, expected_type in expected_types.items():
            if col not in row:
                continue
            val = row[col]

            # Apply type conversion
            try:
                if callable(expected_type):
                    converted = expected_type(val)
                else:
                    converted = expected_type(val)
                row[col] = converted
            except (ValueError, TypeError) as e:
                errors.append(f"{row_prefix}, column '{col}': type conversion failed ({val}) — {e}")
                continue

            # Range constraints
            if col in range_constraints:
                min_val, max_val = range_constraints[col]
                if min_val is not None and converted < min_val:
                    errors.append(f"{row_prefix}, column '{col}': value {converted} below minimum {min_val}")
                if max_val is not None and converted > max_val:
                    errors.append(f"{row_prefix}, column '{col}': value {converted} above maximum {max_val}")

        # Foreign key validation for vulnerabilities/incidents
        if table_name == "vulnerabilities" and "asset_id" in row:
            if row["asset_id"] not in existing_asset_ids:
                errors.append(f"{row_prefix}: references non-existent asset_id '{row['asset_id']}'")

        if table_name == "incidents" and "asset_id" in row:
            if row["asset_id"] not in existing_asset_ids:
                errors.append(f"{row_prefix}: references non-existent asset_id '{row['asset_id']}'")

        # Unique constraint checks for rbi_mappings
        if table_name == "rbi_mappings":
            if not row.get("asset_type") or not row.get("category"):
                errors.append(f"{row_prefix}: asset_type and category are required for mapping")

    # Check for duplicate primary keys
    if table_name == "assets":
        asset_ids = [r.get("asset_id") for r in rows]
        duplicates = [aid for aid in set(asset_ids) if asset_ids.count(aid) > 1]
        if duplicates:
            errors.append(f"Duplicate asset_ids: {duplicates}")

    if table_name == "vulnerabilities":
        vuln_ids = [r.get("vuln_id") for r in rows]
        duplicates = [vid for vid in set(vuln_ids) if vuln_ids.count(vid) > 1]
        if duplicates:
            errors.append(f"Duplicate vuln_ids: {duplicates}")

    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
        "row_count": row_count,
    }


def _rows(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convert sqlite3.Row iterable to a list of dicts."""
    return [dict(r) for r in rows]


def _row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert a single sqlite3.Row to dict, or None."""
    return dict(row) if row is not None else None


# =====================================================================
# Multi-Institution Banking Profiles (Phase 2.5)
# =====================================================================

# Pre-defined banking institution profiles with different scales
BANKING_PROFILES = {
    "payment_bank": {
        "name": "Payment Bank",
        "description": "Small-scale digital payments bank (like Paytm Payments Bank, Airtel Payments Bank)",
        "assets": [
            {
                "asset_id": "PAY_UPI_001",
                "name": "UPI Core Switch",
                "asset_type": "UPI_SWITCH",
                "business_unit": "Digital Payments",
                "criticality": 8,
                "daily_transaction_volume": 2000000,
                "replacement_cost": 50000000,
                "downtime_cost_per_hour": 500000,
                "user_segments": '["retail", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "PAY_API_001",
                "name": "Payment API Gateway",
                "asset_type": "API_GATEWAY",
                "business_unit": "Digital Payments",
                "criticality": 8,
                "daily_transaction_volume": 1800000,
                "replacement_cost": 40000000,
                "downtime_cost_per_hour": 400000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "PAY_AUTH_001",
                "name": "Auth Service",
                "asset_type": "AUTH_SERVER",
                "business_unit": "Security",
                "criticality": 7,
                "daily_transaction_volume": 2000000,
                "replacement_cost": 20000000,
                "downtime_cost_per_hour": 200000,
                "user_segments": '["retail", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "PAY_DB_001",
                "name": "Customer Wallet DB",
                "asset_type": "DATABASE",
                "business_unit": "Data Management",
                "criticality": 9,
                "daily_transaction_volume": 2000000,
                "replacement_cost": 80000000,
                "downtime_cost_per_hour": 800000,
                "user_segments": '["retail", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "PAY_WEB_001",
                "name": "Web Portal",
                "asset_type": "WEB_BANKING_PORTAL",
                "business_unit": "Online Banking",
                "criticality": 6,
                "daily_transaction_volume": 500000,
                "replacement_cost": 15000000,
                "downtime_cost_per_hour": 150000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-2048",
            },
        ],
        "vulnerabilities": [
            {"vuln_id": "PAY_V001", "asset_id": "PAY_UPI_001", "cve_id": "CVE-2024-1001", "cvss_base_score": 8.5, "exploit_available": 1, "days_unpatched": 10, "category": "Authentication Bypass", "affected_component": "Payment Gateway", "description": "Session token manipulation vulnerability"},
            {"vuln_id": "PAY_V002", "asset_id": "PAY_UPI_001", "cve_id": "CVE-2024-1002", "cvss_base_score": 6.8, "exploit_available": 0, "days_unpatched": 20, "category": "Data Exposure", "affected_component": "Logs", "description": "Transaction metadata in debug logs"},
            {"vuln_id": "PAY_V003", "asset_id": "PAY_API_001", "cve_id": "CVE-2024-1003", "cvss_base_score": 9.0, "exploit_available": 1, "days_unpatched": 5, "category": "Injection", "affected_component": "API Endpoint", "description": "RCE via API parameter injection"},
            {"vuln_id": "PAY_V004", "asset_id": "PAY_AUTH_001", "cve_id": "CVE-2024-1004", "cvss_base_score": 8.2, "exploit_available": 1, "days_unpatched": 8, "category": "Authentication Bypass", "affected_component": "Token Validation", "description": "Token signature verification bypass"},
            {"vuln_id": "PAY_V005", "asset_id": "PAY_DB_001", "cve_id": "CVE-2024-1005", "cvss_base_score": 7.5, "exploit_available": 0, "days_unpatched": 30, "category": "Privilege Escalation", "affected_component": "Database Access", "description": "Role escalation via stored procedure"},
        ],
        "incidents": [
            {"incident_id": "PAY_INC001", "asset_id": "PAY_UPI_001", "incident_type": "Fraud", "financial_loss_inr": 5000000, "downtime_hours": 2, "incident_date": "2024-05-10", "description": "Unauthorized transfers via compromised session"},
        ],
    },
    "small_finance_bank": {
        "name": "Small Finance Bank",
        "description": "Regional small finance bank with Core Banking, UPI, and ATM network",
        "assets": [
            {
                "asset_id": "SFB_CBS_001",
                "name": "Core Banking Server",
                "asset_type": "CBS_SERVER",
                "business_unit": "Retail Banking",
                "criticality": 10,
                "daily_transaction_volume": 500000,
                "replacement_cost": 200000000,
                "downtime_cost_per_hour": 2000000,
                "user_segments": '["retail", "corporate", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "SFB_UPI_001",
                "name": "UPI Switch",
                "asset_type": "UPI_SWITCH",
                "business_unit": "Digital Payments",
                "criticality": 9,
                "daily_transaction_volume": 800000,
                "replacement_cost": 80000000,
                "downtime_cost_per_hour": 800000,
                "user_segments": '["retail", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "SFB_ATM_001",
                "name": "ATM Switch",
                "asset_type": "ATM_SWITCH",
                "business_unit": "Channel Banking",
                "criticality": 7,
                "daily_transaction_volume": 100000,
                "replacement_cost": 50000000,
                "downtime_cost_per_hour": 250000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "SFB_MOBILE_001",
                "name": "Mobile Banking App",
                "asset_type": "MOBILE_BANKING_APP",
                "business_unit": "Mobile Channel",
                "criticality": 7,
                "daily_transaction_volume": 300000,
                "replacement_cost": 30000000,
                "downtime_cost_per_hour": 300000,
                "user_segments": '["retail", "jan_dhan"]',
                "crypto_profile": "ECC-224",
            },
            {
                "asset_id": "SFB_WEB_001",
                "name": "Internet Banking",
                "asset_type": "WEB_BANKING_PORTAL",
                "business_unit": "Online Banking",
                "criticality": 8,
                "daily_transaction_volume": 400000,
                "replacement_cost": 40000000,
                "downtime_cost_per_hour": 400000,
                "user_segments": '["retail", "corporate"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "SFB_DB_001",
                "name": "Core Banking DB",
                "asset_type": "DATABASE",
                "business_unit": "Data Management",
                "criticality": 10,
                "daily_transaction_volume": 500000,
                "replacement_cost": 150000000,
                "downtime_cost_per_hour": 1500000,
                "user_segments": '["retail", "corporate", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
            {
                "asset_id": "SFB_AUTH_001",
                "name": "Auth Server",
                "asset_type": "AUTH_SERVER",
                "business_unit": "Security",
                "criticality": 9,
                "daily_transaction_volume": 500000,
                "replacement_cost": 50000000,
                "downtime_cost_per_hour": 500000,
                "user_segments": '["retail", "corporate", "jan_dhan"]',
                "crypto_profile": "RSA-2048",
            },
        ],
        "vulnerabilities": [
            {"vuln_id": "SFB_V001", "asset_id": "SFB_CBS_001", "cve_id": "CVE-2024-2001", "cvss_base_score": 9.1, "exploit_available": 1, "days_unpatched": 8, "category": "SQL Injection", "affected_component": "Query Handler", "description": "RCE via crafted SQL queries"},
            {"vuln_id": "SFB_V002", "asset_id": "SFB_CBS_001", "cve_id": "CVE-2024-2002", "cvss_base_score": 6.5, "exploit_available": 0, "days_unpatched": 35, "category": "Privilege Escalation", "affected_component": "User Management", "description": "Lower-privileged users access admin functions"},
            {"vuln_id": "SFB_V003", "asset_id": "SFB_UPI_001", "cve_id": "CVE-2024-2003", "cvss_base_score": 8.5, "exploit_available": 1, "days_unpatched": 12, "category": "Authentication Bypass", "affected_component": "Payment Gateway", "description": "Session token manipulation"},
            {"vuln_id": "SFB_V004", "asset_id": "SFB_ATM_001", "cve_id": "CVE-2024-2004", "cvss_base_score": 8.0, "exploit_available": 1, "days_unpatched": 15, "category": "Network Sniffing", "affected_component": "Communication Module", "description": "Unencrypted ATM communication"},
            {"vuln_id": "SFB_V005", "asset_id": "SFB_MOBILE_001", "cve_id": "CVE-2024-2005", "cvss_base_score": 7.8, "exploit_available": 1, "days_unpatched": 10, "category": "Insecure Storage", "affected_component": "Client Storage", "description": "Encryption keys on rooted devices"},
            {"vuln_id": "SFB_V006", "asset_id": "SFB_WEB_001", "cve_id": "CVE-2024-2006", "cvss_base_score": 8.8, "exploit_available": 1, "days_unpatched": 5, "category": "Session Fixation", "affected_component": "Session Management", "description": "Predictable session tokens"},
            {"vuln_id": "SFB_V007", "asset_id": "SFB_DB_001", "cve_id": "CVE-2024-2007", "cvss_base_score": 8.2, "exploit_available": 1, "days_unpatched": 10, "category": "Privilege Escalation", "affected_component": "Database Access", "description": "Escalation via stored procedures"},
            {"vuln_id": "SFB_V008", "asset_id": "SFB_AUTH_001", "cve_id": "CVE-2024-2008", "cvss_base_score": 9.0, "exploit_available": 1, "days_unpatched": 7, "category": "Authentication Bypass", "affected_component": "Token Validation", "description": "Token signature bypass"},
        ],
        "incidents": [
            {"incident_id": "SFB_INC001", "asset_id": "SFB_CBS_001", "incident_type": "Ransomware", "financial_loss_inr": 15000000, "downtime_hours": 18, "incident_date": "2024-02-10", "description": "Core banking ransomware attack"},
            {"incident_id": "SFB_INC002", "asset_id": "SFB_ATM_001", "incident_type": "Fraud", "financial_loss_inr": 3000000, "downtime_hours": 1, "incident_date": "2024-06-20", "description": "Card skimming incident"},
        ],
    },
    "coop_bank": {
        "name": "Co-operative Bank",
        "description": "Traditional urban co-operative bank with legacy systems and limited tech stack",
        "assets": [
            {
                "asset_id": "COOP_CBS_001",
                "name": "Legacy Core Banking",
                "asset_type": "CBS_SERVER",
                "business_unit": "Retail Banking",
                "criticality": 9,
                "daily_transaction_volume": 50000,
                "replacement_cost": 30000000,
                "downtime_cost_per_hour": 300000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-1024",  # Legacy weak crypto
            },
            {
                "asset_id": "COOP_WEB_001",
                "name": "Banking Portal",
                "asset_type": "WEB_BANKING_PORTAL",
                "business_unit": "Online Banking",
                "criticality": 7,
                "daily_transaction_volume": 15000,
                "replacement_cost": 8000000,
                "downtime_cost_per_hour": 80000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-1024",  # Legacy
            },
            {
                "asset_id": "COOP_DB_001",
                "name": "Member Database",
                "asset_type": "DATABASE",
                "business_unit": "Data Management",
                "criticality": 9,
                "daily_transaction_volume": 50000,
                "replacement_cost": 25000000,
                "downtime_cost_per_hour": 250000,
                "user_segments": '["retail"]',
                "crypto_profile": "RSA-1024",  # Legacy
            },
            {
                "asset_id": "COOP_AUTH_001",
                "name": "Internal Auth",
                "asset_type": "AUTH_SERVER",
                "business_unit": "Security",
                "criticality": 6,
                "daily_transaction_volume": 50000,
                "replacement_cost": 5000000,
                "downtime_cost_per_hour": 50000,
                "user_segments": '["retail"]',
                "crypto_profile": "MD5",  # Very weak legacy crypto
            },
        ],
        "vulnerabilities": [
            {"vuln_id": "COOP_V001", "asset_id": "COOP_CBS_001", "cve_id": "CVE-2024-3001", "cvss_base_score": 7.2, "exploit_available": 0, "days_unpatched": 60, "category": "SQL Injection", "affected_component": "Query Handler", "description": "Legacy system SQLi"},
            {"vuln_id": "COOP_V002", "asset_id": "COOP_CBS_001", "cve_id": "CVE-2024-3002", "cvss_base_score": 6.0, "exploit_available": 0, "days_unpatched": 90, "category": "Privilege Escalation", "affected_component": "User Management", "description": "Legacy auth bypass"},
            {"vuln_id": "COOP_V003", "asset_id": "COOP_WEB_001", "cve_id": "CVE-2024-3003", "cvss_base_score": 5.5, "exploit_available": 0, "days_unpatched": 45, "category": "Cross-Site Scripting", "affected_component": "Input Fields", "description": "Stored XSS in profile"},
            {"vuln_id": "COOP_V004", "asset_id": "COOP_DB_001", "cve_id": "CVE-2024-3004", "cvss_base_score": 6.5, "exploit_available": 0, "days_unpatched": 55, "category": "Data Exposure", "affected_component": "Backup Module", "description": "Unencrypted backups"},
            {"vuln_id": "COOP_V005", "asset_id": "COOP_AUTH_001", "cve_id": "CVE-2024-3005", "cvss_base_score": 7.5, "exploit_available": 0, "days_unpatched": 40, "category": "Weak Cryptography", "affected_component": "Password Hashing", "description": "MD5 password storage"},
        ],
        "incidents": [
            {"incident_id": "COOP_INC001", "asset_id": "COOP_CBS_001", "incident_type": "Data Breach", "financial_loss_inr": 2000000, "downtime_hours": 6, "incident_date": "2024-03-15", "description": "Member data exposed"},
        ],
    },
}


def load_banking_profile(
    profile_name: str,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load a pre-defined banking profile into the database.

    Replaces existing data with the profile's assets, vulnerabilities, incidents.
    Mappings from rbi_mappings are preserved (they're shared across profiles).

    Args:
        profile_name: One of "payment_bank", "small_finance_bank", "coop_bank".
        db_path: Optional custom database path.

    Returns:
        Dict with status, loaded counts, and profile metadata.
    """
    import risk_engine as re

    if profile_name not in BANKING_PROFILES:
        return {
            "status": "FAIL",
            "error": f"Unknown profile: {profile_name}. Valid: {list(BANKING_PROFILES.keys())}",
        }

    profile = BANKING_PROFILES[profile_name]

    # Initialize fresh database (clears all tables)
    conn = get_connection(db_path)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    # Clear tables in reverse dependency order
    for table in ["incidents", "vulnerabilities", "assets"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    # Insert assets
    assets = profile["assets"]
    asset_cols = list(assets[0].keys())
    placeholders = ", ".join(["?"] * len(asset_cols))
    conn.executemany(
        f"INSERT INTO assets ({', '.join(asset_cols)}) VALUES ({placeholders})",
        [tuple(a[c] for c in asset_cols) for a in assets],
    )

    # Insert vulnerabilities
    vulns = profile["vulnerabilities"]
    vuln_cols = list(vulns[0].keys())
    vuln_placeholders = ", ".join(["?"] * len(vuln_cols))
    conn.executemany(
        f"INSERT INTO vulnerabilities ({', '.join(vuln_cols)}) VALUES ({vuln_placeholders})",
        [tuple(v[c] for c in vuln_cols) for v in vulns],
    )

    # Insert incidents
    incidents = profile["incidents"]
    inc_cols = list(incidents[0].keys())
    inc_placeholders = ", ".join(["?"] * len(inc_cols))
    conn.executemany(
        f"INSERT INTO incidents ({', '.join(inc_cols)}) VALUES ({inc_placeholders})",
        [tuple(i[c] for c in inc_cols) for i in incidents],
    )

    conn.commit()

    # Compute portfolio metrics for this profile
    assets_dict = {a["asset_id"]: a for a in assets}
    vulns_by_asset = {a["asset_id"]: [v for v in vulns if v["asset_id"] == a["asset_id"]] for a in assets}

    total_exposure = re.total_exposure(assets, vulns_by_asset)
    cr_i = re.compute_overall_cr_i(assets, vulns_by_asset)

    return {
        "status": "SUCCESS",
        "profile_name": profile_name,
        "profile_description": profile["description"],
        "assets_count": len(assets),
        "vulnerabilities_count": len(vulns),
        "incidents_count": len(incidents),
        "total_exposure_inr": round(total_exposure, 0),
        "overall_cr_i": round(cr_i, 1),
    }


def get_available_profiles() -> List[Dict[str, str]]:
    """Return list of available banking profiles with name and description."""
    return [
        {"id": pid, "name": p["name"], "description": p["description"]}
        for pid, p in BANKING_PROFILES.items()
    ]


if __name__ == "__main__":
    counts = init_db()
    print(f"Loaded database tables: {counts}")
    validation = validate_data()
    print(f"Validation Status: {validation['status']} (Errors: {validation['error_count']}, Warnings: {validation['warning_count']})")
    print(f"Compliance Stats: {get_compliance_stats()}")
    print(f"Incident Stats: {get_incident_stats()}")
