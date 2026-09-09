# Product Requirements Document (PRD) - CyberLens 2.0

## 1. Overview
CyberLens 2.0 is an AI‑enhanced Cyber Risk Quantification Platform tailored for India’s digital financial infrastructure (UPI, banking, payment systems). It transforms raw vulnerability, asset, and transaction data into RBI‑regulated financial risk metrics (in ₹) and provides an AI‑optimized investment plan that maximizes risk reduction per rupee spent.

## 2. Problem Statement
Indian financial institutions process over 350 million UPI transactions daily (≈₹3.5 lakh crore). Existing risk tools give qualitative scores (Low/Medium/High) that do not translate into financial impact or actionable budget decisions. Regulators (RBI, SEBI, NPCI) require quantifiable risk exposure in monetary terms for effective cyber‑risk governance and budget allocation.

## 3. Goals & Objectives
- Quantify cyber risk in **Indian Rupees (₹)** for assets in the UPI/banking ecosystem.
- Provide an **RBI‑Weighted Cyber Resilience Index (CR‑I)** (0‑100) that incorporates CVSS, asset criticality, RBI/SEBI/NPCI compliance, patch timeliness, exploit availability, threat intelligence, and transaction‑anomaly signals.
- Generate **Few‑Shot LLM‑based remediation steps** in simple Hindi/English for non‑technical staff.
- Offer a **ROSI‑driven budget optimizer** (knapsack) that selects security controls maximizing risk reduction under a given budget (e.g., ₹1 Crore).
- Deliver a **SIH‑ready Streamlit dashboard** with executive (₹ focus, compliance) and technical (asset drill‑down, LLM remediation, what‑if) views.
- Ensure **zero‑setup demo** (`docker compose up`) with pre‑loaded Indian financial sector sample data.
- Provide **clear scalability path** to enterprise deployment (micro‑services, PuLP optimizer, XGBoost model, Kubernetes).

## 4. Target Users
- **Executives** (RBI governors, Bank CFOs, Risk Officers) – need ₹ exposure, compliance score, budget recommendations.
- **CISOs / Security Engineers** – need asset‑level vulnerability details, remediation steps, what‑if simulations.
- **Operations / Branch Staff** – need simple Hindi/English remediation guidance.

## 5. Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Load/sample Indian financial sector data (assets, vulns, incidents) | Must |
| FR2 | Compute RBI‑Weighted CVSS score per vulnerability | Must |
| FR3 | Calculate Cyber Resilience Index (CR‑I) per asset (0‑100) | Must |
| FR4 | Compute Expected Annual Loss (EAL) in ₹ per vulnerability | Must |
| FR5 | Aggregate asset‑level EAL to total annual cyber risk exposure (₹/year) | Must |
| FR6 | Map each vulnerability to exact RBI/SEBI/NPCI circular/clause | Must |
| FR7 | Generate few‑shot LLM remediation steps (Hindi/English) | Should |
| FR8 | Provide What‑If simulator for security controls (toggle impact on CR‑I & EAL) | Should |
| FR9 | ROSI‑driven budget optimizer (knapsack) to select controls under budget | Should |
| FR10 | Executive dashboard: total exposure (₹), CR‑I gauge, top 3 risks, budget allocator, SIH summary generator | Must |
| FR11 | Technical dashboard: asset explorer, vulnerability table, detail modal with LLM remediation, transaction flow impact, compliance heatmap | Must |
| FR12 | Zero‑setup demo via Docker Compose with sample data | Must |
| FR13 | Self‑test script (`validate.sh`) to verify score ranges, ROSI, mappings | Should |
| FR14 | Export SIH submission summary (Markdown/PDF) | Should |

## 6. Non‑Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR1 | Response time < 2 s for dashboard interactions | Must |
| NFR2 | Deployable on a single VM with ≤2 GB RAM, 2 vCPU | Must |
| NFR3 | Data stored locally (SQLite) – no external API keys required for demo | Must |
| NFR4 | Code modular, well‑documented, with clear extension points | Should |
| NFR5 | Open‑source core (AGPL‑3) with contribution guide | Should |
| NFR6 | Support for Hindi/English UI strings (i18n ready) | Should |
| NFR7 | Logging of key actions for audit traceability | Should |

## 7. Assumptions & Constraints
- Demo uses synthetic but realistic Indian financial sector data (UPI switch, CBS servers, mobile banking apps).
- RBI/SEBI/NPCI circular mappings are based on publicly available guidelines as of Sep 2026.
- LLM remediation uses a quantized TinyLlama model (~4 GB) that runs on CPU; no GPU required for demo.
- Budget optimizer uses greedy algorithm for demo; enterprise version can swap to PuLP for exact solution.
- No real‑time feeds are required for demo; hooks exist for future integration (CERT‑In, NVD, SIEM).

## 8. Success Metrics (for SIH judging)
- Dashboard loads and shows baseline risk exposure within 5 s.
- RBI‑Weighted CVSS and CR‑I scores fall within 0‑100 range.
- Budget optimizer returns a feasible control set whose total cost ≤ user‑specified budget.
- LLM remediation output is intelligible Hindi/English and maps to RBI guidelines.
- One‑click “Generate SIH Summary” produces a markdown file covering problem statement, solution, impact, tech stack, future scope.
- All validation tests pass (`./validate.sh` returns 0).

## 9. Open Issues / Future Work
- Integrate real‑time CERT‑In vulnerability feed.
- Train XGBoost model on NVD + RBI breach datasets to replace rule‑based scorer.
- Implement exact integer optimization via PuLP/Pyomo.
- Deploy to Kubernetes with Helm chart.
- Build lightweight “CyberLens for Rural Banks” version running on Raspberry Pi.
- Add multi‑language support (regional Indian languages).

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*