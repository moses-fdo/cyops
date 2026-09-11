# Smart India Hackathon 2026 Idea Proposal

| Field | Details |
| :--- | :--- |
| **Problem Statement ID** | SIH2026-FIN-042 |
| **Problem Statement Title** | AI-Enhanced Cyber Risk Quantification & Automated Remediation Platform for India's Digital Financial Infrastructure |
| **Team ID** | K26032 |
| **Team Name** | Develupers |
| **Mentor** | Mrs. R. Hemalatha (ID: 2862) |

---

## 1. Executive Summary

India's digital payment ecosystem processes over 350 million daily UPI transactions valued at ₹3.5 lakh crore, yet cybersecurity teams still rely on qualitative risk matrices (Low/Medium/High) that cannot justify security spending to boardrooms or regulators. CyberLens 2.0 is an AI-driven Cyber Risk Quantification platform purpose-built for Indian financial infrastructure. It converts technical vulnerabilities into rupee-denominated Expected Annual Loss (EAL) and a regulatory-grounded Cyber Resilience Index (CR-I: 0–100) benchmarked against RBI, SEBI, and NPCI directives. Utilizing an algorithmic Return on Security Investment (ROSI) knapsack optimizer and dual-language (Hindi/English) generative remediation, CyberLens enables CISOs and bank executives to maximize risk reduction per rupee allocated. Serving public-sector banks, payment aggregators, and cooperative lenders, CyberLens bridges technical telemetry with financial governance, protecting critical transaction rails and national economic sovereignty.

---

## 2. The Problem & Existing Landscape

### 2.1. Problem Definition

India has established global leadership in digital public infrastructure, processing over 10 billion monthly transactions across the Unified Payments Interface (UPI). However, the underlying financial infrastructure—spanning Core Banking Systems (CBS), payment switches, API gateways, and regional cooperative bank networks—faces increasingly frequent and sophisticated cyber threats. 

A severe systemic gap exists: current cybersecurity assessment tools evaluate risks through static Common Vulnerability Scoring System (CVSS) numbers or subjective qualitative ratings (Low, Medium, High). These metrics do not reflect:
1. **Financial Exposure:** Traditional tools cannot translate a CVE into projected downtime costs, fraud losses, or balance sheet risk in Indian Rupees (₹).
2. **Transaction Velocity & Criticality:** A vulnerability on a high-throughput UPI switch processing ₹5,000 crore daily poses exponentially greater systemic danger than the same CVE on an internal staging server.
3. **Domestic Regulatory Alignment:** Global tools do not map vulnerabilities to Reserve Bank of India (RBI) Master Directions, SEBI cyber frameworks, or NPCI mandates.
4. **Capital Allocation Dilemma:** Chief Information Security Officers (CISOs) and Chief Financial Officers (CFOs) lack mathematical decision-support tools to prioritize security controls within finite capital budgets.
5. **Operational Accessibility:** Branch staff and tier-2/3 cooperative bank IT teams lack clear, actionable, localized guidance to remediate vulnerabilities rapidly before exploitation occurs.

### 2.2. Current State of the Art & Competitive Analysis

#### National
*Best available solutions currently used in India to address this problem:*

| Existing Solution | How it works | Strengths | Weaknesses / Gaps |
| :--- | :--- | :--- | :--- |
| **CERT-In Advisories & Manual Em-panelled Audits** | Periodic scheduled security audits using manual checklists and vulnerability scanners to assess RBI circular compliance. | Grounded in Indian regulatory requirements; high familiarity among public sector banks. | Static, point-in-time assessment; zero financial quantification in ₹; manual audit reports take weeks to compile; no automated budget optimization. |
| **Domestic Vulnerability Platforms (e.g., TAC Security ESOF, Seqrite Enterprise)** | Automated network scanning and asset inventory tracking with prioritized vulnerability scoring based on CVSS. | Local vendor support; comprehensive vulnerability discovery across Indian enterprise networks. | Scoring remains abstract (0–10 or 0–1000) rather than monetary; lacks automated mapping to exact RBI circular clauses; no built-in ROSI knapsack budget allocator. |

