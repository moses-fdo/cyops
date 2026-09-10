"""CyberLens 2.0 - Technical View
Asset explorer, vulnerability table, detail modal (technical desc, RBI mapping,
LLM remediation, what-if simulator), and compliance heatmap.
"""

import streamlit as st
import pandas as pd

from risk_engine import (
    compute_asset_cr_i,
    expected_annual_loss,
    llm_remediate,
    control_impacts_control,
    simulate_control,
)
from components.widgets import section_header, inr


def render(session):
    assets = session["assets"]
    vulns_by_asset = session["vulns_by_asset"]
    controls = session["controls"]

    section_header("Technical View", "Asset-level drill-down for CISOs and security engineers")

    asset_options = {a["name"]: a for a in assets}
    selected_name = st.selectbox("Select Asset", list(asset_options.keys()))
    asset = asset_options[selected_name]
    vulns = vulns_by_asset.get(asset["asset_id"], [])

    st.caption(
        f"{asset['asset_type']} · Criticality {asset['criticality']}/10 · "
        f"{asset['daily_transaction_volume']:,} txns/day · "
        f"Downtime cost {inr(asset['downtime_cost_per_hour'])}/hr"
    )

    if not vulns:
        st.info("No vulnerabilities recorded for this asset.")
        return

    cr_i = compute_asset_cr_i(asset, vulns)
    asset_eal = sum(expected_annual_loss(v, asset) for v in vulns)
    col1, col2 = st.columns(2)
    col1.metric("Asset CR-I", f"{cr_i:.1f}/100")
    col2.metric("Asset Annual Exposure", inr(asset_eal))

    # Vulnerability table
    table = pd.DataFrame([
        {
            "Vuln ID": v["vuln_id"],
            "CVE": v.get("cve_id") or "N/A",
            "Category": v["category"],
            "CVSS Base": v["cvss_base_score"],
            "RBI CVSS": round(_rbi(v, asset), 2),
            "Days Unpatched": v["days_unpatched"],
            "Exploit": "Yes" if v["exploit_available"] else "No",
            "Annual Loss (₹)": round(expected_annual_loss(v, asset)),
        }
        for v in vulns
    ])
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("### Vulnerability Detail & What-If")
    sel_vuln = st.selectbox("Select Vulnerability", [v["vuln_id"] for v in vulns])
    detail = next(v for v in vulns if v["vuln_id"] == sel_vuln)

    _render_detail(session, detail, asset, controls)


def _rbi(vuln, asset):
    from risk_engine import rbi_weighted_cvss
    return rbi_weighted_cvss(vuln, asset)


def _render_detail(session, vuln, asset, controls):
    from data_loader import get_rbi_mapping
    mapping = get_rbi_mapping(asset["asset_type"], vuln["category"])

    st.subheader(vuln["cve_id"] or vuln["vuln_id"])
    st.write(vuln.get("description") or "No description available.")

    with st.expander("RBI / SEBI / NPCI Mapping"):
        if mapping:
            st.markdown(f"- **RBI:** {mapping['rbi_clause']}")
            st.markdown(f"- **SEBI:** {mapping['sebi_clause'] or 'N/A'}")
            st.markdown(f"- **NPCI:** {mapping['nci_clause'] or 'N/A'}")
            st.caption(mapping["description"])
        else:
            st.warning("No regulatory mapping found for this combination.")

    lang = st.radio("Remediation Language", ["English", "हिंदी"], horizontal=True)
    lang_code = "en" if lang == "English" else "hi"
    with st.expander("Remediation Steps (Template)", expanded=True):
        result = llm_remediate(vuln, asset, language=lang_code)
        for i, step in enumerate(result["steps"], 1):
            st.markdown(f"{i}. {step}")

    st.markdown("#### What-If Simulator")
    from risk_engine import effective_eal
    base_eal = expected_annual_loss(vuln, asset)
    st.caption(f"Current annual loss: {inr(base_eal)}")
    applied = []
    for c in controls:
        if control_impacts_control(c, vuln):
            key = f"wi_{vuln['vuln_id']}_{c['control_id']}"
            if st.toggle(f"{c['name']} (effective {int(c['effectiveness']*100)}%)", key=key):
                applied.append(c)
    if applied:
        new_eal = effective_eal(vuln, asset, applied)
        reduction = base_eal - new_eal
        st.success(
            f"Applying {len(applied)} control(s) reduces this vulnerability's "
            f"annual loss from {inr(base_eal)} to {inr(max(new_eal, 0))} "
            f"({inr(reduction)} saved)."
        )

    st.markdown("#### Compliance Heatmap (this asset)")
    categories = sorted({v["category"] for v in asset_vulns})
    # Color-coded heatmap based on vulnerability score severity per category
    heat_data = []
    for cat in categories:
        cat_vulns = [v for v in asset_vulns if v["category"] == cat]
        avg_rbi = sum(_rbi(v, asset) for v in cat_vulns) / len(cat_vulns)
        status = "Critical" if avg_rbi >= 8 else ("High" if avg_rbi >= 5 else ("Medium" if avg_rbi >= 3 else "Low"))
        color = "#ef4444" if avg_rbi >= 8 else ("#f97316" if avg_rbi >= 5 else ("#eab308" if avg_rbi >= 3 else "#84cc16"))
        heat_data.append({
            "Category": cat,
            "Vulns": len(cat_vulns),
            "Avg RBI CVSS": f"{avg_rbi:.1f}",
            "Status": status,
            "Color": color,
        })
    heat_df = pd.DataFrame(heat_data)
    # Render with colored status badges
    for _, row in heat_df.iterrows():
        st.markdown(
            f'<div style="padding: 6px 12px; margin: 2px 0; border-radius: 4px; '
            f'background-color: {row["Color"]}20; border-left: 4px solid {row["Color"]};">'
            f'<strong>{row["Category"]}</strong> — {row["Vulns"]} vulns — '
            f'Avg CVSS <b>{row["Avg RBI CVSS"]}</b> — <b>{row["Status"]}</b></div>',
            unsafe_allow_html=True,
        )