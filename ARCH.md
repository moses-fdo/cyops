# Architecture Document (ARCH.md) - CyberLens 2.0

## 1. Overview
This document describes the high-level and detailed architecture of CyberLens 2.0, an AI‑enhanced Cyber Risk Quantification Platform for India’s digital financial infrastructure.

## 2. Architectural Goals
- **Modularity**: Separation of concerns between data, risk engine, and presentation.
- **Demo‑Friendly**: Zero‑setup via Docker Compose with sample data.
- **Scalable**: Clear path to micro‑services, Kubernetes, and enterprise upgrades.
- **Extensible**: Plugin‑style architecture for new data sources, ML models, and controls.
- **Observable**: Logging, validation script, and clear metrics.

## 3. High‑Level Architecture (Layers)

```
┌─────────────────────────────────────────────────────┐
│ LAYER 0: DEPLOYMENT & OPS                          │
│  - docker-compose.yml                              │
│  - validate.sh                                     │
│  - SIH_SUBMISSION_MODE.py                          │
│  - Dockerfile                                      │
└───────────────────────────┬─────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│ LAYER 1: INDIAN FINANCIAL DATA LAYER               │
│  - schema.sql                                      │
│  - data_loader.py                                  │
│  - assets.csv, vulnerabilities.csv,                │
│    incidents.csv, rbi_mappings.csv (sample)        │
│  - SQLite database (or in‑memory DataFrames)       │
└───────────────────────────┬─────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│ LAYER 2: CORE RISK & AI ENGINE                     │
│  - risk_engine.py                                  │
│    ├─ rbi_weighted_cvss()                          │
│    ├─ compute_cr_i()                               │
│    ├─ expected_annual_loss()                       │
│    ├─ llm_remediate()                              │
│    ├─ quantum_risk_estimate()                      │
│    └─ optimize_budget()                            │
│  - controls_library.py                             │
│  - constants.py (RBI multipliers, etc.)            │
└───────────────────────────┬─────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────┐
│ LAYER 3: SIH DASHBOARD (Streamlit)                 │
│  - streamlit_app.py                                │
│  - components/                                     │
│    ├─ executive_view.py                            │
│    ├─ technical_view.py                            │
│    ├─ sih_features.py                              │
│    └─ widgets.py                                   │
│  - assets/ (logo, icons, SVG diagrams)            │
│  - i18n/ (optional)                                │
└─────────────────────────────────────────────────────┘
```

## 4. Component Details

### 4.1 Deployment & Ops Layer
- **docker-compose.yml**: Defines services `app` (Streamlit) and optionally `db` (SQLite) – though SQLite is file‑based, we mount a volume for persistence.
- **Dockerfile**: Builds a slim Python image with required dependencies.
- **validate.sh**: Runs a series of checks (score ranges, ROSI calculations, mapping correctness) and exits with non‑zero on failure.
- **SIH_SUBMISSION_MODE.py**: Helper script that, when triggered from the UI, generates a markdown file for SIH submission.

### 4.2 Data Layer
- **schema.sql**: Defines tables `assets`, `vulnerabilities`, `incidents`, `rbi_mappings`.
- **data_loader.py**: Loads CSV files (or provided SQL) into SQLite; provides functions `get_assets()`, `get_vulnerabilities(asset_id=None)`, `get_rbi_mapping(category, asset_type)`.
- Sample data files (`*.csv`) are stored in the `data/` directory and represent a realistic but fictitious UPI/banking ecosystem.

### 4.3 Core Risk & AI Engine
All core logic resides in `risk_engine.py`, which is imported by the Streamlit app.

#### 4.3.1 RBI‑Weighted CVSS
- Takes a vulnerability dict and asset dict, returns a float 0‑10.
- Uses asset criticality, RBI multipliers (by asset_type and vuln category), patch penalty (days_unpatched/7, capped at 3), exploit boost (1.5 if exploit available), and optional threat intel and transaction anomaly factors (default 1.0 for demo).

#### 4.3.2 Cyber Resilience Index (CR‑I)
- Computed per asset as: `CR_I = 100 - Σ[(10 - rbi_weighted_cvss(v)) * w_i] / Σ w_i`, where `w_i = asset.criticality * asset.daily_transaction_volume`.
- Result clamped to 0‑100. Higher CR‑I means more resilient (lower risk).

#### 4.3.3 Expected Annual Loss (EAL)
- Probability of incident = min(rbi_weighted_cvss/10, 0.9).
- Loss per incident = (downtime_cost_per_hour * avg_incident_hrs) + (daily_transaction_volume * fraud_loss_rate).
- EAL = probability * loss_per_incident (₹/year).

#### 4.3.4 Few‑Shot LLM Remediation Generator
- Constructs a prompt with CVE description, asset info, and relevant RBI clause.
- Uses a quantized TinyLlama model (via `llama.cpp` Python bindings or `transformers` with `bitsandbytes`) to generate completion.
- Falls back to a rule‑based template if model loading fails (for demo robustness).

