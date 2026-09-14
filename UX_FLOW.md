# User Experience Flow (UX_FLOW.md) - CyberLens 2.0

This document outlines the key user interactions and flows within the CyberLens 2.0 Streamlit dashboard. The design targets two primary user personas: **Executives** (RBI governors, Bank CFOs, Risk Officers) and **Technical Users** (CISOs, Security Engineers, Operations staff). The dashboard provides a seamless experience for both, with shared components and persona‑specific views.

## 1. Common Entry & Setup
1. **Launch**: User runs `docker compose up` (or executes `streamlit run streamlit_app.py`).
2. **Landing Page**: The app opens to the **Executive View** by default (can be toggled via sidebar).
3. **Sidebar**:
   - Logo and app title: “CyberLens 2.0 – RBI‑Aligned Cyber Risk Dashboard”.
   - Navigation radio: **Executive View** | **Technical View**.
   - Theme toggle (optional): Light/Dark.
   - “Load UPI Switch Demo Scenario” button (primary call‑to‑action for SIH demo).
   - “Generate SIH Summary” button (available in both views).
   - Version info and links to documentation.

## 2. Executive View Flow
*Goal: Provide a high‑level, ₹‑focused overview of cyber risk and actionable budget recommendations.*

### 2.1 Initial Load (No Demo Scenario)
- **Metrics Row** (at the top):
  - **Total Annual Cyber Risk Exposure**: Large font, ₹ amount (e.g., ₹4,200 Cr/year).
  - **Cyber Resilience Index (CR‑I)**: Gauge/semi‑circular progress bar (0‑100) with label (e.g., 38/100 – Low Resilience).
  - **RBI Compliance %**: Percentage of assets compliant with key RBI guidelines (e.g., 58%).
- **Top 3 Risks Cards** (below metrics):
  - Each card shows:
    - Asset name (e.g., “UPI Switch – Mumbai DC”).
    - Risk Contribution (₹/year) (e.g., ₹1,800 Cr/year).
    - Primary Vulnerability Type (e.g., “Authentication Bypass”).
    - RBI Reference (e.g., “Maps to RBI/2023-24/105.A.3”).
    - Small “View Details” link that scrolls to the Technical View (or opens a modal).
- **Budget Allocator Section**:
  - Label: “Available Budget for Security Controls (₹)”.
  - Slider ranging from ₹0 to ₹10 Crore (step ₹10 Lakh), default ₹1 Crore.
  - Button: “Show Optimal Investment Plan”.
- **Optimal Investment Plan Table** (appears after button click):
  - Columns: Control, Cost (₹), Risk Reduction (₹/year), ROSI (%).
  - Rows: Selected controls from the optimizer.
  - Footer: Total Cost, Total Risk Reduction, Remaining Budget, Overall ROSI.
- **Impact Visualization** (below table):
  - Bar chart: “Before vs. After Risk Exposure” (shows baseline and post‑optimization exposure).
  - Optional: Pie chart of risk reduction by control type.

### 2.2 With Demo Scenario Loaded
- Clicking “Load UPI Switch Demo Scenario” triggers:
  - Loads a pre‑defined set of assets/vulnerabilities representing a realistic UPI switch with high‑risk findings.
  - Executive metrics update automatically to reflect the scenario (e.g., exposure jumps to ₹4,200 Cr, CR‑I drops to 38).
  - Top 3 risks reflect the most significant UPI‑specific vulnerabilities.
  - User can then adjust the budget slider and see the optimizer respond in real time.

### 2.3 SIH Summary Generation
- At any point, clicking “Generate SIH Summary”:
  - Triggers a client‑side script that compiles:
    - Problem statement (taken from SIH theme).
    - Solution overview (highlighting RBI‑weighted CR‑I, LLM remediation, ROSI optimizer).
    - Key metrics from current dashboard state (exposure, CR‑I, top risks).
    - Technical stack diagram (markdown mermaid or bullet list).
    - Impact metrics (₹ protected, users safeguarded, MGNREGA‑day equivalence).
    - Future scope and open‑source pledge.
  - Outputs a markdown file `SIH_Submission.md` in the working directory and shows a download link.

## 3. Technical View Flow
*Goal: Provide deep asset‑level vulnerability details, remediation guidance, and what‑if simulation.*

### 3.1 Asset Explorer
- Dropdown labeled “Select Asset to Investigate” (default: “All Assets”).
- On change, the vulnerability table below updates to show only vulnerabilities for the selected asset (or all assets if “All Assets” is chosen).

