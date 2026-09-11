#set page(
  paper: "us-letter",
  margin: (top: 2.7cm, bottom: 2.0cm, left: 2.3cm, right: 2.3cm),
  header: [
    #grid(
      columns: (1fr, 1fr),
      align(left + horizon)[#image("template_assets/karunya_logo.png", height: 26pt)],
      align(right + horizon)[#image("template_assets/sih_logo.png", height: 32pt)]
    )
    #v(4pt)
  ],
  footer: [
    #v(4pt)
    #grid(
      columns: (1fr, 1fr),
      align(left)[#text(size: 9pt, style: "italic", fill: rgb(110, 110, 110))[Version 2.0]],
      align(right)[#text(size: 9pt, style: "italic", fill: rgb(110, 110, 110))[#context counter(page).display()]]
    )
  ]
)

#set text(font: ("Liberation Serif", "Times New Roman"), size: 10pt, lang: "en")
#set par(justify: true, leading: 0.6em)
#show heading: set text(fill: rgb(20, 20, 20), weight: "bold")
#show heading.where(level: 1): it => block(above: 14pt, below: 8pt)[#text(size: 11.5pt)[#it.body]]
#show heading.where(level: 2): it => block(above: 11pt, below: 6pt)[#text(size: 10.5pt)[#it.body]]

// ==========================================
// PAGE 1
// ==========================================

#align(center)[
  #text(size: 13pt, weight: "bold")[Smart India Hackathon 2026 Idea Proposal]
]
#v(6pt)

#table(
  columns: (38%, 62%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 7pt, y: 5.5pt),
  [ *Problem Statement ID:* ], [ SIH2026-FIN-042 ],
  [ *Problem Statement Title:* ], [ AI-Enhanced Cyber Risk Quantification & Automated Remediation Platform for India's Digital Financial Infrastructure ],
  [ *Team ID:* ], [ K26032 ],
  [ *Team Name:* ], [ Develupers ],
  [ *Mentor:* ], [ Mrs. R. Hemalatha (Staff ID: 2862) ]
)

#v(8pt)

= 1. Executive Summary

India's digital payment ecosystem processes over 350 million daily UPI transactions valued at ₹3.5 lakh crore, yet cybersecurity teams still rely on qualitative risk matrices (Low/Medium/High) that cannot justify security spending to boardrooms or regulators. CyberLens 2.0 is an AI-driven Cyber Risk Quantification platform purpose-built for Indian financial infrastructure. It converts technical vulnerabilities into rupee-denominated Expected Annual Loss (EAL) and a regulatory-grounded Cyber Resilience Index (CR-I: 0–100) benchmarked against RBI, SEBI, and NPCI directives. Utilizing an algorithmic Return on Security Investment (ROSI) knapsack optimizer and dual-language (Hindi/English) generative remediation, CyberLens enables CISOs and bank executives to maximize risk reduction per rupee allocated. Serving public-sector banks, payment aggregators, and cooperative lenders, CyberLens bridges technical telemetry with financial governance, protecting critical transaction rails and national economic sovereignty.

#v(8pt)

= 2. The Problem & Existing Landscape

== 2.1. Problem Definition

India has established global leadership in digital public infrastructure, processing over 10 billion monthly transactions across the Unified Payments Interface (UPI). However, the underlying financial infrastructure—spanning Core Banking Systems (CBS), payment switches, API gateways, and regional cooperative bank networks—faces increasingly frequent and sophisticated cyber threats.

A severe systemic gap exists: current cybersecurity assessment tools evaluate risks through static Common Vulnerability Scoring System (CVSS) numbers or subjective qualitative ratings (Low, Medium, High). These metrics fail to reflect:
+ *Financial Exposure:* Traditional tools cannot translate a CVE into projected downtime costs, fraud losses, or balance sheet risk in Indian Rupees (₹).
+ *Transaction Velocity & Criticality:* A vulnerability on a high-throughput UPI switch processing ₹5,000 crore daily poses exponentially greater systemic danger than the same CVE on an internal staging server.
+ *Domestic Regulatory Alignment:* Global tools do not map vulnerabilities to Reserve Bank of India (RBI) Master Directions, SEBI cyber frameworks, or NPCI mandates.
+ *Capital Allocation Dilemma:* Chief Information Security Officers (CISOs) and Chief Financial Officers (CFOs) lack mathematical decision-support tools to prioritize security controls within finite capital budgets.
+ *Operational Accessibility:* Branch staff and tier-2/3 cooperative bank IT teams lack clear, actionable, localized guidance to remediate vulnerabilities rapidly before exploitation occurs.