#### 4.3.5 Quantum‑Ready Risk Estimator
- Checks asset’s `crypto_profile` field (if present) for algorithms weaker than RSA‑2048/ECC‑224.
- Returns a multiplier (e.g., 1.2) to increase risk weight; default 1.0.

#### 4.3.6 ROSI‑Driven Budget Optimizer
- Input: list of controls from `controls_library.py`, each with `cost_inr` and a function to compute `risk_reduction_inr_per_year` (by simulating control effectiveness on affected vulns).
- ROSI = (risk_reduction - cost) / cost * 100.
- Demo uses greedy algorithm: sort by ROSI descending, select while budget allows.
- Enterprise variant can swap `optimize_budget_greedy` with `optimize_budget_pulp` (using PuLP).

### 4.4 Dashboard (Streamlit)
- **streamlit_app.py**: Main entry point; sets page config, loads data, defines sidebar, and routes to views.
- **executive_view.py**: Renders metric cards (total exposure, CR‑I gauge, compliance %), top 3 risks, budget allocator, optimal plan table, and SIH summary button.
- **technical_view.py**: Renders asset explorer, vulnerability table (using `st.dataframe` with column configuration), detail modal (via `st.expander` or custom component), transaction flow diagram, and compliance heatmap.
- **sih_features.py**: Implements “Load UPI Switch Demo Scenario” button and “Generate SIH Summary” functionality.
- **widgets.py**: Reusable Streamlit components (e.g., metric card with tooltip, gauge using `st.progress` or `st.metric`).

## 5. Data Flow
1. **Startup**: `data_loader.py` reads CSV files into SQLite (or DataFrames).
2. **UI Interaction**:
   - User selects asset (optional) → dashboard queries vulnerabilities for that asset.
   - For each vulnerability, `risk_engine.rbi_weighted_cvss` is called.
   - Asset‑level CR‑I and EAL are computed.
   - Total exposure is sum of EAL across all assets (or filtered set).
   - RBI mapping is fetched via `get_rbi_mapping`.
3. **Budget Allocation**:
   - User sets budget slider → `risk_engine.optimize_budget` is called with the budget.
   - Returns selected controls, total cost, total risk reduction, remaining budget.
4. **What‑If Simulation**:
   - User toggles a control in the detail modal → engine recomputes affected vuln scores assuming control effectiveness (e.g., reduce `days_unpatched` to 0 for patching control, set `exploit_available=False` for MFA control).
   - Updated CR‑I and EAL are reflected instantly.
5. **LLM Remediation**:
   - User clicks “Show LLM Remediation” in detail modal → `risk_engine.llm_remediate` is called with vuln and asset details.
   - Result displayed in the modal.

## 6. Communication & APIs (if FastAPI backend is used)
Although the demo runs the engine in‑process, the design allows exposing the engine as a REST API:
- **GET /assets** → list assets.
- **GET /assets/{asset_id}** → asset details.
- **GET /vulnerabilities** → list with filters.
- **GET /vulnerabilities/{vuln_id}** → detail.
- **POST /cr-i** → compute CR‑I for given filters.
- **POST /eal** → compute EAL for given vuln.
- **POST /optimize/budget** → returns optimal control set.
- **POST /llm/remediate** → returns remediation steps.

## 7. Security Considerations
- No external API calls in demo; all data is local.
- No storage of PII; sample data uses fictitious names and volumes.
- Code avoids logging sensitive information.
- Docker image runs as non‑root user (via `USER` directive in Dockerfile).
- Open‑source license (AGPL‑3) permits community review.

## 8. Scalability & Extensibility
- **Micro‑service Ready**: Wrap `risk_engine.py` functions in FastAPI endpoints.
- **Plugin Architecture**: To add a new data source (e.g., SIEM), create a new loader in `data_loader.py` and expose via new API endpoint or direct import.
- **ML Upgrade**: Replace `rbi_weighted_cvss` with a function that loads an XGBoost model and predicts on engineered features (CVSS, days_unpatched, etc.).
- **Exact Optimizer**: Implement `optimize_budget_pulp` using PuLP; switch via config flag.
- **Deployment**: Helm chart provided for Kubernetes; Docker image built via multi‑stage Dockerfile for small size.
- **Observability**: Add Prometheus metrics endpoint (optional) for request latency and error rates.

## 9. Diagram (Textual)
```
+-------------------+      +-------------------+      +-------------------+
|   Deployment &    |      |   Data Layer      |      |   Core Engine     |
|      Ops          |◄────►| (SQLite/CSV)      |◄────►| (Risk Calculations)|
| (docker, validate)|      +-------------------+      +-------------------+
+-------------------+             ▲                         ▲
        │                         │                         │
        ▼                         │                         │
+-------------------+             │                         │
|   Streamlit UI    |─────────────┘                         │
| (Executive/Tech)  │                                       │
+-------------------+                                       │
        │                                                   │
        ▼                                                   ▼
+-------------------+                     +-------------------+
|   User Interaction│                     |   Future Extensions|
| (sliders, toggles)│                     | (ML model, SIEM,   │
+-------------------+                     |  Kubernetes, etc.)  |
                                            +-------------------+
```

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*