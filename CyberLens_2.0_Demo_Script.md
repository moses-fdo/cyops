# CyberLens 2.0 — Phase 2 Demo Video Script
**Project:** RBI-Aligned AI Cyber Risk Quantification Platform (SIH)
**Target length:** ~5-6 minutes
**Format:** Screen recording + voiceover (record_demo.py can help capture the screen segments)

---

## 0. On-Screen Title Card (0:00–0:10)
*Visual: Project logo/title slide, then cut to your face or voiceover-only intro.*

**VO:**
"Hi, I'm [Your Name], and this is CyberLens 2.0 — an AI-powered Cyber Risk Quantification Platform built for India's digital financial infrastructure: UPI, banking, and payment systems."

---

## 1. The Problem (0:10–0:45)
*Visual: Slide with the problem statement, or a simple diagram showing "Low / Medium / High" labels crossed out.*

**VO:**
"Today, most cybersecurity tools give banks and fintechs a qualitative score — Low, Medium, or High risk. But regulators like the RBI, SEBI, and NPCI don't budget in 'Medium.' They need numbers — rupees. How much money is actually at risk, and where should the next crore of security spend go?

That's the gap CyberLens 2.0 closes."

---

## 2. The Novelty / Approach (0:45–1:45)
*Visual: Architecture diagram or bullet list animating in.*

**VO:**
"Our approach has four pillars:

**First**, an RBI-Weighted Cyber Resilience Index — we call it the CR-I. It's a 0-to-100 score that doesn't just use raw CVSS severity — it blends in asset criticality, RBI/SEBI/NPCI compliance weighting, patch timeliness, exploit availability, and live threat intelligence.

**Second**, we convert every vulnerability into an Expected Annual Loss — in actual rupees — using transaction volume, downtime cost, and fraud-loss modeling. So instead of 'this is high risk,' we say 'this vulnerability is expected to cost ₹4,200 crore a year if unaddressed.'

**Third**, every finding is auto-mapped to the exact RBI, SEBI, or NPCI circular and clause it violates — so compliance teams don't have to hunt for the regulation manually.

**Fourth**, we don't just report risk — we optimize spend. Our ROSI-driven budget optimizer treats security investment like a knapsack problem: given a fixed budget, say one crore rupees, it picks the exact combination of controls that maximizes risk reduction per rupee spent."

---

## 3. Architecture Overview (1:45–2:30)
*Visual: Pull up ARCH.md diagram, or show project folder structure briefly.*

**VO:**
"Architecturally, CyberLens is built in clean, swappable layers.

Data flows in from CSVs today — assets, vulnerabilities, incidents, and RBI mappings — through a data loader into a SQLite database. On top of that sits the risk engine: the core Python module that computes RBI-weighted CVSS, the CR-I, Expected Annual Loss, and runs the budget optimizer. A separate controls library defines each security control and its effectiveness.

For remediation guidance, we integrate a quantized TinyLlama model that generates simple Hindi and English remediation steps for branch-level staff — and if the model isn't available, it gracefully falls back to rule-based templates, so the demo never breaks.

All of this is surfaced through a Streamlit dashboard, and optionally through a FastAPI backend with full Swagger docs — so the risk engine can be consumed as a microservice by other systems.

The whole thing is containerized — one `docker compose up` and judges get a fully working demo with zero setup, preloaded with realistic UPI-switch sample data."

---

## 4. Live Demo — Executive View (2:30–3:45)
*Visual: Screen recording of the actual Streamlit app.*

**VO:**
"Let's see it in action. This is the Executive View — built for CISOs and bank leadership.

I'll click 'Load UPI Switch Demo Scenario' in the sidebar to bring in a realistic high-risk asset set.

[pause for load]

Immediately we see the Total Annual Cyber Risk Exposure — in rupees — the Cyber Resilience Index gauge, and the Top 3 Risks specific to UPI infrastructure.

Now here's the optimizer in action. I'll set a budget using the slider — let's say one crore rupees — and click 'Show Optimal Investment Plan.'

[pause for result]

The system returns exactly which controls to buy, their cost, the resulting risk reduction, and the ROSI — Return on Security Investment — for each. This turns a vague security conversation into a board-ready budget decision."

---

## 5. Live Demo — Technical View (3:45–4:45)
*Visual: Switch to Technical View in the app.*

**VO:**
"Switching to the Technical View, built for security analysts.

Here's the full asset explorer and vulnerability table. Clicking into any vulnerability opens a detail modal with the technical description, the exact RBI or NPCI clause it maps to, and AI-generated remediation steps in plain Hindi and English for branch staff.

There's also a What-If Simulator right here — I can toggle a security control on or off and watch the CR-I and Expected Annual Loss update in real time, so teams can see the financial impact of a fix before they commit budget to it.

We also include a compliance heatmap and a transaction-flow diagram, so analysts can trace exactly where in the UPI transaction path a vulnerability sits."

---

## 6. SIH-Specific Feature (4:45–5:10)
*Visual: Click "Generate SIH Summary" button.*

**VO:**
"One more feature built specifically for this hackathon — a one-click 'Generate SIH Summary' button. It produces a submission-ready markdown file with the problem statement, our solution overview, impact metrics in rupees protected and users safeguarded, and our technical stack — ready to upload directly to the SIH portal."

---

## 7. Closing — Future Scope (5:10–5:45)
*Visual: Return to slide/title, maybe a roadmap graphic.*

**VO:**
"Looking ahead, CyberLens is designed to scale: swapping in real-time CERT-In and SIEM feeds, replacing our rule-based scoring with a trained XGBoost model, exact integer optimization via PuLP, Kubernetes-native deployment, and even a lightweight build for resource-constrained rural bank branches.

CyberLens 2.0 turns cybersecurity from a compliance checkbox into a financial decision-making tool — quantified in the currency regulators and boards actually understand: rupees.

Thank you."

---

## Recording Notes
- Keep each screen action on-screen for 2-3 seconds before narrating over it — don't talk and click simultaneously.
- If using `record_demo.py`, do a dry run first to confirm the "Load UPI Switch Demo Scenario" and optimizer flow render correctly before the real take.
- Consider subtitles/captions given the Hindi/English remediation feature — it's a strong visual beat, don't rush past it.
- Total word count above is roughly 750 words, which paces to about 5-6 minutes at natural speaking speed — trim the Architecture section first if you need to cut time.
