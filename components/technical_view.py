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
from components.widgets import section_header, inr, risk_badge, render_html


def render(session):
    assets = session.get("assets", [])
    vulns_by_asset = session.get("vulns_by_asset", {})
    controls = session.get("controls", [])

    section_header("Technical View", "Asset-level telemetry, vulnerability ledger, regulatory mappings, and what-if mitigations.")

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

    # Asset overview banner - Colorized
    if len(active_assets) == 1:
        a = active_assets[0]
        a_vulns = vulns_by_asset.get(a["asset_id"], [])
        a_cri = compute_asset_cr_i(a, a_vulns)
        a_eal = sum(expected_annual_loss(v, a) for v in a_vulns)

        render_html(
            f"""
            <div class="cl-card" style="padding:0.9rem 1.25rem;margin-bottom:0.85rem;display:flex;justify-content:space-between;align-items:center;border-left:3px solid #38BDF8;">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-weight:700;font-size:1.05rem;color:#F8FAFC;letter-spacing:-0.01em;">{a['name']}</span>
                        <span style="background:#161A24;border:1px solid #232838;color:#38BDF8;font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:4px;font-family:'JetBrains Mono',monospace;">{a['asset_type']}</span>
                    </div>
                    <div style="color:#64748B;font-size:0.75rem;margin-top:6px;display:flex;gap:14px;font-weight:500;">
                        <span>Criticality: <strong style="color:#FBBF24;">{a['criticality']}/10</strong></span>
                        <span>·</span>
                        <span>Daily Volume: <strong class="cl-mono" style="color:#CBD5E1;">{a['daily_transaction_volume']:,} txns</strong></span>
                        <span>·</span>
                        <span>Downtime Impact: <strong class="cl-mono" style="color:#FB7185;">{inr(a['downtime_cost_per_hour'])}/hr</strong></span>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="text-align:right;">
                        <div style="font-size:0.65rem;color:#64748B;text-transform:uppercase;font-weight:700;letter-spacing:0.06em;">Resilience Score</div>
                        <span class="cl-mono" style="background:rgba(56,189,248,0.10);border:1px solid rgba(56,189,248,0.30);color:#38BDF8;font-size:0.95rem;font-weight:700;padding:3px 9px;border-radius:4px;display:inline-block;margin-top:3px;">
                            {a_cri:.1f}<span style="font-size:0.7rem;font-weight:500;opacity:0.7;">/100</span>
                        </span>
                    </div>
                    <div style="text-align:right;border-left:1px solid #1E2333;padding-left:20px;">
                        <div style="font-size:0.65rem;color:#64748B;text-transform:uppercase;font-weight:700;letter-spacing:0.06em;">Annual Loss Exposure</div>
                        <div class="cl-mono" style="font-size:1.2rem;font-weight:700;color:#F8FAFC;margin-top:2px;">{inr(a_eal)}</div>
                    </div>
                </div>
            </div>
            """
        )

    # === VULNERABILITY TABLE ===
    if not active_vulns:
        st.info("No vulnerabilities match the current filter.")
    else:
        tbl = '<div class="cl-card" style="padding:0;overflow-x:auto;border-radius:6px;">'
        tbl += '<table style="width:100%;border-collapse:collapse;font-size:0.775rem;">'
        tbl += '<thead><tr style="background:#10131B;border-bottom:1px solid #1E2333;color:#64748B;font-weight:700;text-transform:uppercase;font-size:0.65rem;letter-spacing:0.06em;">'
        for h in ["Vuln ID", "CVE ID", "Category", "CVSS", "RBI Score", "CR-I Δ", "Days", "Exploit", "Annual Loss (₹)"]:
            align = "right" if h in ["CVSS", "RBI Score", "CR-I Δ", "Days", "Annual Loss (₹)"] else "left"
            tbl += f'<th style="padding:10px 12px;text-align:{align};">{h}</th>'
        tbl += '</tr></thead><tbody>'

        for v in active_vulns:
            v_asset = next((a for a in assets if a["asset_id"] == v["asset_id"]), active_assets[0] if active_assets else {})
            r_cvss = rbi_weighted_cvss(v, v_asset)
            eal = expected_annual_loss(v, v_asset)
            cri_impact = -round((10 - r_cvss) * (v_asset.get("criticality", 5) / 10.0), 1)

            exploit_badge = '<span style="background:rgba(244,63,94,0.15);color:#FB7185;border:1px solid rgba(244,63,94,0.40);font-weight:800;padding:2px 7px;border-radius:4px;font-size:0.65rem;font-family:\'JetBrains Mono\',monospace;">YES</span>' if v["exploit_available"] else '<span style="color:#64748B;font-weight:500;">NO</span>'

            if r_cvss >= 9.0:
                score_badge = f'<span class="cl-mono" style="background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.35);color:#FB7185;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.725rem;">{r_cvss:.1f}</span>'
            elif r_cvss >= 7.0:
                score_badge = f'<span class="cl-mono" style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.35);color:#FBBF24;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.725rem;">{r_cvss:.1f}</span>'
            else:
                score_badge = f'<span class="cl-mono" style="background:rgba(148,163,184,0.10);border:1px solid rgba(148,163,184,0.25);color:#94A3B8;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.725rem;">{r_cvss:.1f}</span>'

            tbl += f'<tr style="border-bottom:1px solid #161924;color:#CBD5E1;">'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;color:#F8FAFC;font-weight:600;">{v["vuln_id"]}</td>'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;color:#94A3B8;">{v.get("cve_id") or "N/A"}</td>'
            tbl += f'<td style="padding:8px 12px;"><span style="background:#161A24;border:1px solid #232838;padding:2px 8px;border-radius:3px;font-size:0.7rem;color:#CBD5E1;">{v["category"]}</span></td>'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;text-align:right;color:#94A3B8;">{v["cvss_base_score"]:.1f}</td>'
            tbl += f'<td style="padding:8px 12px;text-align:right;">{score_badge}</td>'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;text-align:right;color:#FB7185;">{cri_impact}</td>'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;text-align:right;color:#94A3B8;">{v["days_unpatched"]}d</td>'
            tbl += f'<td style="padding:8px 12px;text-align:right;">{exploit_badge}</td>'
            tbl += f'<td class="cl-mono" style="padding:8px 12px;text-align:right;color:#F8FAFC;font-weight:700;">{inr(eal)}</td>'
            tbl += '</tr>'

        tbl += '</tbody></table></div>'
        render_html(tbl)

    # === VULNERABILITY DETAIL & WHAT-IF ===
    if active_vulns:
        render_html('<h3 style="margin-top:1.25rem;color:#F8FAFC;font-size:1.1rem;font-weight:700;">Vulnerability Diagnostics & What-If Simulation</h3>')

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
    """Render 5 tabbed detail sections — colorized institutional terminal theme."""
    base_eal = expected_annual_loss(vuln, asset)
    r_cvss = rbi_weighted_cvss(vuln, asset)
    mapping = get_rbi_mapping(asset["asset_type"], vuln["category"])

    severity = "CRITICAL" if base_eal >= 100_00_000 else ("HIGH" if base_eal >= 50_00_000 else "MEDIUM")
    top_color = "#F43F5E" if severity == "CRITICAL" else ("#F59E0B" if severity == "HIGH" else "#38BDF8")
    render_html(
        f"""
        <div class="cl-card" style="padding:0.85rem 1.25rem;margin-bottom:0.75rem;border-left:3px solid {top_color};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span class="cl-mono" style="font-weight:700;font-size:1.05rem;color:#F8FAFC;">{vuln['vuln_id']}</span>
                    <span style="color:#64748B;">·</span>
                    <span class="cl-mono" style="color:#94A3B8;font-size:0.875rem;">{vuln.get('cve_id') or 'N/A'}</span>
                    {risk_badge(severity)}
                </div>
                <span style="color:#64748B;font-size:0.775rem;">Target Asset: <strong style="color:#38BDF8;">{asset['name']}</strong></span>
            </div>
            <div style="color:#94A3B8;font-size:0.825rem;margin-top:0.4rem;line-height:1.45;">{vuln.get('description') or 'Vulnerability detected in critical banking infrastructure component.'}</div>
        </div>
        """
    )

    tab_ov, tab_map, tab_rem, tab_wif, tab_flow = st.tabs([
        "Overview", "RBI / SEBI / NPCI", "Remediation", "What-If Simulation", "Transaction Flow"
    ])

    with tab_ov:
        c1, c2 = st.columns(2)
        with c1:
            exploit_text = '<span style="color:#FB7185;font-weight:700;">Active In Wild</span>' if vuln['exploit_available'] else '<span style="color:#64748B;">None Reported</span>'
            render_html(
                f"""
                <div class="cl-card" style="font-size:0.825rem;padding:0.9rem 1.15rem;">
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2333;"><span style="color:#64748B;">Base CVSS Score:</span> <strong class="cl-mono" style="color:#F8FAFC;">{vuln['cvss_base_score']}/10</strong></div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2333;"><span style="color:#64748B;">RBI-Weighted Score:</span> <strong class="cl-mono" style="color:#38BDF8;">{r_cvss:.2f}/10</strong></div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2333;"><span style="color:#64748B;">Days Unpatched:</span> <strong class="cl-mono" style="color:#FBBF24;">{vuln['days_unpatched']} days</strong></div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;"><span style="color:#64748B;">Exploit Telemetry:</span> {exploit_text}</div>
                </div>
                """
            )
        with c2:
            render_html(
                f"""
                <div class="cl-card" style="font-size:0.825rem;padding:0.9rem 1.15rem;">
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2333;"><span style="color:#64748B;">Vulnerability Category:</span> <strong style="color:#F8FAFC;">{vuln['category']}</strong></div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2333;"><span style="color:#64748B;">Host Asset Type:</span> <strong style="color:#F8FAFC;">{asset['asset_type']}</strong></div>
                    <div style="display:flex;justify-content:space-between;padding:6px 0;"><span style="color:#64748B;">Annual Loss Contribution:</span> <strong class="cl-mono" style="color:#FB7185;font-size:0.95rem;">{inr(base_eal)}/yr</strong></div>
                </div>
                """
            )

    with tab_map:
        if mapping:
            render_html(
                f"""
                <div class="cl-card" style="padding:1rem 1.25rem;border-left:3px solid #38BDF8;">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px;">
                        <div>
                            <div style="color:#64748B;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">RBI Master Direction Clause</div>
                            <div class="cl-mono" style="color:#38BDF8;font-size:0.925rem;font-weight:700;margin-top:3px;">{mapping['rbi_clause']}</div>
                        </div>
                        <div>
                            <div style="color:#64748B;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">NPCI / SEBI Mandate Reference</div>
                            <div class="cl-mono" style="color:#CBD5E1;font-size:0.9rem;font-weight:600;margin-top:3px;">{mapping.get('nci_clause') or mapping.get('sebi_clause') or 'N/A'}</div>
                        </div>
                    </div>
                    <div style="padding:12px 14px;background:#161A24;border:1px solid #232838;border-radius:4px;font-size:0.8rem;color:#CBD5E1;line-height:1.5;">
                        <span style="color:#38BDF8;font-weight:700;">Mandate Context:</span> {mapping['description']}
                    </div>
                </div>
                """
            )
        else:
            st.info("No regulatory mapping found for this combination.")

    with tab_rem:
        lang_selection = st.radio("Language", ["English", "हिंदी"], horizontal=True, key=f"lang_{vuln['vuln_id']}")
        lang_code = "en" if lang_selection == "English" else "hi"
        remed_result = llm_remediate(vuln, asset, language=lang_code)
        render_html(
            """
            <div style="font-size:0.75rem;color:#64748B;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
                <span style="color:#10B981;">●</span> Deterministic remediation instructions (Quantized LLM fallback active)
            </div>
            """
        )
        for i, step in enumerate(remed_result["steps"], 1):
            render_html(
                f"""
                <div class="cl-card" style="padding:0.7rem 1rem;margin-bottom:0.4rem;display:flex;align-items:flex-start;gap:12px;">
                    <span class="cl-mono" style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.30);color:#38BDF8;font-weight:700;width:24px;height:24px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-size:0.725rem;flex-shrink:0;">{i:02d}</span>
                    <span style="color:#F8FAFC;font-size:0.825rem;line-height:1.45;">{step}</span>
                </div>
                """
            )

    with tab_wif:
        render_html('<h4 style="color:#F8FAFC;font-size:0.95rem;font-weight:700;margin-bottom:0.5rem;">Simulate Security Controls Mitigation</h4>')
        matching_controls = [c for c in controls if control_impacts_control(c, vuln)]
        if not matching_controls:
            st.info(f"No controls target '{vuln['category']}' in the library.")
        else:
            selected_toggles = []
            for c in matching_controls:
                key = f"toggle_{vuln['vuln_id']}_{c['control_id']}"
                toggled = st.toggle(
                    f"{c['name']} — {inr(c['cost_inr'])} ({int(c['effectiveness']*100)}% mitigation)",
                    key=key,
                )
                if toggled:
                    selected_toggles.append(c)

            if selected_toggles:
                new_eal = effective_eal(vuln, asset, selected_toggles)
                reduction = base_eal - new_eal
                pct_red = (reduction / base_eal * 100) if base_eal > 0 else 0.0
                render_html(
                    f"""
                    <div class="cl-card" style="margin-top:0.75rem;padding:0.85rem 1.25rem;border-left:3px solid #10B981;">
                        <div style="font-size:0.7rem;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Simulated Residual Exposure</div>
                        <div class="cl-mono" style="font-size:1.25rem;font-weight:700;color:#F8FAFC;margin-top:0.25rem;">Residual Loss: {inr(new_eal)}/yr</div>
                        <div class="cl-mono" style="color:#34D399;font-weight:700;font-size:0.85rem;margin-top:0.25rem;">↓ {pct_red:.1f}% Reduction · {inr(reduction)} Saved/year</div>
                    </div>
                    """
                )

            if st.button("Use This Plan in Budget Optimizer →", key=f"use_plan_{vuln['vuln_id']}", width="stretch"):
                session["current_view"] = "Executive View"
                if matching_controls:
                    total_match_cost = sum(c["cost_inr"] for c in matching_controls)
                    session["budget_crores"] = round(max(0.5, total_match_cost / 1_00_00_000), 1)
                st.rerun()

    with tab_flow:
        render_html(
            f"""
            <div class="cl-card" style="padding:1rem 1.25rem;">
                <div style="font-weight:700;color:#F8FAFC;margin-bottom:12px;font-size:0.875rem;">UPI Core Transaction Flow Impact</div>
                <div style="text-align:center;padding:1.2rem;background:#161A24;border-radius:6px;border:1px solid #232838;">
                    <span style="background:#10131B;border:1px solid #1E2333;color:#CBD5E1;padding:6px 14px;border-radius:4px;font-size:0.8rem;font-weight:600;">Payer Application</span>
                    <span style="color:#38BDF8;margin:0 10px;font-weight:700;">→</span>
                    <span style="background:rgba(244,63,94,0.15);border:1px solid #F43F5E;color:#FB7185;padding:6px 14px;border-radius:4px;font-weight:800;font-size:0.8rem;">{asset['name']}</span>
                    <span style="color:#38BDF8;margin:0 10px;font-weight:700;">→</span>
                    <span style="background:#10131B;border:1px solid #1E2333;color:#CBD5E1;padding:6px 14px;border-radius:4px;font-size:0.8rem;font-weight:600;">NPCI Switch</span>
                    <span style="color:#38BDF8;margin:0 10px;font-weight:700;">→</span>
                    <span style="background:#10131B;border:1px solid #1E2333;color:#CBD5E1;padding:6px 14px;border-radius:4px;font-size:0.8rem;font-weight:600;">CBS Core Banking</span>
                </div>
                <div style="color:#F8FAFC;font-size:0.775rem;margin-top:12px;display:flex;align-items:center;gap:8px;font-weight:500;">
                    <span style="background:#F43F5E;color:#09090B;font-weight:800;padding:2px 7px;border-radius:3px;font-size:0.65rem;font-family:'JetBrains Mono',monospace;">CRITICAL NODE</span>
                    <span>Exploit on <strong style="color:#38BDF8;">{asset['name']}</strong> compromises <span class="cl-mono" style="color:#FB923C;">{asset['daily_transaction_volume']:,}</span> daily txns · <span class="cl-mono" style="color:#FB7185;">{inr(asset['downtime_cost_per_hour'])}/hr</span> downtime liability</span>
                </div>
            </div>
            """
        )


