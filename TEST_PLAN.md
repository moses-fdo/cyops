# Test Plan (TEST_PLAN.md) - CyberLens 2.0

This document outlines the testing strategy for CyberLens 2.0 to ensure correctness, reliability, and readiness for SIH demonstration and evaluation. It covers unit tests, integration tests, end‑to‑end (demo) tests, and validation checks.

## 1. Testing Goals
- Verify that all core calculations (RBI‑weighted CVSS, CR‑I, EAL) produce correct and expected outputs.
- Ensure that data loading and mapping functions work with the provided sample data.
- Confirm that the Streamlit dashboard renders correctly and responds to user interactions.
- Validate that the budget optimizer returns feasible solutions under given constraints.
- Check that the LLM remediation function returns intelligible Hindi/English steps (or falls back gracefully).
- Provide a simple validation script (`validate.sh`) that SIH judges can run to gain confidence in the demo.

## 2. Test Levels

### 2.1 Unit Tests
**Location**: `tests/unit/`
**Framework**: `pytest`
**Target**: Individual functions in `risk_engine.py`, `data_loader.py`, and helper modules.

#### Key Units to Test
| Module | Function | Test Cases |
|--------|----------|------------|
| risk_engine | `rbi_weighted_cvss(vuln, asset)` | - Base CVSS 5.0, asset criticality 5 → expected 2.5 (no other modifiers).<br>- Asset criticality 10, base CVSS 10 → 10 (before multipliers).<br>- RBI multiplier 2.0 → double.<br>- Days unpatched 14 → patch penalty 2.0 → factor (1+2/10)=1.2.<br>- Exploit available → boost 1.5.<br>- Combined: ensure result clamped at 10.0.<br>- Edge: days_unpatched=0 → penalty 0.<br>- Edge: exploit_available=False → boost 1.0. |
| risk_engine | `compute_cr_i(assets, vulnerabilities)` | - Single asset, single vuln with known scores → compute CR‑I manually and assert.<br>- Multiple assets, weighted by criticality * txn volume.<br>- Ensure result in [0,100].<br>- If all assets have CR‑I 100 (no risk) → CR‑I = 100. |
| risk_engine | `expected_annual_loss(vuln, asset)` | - Verify formula with mock numbers.<br>- Check that probability capped at 0.9.<br>- Ensure loss per incident uses downtime cost and fraud loss rate (configurable). |
| risk_engine | `llm_remediate(vuln, asset)` (if model loads) | - Ensure output is a list of strings, length 3.<br>- Each string contains Hindi/English words.<br>- If model fails, ensure fallback returns a list of strings (template‑based). |
| risk_engine | `optimize_budget(controls, budget)` (greedy) | - Given controls with known cost and risk reduction, ROSI sorting works.<br>- Budget exactly fits one control → select it.<br>- Budget too low for any → return empty list.<br>- Ensure total cost ≤ budget.<br>- Ensure risk reduction is sum of selected controls’ reductions. |
| data_loader | `load_assets()` | - Returns list of Asset dataclasses/dicts with expected fields.<br>- Check that asset_id is unique. |
| data_loader | `get_rbi_mapping(category, asset_type)` | - Returns correct clause from sample data.<br>- Returns None if not found. |

#### Test Data
- Use small fixtures defined in `tests/unit/fixtures.py` or inline in test files.
- For risk engine tests, create minimal vuln and asset dicts.

### 2.2 Integration Tests
**Location**: `tests/integration/`
**Framework**: `pytest`
**Target**: Interaction between layers (data loader → risk engine → dashboard callbacks).

#### Scenarios
1. **Full Calculation Pipeline**
   - Load sample assets and vulnerabilities from CSV.
   - For each vulnerability, compute RBI‑weighted CVSS.
   - Compute asset‑level CR‑I and EAL.
   - Sum EAL to get total exposure.
   - Assert that total exposure matches a pre‑calculated value (based on sample data).
2. **Budget Optimization Integration**
   - Given the loaded controls library and a budget (e.g., ₹1 Crore), run the optimizer.
   - Verify that selected controls’ total cost ≤ budget.
   - Verify that the total risk reduction is the sum of the EAL reductions for the affected vulnerabilities (can compute by simulating control effectiveness).
