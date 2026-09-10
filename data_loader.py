"""CyberLens 2.0 - Data Loader
Loads sample CSV data into SQLite and provides query functions.

Ponytail: in-memory SQLite keeps the demo zero-setup. Swap to PostgreSQL
by changing the connection string if this goes to production.
"""

import csv
import os
import sqlite3

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

_conn = None


def get_connection():
    global _conn
    if _conn is None:
        # check_same_thread=False: Streamlit reruns across threads; SQLite is
        # serialized, so shared read-only queries are safe.
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


ALLOWED_TABLES = {"assets", "vulnerabilities", "incidents", "rbi_mappings"}


def load_csv_to_table(conn, table, csv_path):
    """Load a CSV file into an existing table, replacing its current rows."""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' is not in the allowed whitelist.")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    if not rows:
        return 0
    # Type conversion for specific tables
    if table == "vulnerabilities":
        for row in rows:
            row["exploit_available"] = 1 if row.get("exploit_available", "").lower() == "true" else 0
            row["cvss_base_score"] = float(row.get("cvss_base_score", 0))
            row["days_unpatched"] = int(row.get("days_unpatched", 0))
    elif table == "assets":
        for row in rows:
            row["criticality"] = int(row.get("criticality", 5))
            row["daily_transaction_volume"] = int(row.get("daily_transaction_volume", 0))
            row["replacement_cost"] = int(row.get("replacement_cost", 0))
            row["downtime_cost_per_hour"] = int(row.get("downtime_cost_per_hour", 0))
    elif table == "incidents":
        for row in rows:
            row["financial_loss_inr"] = int(row.get("financial_loss_inr", 0))
            row["downtime_hours"] = int(row.get("downtime_hours", 0))
    columns = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)
    conn.execute(f"DELETE FROM {table}")
    conn.executemany(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
        [tuple(r[c] for c in columns) for r in rows],
    )
    conn.commit()
    return len(rows)


def init_db(conn=None):
    """Create tables from schema.sql and load CSV data."""
    conn = conn or get_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    counts = {}
    for table, filename in CSV_FILES.items():
        counts[table] = load_csv_to_table(conn, table, os.path.join(DATA_DIR, filename))
    return counts


def get_assets():
    return _rows(get_connection().execute("SELECT * FROM assets ORDER BY criticality DESC").fetchall())


def get_asset(asset_id):
    row = get_connection().execute(
        "SELECT * FROM assets WHERE asset_id = ?", (asset_id,)
    ).fetchone()
    return _row(row)


def get_vulnerabilities(asset_id=None):
    conn = get_connection()
    if asset_id:
        return _rows(conn.execute(
            "SELECT * FROM vulnerabilities WHERE asset_id = ?", (asset_id,)
        ).fetchall())
    return _rows(conn.execute("SELECT * FROM vulnerabilities").fetchall())


def get_rbi_mapping(asset_type, category):
    row = get_connection().execute(
        "SELECT * FROM rbi_mappings WHERE asset_type = ? AND category = ?",
        (asset_type, category),
    ).fetchone()
    return _row(row)


def get_incidents(asset_id=None):
    conn = get_connection()
    if asset_id:
        return _rows(conn.execute(
            "SELECT * FROM incidents WHERE asset_id = ?", (asset_id,)
        ).fetchall())
    return _rows(conn.execute("SELECT * FROM incidents").fetchall())


def _rows(rows):
    return [dict(r) for r in rows]


def _row(row):
    return dict(row) if row is not None else None


def get_controls():
    """Return controls from controls_library — deferred import avoids a hard dependency."""
    from controls_library import CONTROLS
    return list(CONTROLS.values())


if __name__ == "__main__":
    counts = init_db()
    print(f"Loaded database: {counts}")
    print(f"Assets: {len(get_assets())}, Vulnerabilities: {len(get_vulnerabilities())}")