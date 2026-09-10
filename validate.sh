#!/usr/bin/env bash
# CyberLens 2.0 — Validation script for SIH judges
# Runs score range checks, ROSI constraints, and LLM fallback verification.
set -e

echo "=== CyberLens 2.0 Validation ==="

# Auto-detect Python executable (prefer workspace virtualenvs if present)
if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif [ -x "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi
echo "Using Python: $($PYTHON --version 2>&1) at $PYTHON"

$PYTHON - << 'PY'
import sys

def main():
    try:
        import data_loader
        from risk_engine import (
            rbi_weighted_cvss, compute_asset_cr_i, compute_overall_cr_i,
            expected_annual_loss, total_exposure, optimize_budget,
            enrich_controls_with_reduction, llm_remediate,
            quantum_risk_estimate, compute_risk_matrix,
        )
        from controls_library import CONTROLS
        from components.widgets import inr, inr_indian
        from components.sih_features import load_demo_scenario, reset_full_portfolio
    except ImportError as e:
        print(f"FAIL — import error: {e}", file=sys.stderr)
        sys.exit(1)

    # 1. Init DB
    data_loader.init_db()
    assets = data_loader.get_assets()
    vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in assets}
    assert assets, "FAIL — no assets loaded"
    assert any(vulns_by_asset.values()), "FAIL — no vulnerabilities loaded"
    print(f"  Assets loaded: {len(assets)}")
    print(f"  Vulnerabilities loaded: {sum(len(v) for v in vulns_by_asset.values())}")

    # 2. Score ranges: RBI-weighted CVSS 0-10, CR-I 0-100, EAL >= 0
    risk_matrix = compute_risk_matrix(assets, vulns_by_asset)
    for r in risk_matrix:
        assert 0 <= r["rbi_cvss"] <= 10, f"FAIL — RBI CVSS out of range: {r['rbi_cvss']}"
        assert 0 <= r["cr_i"] <= 100, f"FAIL — CR-I out of range: {r['cr_i']}"
        assert r["eal_inr"] >= 0, f"FAIL — negative EAL: {r['eal_inr']}"
    print(f"  Score range checks: PASS ({len(risk_matrix)} vuln-rows)")

    # 3. Overall CR-I & Total Exposure
    overall_cr_i = compute_overall_cr_i(assets, vulns_by_asset)
    assert 0 <= overall_cr_i <= 100, f"FAIL — overall CR-I out of range: {overall_cr_i}"
    exposure = total_exposure(assets, vulns_by_asset)
    assert exposure > 0, f"FAIL — non-positive total exposure: {exposure}"
    print(f"  Overall CR-I: {overall_cr_i:.1f}/100, Total Exposure: {inr(exposure)}")

    # 4. Quantum risk: weak crypto flag
    weak_asset = {"crypto_profile": "RSA-1024"}
    safe_asset = {"crypto_profile": "RSA-2048"}
    assert quantum_risk_estimate(weak_asset) == 1.2, "FAIL — weak crypto not flagged"
    assert quantum_risk_estimate(safe_asset) == 1.0, "FAIL — safe crypto wrongly flagged"
    print("  Quantum risk check: PASS")

    # 5. Budget optimizer: total cost <= budget
    enriched = enrich_controls_with_reduction(list(CONTROLS.values()), assets, vulns_by_asset)
    budget = 1_00_00_000  # ₹1 Crore
    plan = optimize_budget(enriched, budget, assets, vulns_by_asset)
    total_cost = sum(c["cost_inr"] for c in plan["controls"])
    assert total_cost <= budget, f"FAIL — cost {total_cost} exceeds budget {budget}"
    print(f"  Optimizer check: PASS (cost={total_cost}, reduction={plan['total_reduction']:.0f})")

    # 6. LLM remediation returns a list of strings
    sample_vuln = list(vulns_by_asset.values())[0][0]
    sample_asset = assets[0]
    for lang in ["en", "hi"]:
        result = llm_remediate(sample_vuln, sample_asset, language=lang)
        assert isinstance(result["steps"], list), f"FAIL — remediation not a list ({lang})"
        assert all(isinstance(s, str) for s in result["steps"]), f"FAIL — step not string ({lang})"
        assert len(result["steps"]) >= 1, f"FAIL — empty remediation ({lang})"
    print("  LLM remediation fallback check: PASS (en, hi)")

    # 7. RBI mapping lookup
    mapped = sum(1 for r in risk_matrix if r["rbi_clause"] != "Unmapped")
    print(f"  RBI mapping coverage: {mapped}/{len(risk_matrix)} vuln-rows mapped")

    # 8. Formatting check
    assert inr(10000000) == "₹1,00,00,000", f"FAIL — INR formatting: {inr(10000000)}"
    print("  Rupee formatting check: PASS")

    print("\n=== ALL CHECKS PASSED ===")

if __name__ == "__main__":
    main()
    sys.exit(0)
PY

echo "Validation complete."
