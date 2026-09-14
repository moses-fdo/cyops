# CyberLens 2.0 – RBI‑Aligned AI Cyber Risk Quantification Platform

**An AI‑enhanced Cyber Risk Quantification Platform tailored for India’s digital financial infrastructure (UPI, banking, payment systems).**  
Transforms raw vulnerability, asset, and transaction data into RBI‑regulated financial risk metrics (in ₹) and provides an AI‑optimized investment plan that maximizes risk reduction per rupee spent.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start (Demo)](#quick-start-demo)
- [Running the API (Optional)](#running-the-api-optional)
- [Running Tests](#running-tests)
- [Validation Script](#validation-script)
- [SIH Submission](#sih-submission)
- [Architecture & Documentation](#architecture--documentation)
- [Future Work & Scaling](#future-work--scaling)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview
CyberLens 2.0 addresses a critical gap: existing cyber‑risk tools give qualitative scores (Low/Medium/High) that do not translate into financial impact or actionable budget decisions. Regulators (RBI, SEBI, NPCI) require quantifiable risk exposure in monetary terms for effective cyber‑risk governance and budget allocation.

The platform delivers:
- **RBI‑Weighted Cyber Resilience Index (CR‑I)** – a 0‑100 score blending CVSS, asset criticality, RBI/SEBI/NPCI compliance, patch timeliness, exploit availability, threat intel, and transaction‑anomaly signals.
- **Financial Impact in ₹** – Expected Annual Loss (EAL) per vulnerability and total annual exposure.
- **Few‑Shot LLM Remediation** – generates simple Hindi/English remediation steps for branch staff.
- **ROSI‑Driven Budget Optimizer** – selects security controls maximizing risk reduction under a given budget (e.g., ₹1 Crore).
- **SIH‑Ready Streamlit Dashboard** – executive (₹ focus, compliance) and technical (asset drill‑down, LLM remediation, what‑if) views.
- **Zero‑Setup Demo** – `docker compose up` launches a fully functional dashboard with pre‑loaded Indian financial sector sample data.

---

## Features
| Feature | Description |
|---------|-------------|
| **RBI‑Weighted CVSS** | Adjusts base CVSS with asset criticality, RBI multipliers, patch penalty, exploit boost, and optional threat/intel factors. |
| **Cyber Resilience Index (CR‑I)** | 0‑100 index (higher = more resilient) computed per asset and aggregated. |
| **Expected Annual Loss (EAL)** | Calculates annual financial loss in ₹ per vulnerability using transaction volume, downtime cost, and fraud loss assumptions. |
| **RBI/SEBI/NPCI Mapping** | Auto‑tags each vulnerability with the exact circular/clause (e.g., RBI/2023-24/105.A.3). |
| **Few‑Shot LLM Remediation** | Uses a quantized TinyLlama model to generate 3 concise remediation steps in simple Hindi/English; falls back to template if model unavailable. |
| **What‑If Simulator** | Toggle security controls in the vulnerability detail modal to see real‑time impact on CR‑I and EAL. |
| **ROSI‑Driven Knapsack Optimizer** | Greedy (demo) or PuLP (enterprise) optimizer that picks controls maximizing risk reduction under budget. |
| **Executive Dashboard** | Total exposure (₹), CR‑I gauge, RBI compliance %, top 3 risks, budget allocator, optimal plan table, SIH summary generator. |
| **Technical Dashboard** | Asset explorer, vulnerability table, detail modal (technical desc, RBI mapping, LLM remediation, what‑if), transaction flow diagram, compliance heatmap. |
| **Zero‑Setup Demo** | Pre‑loaded sample data representing a realistic UPI switch and banking assets; no external API keys needed. |
| **Validation Script** | `./validate.sh` runs quick checks on score ranges, ROSI, mappings, and LLM fallback. |
| **SIH Submission Helper** | One‑click “Generate SIH Summary” creates a markdown file ready for upload to the SIH portal. |
| **Extensible Architecture** | Clean layer separation; easy to swap in real ML models (XGBoost), integrate real‑time feeds (CERT‑In, SIEM), or deploy as micro‑services (FastAPI + Kubernetes). |

---

## Project Structure
```
cyberlens-2.0/
├── data/                         # Sample CSV files (assets, vulnerabilities, incidents, rbi_mappings)
│   ├── assets.csv
│   ├── vulnerabilities.csv
│   ├── incidents.csv
│   └── rbi_mappings.csv
├── docs/                         # Additional documentation (if any)
│   └── ...
├── tests/                        # Unit, integration, and end‑to‑end tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .dockerignore
├── .gitignore
├── docker-compose.yml            # Defines the Streamlit app service
├── Dockerfile                    # Builds the runtime image
├── PRD.md                        # Product Requirements Document
├── TRD.md                        # Technical Requirements Document
├── ARCH.md                       # Architecture Document
├── API_SPEC.md                   # API Specification (if enabling FastAPI backend)
├── DATA_MODEL.md                 # Data Model (SQLite schema)
├── UX_FLOW.md                    # User Experience Flow
├── TEST_PLAN.md                  # Test Plan
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── validate.sh                   # Validation script for SIH judges
├── schema.sql                    # SQLite table definitions
├── data_loader.py                # Loads CSV into SQLite (or DataFrames)
├── risk_engine.py                # Core risk calculations (CVSS, CR‑I, EAL, LLM, optimizer)
├── controls_library.py           # Defines security controls and their effectiveness
├── streamlit_app.py              # Main Streamlit application
├── components/                   # Streamlit UI components
│   ├── executive_view.py
│   ├── technical_view.py
│   ├── sih_features.py
│   └── widgets.py
└── (optional) api.py             # FastAPI entry point (if ENABLE_API=true)
```

---

## Requirements
- **Python 3.11+** (used in the Docker image)
- **Docker Engine** (for the zero‑setup demo)
- **Internet access** (only needed at build time to fetch dependencies; the demo runs fully offline)

The `requirements.txt` includes:
```
streamlit==1.38.0
pandas==2.2.2
scikit-learn==1.5.0
torch==2.4.0
transformers==4.44.0
bitsandbytes==0.43.1  # for 4‑bit quantized LLM (optional)
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.9.2
```

*Note*: The LLM dependencies (`torch`, `transformers`, `bitsandbytes`) are only required if you want to use the LLM remediation feature. The demo will gracefully fall back to a rule‑based template if they are not installed or if model loading fails.

---

## Quick Start (Demo)

### Using Docker (Recommended)
```bash
# Clone the repository (if not already)
git clone https://github.com/your-org/cyberlens-2.0.git
cd cyberlens-2.0

# Build and start the services
docker compose up --build
```
The command will:
1. Build a Docker image with all dependencies.
2. Launch a Streamlit app accessible at **http://localhost:8501**.
3. Load the sample data from the `data/` directory into an internal SQLite database.

### Without Docker (Directly)
```bash
# Clone and enter the directory
git clone https://github.com/your-org/cyberlens-2.0.git
cd cyberlens-2.0

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
```
The app will be available at **http://localhost:8501**.

### First‑Time Demo Flow
1. The dashboard opens to the **Executive View**.
2. Click **“Load UPI Switch Demo Scenario”** (sidebar) to load a pre‑defined high‑risk set of assets/vulnerabilities.
3. Observe the Executive metrics update:
   - **Total Annual Cyber Risk Exposure** (e.g., ₹4,200 Cr/year)
   - **Cyber Resilience Index (CR‑I)** (e.g., 38/100)
   - **Top 3 Risks** cards showing UPI‑specific vulnerabilities.
4. Use the **Budget Allocator** slider to set your available budget (e.g., ₹1 Crore).
5. Click **“Show Optimal Investment Plan”** to see the optimizer’s recommendation (controls, cost, risk reduction, ROSI).
6. Switch to the **Technical View** via the sidebar to explore assets, see vulnerability details, LLM‑generated remediation steps, and run what‑if simulations.
7. At any point, click **“Generate SIH Summary”** (sidebar) to create a markdown file (`SIH_Submission.md`) ready for upload to the SIH portal.

---

## Running the API (Optional)
If you wish to expose the risk engine as a RESTful service (e.g., for micro‑service deployment or integration with other systems):

1. Set the environment variable `ENABLE_API=true` (or edit `docker-compose.yml` to uncomment the `api` service).
2. Rebuild and restart:
   ```bash
   docker compose up --build
   ```
3. The API will be available at **http://localhost:8000**.
   - Interactive docs: **http://localhost:8000/docs** (Swagger UI)
   - Alternative docs: **http://localhost:8000/redoc** (ReDoc)

Refer to `API_SPEC.md` for the complete list of endpoints.

---

## Running Tests
Unit and integration tests are written with `pytest`. To run them:

```bash
# Ensure you are in the project root
pip install -r requirements.txt  # if not already installed
pip install pytest               # test runner

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest
```

End‑to‑end (E2E) tests require a running Streamlit instance. A simple E2E check is performed by the validation script (see below).

---

## Validation Script
The `validate.sh` script provides a quick sanity check that SIH judges can run to gain confidence in the demo.

```bash
chmod +x validate.sh
./validate.sh
```

The script will:
1. Launch the Streamlit app in the background.
2. Call key functions (via direct import or HTTP if API enabled) to verify:
   - RBI‑weighted CVSS values are within 0‑10.
   - CR‑I is within 0‑100.
   - EAL is non‑negative.
   - Budget optimizer returns a set where total cost ≤ budget.
   - LLM remediation returns a list of strings (or falls back to template).
3. Shut down the background app.
4. Print a summary and exit with code `0` on success, or non‑zero on failure.

You can also run it with Docker:
```bash
./validate.sh   # assumes Docker is available and will use docker compose
```

---

## SIH Submission
To generate the required submission markdown:
1. Run the demo (via Docker or directly).
2. Optionally load the “UPI Switch Demo Scenario” for impactful metrics.
3. Click the **“Generate SIH Summary”** button in the sidebar (available in both views).
4. A file named `SIH_Submission.md` will appear in the working directory.
5. Upload this file to the SIH portal as part of your submission.

The generated markdown includes:
- Problem statement (taken from SIH theme)
- Solution overview (highlighting key innovations)
- Impact metrics (₹ protected, users safeguarded, MGNREGA‑day equivalence)
- Technical stack diagram
- Future scope and open‑source pledge

---

## Architecture & Documentation
For deeper details, refer to the following documents in the repository root:
- **[PRD.md](./PRD.md)** – Product Requirements
- **[TRD.md](./TRD.md)** – Technical Requirements
- **[ARCH.md](./ARCH.md)** – Architecture (layers, components, data flow)
- **[API_SPEC.md](./API_SPEC.md))** – API Specification (if enabling FastAPI)
- **[DATA_MODEL.md](./DATA_MODEL.md))** – Data Model (SQLite schema)
- **[UX_FLOW.md](./UX_FLOW.md))** – User Experience Flow
- **[TEST_PLAN.md](./TEST_PLAN.md))** – Test Plan

---

## Future Work & Scaling
While the demo delivers full SIH‑ready functionality, the architecture is designed for growth:
- **Real‑Time Feeds**: Integrate CERT‑In vulnerability alerts, NVD streams, or SIEM logs via the data loader plugin architecture.
- **ML‑Enhanced Scoring**: Replace the rule‑based RBI‑weighted CVSS with an XGBoost model trained on NVD + RBI breach datasets (feature engineering script provided).
- **Exact Optimization**: Swap the greedy knapsack with PuLP/Pyomo for an optimal integer solution.
- **Cloud‑Native Deployment**: Helm chart provided for Kubernetes; the API can be scaled horizontally.
- **Multi‑Language Support**: Add Hindi/English toggle and expand to other Indian languages.
- **Lightweight Rural Build**: A stripped‑down version that runs on a Raspberry Pi for deployment in resource‑constrained bank branches.
- **Audit & Reporting**: Automated PDF/Excel reports for RBI inspections.

---

## License
CyberLens 2.0 is released under the **GNU Affero General Public License v3.0 (AGPL‑3)**. See the [LICENSE](LICENSE) file for details.

> This license ensures that any modifications or deployments of the software (including as a service over a network) must also make the source code available to users.

---

## Acknowledgements
- **RBI, SEBI, NPCI** – For publishing the cybersecurity guidelines and circulars that informed the RBI‑weighted scoring and compliance mapping.
- **NVD & CERT‑In** – For public vulnerability data used to calibrate and validate the model.
- **Open‑Source Community** – For Streamlit, FastAPI, PyTorch, Hugging Face Transformers, and many other libraries that made rapid development possible.
- **Smart India Hackathon (SIH) Organizers** – For providing the platform to showcase innovative solutions for India’s digital future.

---

**Ready to demo. Ready to impact. Ready to win.**  
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*