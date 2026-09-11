-- =====================================================================
-- CyberLens 2.0 Database Schema
-- Multi-Regulatory Banking Risk Quantification & Compliance Data Model
-- Enforces 3NF Normalization, Check Constraints, and Foreign Key Integrity.
-- =====================================================================

-- 1. ASSETS TABLE: Master inventory of banking digital assets
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    business_unit TEXT NOT NULL,
    criticality INTEGER NOT NULL CHECK (criticality BETWEEN 1 AND 10),
    daily_transaction_volume INTEGER NOT NULL CHECK (daily_transaction_volume >= 0),
    replacement_cost INTEGER NOT NULL CHECK (replacement_cost >= 0),
    downtime_cost_per_hour INTEGER NOT NULL CHECK (downtime_cost_per_hour >= 0),
    user_segments TEXT,          -- JSON array string (e.g. '["RETAIL", "MERCHANT"]')
    crypto_profile TEXT         -- Cryptographic suite (e.g. 'RSA-2048', 'RSA-1024', 'ECC-256')
);

-- 2. VULNERABILITIES TABLE: Active technical vulnerability catalog
CREATE TABLE IF NOT EXISTS vulnerabilities (
    vuln_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    cve_id TEXT,
    cvss_base_score REAL NOT NULL CHECK (cvss_base_score BETWEEN 0.0 AND 10.0),
    exploit_available INTEGER NOT NULL CHECK (exploit_available IN (0, 1)),
    days_unpatched INTEGER NOT NULL CHECK (days_unpatched >= 0),
    category TEXT NOT NULL,
    affected_component TEXT,
    description TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

-- 3. INCIDENTS TABLE: Historical security incidents and financial loss tracking
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    financial_loss_inr INTEGER NOT NULL CHECK (financial_loss_inr >= 0),
    downtime_hours INTEGER NOT NULL CHECK (downtime_hours >= 0),
    incident_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
);

-- 4. REGULATORY MAPPINGS TABLE: Crosswalk across RBI, NPCI, and SEBI compliance mandates
CREATE TABLE IF NOT EXISTS rbi_mappings (
    mapping_id TEXT PRIMARY KEY,
    asset_type TEXT NOT NULL,
    category TEXT NOT NULL,
    rbi_clause TEXT,            -- Master Direction on Digital Payment Security Controls
    nci_clause TEXT,            -- NPCI UPI/NFS/NUUP Procedural Guidelines
    sebi_clause TEXT,           -- SEBI Cybersecurity & Cyber Resilience Framework (CSCRF)
    description TEXT,
    UNIQUE(asset_type, category)
);

-- =====================================================================
-- Performance & Query Optimization Indexes
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_assets_asset_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_business_unit ON assets(business_unit);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_asset_id ON vulnerabilities(asset_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_category ON vulnerabilities(category);
CREATE INDEX IF NOT EXISTS idx_incidents_asset_id ON incidents(asset_id);
CREATE INDEX IF NOT EXISTS idx_rbi_mappings_asset_category ON rbi_mappings(asset_type, category);