#### Global
*Leading global solutions in the market and under active research and development:*

| Existing Solution | How it works | Strengths | Weaknesses / Gaps |
| :--- | :--- | :--- | :--- |
| **FAIR-Based Quantification Tools (e.g., RiskLens, Axio360)** | Implements Factor Analysis of Information Risk (FAIR) utilizing Monte Carlo simulations to estimate cyber loss distributions. | Statistically sound; well-recognized among Fortune 500 boardrooms and insurers. | Prohibitive licensing cost ($50k+/year); requires complex manual parameter calibration; lacks native integration with Indian banking regulations (RBI/NPCI). |
| **Enterprise VM Suites (e.g., Tenable Lumin, Qualys VMDR, Rapid7 InsightVM)** | Continuous asset discovery, vulnerability correlation, and machine-learning-driven vulnerability prioritization. | Massive CVE databases; automated endpoint agents; robust scanning coverage. | Risk scores are proprietary index numbers rather than direct financial metrics; no Return on Security Investment (ROSI) optimization; English-only output inaccessible to rural branch administrators. |

---

## 3. The Proposed Solution

### 3.1. Solution Overview

CyberLens 2.0 is an AI-enhanced Cyber Risk Quantification and Optimization Platform designed specifically for India's digital financial rails. The platform ingests vulnerability telemetry, asset criticality, and transaction volumes to calculate an RBI-Weighted CVSS and an overall Cyber Resilience Index (CR-I: 0–100). It computes the Expected Annual Loss (EAL) in Indian Rupees (₹) for each asset, automatically tags vulnerabilities to specific RBI/SEBI/NPCI circular clauses, selects the optimal combination of security controls under fixed budgetary limits using a ROSI-driven knapsack optimizer, and delivers bilingual (Hindi/English) step-by-step remediation workflows via a quantized, on-premise LLM.

### 3.2. Core Objectives

- **Objective 1: To develop an RBI-Weighted Risk Engine** that modifies base CVSS 3.1 metrics using asset criticality, unpatched longevity penalties, active exploit availability, and regulatory circular weights within a 150ms execution window.
- **Objective 2: To implement a Monetary Risk & ROSI Optimization Module** that quantifies Expected Annual Loss (EAL in ₹) based on transaction volume, downtime costs, and fraud rates, solving the 0/1 knapsack problem to maximize risk reduction per rupee spent.
- **Objective 3: To integrate Automated Compliance Tagging & Dual-Language Remediation** by cross-referencing findings against RBI/SEBI/NPCI circular clauses and generating 3-step remediation protocols in plain Hindi and English using a 4-bit quantized on-premise LLM.
- **Objective 4: To deliver a Role-Based Dual Interface (Executive & Technical)** featuring real-time "What-If" control simulation toggles, compliance heatmaps, and one-click export of official audit-ready governance summaries.

### 3.3. Novelty and Innovation

- **Novelty 1: Regulatory-Grounded Financial Quantification (RBI-Weighted CVSS & CR-I):** Unlike generic security scoring, CyberLens applies financial-institution-specific multipliers (e.g., UPI Switch Authentication Bypass = 1.5x, CBS SQL Injection = 1.6x) and evaluates unpatched age penalties. It mathematically converts technical vulnerabilities into Expected Annual Loss (EAL in ₹), making cyber risk understandable to CFOs and Board Risk Committees.
- **Novelty 2: Algorithmic ROSI-Driven Knapsack Optimizer:** Replaces arbitrary security spending with algorithmic discipline. Given an enterprise budget (e.g., ₹1 Crore), the engine evaluates candidate security controls (WAF, MFA, EDR, Micro-segmentation) and selects the mathematically optimal package that maximizes risk reduction per rupee invested.
- **Novelty 3: Bilingual AI Remediation with Instant Regulatory Traceability:** Features an air-gapped, 4-bit quantized local LLM that translates complex CVE descriptions into plain Hindi and English action steps tailored for non-specialist branch IT staff. Every finding is linked directly to its governing regulatory clause (e.g., RBI/2023-24/105.A.3).

