"""CyberLens 2.0 - Executive View
Is-focused metrics: total exposure (₹), CR-I gauge, compliance %, top risks,
budget allocator with optimal plan table.
"""

import streamlit as st
import pandas as pd

from risk_engine import (
    compute_overall_cr_i,
    expected_annual_loss,
    optimize_budget,
    enrich_controls_with_reduction,
    total_exposure,
)
from components.widgets import metric_card, cr_i_gauge, section_header, inr


def compliance_pct(rows):
    """Share of vuln-rows that map to a known RBI clause."""
    if not rows:
        return 100.0
    mapped = sum(1 for r in rows if r["rbi_clause"] != "Unmapped")
    return round(mapped / len(rows) * 100, 1)


def risk_badge(eal_inr):
    """Return HTML badge for risk severity based on EAL amount."""
    # Using quintiles based on sample data distribution
    if eal_inr >= 10000000:  # ₹1 Cr+
        return '<span style="background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🔴 CRITICAL</span>'
    elif eal_inr >= 5000000:  # ₹50 Lakh+
        return '<span style="background-color: #f97316; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🟠 HIGH</span>'
    elif eal_inr >= 1000000:  # ₹10 Lakh+
        return '<span style="background-color: #eab308; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🟡 MEDIUM</span>'
    elif eal_inr >= 500000:   # ₹5 Lakh+
        return '<span style="background-color: #84cc16; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">🟢 LOW</span>'
    else:
        return '<span style="background-color: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">⚪ MINIMAL</span>'


def render(session):
    rows = session["risk_matrix"]
    assets = session["assets"]
    vulns_by_asset = session["vulns_by_asset"]
    overall_cr_i = compute_overall_cr_i(assets, vulns_by_asset)
    exposure = total_exposure(assets, vulns_by_asset)

    section_header("Executive Overview", "RBI-Aligned Cyber Risk Quantification")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Total Annual Cyber Risk Exposure", inr(exposure), help_text="Expected Annual Loss across all assets")
    with col2:
        metric_card("Cyber Resilience Index (CR-I)", f"{overall_cr_i:.1f}/100", help_text="Higher = more resilient")
    with col3:
        metric_card("Vulnerability-to-Regulation Mapping Rate", f"{compliance_pct(rows)}%", help_text="Share of vulnerabilities mapped to a known RBI/SEBI/NPCI clause")

    st.markdown("### Cyber Resilience Index")
    cr_i_gauge(overall_cr_i)

    st.markdown("### Top Risk Contributors")
    top = sorted(rows, key=lambda r: r["eal_inr"], reverse=True)[:3]
    for r in top:
        badge = risk_badge(r["eal_inr"])
        st.markdown(
            f"- **{r['asset_name']}** — {inr(r['eal_inr'])}/yr · {r['category']} · {badge} "
            f"· RBI {r['rbi_clause']}"
        )

    st.markdown("### ROSI-Driven Budget Allocator")
    budget = st.slider(
        "Available Budget (₹ Crore)",
        min_value=0.0, max_value=10.0, value=1.0, step=0.5,
        format="₹%.1f Cr",
    )
    budget_inr = budget * 1_00_00_000

    enriched = enrich_controls_with_reduction(
        session["controls"], assets, vulns_by_asset
    )
    plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

    st.markdown(
        f"**Optimal plan for ₹{budget:.1f} Cr:** {len(plan['controls'])} controls, "
        f"total cost {inr(plan['total_cost'])}, "
        f"risk reduction {inr(plan['total_reduction'])}/yr, "
        f"{inr(plan['remaining_budget'])} unallocated."
    )
    if plan["controls"]:
        table = pd.DataFrame([
            {
                "Control": c["name"],
                "Cost (₹)": c["cost_inr"],
                "Risk Reduction (₹/yr)": round(c["risk_reduction_inr"]),
                "ROSI %": round((c["risk_reduction_inr"] - c["cost_inr"]) / c["cost_inr"] * 100, 1) if c.get("cost_inr", 0) > 0 else 0.0,
            }
            for c in sorted(plan["controls"], key=lambda c: c["cost_inr"])
        ])
        try:
            st.dataframe(table, width="stretch", hide_index=True)
        except TypeError:
            st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.info("No controls fit within the selected budget.")

    return {"exposure": exposure, "cr_i": overall_cr_i, "plan": plan}