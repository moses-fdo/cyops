# Data Model (DATA_MODEL.md) - CyberLens 2.0

This document describes the data model used by CyberLens 2.0 for storing assets, vulnerabilities, incidents, and compliance mappings. The model is implemented using SQLite (for the demo) but can be easily adapted to PostgreSQL or other relational databases.

## 1. Entity-Relationship Overview

```
Assets 1 --* Vulnerabilities
Assets 1 --* Incidents
Vulnerabilities * --1 RBI_Mappings (via category + asset_type)
```

## 2. Tables

### 2.1 Assets
Stores information about each asset in the UPI/banking ecosystem.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| asset_id | TEXT | PRIMARY KEY | Unique identifier (e.g., UPI_SWITCH_001) |
| name | TEXT | NOT NULL | Human‑readable name |
| asset_type | TEXT | NOT NULL | Type of asset (e.g., UPI_SWITCH, CBS_SERVER, MOBILE_BANKING_APP) |
| business_unit | TEXT | NOT NULL | Business unit owning the asset (e.g., Payments, Retail Banking) |
| criticality | INTEGER | NOT NULL, CHECK (criticality BETWEEN 1 AND 10) | Business impact scale (1‑Low, 10‑Critical) |
| daily_transaction_volume | INTEGER | NOT NULL | Number of transactions processed per day (for payment assets) |
| replacement_cost | INTEGER | NOT NULL | Estimated cost to replace the asset (in ₹) |
| downtime_cost_per_hour | INTEGER | NOT NULL | Cost incurred per hour of downtime (in ₹) |
| user_segments | TEXT | NULL | JSON array of user segments served (e.g., ["retail","corporate","jan_dhan"]) |
| crypto_profile | TEXT | NULL | Description of cryptographic algorithms used (for quantum risk) |

### 2.2 Vulnerabilities
Stores details of each vulnerability discovered in an asset.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| vuln_id | TEXT | PRIMARY KEY | Unique identifier (e.g., V_UPI_001) |
| asset_id | TEXT | NOT NULL, FOREIGN KEY (assets.asset_id) | Reference to the affected asset |
| cve_id | TEXT | NULL | CVE identifier (if available) |
| cvss_base_score | REAL | NOT NULL, CHECK (cvss_base_score BETWEEN 0 AND 10) | Base CVSS score |
| exploit_available | BOOLEAN | NOT NULL | Whether a public exploit exists |
| days_unpatched | INTEGER | NOT NULL, CHECK (days_unpatched >= 0) | Number of days since the vulnerability was disclosed/patch available |
| category | TEXT | NOT NULL | Vulnerability category (e.g., Authentication Bypass, Data Exposure) |
| affected_component | TEXT | NULL | Specific component or module affected |
| description | TEXT | NULL | Brief description of the vulnerability |

### 2.3 Incidents (Optional – for model calibration)
Stores historical cyber incidents that have impacted assets.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| incident_id | TEXT | PRIMARY KEY | Unique identifier |
| asset_id | TEXT | NOT NULL, FOREIGN KEY (assets.asset_id) | Reference to the affected asset |
| incident_type | TEXT | NOT NULL | Type of incident (e.g., Ransomware, Fraud, DDoS) |
| financial_loss_inr | INTEGER | NOT NULL | Direct financial loss incurred (in ₹) |
| downtime_hours | INTEGER | NOT NULL | Duration of downtime (in hours) |
| incident_date | DATE | NOT NULL | Date when the incident occurred |
| description | TEXT | NULL | Brief description |

### 2.4 RBI_Mappings
Maps vulnerability categories and asset types to specific RBI/SEBI/NPCI circular clauses.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| mapping_id | TEXT | PRIMARY KEY | Unique identifier (could be composite key) |
| asset_type | TEXT | NOT NULL | Asset type (matches Assets.asset_type) |
| category | TEXT | NOT NULL | Vulnerability category (matches Vulnerabilities.category) |
| rbi_clause | TEXT | NULL | RBI circular reference (e.g., RBI/2023-24/105.A.3) |
| nci_clause | TEXT | NULL | SEBI/HO/ISD/ISD/CIR/P/2020/168 style reference (if applicable) |
| sebi_clause | TEXT | NULL | SEBI circular reference (if applicable) |
| description | TEXT | NULL | Explanation of what the clause requires |

> **Note**: The combination of (`asset_type`, `category`) is intended to be unique; a unique constraint can be added.

### 2.5 Controls_Library (Configuration Table – not persisted, but could be)
Defines available security controls for the optimizer. In the demo this is a Python dict, but it could be stored in a table.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| control_id | TEXT | PRIMARY KEY | Unique identifier (e.g., CTRL_MFA_UPI) |
| name | TEXT | NOT NULL | Human‑readable name |
| cost_inr | INTEGER | NOT NULL | Cost to implement/operate per year (in ₹) |
| affected_categories | TEXT | NULL | JSON array of vulnerability categories this control mitigates |
| effectiveness | REAL | NOT NULL, CHECK (effectiveness BETWEEN 0 AND 1) | Fractional risk reduction for affected vulnerabilities (e.g., 0.7 = 70% reduction) |
| description | TEXT | NULL | Brief description of the control |

## 3. Sample Data (for demo)
The `data/` directory contains CSV files that mirror the above tables:
- `assets.csv`
- `vulnerabilities.csv`
- `incidents.csv` (may be empty or minimal)
- `rbi_mappings.csv`

These are loaded into SQLite on startup by `data_loader.py`.

## 4. Extensibility
- To add new asset types, simply insert a row into the Assets table.
- To add new vulnerability categories, add rows to Vulnerabilities and ensure a mapping exists in RBI_Mappings.
- New RBI/SEBI/NPCI guidelines can be added as new rows in RBI_Mappings.
- The model is deliberately kept in 3NF to avoid update anomalies and support complex queries (e.g., “Show all unpatched critical vulnerabilities in UPI switches mapped to RBI circular X”).

## 5. Indexes (for performance)
Recommended indexes on the SQLite (or PostgreSQL) implementation:
- `CREATE INDEX idx_vulnerabilities_asset_id ON vulnerabilities(asset_id);`
- `CREATE INDEX idx_vulnerabilities_category ON vulnerabilities(category);`
- `CREATE INDEX idx_rbi_mappings_asset_category ON rbi_mappings(asset_type, category);`
- `CREATE INDEX idx_assets_asset_type ON assets(asset_type);`

These ensure fast lookups for the risk engine.

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*