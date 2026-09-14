"""CyberLens 2.0 - Streamlit Dashboard
Executive and Technical views for RBI-aligned cyber risk quantification.
Run: streamlit run streamlit_app.py
"""

import copy
import time
import streamlit as st
import os

import data_loader
from controls_library import CONTROLS
from risk_engine import compute_risk_matrix
from components.widgets import inject_swiss_css, render_html

st.set_page_config(
    page_title="CyberLens 2.0 — RBI-Aligned Cyber Risk Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def _load_data():
    """Load dataset once and cache the computed risk matrix."""
    data_loader.init_db()
    assets = data_loader.get_assets()
    vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in assets}
    risk_matrix = compute_risk_matrix(assets, vulns_by_asset)
    return {
        "assets": assets,
        "vulns_by_asset": vulns_by_asset,
        "risk_matrix": risk_matrix,
        "controls": list(CONTROLS.values()),
    }


def main():
    # Inject themed banking dashboard CSS (light/dark driven by session_state)
    inject_swiss_css(st.session_state.get("theme", "dark"))

    # Authentication Landing Page
    session_auth = st.session_state.get("authenticated")
    if not session_auth:
        render_html(
            """
            <div style="max-width:920px;margin:20px auto 40px auto;">
                <!-- TOP INSTITUTIONAL TELEMETRY BAR -->
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:28px;padding:10px 18px;background:var(--cl-panel);border:1px solid var(--cl-border);border-radius:8px;box-shadow:var(--cl-shadow);">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:34px;height:34px;border-radius:6px;background:var(--cl-panel-3);border:1px solid var(--cl-border-2);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--cl-accent-strong);font-size:0.8rem;">
                            RBI
                        </div>
                        <div>
                            <div style="font-size:0.68rem;font-weight:700;color:var(--cl-accent-strong);text-transform:uppercase;letter-spacing:0.09em;font-family:'JetBrains Mono',monospace;">
                                RESERVE BANK OF INDIA · FINANCIAL SUPERVISION PORTAL
                            </div>
                            <div style="font-size:0.775rem;color:var(--cl-text-3);font-weight:600;margin-top:1px;">
                                Cyber Security & Payment Infrastructure Oversight Division
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:14px;">
                        <div class="cl-status-badge">
                            <span class="cl-status-dot"></span>
                            PROD-GATEWAY-01 // SECURE
                        </div>
                        <div style="font-size:0.725rem;color:var(--cl-faint);font-family:'JetBrains Mono',monospace;background:var(--cl-panel-2);padding:4px 10px;border-radius:4px;border:1px solid var(--cl-border);">
                            CIRCULAR: RBI/2023-24/105
                        </div>
                    </div>
                </div>

                <!-- MAIN HERO HEADER -->
                <div style="text-align:center;margin-bottom:32px;padding:10px 15px;">
                    <div style="display:inline-flex;align-items:center;gap:8px;background:var(--cl-panel-2);border:1px solid var(--cl-border);padding:4px 14px;border-radius:6px;font-size:0.75rem;font-weight:600;color:var(--cl-accent-strong);font-family:'JetBrains Mono',monospace;margin-bottom:14px;">
                        CYBER RISK QUANTIFICATION & CAPITAL ALLOCATION ENGINE
                    </div>
                    <h1 style="font-size:2.3rem;font-weight:800;letter-spacing:-0.03em;color:var(--cl-text);margin-bottom:12px;line-height:1.2;">
                        CyberLens Platform <span style="color:var(--cl-accent-strong);font-weight:800;">2.0</span>
                    </h1>
                    <p style="max-width:680px;margin:0 auto;color:var(--cl-muted);font-size:0.925rem;line-height:1.6;">
                        Quantifying cyber vulnerabilities into monetary risk metrics (₹ Expected Annual Loss & VaR) and delivering ROSI Knapsack capital allocation for critical national financial nodes (UPI, CBS, ATM).
                    </p>
                </div>

                <!-- 3 FEATURE PILLARS GRID -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin-bottom:32px;">
                    <div class="cl-feature-box">
                        <div style="font-size:0.875rem;font-weight:700;color:var(--cl-text);margin-bottom:4px;">
                            RBI Cyber Resilience Index (CR-I)
                        </div>
                        <div style="font-size:0.775rem;color:var(--cl-muted);line-height:1.5;">
                            Weighted 0–100 score combining CVSS, asset criticality, patch timeliness, and threat feeds aligned with RBI Master Directions.
                        </div>
                    </div>
                    <div class="cl-feature-box">
                        <div style="font-size:0.875rem;font-weight:700;color:var(--cl-text);margin-bottom:4px;">
                            Financial Loss Exposure (₹ EAL)
                        </div>
                        <div style="font-size:0.775rem;color:var(--cl-muted);line-height:1.5;">
                            Real-time calculation of Expected Annual Loss in ₹ across banking transaction systems and critical payment gateways.
                        </div>
                    </div>
                    <div class="cl-feature-box">
                        <div style="font-size:0.875rem;font-weight:700;color:var(--cl-text);margin-bottom:4px;">
                            ROSI Capital Allocator
                        </div>
                        <div style="font-size:0.775rem;color:var(--cl-muted);line-height:1.5;">
                            Knapsack 0-1 optimization algorithm recommending security controls that maximize financial risk reduction per rupee invested.
                        </div>
                    </div>
                </div>

                <!-- LOGIN PORTAL CONTAINER (COMPACT & CENTERED) -->
                <div style="max-width:440px;margin:0 auto 20px auto;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:var(--cl-accent-strong);text-transform:uppercase;letter-spacing:0.09em;font-family:'JetBrains Mono',monospace;margin-bottom:4px;">
                        RBI FINANCIAL SUPERVISION PORTAL
                    </div>
                    <div style="font-size:1.2rem;font-weight:800;color:var(--cl-text);margin-bottom:16px;letter-spacing:-0.01em;">
                        Cyber Risk Oversight Console
                    </div>
                </div>
            </div>
            """
        )

        c1, c2, c3 = st.columns([1, 1.8, 1])
        with c2:
            if st.button("Access CyberLens Platform 2.0 →", key="direct_login_btn", type="primary", use_container_width=True):
                st.session_state.authenticated = True
                st.rerun()

        st.stop()

    # Rate limiting
    rate_window = st.session_state.get("rate_window", 0)
    rate_count = st.session_state.get("rate_count", 0)
    now = time.time()
    if now - rate_window > 60.0:
        rate_window = now
        rate_count = 1
    else:
        rate_count += 1
    st.session_state.rate_window = rate_window
    st.session_state.rate_count = rate_count
    if rate_count > 120:
        st.error("Rate limit exceeded (120 requests/minute). Please slow down.")
        st.stop()

    # Log action
    audit_log = st.session_state.get("audit_log", [])
    audit_log.append({"action": "session_start", "timestamp": time.time(), "view": "dashboard"})
    st.session_state.audit_log = audit_log[:1000]

    # Load dataset into session
    data = _load_data()
    session = st.session_state
    if not session.get("loaded"):
        session.update(copy.deepcopy(data))
        session["loaded"] = True

    if "current_view" not in session:
        session["current_view"] = "Executive View"

    # === TOP NAVIGATION HEADER ===
    header_col1, header_col2, header_col3 = st.columns([3.2, 3.2, 3.6], vertical_alignment="center")

    with header_col1:
        render_html(
            """
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.35);color:var(--cl-accent-strong);font-weight:700;font-size:0.825rem;padding:6px 11px;border-radius:6px;font-family:'JetBrains Mono',monospace;letter-spacing:0.04em;">
                    CRQ//2.0
                </div>
                <div style="display:flex;flex-direction:column;justify-content:center;">
                    <div style="font-size:1.1rem;font-weight:700;color:var(--cl-text);letter-spacing:-0.02em;line-height:1.2;">
                        CyberLens Platform
                    </div>
                    <div style="font-size:0.7rem;color:var(--cl-faint);font-weight:500;display:flex;align-items:center;gap:6px;margin-top:2px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 8px #10B981;display:inline-block;"></span>
                        <span style="color:var(--cl-muted);">RBI Master Direction (RBI/2023-24/105)</span> · Active
                    </div>
                </div>
            </div>
            """
        )

    with header_col2:
        curr_view = session.get("current_view", "Executive View")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            if st.button(
                "Executive View",
                key="nav_top_exec",
                type="primary" if curr_view == "Executive View" else "secondary",
                width="stretch",
            ):
                session["current_view"] = "Executive View"
                st.rerun()
        with v_col2:
            if st.button(
                "Technical View",
                key="nav_top_tech",
                type="primary" if curr_view == "Technical View" else "secondary",
                width="stretch",
            ):
                session["current_view"] = "Technical View"
                st.rerun()

    with header_col3:
        a_col1, a_col2, a_col3, a_col4 = st.columns([1.3, 1.3, 1.3, 1.1], vertical_alignment="center")
        with a_col1:
            if st.button("UPI Demo", key="top_upi_demo", type="secondary", help="Load high-risk payment switch demo subset", width="stretch"):
                from components.sih_features import load_demo_scenario
                load_demo_scenario(session)
                st.rerun()
        with a_col2:
            if st.button("Reset", key="top_reset_portfolio", type="secondary", help="Reset full 10-asset portfolio", width="stretch"):
                from components.sih_features import reset_full_portfolio
                reset_full_portfolio(session)
                st.rerun()
        with a_col3:
            if st.button("SIH Export", key="top_sih_summary", type="secondary", help="Generate and download SIH Dossier", width="stretch"):
                from components.sih_features import generate_sih_summary
                generate_sih_summary(session)
        with a_col4:
            current_theme = st.session_state.get("theme", "dark")
            light_on = st.toggle(
                "Light",
                key="theme_switch",
                value=(current_theme == "light"),
                help="Toggle between light and dark visual themes",
            )
            new_theme = "light" if light_on else "dark"
            if new_theme != current_theme:
                st.session_state["theme"] = new_theme
                st.rerun()

    render_html('<div style="border-bottom:1px solid var(--cl-border);margin-top:0.35rem;margin-bottom:0.95rem;"></div>')

    # === SUPERVISORY TOOLS DRAWER ===
    with st.expander("Supervisory Audit & Breach Simulation Console (RBI Compliance · Stress Testing)", expanded=False):
        st_col1, st_col2 = st.columns(2)
        with st_col1:
            st.markdown("#### Regulatory Compliance Audit")
            st.caption("Generate formal audit package cross-referencing all vulnerabilities against RBI, SEBI, and NPCI circulars.")
            if st.button("Generate Compliance Audit Package", key="main_compliance_report", type="secondary", width="stretch"):
                with st.spinner("Building regulatory compliance package..."):
                    result = data_loader.export_compliance_report()
                    st.session_state["compliance_report_result"] = result
                    st.session_state["compliance_report_generated"] = True
                    st.rerun()

            if st.session_state.get("compliance_report_generated"):
                result = st.session_state.get("compliance_report_result", {})
                summary = result.get("summary", {})
                cov = summary.get("compliance_coverage", {}).get("coverage_percentage", 0)
                render_html(
                    f"""
                    <div class="cl-card" style="margin-top:0.75rem;padding:0.85rem 1rem;border-left:3px solid #10B981;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:0.8rem;color:var(--cl-text);font-weight:600;">Framework Coverage: <span class="cl-mono" style="color:#34D399;font-weight:700;">{cov}%</span></span>
                            <span style="font-size:0.7rem;color:var(--cl-faint);font-family:'JetBrains Mono',monospace;">Status: VERIFIED</span>
                        </div>
                    </div>
                    """
                )
                dl_col1, dl_col2 = st.columns(2)
                for fpath in result.get("files_generated", []):
                    fname = os.path.basename(fpath)
                    target_col = dl_col1 if fname.endswith(".csv") else dl_col2
                    with target_col:
                        with open(fpath, "rb") as f:
                            st.download_button(
                                label=f"{fname}",
                                data=f.read(),
                                file_name=fname,
                                mime="text/csv" if fname.endswith(".csv") else "application/json",
                                key=f"main_dl_{fname}",
                                width="stretch",
                            )

        with st_col2:
            st.markdown("#### Judge Breach Simulation")
            st.caption("Simulate full node collapse on the highest-EAL payment switch and quantify Single Loss Expectancy (SLE).")
            if st.button("Run Before/After Breach Simulation", key="main_breach_demo", type="secondary", width="stretch"):
                with st.spinner("Simulating systemic breach on critical infrastructure..."):
                    scenario = data_loader.load_judge_demo_scenario()
                    st.session_state["breach_scenario"] = scenario
                    st.session_state["breach_scenario_generated"] = True
                    st.rerun()

            if st.session_state.get("breach_scenario_generated"):
                scenario = st.session_state.get("breach_scenario")
                if scenario:
                    render_html(
                        f"""
                        <div class="cl-card" style="margin-top:0.75rem;padding:0.85rem 1.15rem;border-left:3px solid #F43F5E;">
                            <div style="font-size:0.7rem;font-weight:700;color:#FB7185;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">
                                Target: {scenario.get('breach', {}).get('asset_name', 'Payment Switch') if isinstance(scenario.get('breach'), dict) else 'Payment Switch'}
                            </div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.78rem;">
                                <div>Pre-Breach CR-I: <strong class="cl-mono" style="color:var(--cl-text);">{scenario['before']['overall_cr_i']}/100</strong></div>
                                <div>Single Incident Loss: <strong class="cl-mono" style="color:#FB7185;">₹{scenario['breach']['realized_single_loss_inr']:,.0f}</strong></div>
                                <div>Annual Exposure: <strong class="cl-mono" style="color:var(--cl-text);">{scenario['before']['total_exposure_inr']:,.0f}</strong></div>
                                <div>Knapsack Control ROI: <strong class="cl-mono" style="color:#34D399;">{scenario['delta']['loss_multiple_of_controls']}×</strong></div>
                            </div>
                        </div>
                        """
                    )

    # === HIDDEN SIDEBAR FOR BACKWARD TEST COMPATIBILITY ===
    st.sidebar.markdown(
        """
        <div style="margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid var(--cl-border-4);">
            <div style="font-size:1.05rem;font-weight:700;color:var(--cl-text);letter-spacing:-0.02em;">CyberLens 2.0</div>
            <div style="font-size:0.7rem;color:var(--cl-muted);font-weight:500;margin-top:2px;">RBI-Aligned Cyber Risk Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Sync nav_radio key if current_view was changed programmatically (e.g. via View Details or Top Nav)
    if session.get("current_view"):
        session["nav_radio"] = session["current_view"]

    nav_selection = st.sidebar.radio(
        "Navigation",
        ["Executive View", "Technical View"],
        key="nav_radio",
    )
    session["current_view"] = nav_selection

    if st.sidebar.button("Load UPI Switch Demo", key="sb_upi_demo"):
        from components.sih_features import load_demo_scenario
        load_demo_scenario(session)
        st.rerun()

    if st.sidebar.button("Reset Full Portfolio", key="sb_reset"):
        from components.sih_features import reset_full_portfolio
        reset_full_portfolio(session)
        st.rerun()

    if st.sidebar.button("Generate SIH Summary", key="sb_sih"):
        from components.sih_features import generate_sih_summary
        generate_sih_summary(session)

    # Phase 2.1: Compliance Report Export (Sidebar hook for tests/automation)
    if st.sidebar.button("Generate Compliance Report", key="sb_compliance_report"):
        with st.spinner("Building compliance audit report..."):
            result = data_loader.export_compliance_report()
            st.session_state["compliance_report_result"] = result
            st.session_state["compliance_report_generated"] = True
            st.rerun()

    if st.session_state.get("compliance_report_generated"):
        result = st.session_state.get("compliance_report_result")
        if result:
            st.sidebar.divider()
            st.sidebar.markdown("### Compliance Report")
            for fpath in result.get("files_generated", []):
                fname = os.path.basename(fpath)
                with open(fpath, "rb") as f:
                    st.sidebar.download_button(
                        label=f"Download {fname}",
                        data=f.read(),
                        file_name=fname,
                        mime="text/csv" if fname.endswith(".csv") else "application/json",
                        key=f"dl_{fname}",
                    )
            summary = result.get("summary", {})
            st.sidebar.metric("Coverage", f"{summary.get('compliance_coverage', {}).get('coverage_percentage', 0)}%")
            if st.sidebar.button("Clear Report", key="sb_clear_report"):
                st.session_state.pop("compliance_report_result", None)
                st.session_state.pop("compliance_report_generated", None)
                st.rerun()

    # Phase 2.2: Before/After Breach Demo (Sidebar hook for tests/automation)
    if st.sidebar.button("Run Breach Demo", key="sb_breach_demo"):
        with st.spinner("Simulating breach scenario..."):
            scenario = data_loader.load_judge_demo_scenario()
            st.session_state["breach_scenario"] = scenario
            st.session_state["breach_scenario_generated"] = True
            st.rerun()

    if st.session_state.get("breach_scenario_generated"):
        scenario = st.session_state.get("breach_scenario")
        if scenario:
            st.sidebar.divider()
            st.sidebar.markdown("### Breach Demo Result")
            st.sidebar.metric("Portfolio CR-I", f"{scenario['before']['overall_cr_i']}/100")
            st.sidebar.metric("Annual Exposure", f"₹{scenario['before']['total_exposure_inr']:,.0f}")
            st.sidebar.metric("Single Breach Loss", f"₹{scenario['breach']['realized_single_loss_inr']:,.0f}")
            st.sidebar.metric("Control ROI", f"{scenario['delta']['loss_multiple_of_controls']}×")
            if st.sidebar.button("Clear Demo", key="sb_clear_breach_demo"):
                st.session_state.pop("breach_scenario", None)
                st.session_state.pop("breach_scenario_generated", None)
                st.rerun()


    # === VIEW ROUTER ===
    if session["current_view"] == "Executive View":
        from components.executive_view import render as render_executive
        render_executive(session)
    else:
        from components.technical_view import render as render_technical
        render_technical(session)


if __name__ == "__main__":
    import sys
    if not st.runtime.exists():
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
        sys.exit(stcli.main())
    else:
        main()