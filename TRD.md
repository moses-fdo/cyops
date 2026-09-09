# Technical Requirements Document (TRD) - CyberLens 2.0

## 1. Purpose
This document outlines the technical specifications, architecture, and implementation details for CyberLens 2.0, an AI‑enhanced Cyber Risk Quantification Platform for India’s digital financial infrastructure.

## 2. System Architecture Overview
CyberLens follows a layered, modular architecture:
- **Layer 0: Deployment & Ops** – Docker Compose, validation script, SIH submission helper.
- **Layer 1: Indian Financial Data Layer** – SQLite/CSV storage of assets, vulnerabilities, incidents, RBI/SEBI/NPCI mappings.
- **Layer 2: Core Risk & AI Engine** – RBI‑Weighted CVSS, Cyber Resilience Index (CR‑I), Financial Impact Calculator, Few‑Shot LLM Remediation Generator, Quantum‑Ready Risk Estimator, ROSI‑driven Budget Optimizer.
- **Layer 3: SIH Dashboard (Streamlit)** – Executive & Technical views, SIH‑specific features (demo loader, summary generator).

Components communicate via well‑defined Python functions/APIs; the Streamlit frontend calls the backend engine directly (in‑process) for the demo, but the engine is designed to be exposed as a FastAPI micro‑service for future scaling.

## 3. Technology Stack
| Layer | Technology | Reason |
|-------|------------|--------|
| Frontend | Streamlit (v1.38+) | Rapid UI development, built‑in charting, easy deployment. |
| Backend Engine | Python 3.11+, FastAPI (optional) | Core risk calculations; can be exposed as REST API. |
| Data Storage | SQLite (demo) / CSV | Zero‑setup, portable, suitable for demo data. |
| ML / AI | scikit‑learn (optional), TinyLlama (4‑bit quantized, via `llama.cpp` or `transformers`) | Optional XGBoost scorer; LLM for remediation runs on CPU. |
| Deployment | Docker Compose | One‑command launch, reproducible environment. |
| Testing | pytest | Unit and integration tests. |
| Documentation | MkDocs / Sphinx (optional) | For future docs generation. |

## 4. Component Specifications

### 4.1 Data Layer
- **Assets Table**: `asset_id`, `name, asset_type, business_unit, criticality (1‑10), daily_transaction_volume, replacement_cost, downtime_cost_per_hour, user_segments (e.g., retail, corporate, jan_dhan)`.
- **Vulnerabilities Table**: `vuln_id, asset_id, cve_id, cvss_base_score, exploit_available (bool), days_unpatched, category (e.g., Authentication Bypass), affected_component`.
- **Incidents Table** (optional for calibration): `incident_id, asset_id, type, financial_loss_inr, downtime_hours, date`.
- **RBI Mappings Table**: `vuln_category, asset_type, rbi_clause, nci_clause, sebi_clause, description`.

All tables are defined in `schema.sql` and loaded via `data_loader.py`.

### 4.2 Core Risk & AI Engine
#### 4.2.1 RBI‑Weighted CVSS
```python
def rbi_weighted_cvss(vuln: dict, asset: dict) -> float:
    base = vuln['cvss_base_score']
    crit_mult = asset['criticality'] / 10.0
    rbi_mult = RBI_MULTIPLIERS.get(asset['asset_type'], {}).get(vuln['category'], 
                                 RBI_MULTIPLIERS.get(asset['asset_type'], {}).get('Default', 1.0))
    patch_penalty = min(vuln['days_unpatched'] / 7.0, 3.0)  # RBI expects ≤7 days for critical
    exploit_boost = 1.5 if vuln['exploit_available'] else 1.0
    # Optional threat intel factor (1.0 if not integrated)
    threat_factor = 1.0
    # Optional transaction anomaly factor (1.0 if not integrated)
    txn_anomaly_factor = 1.0
    score = base * crit_mult * rbi_mult * (1 + patch_penalty/10) * exploit_boost * threat_factor * txn_anomaly_factor
    return min(score, 10.0)
```

#### 4.2.2 Cyber Resilience Index (CR‑I)
CR‑I = 100 – (Weighted Average of (10 – RBI‑Weighted CVSS) across assets, weighted by asset criticality and transaction volume).  
Formula:
```
CR_I = 100 - Σ [ (10 - rbi_weighted_cvss(v)) * w_i ] / Σ w_i
where w_i = asset[i].criticality * asset[i].daily_transaction_volume
```
Result clamped to 0‑100.

#### 4.2.3 Financial Impact Calculator (EAL)
```python
def expected_annual_loss(vuln: dict, asset: dict) -> float:
    # Probability of incident in a year (simplified)
    prob = min(rbi_weighted_cvss(vuln, asset) / 10.0, 0.9)  # max 90%
    # Loss per incident: downtime cost + estimated fraud loss
    avg_incident_hrs = 6.0  # assumption
    downtime_loss = asset['downtime_cost_per_hour'] * avg_incident_hrs
    fraud_loss = asset['daily_transaction_volume'] * 0.0001  # 0.01% of daily volume as fraud
    loss_per_incident = downtime_loss + fraud_loss
    eal = prob * loss_per_incident
    return eal  # ₹/year
```