### 3.4. Success Metrics

- **Performance:** Dashboard response time < 2.0 seconds; risk engine calculation latency < 150ms per batch; containerized cold start < 15 seconds; server uptime > 99.9%.
- **Accuracy:** 100% deterministic regulatory clause mapping precision across the test database; strict score bounding (CVSS: 0.0–10.0, CR-I: 0.0–100.0, EAL ≥ 0); 100% budget adherence (total cost of selected controls ≤ allocated budget).
- **User Adoption:** Validation against representative multi-asset banking scenarios (UPI switches, CBS, mobile apps); 100 beta test validations conducted across system administrators and governance officers.

---

## 4. Technical Architecture & Feasibility

### 4.1. Technical Approach & System Design

CyberLens 2.0 is built on a modular four-tier architecture designed for rapid air-gapped deployment and microservice extensibility:

1. **Deployment & Operations Tier:** Containerized execution using Docker Compose, automated verification script (`validate.sh`), and SIH submission export pipeline.
2. **Indian Financial Data Tier:** SQLite database structured with relational schemas (`assets`, `vulnerabilities`, `incidents`, `rbi_mappings`), ingesting transaction metrics, unpatched timelines, and regulatory mandates.
3. **Core Risk & AI Computation Engine (`risk_engine.py`):**
   - *RBI-Weighted CVSS:* Computes adjusted score factoring base CVSS, asset criticality, regulatory multipliers, patch delays, and exploit availability.
   - *Cyber Resilience Index (CR-I):* Computes 0–100 asset and global resilience scores weighted by daily transaction volume.
   - *Expected Annual Loss (EAL):* `EAL = Probability of Incident × Loss per Incident`, where `Loss = (Downtime Hours × Hourly Cost) + (Transaction Volume × Fraud Loss Rate)`.
   - *ROSI Knapsack Optimizer:* Solves `Maximize Σ(Risk Reduction) subject to Σ(Control Cost) ≤ Budget`.
   - *Bilingual Remediation:* Few-shot prompt pipeline backed by a 4-bit quantized TinyLlama model with zero-latency deterministic template fallbacks.
4. **Presentation & Dashboard Tier:** Multi-view Streamlit interface providing an Executive Dashboard (rupee exposure, CR-I gauge, budget slider, top risks) and a Technical Dashboard (asset tree, interactive What-If control toggles, compliance heatmaps, and audit logs).

```
+-----------------------------------------------------------------------+
|                            USER INTERFACE                             |
|       Executive View (CFO / Board)      Technical View (CISO / SOC)   |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                        CORE RISK & AI ENGINE                          |
|  [RBI-Weighted CVSS]     [CR-I Aggregator]     [EAL Financial Engine] |
|  [ROSI Knapsack Optimizer]  [Quantum Risk]     [Bilingual LLM Engine] |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                              DATA TIER                                |
|  Assets Table   Vulnerabilities Table   Incidents Table   RBI Mappings|
|                     (SQLite / PostgreSQL Schema)                      |
+-----------------------------------------------------------------------+
```

**Step-by-Step Process Flow:**
1. **Telemetry Ingestion:** System loads asset details (asset type, criticality, daily transaction volume, downtime cost) and vulnerability parameters (CVSS, days unpatched, exploit status).
2. **Contextual Risk Evaluation:** The risk engine applies asset-specific RBI multipliers and patch delay penalties to determine the RBI-Weighted CVSS.
3. **Financial Quantification:** Transaction volumes and downtime figures are synthesized to calculate the Expected Annual Loss (EAL in ₹) per vulnerability and aggregate organizational exposure.
4. **Resilience Index Calculation:** The platform generates the 0–100 Cyber Resilience Index (CR-I) weighted by transaction volume.
5. **Optimization & Remediation:** The user sets a budget; the ROSI knapsack algorithm recommends the optimal control set. Concurrently, the LLM generates actionable bilingual remediation steps linked to RBI circulars.
6. **Executive & Technical Delivery:** Metrics, What-If simulation outputs, and regulatory compliance statuses are rendered across executive and technical dashboards.