3. **Data Mapping Integrity**
   - For each vulnerability in the sample, call `get_rbi_mapping` with its category and asset’s asset_type.
   - Assert that a mapping is returned (non‑None) for at least 80% of vulnerabilities (depending on sample coverage).
4. **Streamlit Callback Simulation** (using `streamlit-runner` or `pytest` with `mock`)
   - Simulate a user clicking the “Load UPI Switch Demo Scenario” button → verify that session state contains the demo data and that the executive metrics update.
   - Simulate adjusting the budget slider and clicking “Show Optimal Plan” → verify that the optimal plan table appears with correct numbers.

### 2.3 End‑to‑End (Demo) Test
**Location**: `tests/e2e/`
**Tool**: Use `pytest` with `playwright` or `selenium` to launch the actual Streamlit app (via `docker compose up` or `streamlit run`) and interact with the UI.
Given time constraints for SIH, a simplified end‑to‑end check can be performed via the validation script.

#### Key Flows to Test
- **Launch**: Docker compose starts, Streamlit accessible on http://localhost:8501.
- **Load Demo Scenario**: Click button → verify that the “Total Exposure” metric changes from a default value (if any) to a known high value (e.g., ₹4,200 Cr).
- **Budget Allocator**: Move slider to ₹2 Cr → click “Show Optimal Plan” → verify that a plan appears with total cost ≤ ₹2 Cr.
- **Technical View**: Switch to Technical View → select an asset → verify that the vulnerability table populates.
- **Show Details**: Click “Show Details” on a row → verify that a modal/expander appears with technical description, RBI mapping, LLM remediation steps, and what‑if toggles.
- **What‑If**: Toggle a control → verify that the Risk Contribution updates.
- **Generate SIH Summary**: Click button → verify that a markdown file is created and contains expected sections (problem statement, solution, impact, etc.).
- **Responsiveness**: Verify that each interaction updates the UI within 2 seconds (can be measured crudely).

### 2.4 Validation Script (`validate.sh`)
A bash script that SIH judges can run to get a quick sanity check. It should:
1. Check that Docker is available and the image builds (optional).
2. Run the Streamlit app in the background, send a few HTTP requests to the endpoints (if API enabled) or directly call Python functions to verify:
   - RBI‑weighted CVSS for a known sample vulnerability yields expected value (within tolerance).
   - CR‑I is between 0 and 100.
   - EAL is non‑negative.
   - Budget optimizer returns a set where total cost ≤ budget.
   - LLM remediation returns a list of strings (or fallback).
3. Shut down the background app.
4. Exit with code 0 if all checks pass, non‑zero otherwise, printing helpful messages.

## 3. Test Environment
- **Language**: Python 3.11+
- **Dependencies**: Listed in `requirements.txt` (streamlit, pandas, scikit-learn, etc.). For unit tests: `pytest`. For LLM: `transformers`, `torch`, `bitsandbytes` (optional – if not present, tests should skip or expect fallback).
- **Data**: Sample CSV files in `data/`.
- **Docker**: Used for demo; tests can run locally without Docker for speed.

## 4. Acceptance Criteria (for SIH)
| Test Type | Minimum Pass Rate |
|-----------|-------------------|
| Unit Tests | 90% |
| Integration Tests | 80% |
| End‑to‑End Demo Flow | All critical steps must work (launch, load demo, budget optimizer, show details, generate summary). |
| Validation Script | Must exit with code 0 when run in the repo root. |

## 5. Reporting
- After running `pytest`, a summary will show passed/failed tests.
- For CI/GitHub Actions (if used), a badge can be added.
- For SIH, we can include a short `TEST_RESULTS.md` file that logs the outcome of the validation script on the demo machine.

## 6. Open Issues & Future Work
- Add property‑based testing (e.g., with `hypothesis`) for score ranges.
- Performance test: ensure that with 10k assets/vulns the dashboard remains responsive.
- Security test: verify no secrets are logged.
- Load test: simulate many concurrent users (if deploying to cloud).

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*