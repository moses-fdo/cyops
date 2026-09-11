"""CyberLens 2.0 - Streamlit Dashboard
Executive and Technical views for RBI-aligned cyber risk quantification.
Run: streamlit run streamlit_app.py
"""

import copy
import time
import streamlit as st

import data_loader
from controls_library import CONTROLS
from risk_engine import compute_risk_matrix
from components.widgets import inject_swiss_css, render_html

st.set_page_config(
    page_title="CyberLens 2.0 — RBI-Aligned Cyber Risk Dashboard",
    page_icon="🛡️",
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
    # Inject dark banking dashboard CSS
    inject_swiss_css()

    # Authentication
    session_auth = st.session_state.get("authenticated")
    if not session_auth:
        render_html(
            """
            <div class="cl-card" style="max-width:460px;margin:80px auto 20px auto;padding:28px 26px;border:1px solid #1E2333;border-top:3px solid #38BDF8;">
                <div style="font-size:0.68rem;font-weight:700;color:#38BDF8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.35rem;font-family:'JetBrains Mono',monospace;">
                    RESERVE BANK OF INDIA · FINANCIAL SUPERVISION PORTAL
                </div>
                <h1 style="font-size:1.35rem;margin-bottom:0.35rem;color:#F8FAFC;letter-spacing:-0.02em;">CyberLens Platform 2.0</h1>
                <p style="color:#94A3B8;font-size:0.8rem;margin-bottom:1.15rem;line-height:1.45;">
                    Cyber Risk Quantification (CRQ) & Capital Allocation System for Critical Payment Infrastructure (UPI, CBS, ATM).
                </p>
                <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(56,189,248,0.10);border:1px solid rgba(56,189,248,0.30);padding:3px 10px;border-radius:4px;font-size:0.725rem;color:#38BDF8;margin-bottom:1rem;font-family:'JetBrains Mono',monospace;">
                    Audit Compliance: RBI/2023-24/105
                </div>
            </div>
            """
        )
        st.warning("Authentication required. Demo key: `cyberlens-demo-2024`")
        with st.form("login_form"):
            auth_key = st.text_input("Access Key", type="password")
            submitted = st.form_submit_button("Authenticate →")
            if submitted:
                if auth_key == "cyberlens-demo-2024":
                    st.session_state.authenticated = True
                    st.success("Authenticated. Loading dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid access key.")
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
    header_col1, header_col2, header_col3, header_col4 = st.columns([2.8, 3.1, 3.6, 2.5], vertical_alignment="center")

    with header_col1:
        render_html(
            """
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.35);color:#38BDF8;font-weight:700;font-size:0.8rem;padding:5px 9px;border-radius:4px;font-family:'JetBrains Mono',monospace;letter-spacing:0.04em;">
                    CRQ//2.0
                </div>
                <div style="display:flex;flex-direction:column;justify-content:center;">
                    <div style="font-size:1.05rem;font-weight:700;color:#F8FAFC;letter-spacing:-0.02em;line-height:1.2;">
                        CyberLens Platform
                    </div>
                    <div style="font-size:0.675rem;color:#64748B;font-weight:500;display:flex;align-items:center;gap:6px;margin-top:1px;">
                        <span style="width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;display:inline-block;"></span>
                        <span style="color:#94A3B8;">RBI Master Direction Framework</span> · Active
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
        a_col1, a_col2, a_col3 = st.columns([1.2, 1.3, 1.3])
        with a_col1:
            if st.button("UPI Switch Demo", key="top_upi_demo", help="Load UPI Switch Demo Scenario", width="stretch"):
                from components.sih_features import load_demo_scenario
                load_demo_scenario(session)
                st.rerun()
        with a_col2:
            if st.button("Reset Portfolio", key="top_reset_portfolio", help="Reset Full Portfolio", width="stretch"):
                from components.sih_features import reset_full_portfolio
                reset_full_portfolio(session)
                st.rerun()
        with a_col3:
            if st.button("Generate SIH", key="top_sih_summary", help="Generate SIH Summary", width="stretch"):
                from components.sih_features import generate_sih_summary
                generate_sih_summary(session)

    with header_col4:
        st.text_input(
            "Search",
            placeholder="Filter assets or CVEs...",
            label_visibility="collapsed",
            key="global_search_input",
        )

    render_html('<div style="border-bottom:1px solid #1E2333;margin-top:0.4rem;margin-bottom:1.1rem;"></div>')

    # === HIDDEN SIDEBAR FOR BACKWARD TEST COMPATIBILITY ===
    st.sidebar.markdown(
        """
        <div style="margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid #263241;">
            <div style="font-size:1.05rem;font-weight:700;color:#F5F7FA;letter-spacing:-0.02em;">🛡️ CyberLens 2.0</div>
            <div style="font-size:0.7rem;color:#718096;font-weight:500;margin-top:2px;">RBI-Aligned Cyber Risk Dashboard</div>
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

    if st.sidebar.button("▶ Load UPI Switch Demo", key="sb_upi_demo"):
        from components.sih_features import load_demo_scenario
        load_demo_scenario(session)
        st.rerun()

    if st.sidebar.button("↻ Reset Full Portfolio", key="sb_reset"):
        from components.sih_features import reset_full_portfolio
        reset_full_portfolio(session)
        st.rerun()

    if st.sidebar.button("📄 Generate SIH Summary", key="sb_sih"):
        from components.sih_features import generate_sih_summary
        generate_sih_summary(session)

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