### 4.2. Tech Stack

| Category | Technology / Tool |
| :--- | :--- |
| **Frontend** | Streamlit 1.38.0, Custom CSS Components, Plotly Data Visualizations |
| **Backend** | Python 3.11, FastAPI 0.115.0, Uvicorn 0.32.0, Pydantic 2.9.2 |
| **Database** | SQLite 3 (Demonstration / Branch Edge), PostgreSQL 15 (Enterprise) |
| **AI/ML Model(s)** | Quantized TinyLlama 1.1B (PyTorch 2.4.0, Hugging Face Transformers 4.44.0, BitsAndBytes 4-bit), Scikit-Learn 1.5.0 |
| **Cloud & DevOps** | Docker, Docker Compose, Bash Automation (`validate.sh`), Linux / Kubernetes Helm Ready |

### 4.3. Hardware & Data Requirements

#### Hardware Components
*Estimated Bill of Materials (BOM) for enterprise/branch deployment:*

| Hardware Component | Quantity | Estimated Unit Price (₹) |
| :--- | :--- | :--- |
| **Enterprise Server Node** (Intel Xeon / AMD EPYC 8-Core, 16GB RAM, 256GB SSD) | 1 | ₹85,000 |
| **Edge Deployment Terminal** (Quad-Core x86 / Raspberry Pi 4 4GB, 64GB High-Endurance Card) | 1 | ₹6,500 |
| **Total Cost:** | | **₹91,500** |

*(Note: Prototype and hackathon demo runs entirely on existing standard laptops or commodity cloud instances with zero additional hardware expenditure).*

#### Data Requirements

