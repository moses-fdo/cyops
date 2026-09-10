"""CyberLens 2.0 - Streamlit Dashboard
Executive and Technical views for RBI-aligned cyber risk quantification.
Run: streamlit run streamlit_app.py
"""

import streamlit as st

import data_loader
from controls_library import CONTROLS
from risk_engine import compute_risk_matrix

st.set_page_config(
    page_title="CyberLens 2.0 — RBI-Aligned Cyber Risk Quantification",
    page_icon="🛡️",
    layout="wide",
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
    # Authentication: require session pass before loading data
    session_auth = st.session_state.get("authenticated")
    if not session_auth:
        st.title("CyberLens 2.0 — RBI-Aligned Cyber Risk Quantification")
        st.warning("Authentication required. This is a demo with synthetic data — production deployment requires OAuth2/JWT.")
        with st.form("login_form"):
            auth_key = st.text_input("Access Key (demo: 'cyberlens-demo-2024')", type="password")
            submitted = st.form_submit_button("Authenticate")
            if submitted:
                if auth_key == "cyberlens-demo-2024":
                    st.session_state.authenticated = True
                    st.success("Authenticated. Loading data...")
                    st.rerun()
                else:
                    st.error("Invalid access key.")
        st.stop()

    # Rate limiting: 120 requests per minute (server-session based)
    import time
    rate_window = st.session_state.get("rate_window", 0)
    rate_count = st.session_state.get("rate_count", 0)
    now = time.time()
    if now - rate_window > 60.0:  # New minute window
        rate_window = now
        rate_count = 1
    else:
        rate_count += 1
    st.session_state.rate_window = rate_window
    st.session_state.rate_count = rate_count
    if rate_count > 120:
        st.error("Too many requests (rate limit exceeded: 120/min). Please wait a moment.")
        st.stop()

    # Audit logging: register session start
    audit_log = st.session_state.get("audit_log", [])
    audit_log.append({"action": "session_start", "timestamp": time.time(), "view": "dashboard"})
    st.session_state.audit_log = audit_log[:1000]  # cap at 1000 entries

    # Load cached dataset after auth passes
    import copy
    data = _load_data()
    session = st.session_state
    if not session.get("loaded"):
        session.update(copy.deepcopy(data))
        session["loaded"] = True

    st.sidebar.title("CyberLens 2.0")
    st.sidebar.caption("RBI-Aligned Cyber Risk Quantification")

    if st.sidebar.button("Load UPI Switch Demo Scenario"):
        from components.sih_features import load_demo_scenario
        load_demo_scenario(session)

    if st.sidebar.button("Reset Full Portfolio"):
        from components.sih_features import reset_full_portfolio
        reset_full_portfolio(session)

    view = st.sidebar.radio("Dashboard View", ["Executive View", "Technical View"])

    if st.sidebar.button("Generate SIH Summary"):
        from components.sih_features import generate_sih_summary
        generate_sih_summary(session)

    if view == "Executive View":
        from components.executive_view import render as render_executive
        render_executive(session)
    else:
        from components.technical_view import render as render_technical
        render_technical(session)

    st.sidebar.divider()
    st.sidebar.caption("⚠️ DEMO ONLY — Not for production banking use. See README for security limitations and hardening requirements.")
    st.sidebar.caption("Demo uses synthetic Indian financial sector data.")


if __name__ == "__main__":
    import sys
    if not st.runtime.exists():
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
        sys.exit(stcli.main())
    else:
        main()