#pagebreak()

// ==========================================
// PAGE 2
// ==========================================

== 2.2. Current State of the Art & Competitive Analysis

#v(2pt)
*National:* _Briefly discuss the best available solutions currently used in India to address the problem you are tackling._
#v(4pt)

#table(
  columns: (22%, 28%, 25%, 25%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 5pt, y: 5pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Existing Solution* ], [ *How it works* ], [ *Strengths* ], [ *Weaknesses/Gaps* ],
  
  [ *CERT-In Advisories & Manual Empanelled Audits* ],
  [ Periodic scheduled audits using manual checklists and vulnerability scanners to verify RBI compliance. ],
  [ High familiarity in public-sector banks; direct alignment with Indian statutory guidelines. ],
  [ Static, point-in-time assessment; zero monetary quantification (in ₹); audits take weeks to compile. ],
  
  [ *Domestic Platforms (e.g., TAC Security ESOF, Seqrite Enterprise)* ],
  [ Network vulnerability scanning and asset inventory tracking with prioritized CVSS-based scoring. ],
  [ Local enterprise support; good asset discovery and threat signatures for Indian IT setups. ],
  [ Abstract risk scores (0–1000) rather than monetary loss; lacks automated mapping to exact RBI clauses; no ROSI budget optimization. ]
)

#v(10pt)
*Global:* _Describe the leading global solutions for this problem, including existing technologies in the market and those under active research and development._
#v(4pt)

#table(
  columns: (22%, 28%, 25%, 25%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 5pt, y: 5pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Existing Solution* ], [ *How it works* ], [ *Strengths* ], [ *Weaknesses/Gaps* ],
  
  [ *FAIR-Based Quantitative Tools (e.g., RiskLens, Axio360)* ],
  [ Factor Analysis of Information Risk (FAIR) Monte Carlo simulations estimating cyber loss distributions. ],
  [ Statistically rigorous; widely recognized by Fortune 500 boardrooms and cyber insurers. ],
  [ Prohibitive licensing cost (\$50k+/yr); complex manual calibration; lacks native integration with RBI/NPCI frameworks. ],
  
  [ *Enterprise VM Suites (e.g., Tenable Lumin, Qualys VMDR, Rapid7)* ],
  [ Automated agent scanning, vulnerability correlation, and machine-learning risk scoring. ],
  [ Massive CVE vulnerability feeds; automated continuous scanning across thousands of endpoints. ],
  [ Abstract proprietary severity scores; no direct financial quantification in INR; no budget knapsack optimization; English-only workflows. ]
)

#pagebreak()

// ==========================================
// PAGE 3
// ==========================================

= 3. The Proposed Solution

== 3.1. Solution Overview

CyberLens 2.0 is an AI-enhanced Cyber Risk Quantification and Optimization Platform designed specifically for India's digital financial rails. The platform ingests vulnerability telemetry, asset criticality, and transaction volumes to calculate an RBI-Weighted CVSS and an overall Cyber Resilience Index (CR-I: 0–100). It computes the Expected Annual Loss (EAL) in Indian Rupees (₹) for each asset, automatically tags vulnerabilities to specific RBI/SEBI/NPCI circular clauses, selects the optimal combination of security controls under fixed budgetary limits using a ROSI-driven knapsack optimizer, and delivers bilingual (Hindi/English) step-by-step remediation workflows via a quantized, on-premise LLM.

#v(4pt)

== 3.2. Core Objectives