### 3.2 Vulnerability Table
- Columns:
  - Vuln ID
  - CVE ID
  - CVSS (base score)
  - RBI‑Weighted Score (0‑10)
  - CR‑I Impact (derived)
  - Days Unpatched
  - Exploit Available? (Yes/No)
  - Risk Contribution (₹/year)
  - Actions (buttons: “Show Details”, “Simulate Fix”)
- Table is searchable and sortable via Streamlit’s built‑in features.
- Row highlighting: rows with Risk Contribution > threshold (e.g., top 10%) get a subtle background.

### 3.3 Show Details Modal (expander or custom modal)
When user clicks “Show Details” on a row:
- Expands a section below the row (or opens a modal) with:
  - **Technical Description**: CVE description, affected component.
  - **RBI/SEBI/NPCI Mapping** (expandable):
    - Lists exact circular/clause references (e.g., RBI/2023-24/105.A.3, SEBI/HO/ISD/ISD/CIR/P/2020/168).
    - Short explanation of what each guideline requires.
  - **LLM‑Generated Remediation Steps**:
    - Heading: “Suggested Remediation (Hindi/English)”.
    - Numbered list of 3 concise steps (e.g., “Admin पैनल पर SMS‑OTP अनिवार्य करें।”).
    - Note: “Generated by TinyLlama‑1.1B‑Chat (4‑bit quantized)”.
  - **What‑If Simulator**:
    - Heading: “Simulate Security Controls”.
    - List of relevant controls (from controls library) with toggle switches.
    - Each toggle shows control name, cost, and effectiveness.
    - As toggles are changed, the “Risk Contribution (₹/year)” field updates in real time (re‑calculates EAL assuming control effectiveness).
    - Below, a small summary shows: “New Risk Contribution: ₹XXX Cr/year (ΔYYY%)”.
    - Optional: “Updated CR‑I for this asset: ZZ/100”.
  - **Transaction Flow Impact** (small diagram):
    - SVG/PNG showing the UPI transaction flow (Collect → Switch → Settle) with a red overlay on the affected component (e.g., “UPI API Gateway”).
    - Tooltip: “A breach here could disrupt the entire switch, impacting millions of transactions.”

### 3.4 Simulate Fix (Alternative Action)
- Clicking “Simulate Fix” on a row could open a focused view that:
  - Pre‑selects the most effective control for that vulnerability (based on ROSI).
  - Shows the before/after risk contribution and CR‑I change.
  - Provides a “Apply this control to budget optimizer” button that adds the control’s cost to the budget allocator (switches to Executive View with updated budget).

### 3.5 Compliance Heatmap (bottom of Technical View)
- Title: “RBI Guideline Compliance Heatmap”.
- Rows: Key RBI guidelines (e.g., “Authentication Security”, “Patch Management (<7 days)”, “Data Encryption at Rest”, “Network Segmentation”).
- Columns: Assets (or asset types) – for demo, shows a few representative assets.
- Cell color: Green (≥90% compliant), Yellow (60‑89%), Red (<60%).
- Hover shows exact % and asset‑guideline detail.
- Helps technical users spot weak areas across the estate.

## 4. Cross‑View Interactions
- **From Executive to Technical**: Clicking a “View Details” link on a Top 3 Risks card switches the sidebar to Technical View and auto‑selects the associated asset in the explorer.
- **From Technical to Executive**: After simulating controls in the detail modal, user can click “Use This Plan in Budget Optimizer” → switches to Executive View, sets budget slider to include the control cost, and triggers the optimizer.
- **SIH Summary**: Available in both views; uses current state (whether demo loaded or not) to generate the submission.

## 5. Edge Cases & Error Handling
- **No Data**: If data fails to load, show an error banner with instructions to check the `data/` directory.
- **LLM Unavailable**: If the LLM model fails to load, fall back to a rule‑based remediation template and show an info banner: “LLM remediation unavailable; using template‑based guidance.”
- **Invalid Budget**: Slider prevents negative values; if user types an invalid number, clamp to min/max.
- **Empty Optimizer Result**: If budget is too low to select any control, show a message: “No controls fit within the selected budget. Consider increasing the budget.”

## 6. Accessibility & Localization (Future)
- All text strings are externalized for easy i18n (Hindi/English toggle planned).
- Ensure sufficient color contrast for gauges and heatmap.
- Support keyboard navigation (Tab to move between controls, Enter to activate).

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*