#### 4.2.4 Few‑Shot LLM Remediation Generator
- Uses a prompt template:
  ```
  You are a cybersecurity advisor for Indian banks. Given the following vulnerability:
  CVE: {cve_id}
  Description: {cve_description}
  Affected Asset: {asset_name} ({asset_type})
  RBI Guideline: {rbi_clause}
  Provide 3 concise remediation steps in simple Hindi/English that a branch officer can implement.
  ```
- Model: TinyLlama‑1.1B‑Chat‑v1.0 quantized to 4‑bit (uses ~4 GB RAM).  
- For demo, if model loading fails, fall back to a rule‑based template.

#### 4.2.5 Quantum‑Ready Risk Estimator
- Flags assets using cryptographic algorithms weaker than RSA‑2048 or ECC‑224 (based on `asset.crypto_profile` field, if present).
- Returns a multiplier (e.g., 1.2) to increase CR‑I risk weight for such assets.
- Placeholder for future integration with asset inventory scanners.

#### 4.2.6 ROSI‑Driven Budget Optimizer (Knapsack)
- Input: list of controls, each with `cost_inr`, `risk_reduction_inr_per_year` (calculated as sum of EAL reduction for affected vulns).
- ROSI = (risk_reduction - cost) / cost * 100.
- Greedy algorithm (demo): sort by ROSI descending, pick while budget allows.
- Enterprise variant: replace with PuLP integer linear programming to maximize total risk reduction under budget.

### 4.3 Dashboard (Streamlit)
- **Executive View**:
  - Metric cards: Total Exposure (₹/year), CR‑I (gauge), RBI Compliance %.
  - Top 3 Risks cards: Asset name, ₹ Contribution, Primary Vuln, RBI Reference.
  - Budget Allocator slider (₹0‑10 Cr) + “Show Optimal Plan” button.
  - Optimal Plan table: Control, Cost, Risk Reduction, ROSI.
  - “Generate SIH Summary” button → creates `SIH_Submission.md`.
- **Technical View**:
  - Asset Explorer dropdown.
  - Vulnerability Table (sortable) with columns: Vuln ID, CVE, CVSS, CR‑I Score, Days Unpatched, Exploit, Risk Contribution (₹/year), Actions.
  - Action buttons: “Show Details”, “Simulate Fix”.
  - Detail Modal:
    - Technical description (CVE).
    - Expandable RBI/SEBI/NPCI Mapping.
    - LLM‑Generated Remediation Steps.
    - What‑If Simulator: toggle controls → live update of CR‑I and Risk Contribution.
  - Transaction Flow Impact Diagram (static SVG/PNG) showing UPI flow with risk overlay.
  - Compliance Heatmap: % adherence per RBI guideline (Auth, Patch Mgmt, Data Protection, etc.).
  - Bottom: “Export Report” button (placeholder for PDF).

### 4.4 APIs (if FastAPI backend is used)
- `GET /assets` – list assets.
- `GET /assets/{asset_id}` – asset details.
- `GET /vulnerabilities` – list vulnerabilities (filter by asset_id).
- `GET /vulnerabilities/{vuln_id}` – vulnerability detail.
- `POST /calculate/cr-i` – returns CR‑I for given asset filters.
- `POST /calculate/eal` – returns EAL for given vuln.
- `POST /optimize/budget` – returns optimal control set for given budget.
- `POST /llm/remediate` – returns remediation steps.

## 5. Data Flow
1. Data Loader reads `assets.csv`, `vulnerabilities.csv`, `incidents.csv`, `rbi_mappings.csv` into SQLite tables (or uses in‑memory DataFrames for demo).
2. Streamlit UI triggers calculations:
   - For each vulnerability, compute RBI‑Weighted CVSS via engine.
   - Compute asset‑level CR‑I (weighted average).
   - Compute asset‑level EAL.
   - Sum EAL for total exposure.
   - Map vuln to RBI clause via lookup table.
3. User interacts:
   - Adjusts budget slider → calls optimizer.
   - Toggles control in What‑If → recomputes affected vuln scores (adjusting days_unpatched or exploit_boost per control effectiveness).
   - Views LLM remediation → calls generator.
4. All results cached in Streamlit session state for performance.

## 6. Security & Privacy
- No external API calls in demo; all data local.
- No PII stored; sample data uses fictitious asset names and volumes.
- Code does not log sensitive information.
- Open‑source license (AGPL‑3) ensures community auditability.

## 7. Scalability & Extensibility
- **Micro‑service Ready**: Core engine functions can be wrapped in FastAPI endpoints.
- **Plugin Architecture**: New data sources (SIEM, vuln scanners) can add tables and loader functions.
- **ML Upgrade Path**: Replace `rbi_weighted_cvss` with `xgboost_model.predict(features)`; feature engineering script provided.
- **Exact Optimizer**: Swap greedy knapsack with PuLP model in `optimizer.py`.
- **Deployment**: Helm chart provided for Kubernetes; Docker image built via `Dockerfile`.

## 8. Testing Strategy (see TEST_PLAN.md for details)
- Unit tests for each engine function (score ranges, mapping correctness).
- Integration tests for data loader and dashboard callbacks.
- End‑to‑end test: launch docker compose, verify dashboard loads and shows expected metrics.
- Validation script (`validate.sh`) runs key checks.

## 9. Open Issues & Future Work
- Integrate real‑time CERT‑In feed via periodic pull.
- Implement authentication/authorization for multi‑user deployment.
- Add support for regional Indian languages in UI.
- Build lightweight version for Raspberry Pi (rural banks).
- Conduct pilot with RBI sandbox or NPCI.

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*