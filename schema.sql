-- CyberLens 2.0 Database Schema

CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    business_unit TEXT NOT NULL,
    criticality INTEGER NOT NULL CHECK (criticality BETWEEN 1 AND 10),
    daily_transaction_volume INTEGER NOT NULL,
    replacement_cost INTEGER NOT NULL,
    downtime_cost_per_hour INTEGER NOT NULL,
    user_segments TEXT,
    crypto_profile TEXT
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    vuln_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    cve_id TEXT,
    cvss_base_score REAL NOT NULL CHECK (cvss_base_score BETWEEN 0 AND 10),
    exploit_available BOOLEAN NOT NULL,
    days_unpatched INTEGER NOT NULL CHECK (days_unpatched >= 0),
    category TEXT NOT NULL,
    affected_component TEXT,
    description TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    financial_loss_inr INTEGER NOT NULL,
    downtime_hours INTEGER NOT NULL,
    incident_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS rbi_mappings (
    mapping_id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    category TEXT NOT NULL,
    rbi_clause TEXT,
    nci_clause TEXT,
    sebi_clause TEXT,
    description TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_asset_id ON vulnerabilities(asset_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_category ON vulnerabilities(category);
CREATE INDEX IF NOT EXISTS idx_rbi_mappings_asset_category ON rbi_mappings(asset_type, category);
CREATE INDEX IF NOT EXISTS idx_assets_asset_type ON assets(asset_type);