- *Objective 1: To develop an RBI-Weighted Risk Engine* that modifies base CVSS 3.1 metrics using asset criticality, unpatched longevity penalties, active exploit availability, and regulatory circular weights within a 150ms execution window.
- *Objective 2: To implement a Monetary Risk & ROSI Optimization Module* that quantifies Expected Annual Loss (EAL in ₹) based on transaction volume, downtime costs, and fraud rates, solving the 0/1 knapsack problem to maximize risk reduction per rupee spent.
- *Objective 3: To integrate Automated Compliance Tagging & Dual-Language Remediation* by cross-referencing findings against RBI/SEBI/NPCI circular clauses and generating 3-step remediation protocols in plain Hindi and English using a 4-bit quantized on-premise LLM.
- *Objective 4: To deliver a Role-Based Dual Interface (Executive & Technical)* featuring real-time "What-If" control simulation toggles, compliance heatmaps, and one-click export of official audit-ready governance summaries.

#v(4pt)

== 3.3. Novelty and Innovation

- *Novelty 1: Regulatory-Grounded Financial Quantification (RBI-Weighted CVSS & CR-I):* Unlike generic security scoring, CyberLens applies financial-institution-specific multipliers (e.g., UPI Switch Authentication Bypass = 1.5x, CBS SQL Injection = 1.6x) and evaluates unpatched age penalties. It mathematically converts technical vulnerabilities into Expected Annual Loss (EAL in ₹), making cyber risk understandable to CFOs and Board Risk Committees.

- *Novelty 2: Algorithmic ROSI-Driven Knapsack Optimizer:* Replaces arbitrary security spending with algorithmic discipline. Given an enterprise budget (e.g., ₹1 Crore), the engine evaluates candidate security controls (WAF, MFA, EDR, Micro-segmentation) and selects the mathematically optimal package that maximizes risk reduction per rupee invested.

#pagebreak()

// ==========================================
// PAGE 4
// ==========================================

- *Novelty 3: Bilingual AI Remediation with Instant Regulatory Traceability:* Features an air-gapped, 4-bit quantized local LLM that translates complex CVE descriptions into plain Hindi and English action steps tailored for non-specialist branch IT staff. Every finding is linked directly to its governing regulatory clause (e.g., RBI/2023-24/105.A.3).

#v(6pt)

== 3.4. Success Metrics

- *Performance:* Dashboard response time < 2.0 seconds; risk engine calculation latency < 150ms per batch; containerized cold start < 15 seconds; server uptime > 99.9%.
- *Accuracy:* 100% deterministic regulatory clause mapping precision across the test database; strict score bounding (CVSS: 0.0–10.0, CR-I: 0.0–100.0, EAL ≥ 0); 100% budget adherence (total cost of selected controls ≤ allocated budget).
- *User Adoption:* Validation against representative multi-asset banking scenarios (UPI switches, CBS, mobile apps); 100 beta test validations conducted across system administrators and governance officers.

#v(8pt)

= 4. Technical Architecture & Feasibility

== 4.1. Technical Approach & System Design

CyberLens 2.0 is built on a modular four-tier architecture designed for rapid air-gapped deployment and microservice extensibility:
+ *Deployment & Operations Tier:* Containerized execution using Docker Compose, automated verification script (`validate.sh`), and SIH submission export pipeline.
+ *Indian Financial Data Tier:* Relational SQLite schema storing assets, vulnerabilities, incidents, and RBI circular mappings.
+ *Core Risk & AI Computation Engine (`risk_engine.py`):* Executes RBI-weighted CVSS scoring, CR-I calculation, Expected Annual Loss (EAL in ₹), greedy/integer ROSI knapsack budget optimizer, and bilingual few-shot LLM remediation.
+ *Presentation & Dashboard Tier:* Streamlit multi-view interface providing an Executive Dashboard (rupee risk exposure, CR-I gauge, budget allocator) and Technical Dashboard (asset tree, What-If simulator, compliance heatmap).

