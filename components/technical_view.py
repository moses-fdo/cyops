"""CyberLens 2.0 - Technical View (Dark Banking Dashboard).
Asset-level drill-down for CISOs and security engineers.
"""

import streamlit as st
import pandas as pd

from risk_engine import (
    compute_asset_cr_i,
    expected_annual_loss,
    rbi_weighted_cvss,
    llm_remediate,
    control_impacts_control,
    effective_eal,
)
from data_loader import get_rbi_mapping
from components.widgets import section_header, inr, risk_badge


def render(session):
    assets = session.get("assets", [])
    vulns_by_asset = session.get("vulns_by_asset", {})
    controls = session.get("controls", [])

    section_header("Technical View", "Deep dive into vulnerabilities, remediation guidance, and what-if simulation.")

    if not assets:
        st.info("No assets recorded in the database.")
        return

    # === ASSET EXPLORER + SEARCH ===
    sel_col, search_col = st.columns([1, 1])
    with sel_col:
        asset_names = ["All Assets"] + [a["name"] for a in assets]
        default_index = 0
        if session.get("selected_asset") in asset_names:
            default_index = asset_names.index(session["selected_asset"])
        selected_asset_name = st.selectbox("Select Asset", asset_names, index=default_index, key="asset_select")
        session["selected_asset"] = selected_asset_name

    with search_col:
        search_default = session.get("global_search_input", "")
        search_query = st.text_input("Search vulnerabilities", value=search_default, key="vuln_search", placeholder="CVE ID, Category, Vuln ID...")

    # Filter
    if selected_asset_name == "All Assets":
        active_assets = assets
        active_vulns = [v for vlist in vulns_by_asset.values() for v in vlist]
    else:
        active_assets = [a for a in assets if a["name"] == selected_asset_name]
        active_vulns = vulns_by_asset.get(active_assets[0]["asset_id"], []) if active_assets else []

    if search_query.strip():
        q = search_query.strip().lower()
        active_vulns = [
            v for v in active_vulns
            if q in (v.get("cve_id") or "").lower()
            or q in v.get("vuln_id", "").lower()
            or q in v.get("category", "").lower()
        ]

    # Asset overview banner (single asset)
    if len(active_assets) == 1:
        a = active_assets[0]
        a_vulns = vulns_by_asset.get(a["asset_id"], [])
        a_cri = compute_asset_cr_i(a, a_vulns)
        a_eal = sum(expected_annual_loss(v, a) for v in a_vulns)
        cri_color = "#FF4D5A" if a_cri < 40 else ("#FFB547" if a_cri < 70 else "#35D39A")

        st.markdown(
            f"""
            <div class="cl-card" style="padding:0.65rem 1rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-weight:600;font-size:0.9rem;color:#F5F7FA;">{a['name']}</span>
                    <span style="color:#718096;font-size:0.75rem;margin-left:8px;">{a['asset_type']}</span>
                    <div style="color:#718096;font-size:0.725rem;margin-top:2px;">
                        Criticality: <strong style="color:#AAB4C3;">{a['criticality']}/10</strong> · Txns: <strong style="color:#AAB4C3;">{a['daily_transaction_volume']:,}/day</strong> · Downtime: <strong style="color:#AAB4C3;">{inr(a['downtime_cost_per_hour'])}/hr</strong>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.725rem;color:#718096;">CR-I: <strong style="color:{cri_color};font-size:0.95rem;">{a_cri:.1f}</strong>/100</div>
                    <div style="font-size:0.725rem;color:#718096;">Exposure: <strong style="color:#F5F7FA;font-size:0.95rem;">{inr(a_eal)}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # === VULNERABILITY TABLE ===
    if not active_vulns:
        st.info("No vulnerabilities match the current filter.")
    else:
        # Build HTML table for dark SOC styling
        tbl = '<div class="cl-card" style="padding:0;overflow-x:auto;">'
        tbl += '<table style="width:100%;border-collapse:collapse;font-size:0.775rem;">'
        tbl += '<thead><tr style="background:#111722;border-bottom:1px solid #263241;color:#718096;font-weight:600;text-transform:uppercase;font-size:0.625rem;letter-spacing:0.05em;">'
        for h in ["Vuln ID", "CVE ID", "Category", "CVSS", "RBI Score", "CR-I Δ", "Days", "Exploit", "Annual Loss (₹)"]:
            align = "right" if h in ["CVSS", "RBI Score", "CR-I Δ", "Days", "Annual Loss (₹)"] else "left"
            tbl += f'<th style="padding:6px 8px;text-align:{align};">{h}</th>'
        tbl += '</tr></thead><tbody>'

        for v in active_vulns:
            v_asset = next((a for a in assets if a["asset_id"] == v["asset_id"]), active_assets[0] if active_assets else {})
            r_cvss = rbi_weighted_cvss(v, v_asset)
            eal = expected_annual_loss(v, v_asset)
            cri_impact = -round((10 - r_cvss) * (v_asset.get("criticality", 5) / 10.0), 1)

            # Severity color for RBI score
            score_color = "#FF4D5A" if r_cvss >= 8 else ("#FFB547" if r_cvss >= 5 else ("#1683FF" if r_cvss >= 3 else "#35D39A"))
            exploit_badge = '<span style="color:#FF4D5A;font-weight:600;">Yes</span>' if v["exploit_available"] else '<span style="color:#718096;">No</span>'

            tbl += f'<tr style="border-bottom:1px solid #1A2431;color:#AAB4C3;">'
            tbl += f'<td style="padding:5px 8px;color:#F5F7FA;font-weight:500;">{v["vuln_id"]}</td>'
            tbl += f'<td style="padding:5px 8px;">{v.get("cve_id") or "N/A"}</td>'
            tbl += f'<td style="padding:5px 8px;">{v["category"]}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;">{v["cvss_base_score"]:.1f}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;color:{score_color};font-weight:600;">{r_cvss:.1f}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;">{cri_impact}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;">{v["days_unpatched"]}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;">{exploit_badge}</td>'
            tbl += f'<td style="padding:5px 8px;text-align:right;color:#F5F7FA;font-weight:500;">{inr(eal)}</td>'
            tbl += '</tr>'

        tbl += '</tbody></table></div>'
        st.markdown(tbl, unsafe_allow_html=True)

    # === VULNERABILITY DETAIL & WHAT-IF ===
    if active_vulns:
        st.markdown('<h3 style="margin-top:0.5rem;">Vulnerability Detail & Simulation</h3>', unsafe_allow_html=True)

        vuln_options = [f"{v['vuln_id']} ({v.get('cve_id') or 'N/A'} · {v['category']})" for v in active_vulns]
        selected_vuln_id = st.selectbox("Select Vulnerability", vuln_options, key="vuln_detail_select")

        if selected_vuln_id:
            v_id = selected_vuln_id.split(" ")[0]
            vuln = next((v for v in active_vulns if v["vuln_id"] == v_id), None)
            asset = next((a for a in assets if a["asset_id"] == vuln["asset_id"]), assets[0]) if vuln else None
            if vuln and asset:
                _render_vulnerability_detail_tabs(session, vuln, asset, controls, active_vulns)

    # === COMPLIANCE HEATMAP ===
    _render_compliance_heatmap(assets, vulns_by_asset)


def _render_vulnerability_detail_tabs(session, vuln, asset, controls, asset_vulns):
    """Render 5 tabbed detail sections — dark theme."""
    base_eal = expected_annual_loss(vuln, asset)
    r_cvss = rbi_weighted_cvss(vuln, asset)
    mapping = get_rbi_mapping(asset["asset_type"], vuln["category"])

    severity = "CRITICAL" if base_eal >= 100_00_000 else ("HIGH" if base_eal >= 50_00_000 else "MEDIUM")
    st.markdown(
        f"""
        <div class="cl-card" style="padding:0.65rem 1rem;margin-bottom:0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-weight:700;font-size:1rem;color:#F5F7FA;">{vuln['vuln_id']}</span>
                    <span style="color:#718096;margin:0 6px;">·</span>
                    <span style="color:#AAB4C3;font-size:0.9rem;">{vuln.get('cve_id') or 'N/A'}</span>
                    <span style="margin-left:8px;">{risk_badge(severity)}</span>
                </div>
                <span style="color:#718096;font-size:0.775rem;">Asset: <strong style="color:#AAB4C3;">{asset['name']}</strong></span>
            </div>
            <div style="color:#718096;font-size:0.8rem;margin-top:0.25rem;">{vuln.get('description') or 'Vulnerability in critical banking infrastructure.'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_ov, tab_map, tab_rem, tab_wif, tab_flow = st.tabs([
        "Overview", "RBI/SEBI/NPCI", "Remediation", "What-If", "Txn Flow"
    ])

    with tab_ov:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div style="font-size:0.825rem;">
                    <div style="margin-bottom:4px;"><span style="color:#718096;">CVSS Base:</span> <strong style="color:#F5F7FA;">{vuln['cvss_base_score']}/10</strong></div>
                    <div style="margin-bottom:4px;"><span style="color:#718096;">RBI-Weighted:</span> <strong style="color:#F5F7FA;">{r_cvss:.2f}/10</strong></div>
                    <div style="margin-bottom:4px;"><span style="color:#718096;">Days Unpatched:</span> <strong style="color:#F5F7FA;">{vuln['days_unpatched']}</strong></div>
                    <div><span style="color:#718096;">Exploit:</span> <strong style="color:{'#FF4D5A' if vuln['exploit_available'] else '#35D39A'};">{'Yes' if vuln['exploit_available'] else 'No'}</strong></div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div style="font-size:0.825rem;">
                    <div style="margin-bottom:4px;"><span style="color:#718096;">Component:</span> <strong style="color:#F5F7FA;">{vuln['category']}</strong></div>
                    <div style="margin-bottom:4px;"><span style="color:#718096;">Asset Type:</span> <strong style="color:#F5F7FA;">{asset['asset_type']}</strong></div>
                    <div><span style="color:#718096;">Risk Contribution:</span> <strong style="color:#F5F7FA;font-size:0.95rem;">{inr(base_eal)}/yr</strong></div>
                </div>""",
                unsafe_allow_html=True,
            )

    with tab_map:
        if mapping:
            st.markdown(
                f"""<div style="font-size:0.825rem;">
                    <div style="margin-bottom:6px;"><span style="color:#718096;">RBI Clause:</span><br/><strong style="color:#1683FF;font-size:0.9rem;">{mapping['rbi_clause']}</strong></div>
                    <div style="margin-bottom:6px;"><span style="color:#718096;">SEBI Reference:</span><br/><strong style="color:#AAB4C3;">{mapping.get('sebi_clause') or 'N/A'}</strong></div>
                    <div style="margin-bottom:6px;"><span style="color:#718096;">NPCI Mandate:</span><br/><strong style="color:#AAB4C3;">{mapping.get('nci_clause') or 'N/A'}</strong></div>
                    <div style="margin-top:8px;padding:8px 10px;background:#111722;border-left:3px solid #1683FF;border-radius:4px;font-size:0.8rem;color:#AAB4C3;">
                        {mapping['description']}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.info("No regulatory mapping found for this combination.")

    with tab_rem:
        lang_selection = st.radio("Language", ["English", "हिंदी"], horizontal=True, key=f"lang_{vuln['vuln_id']}")
        lang_code = "en" if lang_selection == "English" else "hi"
        remed_result = llm_remediate(vuln, asset, language=lang_code)
        st.markdown('<div style="font-size:0.725rem;color:#718096;margin-bottom:6px;">ℹ️ Template-based guidance (LLM fallback ready)</div>', unsafe_allow_html=True)
        for i, step in enumerate(remed_result["steps"], 1):
            st.markdown(f"**{i}.** {step}")

    with tab_wif:
        st.markdown("#### Simulate Security Controls")
        matching_controls = [c for c in controls if control_impacts_control(c, vuln)]
        if not matching_controls:
            st.info(f"No controls target '{vuln['category']}' in the library.")
        else:
            selected_toggles = []
            for c in matching_controls:
                key = f"toggle_{vuln['vuln_id']}_{c['control_id']}"
                toggled = st.toggle(
                    f"{c['name']} — {inr(c['cost_inr'])} ({int(c['effectiveness']*100)}%)",
                    key=key,
                )
                if toggled:
                    selected_toggles.append(c)

            if selected_toggles:
                new_eal = effective_eal(vuln, asset, selected_toggles)
                reduction = base_eal - new_eal
                pct_red = (reduction / base_eal * 100) if base_eal > 0 else 0.0
                st.markdown(
                    f"""<div class="cl-card" style="margin-top:0.5rem;padding:0.65rem 1rem;">
                        <div style="font-size:0.75rem;color:#718096;font-weight:500;">Simulation Result</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#F5F7FA;margin-top:0.15rem;">New Risk: {inr(new_eal)}/yr</div>
                        <div style="color:#35D39A;font-weight:600;font-size:0.85rem;margin-top:0.15rem;">↓ {pct_red:.1f}% · {inr(reduction)} saved/yr</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            if st.button("Use This Plan in Budget Optimizer →", key=f"use_plan_{vuln['vuln_id']}"):
                session["current_view"] = "Executive View"
                if matching_controls:
                    total_match_cost = sum(c["cost_inr"] for c in matching_controls)
                    session["budget_crores"] = round(max(0.5, total_match_cost / 1_00_00_000), 1)
                st.rerun()

    with tab_flow:
        st.markdown(
            f"""<div style="font-size:0.85rem;">
                <div style="font-weight:600;color:#F5F7FA;margin-bottom:6px;">UPI Transaction Flow Impact</div>
                <div class="cl-card" style="text-align:center;padding:0.75rem;">
                    <span style="background:#1A2431;color:#AAB4C3;padding:4px 10px;border-radius:4px;font-size:0.8rem;">Payer App</span>
                    <span style="color:#718096;margin:0 6px;">→</span>
                    <span style="background:#1683FF;color:#fff;padding:4px 10px;border-radius:4px;font-weight:600;font-size:0.8rem;">{asset['name']}</span>
                    <span style="color:#718096;margin:0 6px;">→</span>
                    <span style="background:#1A2431;color:#AAB4C3;padding:4px 10px;border-radius:4px;font-size:0.8rem;">NPCI</span>
                    <span style="color:#718096;margin:0 6px;">→</span>
                    <span style="background:#1A2431;color:#AAB4C3;padding:4px 10px;border-radius:4px;font-size:0.8rem;">CBS</span>
                </div>
                <div style="color:#718096;font-size:0.75rem;margin-top:6px;">⚠️ Exploit on <strong style="color:#AAB4C3;">{asset['name']}</strong> threatens {asset['daily_transaction_volume']:,} daily txns · {inr(asset['downtime_cost_per_hour'])}/hr downtime</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_compliance_heatmap(assets, vulns_by_asset):
    """Compact dark compliance heatmap."""
    st.markdown(
        '<div style="border-top:1px solid #263241;margin-top:0.5rem;padding-top:0.5rem;">'
        '<h2 style="margin:0;color:#F5F7FA;">RBI Guideline Compliance Heatmap</h2>'
        '<div style="color:#718096;font-size:0.75rem;margin-bottom:0.35rem;">Compliance across key RBI guidelines</div></div>',
        unsafe_allow_html=True,
    )

    guidelines = [
        "Authentication Security",
        "Patch Management (<7 days)",
        "Data Encryption at Rest",
        "Network Segmentation",
    ]
    asset_list = assets[:5]

    # Build compact HTML table
    tbl = '<div class="cl-card" style="padding:0.5rem 0.75rem;overflow-x:auto;">'
    tbl += '<table style="width:100%;border-collapse:collapse;font-size:0.725rem;">'
    tbl += '<tr style="border-bottom:1px solid #263241;"><th style="padding:5px 6px;color:#718096;text-align:left;font-weight:600;">Guideline</th>'
    for a in asset_list:
        short = a["name"].split("–")[0].split("(")[0].strip()[:18]
        tbl += f'<th style="padding:5px 6px;color:#AAB4C3;text-align:center;font-weight:600;">{short}</th>'
    tbl += '</tr>'

    for g_idx, g in enumerate(guidelines):
        tbl += f'<tr style="border-bottom:1px solid #1A2431;"><td style="padding:5px 6px;color:#AAB4C3;">{g}</td>'
        for a in asset_list:
            a_vulns = vulns_by_asset.get(a["asset_id"], [])
            unpatched_avg = (sum(v["days_unpatched"] for v in a_vulns) / len(a_vulns)) if a_vulns else 0
            score = max(45, min(98, 100 - int(unpatched_avg * 1.5) - (g_idx * 5)))

            if score >= 90:
                bg, fg = "rgba(53,211,154,0.15)", "#35D39A"
            elif score >= 60:
                bg, fg = "rgba(255,181,71,0.1)", "#FFB547"
            else:
                bg, fg = "rgba(255,77,90,0.15)", "#FF4D5A"

            tbl += f'<td style="padding:4px 6px;text-align:center;"><span style="background:{bg};color:{fg};padding:2px 6px;border-radius:3px;font-weight:600;font-size:0.675rem;">{score}%</span></td>'
        tbl += '</tr>'

    tbl += '</table></div>'
    st.markdown(tbl, unsafe_allow_html=True)