| Dataset Name | Source / URL | License Type |
| :--- | :--- | :--- |
| **National Vulnerability Database (NVD)** | NIST (https://nvd.nist.gov/) | Public Domain |
| **RBI Master Directions on IT Governance & Cybersecurity** | Reserve Bank of India (https://www.rbi.org.in/) | Open Public Regulatory Standard |
| **NPCI Security Directives & UPI Guidelines** | NPCI (https://www.npci.org.in/) | Open Public Financial Standard |
| **Synthetic Financial Infrastructure & Vulnerability Dataset** | CyberLens Project Internal Dataset (`data/*.csv`) | Open Source (AGPL-3.0) |

---

## 5. Project Plan & Team

### 5.1. Work Plan & Milestones

| Phase / Milestone | Key Tasks | Estimated Duration |
| :--- | :--- | :--- |
| **Day 1: Setup & Core Logic** | Project initialization, SQLite schema creation, data ingestion pipelines, RBI-weighted CVSS algorithm, EAL calculation logic. | 8 Hours |
| **Day 1: Frontend Basics** | Streamlit architecture setup, Executive view KPIs (Total ₹ Exposure, CR-I gauge, Top Risks), Technical asset exploration view. | 6 Hours |
| **Day 2: Integration & Testing** | ROSI knapsack budget optimizer integration, quantized bilingual LLM pipeline, What-If simulator, automated test suite (`validate.sh`). | 10 Hours |
| **Final Hours: Polish & Pitch** | UI/UX refining, edge-case validation, end-to-end demo execution, one-click SIH summary export, final pitch deck preparation. | 6 Hours |

### 5.2. Team Roles and Responsibilities

| Team Member | Role | Key Contributions & Relevant Skills |
| :--- | :--- | :--- |
| **Mr. Moses.D**<br>(URK24CS7104) | Team Leader & Backend Architect | Project management, mathematical formulation of RBI-weighted CVSS, risk aggregation engine architecture, and system integration (Python, Algorithms, Systems Architecture). |
| **Mr. John Oliver W**<br>(URK24CS7038) | Full-Stack Developer | Database schema optimization (SQLite/PostgreSQL), data loader pipelines, FastAPI REST service implementation, and API testing (Python, FastAPI, SQL). |
| **Mr. Flynn Maxwel D**<br>(URK24CS7016) | Frontend & Visualization Developer | Multi-persona dashboard development (Executive & Technical views), interactive What-If simulation widgets, KPI gauge visualization, and UI/UX polish (Streamlit, UI/UX, CSS). |
| **Ms. S J Nithika**<br>(URK24CS7010) | AI/ML Specialist | 4-bit TinyLlama LLM quantization, prompt engineering for Hindi/English bilingual remediation, and predictive ML scoring models (PyTorch, Transformers, Scikit-learn). |
| **Mr. Thilak Divyadharshan B**<br>(URK24CS7017) | Financial Modeling & Optimization Engineer | Expected Annual Loss (EAL in ₹) model formulation, ROSI-driven knapsack budget optimizer algorithm, and quantitative risk validation (Python, Discrete Optimization, Financial Modeling). |
| **Ms. Koppisetti Jyothika**<br>(URK24CS7102) | Security Analyst & QA Engineer | Regulatory circular mapping (RBI, SEBI, NPCI), security controls effectiveness library design, automated test suite execution (`validate.sh`, pytest), and audit log validation (Cybersecurity, Compliance, QA). |
| **Mrs. R. Hemalatha**<br>(Staff ID: 2862) | Faculty Mentor & Technical Advisor | Technical architecture review, regulatory compliance alignment guidance, problem scope validation, and project evaluation. |

---

## 6. Outcomes

- **Solution Type:** A deployable enterprise software platform with an open-source core (AGPL-3.0) and high commercial viability as an enterprise SaaS product for Indian banks, NBFCs, and payment gateways.
- **Societal & National Impact:** Directly enhances the security posture of India's national financial payment rails. By protecting critical banking switches, it shields over 500 million citizen account holders from payment disruptions and fraud.
- **Economic Impact:** Cyber attacks on banking infrastructure carry an average incident cost of ₹15–20 Crore in direct fraud, forensic remediation, and regulatory penalties. CyberLens enables institutions to prioritize security spending with scientific precision, achieving an estimated 30–45% increase in risk reduction per rupee spent. In rural and cooperative banking clusters, protecting ₹10 Crore in cyber exposure equates to safeguarding over 400,000 days of rural agricultural and MGNREGA wages.

---

## 7. Stretch Goal

An automated, continuous threat intelligence ingestion pipeline directly interfacing with CERT-In advisory feeds and enterprise SIEM/EDR endpoints. Furthermore, replacing static rule multipliers with an XGBoost machine learning model trained on historical Indian banking breach datasets, coupled with a Post-Quantum Cryptography (PQC) readiness evaluator assessing vulnerability to quantum decryption attacks across financial transaction logs.

---

## 8. Research References

1. **Reserve Bank of India (RBI):** *Master Direction – Information Technology Governance, Risk, Controls and Assurance Practices*, RBI/2023-24/107, Nov 2023. [rbi.org.in](https://www.rbi.org.in)
2. **National Payments Corporation of India (NPCI):** *Unified Payments Interface (UPI) Procedural and System Guidelines*, circulars and security mandates. [npci.org.in](https://www.npci.org.in)
3. **National Institute of Standards and Technology (NIST):** *Common Vulnerability Scoring System (CVSS v3.1) Specification Guide* and *Special Publication 800-30: Guide for Conducting Risk Assessments*. [csrc.nist.gov](https://csrc.nist.gov)
4. **The FAIR Institute:** *Factor Analysis of Information Risk (FAIR) Standard for Cyber Risk Quantification*. [fairinstitute.org](https://www.fairinstitute.org)
5. **Indian Computer Emergency Response Team (CERT-In):** *Guidelines on Information Security Practices and Vulnerability Remediation for Financial Entities*. [cert-in.org.in](https://www.cert-in.org.in)