#v(4pt)
#align(center)[
#rect(stroke: 0.5pt + rgb(160, 160, 160), inset: 6pt, radius: 2pt, fill: rgb(250, 250, 250))[
#text(size: 8.5pt, font: ("DejaVu Sans Mono", "Courier New"))[
┌────────────────────────────────────────────────────────────────────────┐\
│                  LAYER 3: USER DASHBOARD (Streamlit)                   │\
│     Executive View (CFO / Board)   │   Technical View (CISO / SOC)     │\
└───────────────────────────────────┬────────────────────────────────────┘\
                                    ▼\
┌────────────────────────────────────────────────────────────────────────┐\
│                   LAYER 2: CORE RISK & AI ENGINE                       │\
│   RBI-Weighted CVSS  │  CR-I Aggregator  │  EAL Financial Engine (₹)   │\
│   ROSI Knapsack Optimizer │ Quantum Risk │ Bilingual LLM Remediation   │\
└───────────────────────────────────┬────────────────────────────────────┘\
                                    ▼\
┌────────────────────────────────────────────────────────────────────────┐\
│              LAYER 1: INDIAN FINANCIAL DATA LAYER (SQLite)             │\
│     assets.csv   │   vulnerabilities.csv   │   rbi_mappings.csv        │\
└────────────────────────────────────────────────────────────────────────┘
]
]
]

#v(4pt)
*Step-by-Step Process Flow:*
1. _Telemetry Ingestion:_ Asset parameters (criticality, daily transaction volume, hourly downtime cost) and vulnerability parameters (CVSS, days unpatched, exploit status) are loaded.
2. _Contextual Risk Scoring:_ The engine calculates RBI-Weighted CVSS incorporating asset multipliers and patch latency penalties.
3. _Financial Quantification & Resilience Index:_ Calculates Expected Annual Loss (EAL = P × Loss) in ₹ and aggregates the 0–100 Cyber Resilience Index (CR-I).
4. _Optimization & AI Guidance:_ Generates an optimal control allocation under budget and produces 3-step bilingual remediation instructions mapped to RBI circulars.

#pagebreak()

// ==========================================
// PAGE 5
// ==========================================

== 4.2. Tech Stack

#table(
  columns: (30%, 70%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 8pt, y: 7pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Category* ], [ *Technology / Tool* ],
  [ *Frontend* ], [ Streamlit 1.38.0, Custom CSS Components, Plotly Data Visualizations ],
  [ *Backend* ], [ Python 3.11, FastAPI 0.115.0, Uvicorn 0.32.0, Pydantic 2.9.2 ],
  [ *Database* ], [ SQLite 3 (Demonstration / Branch Edge), PostgreSQL 15 (Enterprise) ],
  [ *AI/ML Model(s)* ], [ Quantized TinyLlama 1.1B (PyTorch 2.4.0, Hugging Face Transformers 4.44.0, BitsAndBytes 4-bit), Scikit-Learn 1.5.0 ],
  [ *Cloud Services & DevOps* ], [ Docker, Docker Compose, Bash Automation (`validate.sh`), Linux / Kubernetes Helm Ready ]
)

#v(14pt)

== 4.3. Hardware & Data Requirements

_List any specific hardware components required, including a cost estimate (Bill of Materials). Also, describe the datasets you will use, their source, and your data collection strategy if applicable._

#v(4pt)
#table(
  columns: (45%, 20%, 35%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 8pt, y: 7pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Hardware Component* ], [ *Quantity* ], [ *Estimated Unit Price (₹)* ],
  [ *Enterprise Server Node* \ (Intel Xeon / AMD EPYC 8-Core, 16GB RAM, 256GB SSD) ], [ 1 ], [ ₹85,000 ],
  [ *Edge Deployment Terminal* \ (Quad-Core x86 / Raspberry Pi 4 4GB, 64GB High-Endurance Card) ], [ 1 ], [ ₹6,500 ],
  [ *Branch Security Gateway Appliance* \ (Dual NIC Embedded Gateway, 8GB RAM, Hardware Keystore) ], [ 1 ], [ ₹22,000 ],
  [ *Offline HSM Crypto Acceleration Card (Optional)* \ (PCIe Cryptographic Module for Key Zeroization) ], [ 1 ], [ ₹35,000 ]
)