def _render_compliance_heatmap(assets, vulns_by_asset):
    """Colorized institutional compliance matrix."""
    render_html(
        """
        <div style="border-top:1px solid #1E2333;margin-top:1.25rem;padding-top:0.85rem;">
            <h3 style="margin:0;color:#F8FAFC;font-size:1.1rem;font-weight:700;">RBI Guideline Compliance Matrix</h3>
            <div style="color:#64748B;font-size:0.75rem;margin-bottom:0.75rem;font-weight:500;">Compliance audit index across core banking regulatory mandates</div>
        </div>
        """
    )

    guidelines = [
        "Authentication Security",
        "Patch Management (<7 days)",
        "Data Encryption at Rest",
        "Network Segmentation",
    ]
    asset_list = assets[:5]

    tbl = '<div class="cl-card" style="padding:0;overflow-x:auto;border-radius:6px;">'
    tbl += '<table style="width:100%;border-collapse:collapse;font-size:0.75rem;">'
    tbl += '<tr style="background:#10131B;border-bottom:1px solid #1E2333;"><th style="padding:10px 12px;color:#64748B;text-align:left;font-weight:700;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.06em;">Regulatory Mandate</th>'
    for a in asset_list:
        short = a["name"].split("–")[0].split("(")[0].strip()[:18]
        tbl += f'<th style="padding:10px 12px;color:#CBD5E1;text-align:center;font-weight:600;font-size:0.725rem;">{short}</th>'
    tbl += '</tr>'

    for g_idx, g in enumerate(guidelines):
        tbl += f'<tr style="border-bottom:1px solid #161924;"><td style="padding:10px 12px;color:#F8FAFC;font-weight:600;">{g}</td>'
        for a in asset_list:
            a_vulns = vulns_by_asset.get(a["asset_id"], [])
            unpatched_avg = (sum(v["days_unpatched"] for v in a_vulns) / len(a_vulns)) if a_vulns else 0
            score = max(45, min(98, 100 - int(unpatched_avg * 1.5) - (g_idx * 5)))

            if score >= 90:
                bg, fg, border = "rgba(16,185,129,0.12)", "#34D399", "rgba(16,185,129,0.35)"
            elif score >= 60:
                bg, fg, border = "rgba(245,158,11,0.12)", "#FBBF24", "rgba(245,158,11,0.35)"
            else:
                bg, fg, border = "rgba(244,63,94,0.12)", "#FB7185", "rgba(244,63,94,0.35)"

            tbl += f'<td style="padding:8px 12px;text-align:center;"><span class="cl-mono" style="background:{bg};border:1px solid {border};color:{fg};padding:3px 8px;border-radius:4px;font-weight:700;font-size:0.725rem;">{score}%</span></td>'
        tbl += '</tr>'

    tbl += '</table></div>'
    render_html(tbl)