#pagebreak()

// ==========================================
// PAGE 6
// ==========================================

#table(
  columns: (45%, 20%, 35%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 8pt, y: 7pt),
  [ *Backup & Failover Storage Unit* \ (1TB Encrypted NVMe External Array) ], [ 1 ], [ ₹11,500 ],
  [ *Network Tap & Diagnostic Bridge* \ (Passive Gigabit LAN Monitoring Interface) ], [ 1 ], [ ₹8,000 ],
  [ *Total Cost:* ], [ ], [ *₹1,68,000* ]
)

#v(4pt)
#text(size: 8.5pt, style: "italic", fill: rgb(90, 90, 90))[
  \*Note: Prototype and hackathon demonstration runs entirely on standard laptops or commodity cloud instances at ₹0 additional hardware expenditure. The BOM above represents a production branch/enterprise on-premise installation.
]

#v(14pt)
*Data Requirements:*
#v(4pt)

#table(
  columns: (35%, 45%, 20%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 8pt, y: 7pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Dataset Name* ], [ *Source/URL* ], [ *License Type* ],
  [ *National Vulnerability Database (NVD)* ], [ NIST (https://nvd.nist.gov/) ], [ Public Domain ],
  [ *RBI Master Directions on IT Governance & Cyber Security* ], [ Reserve Bank of India (https://www.rbi.org.in/) ], [ Open Public Regulatory Standard ],
  [ *NPCI Security Directives & UPI Guidelines* ], [ NPCI (https://www.npci.org.in/) ], [ Open Public Financial Standard ],
  [ *Synthetic Financial Infrastructure & Vulnerability Dataset* ], [ CyberLens Project Internal Dataset (`data/*.csv`) ], [ Open Source (AGPL-3.0) ],
  [ *CERT-In Cyber Threat Advisories & Vulnerability Notes* ], [ Indian Computer Emergency Response Team (https://www.cert-in.org.in/) ], [ Public Government Advisory ]
)

#pagebreak()

// ==========================================
// PAGE 7
// ==========================================

= 5. Project Plan & Team

== 5.1. Work Plan & Milestones

#table(
  columns: (28%, 54%, 18%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 8pt, y: 7pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Phase / Milestone* ], [ *Key Tasks* ], [ *Estimated Duration* ],
  [ *Day 1: Setup & Core Logic* ], [ Environment setup, SQLite schema design, data ingestion loader, RBI-weighted CVSS algorithm, EAL loss calculation logic. ], [ 8 Hours ],
  [ *Day 1: Frontend Basics* ], [ Streamlit dashboard layout, Executive view KPI metric cards, gauge visualization, basic asset exploration view. ], [ 6 Hours ],
  [ *Day 2: Integration & Testing* ], [ ROSI knapsack budget optimizer integration, quantized bilingual LLM pipeline, What-If simulator, automated test suite (`validate.sh`). ], [ 10 Hours ],
  [ *Final Hours: Polish & Pitch* ], [ UI/UX polish, edge-case validation, end-to-end demo execution, one-click SIH summary export, final pitch preparation. ], [ 6 Hours ]
)

#v(14pt)

== 5.2. Team Roles and Responsibilities

#table(
  columns: (28%, 27%, 45%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 7pt, y: 6pt),
  fill: (_, row) => if row == 0 { rgb(242, 242, 242) } else { none },
  [ *Team Member* ], [ *Role* ], [ *Key Contributions & Relevant Skills* ],
  
  [ *Mr. Moses.D* \ (URK24CS7104) ],
  [ Team Leader & Backend Architect ],
  [ Project management, mathematical formulation of RBI-weighted CVSS, risk aggregation engine architecture, and system integration (Python, Algorithms, Systems Architecture). ],
  
  [ *Mr. John Oliver W* \ (URK24CS7038) ],
  [ Full-Stack Developer ],
  [ Database schema optimization (SQLite/PostgreSQL), data loader pipelines, FastAPI REST service implementation, and API testing (Python, FastAPI, SQL). ],
  
  [ *Mr. Flynn Maxwel D* \ (URK24CS7016) ],
  [ Frontend & Visualization Developer ],
  [ Multi-persona dashboard development (Executive & Technical views), interactive What-If simulation widgets, KPI gauge visualization, and UI/UX polish (Streamlit, UI/UX, CSS). ]
)

#pagebreak()

// ==========================================
// PAGE 8
// ==========================================

#table(
  columns: (28%, 27%, 45%),
  stroke: 0.5pt + rgb(160, 160, 160),
  inset: (x: 7pt, y: 6pt),
  [ *Ms. S J Nithika* \ (URK24CS7010) ],
  [ AI/ML Specialist ],
  [ 4-bit TinyLlama LLM quantization, prompt engineering for Hindi/English bilingual remediation, and predictive ML scoring models (PyTorch, Transformers, Scikit-learn). ],
  
  [ *Mr. Thilak Divyadharshan B* \ (URK24CS7017) ],
  [ Financial Modeling & Optimization Engineer ],
  [ Expected Annual Loss (EAL in ₹) model formulation, ROSI-driven knapsack budget optimizer algorithm, and quantitative risk validation (Python, Discrete Optimization, Financial Modeling). ],
  
  [ *Ms. Koppisetti Jyothika* \ (URK24CS7102) ],
  [ Security Analyst & QA Engineer ],
  [ Regulatory circular mapping (RBI, SEBI, NPCI), security controls effectiveness library design, automated test suite execution (`validate.sh`, pytest), and audit log validation (Cybersecurity, Compliance, QA). ],
  
  [ *Mrs. R. Hemalatha* \ (Staff ID: 2862) ],
  [ Faculty Mentor & Technical Advisor ],
  [ Technical architecture review, regulatory compliance alignment guidance, problem scope validation, and project evaluation. ]
)

#v(10pt)

*Outcomes:* CyberLens 2.0 delivers a deployable enterprise software platform with an open-source core (AGPL-3.0) and high commercial viability as an enterprise SaaS product for Indian banks, NBFCs, and payment gateways. It directly enhances the security posture of India's national financial payment rails, shielding over 500 million citizen account holders from payment disruptions and fraud. A single banking switch outage costs ₹15–20 Crore in downtime and fraud; CyberLens optimizes security capital expenditures by 30–45% using algorithmic ROSI knapsack allocation. In rural clusters, protecting ₹10 Crore in exposure safeguards over 400,000 days of rural agricultural and MGNREGA wages.

#v(8pt)

*Stretch Goal:* An automated, continuous threat intelligence ingestion pipeline directly interfacing with CERT-In advisory feeds and enterprise SIEM/EDR endpoints. Furthermore, replacing static rule multipliers with an XGBoost machine learning model trained on historical Indian banking breach datasets, coupled with a Post-Quantum Cryptography (PQC) readiness evaluator assessing vulnerability to quantum decryption attacks across financial transaction logs.

#v(8pt)

*Research References:*
1. _Reserve Bank of India (RBI):_ Master Direction – Information Technology Governance, Risk, Controls and Assurance Practices, RBI/2023-24/107, Nov 2023. [rbi.org.in](https://www.rbi.org.in)
2. _National Payments Corporation of India (NPCI):_ Unified Payments Interface (UPI) Procedural and System Guidelines, security circulars. [npci.org.in](https://www.npci.org.in)
3. _National Institute of Standards and Technology (NIST):_ Common Vulnerability Scoring System (CVSS v3.1) Specification Guide and SP 800-30. [csrc.nist.gov](https://csrc.nist.gov)
4. _The FAIR Institute:_ Factor Analysis of Information Risk (FAIR) Standard for Cyber Risk Quantification. [fairinstitute.org](https://www.fairinstitute.org)
5. _Indian Computer Emergency Response Team (CERT-In):_ Guidelines on Information Security Practices and Vulnerability Remediation for Financial Entities. [cert-in.org.in](https://www.cert-in.org.in)
