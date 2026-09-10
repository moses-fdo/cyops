"""CyberLens 2.0 - Reusable UI Components & Dark Banking Dashboard Design System."""

import streamlit as st


def inject_swiss_css():
    """Inject dark banking command-center CSS theme."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* === GLOBAL RESET & DARK CANVAS === */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #F5F7FA;
        }
        /* === GLOBAL RESET & DARK CANVAS === */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #F5F7FA;
        }
        .stApp {
            background-color: #081018 !important;
        }

        /* === ABSOLUTE SIDEBAR REMOVAL & FULL-WIDTH CANVAS === */
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarCollapsedControl"],
        section[data-testid="stSidebar"],
        section[aria-label="sidebar"],
        button[data-testid="baseButton-headerNoPadding"],
        .stSidebar,
        div[data-testid="collapsedControl"] {
            display: none !important;
            width: 0px !important;
            min-width: 0px !important;
            max-width: 0px !important;
            visibility: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .stApp > header {
            display: none !important;
        }

        [data-testid="stAppViewContainer"],
        .stAppViewContainer,
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .main,
        div[data-testid="stAppViewBlockContainer"] {
            margin-left: 0 !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 0.5rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        /* === REDUCE STREAMLIT VERTICAL GAPS === */
        [data-testid="stVerticalBlock"] > div {
            gap: 0.5rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            gap: 0.75rem !important;
        }
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stMarkdown"]) {
            min-height: 0 !important;
        }
        div[data-testid="stMarkdownContainer"] > div {
            margin-bottom: 0 !important;
        }
        .stMarkdown { min-height: 0 !important; }

        /* === HEADER === */
        header[data-testid="stHeader"] {
            background-color: #081018 !important;
            border-bottom: 1px solid #213447 !important;
        }

        /* === TOP NAVIGATION BAR === */
        .cl-topbar {
            background-color: #0B141E;
            border: 1px solid #213447;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
            min-height: 62px;
        }

        /* === TYPOGRAPHY HIERARCHY (DARK) === */
        h1 {
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            color: #F5F7FA !important;
            font-size: 1.65rem !important;
            margin-bottom: 0.15rem !important;
            margin-top: 0 !important;
        }
        h2 {
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
            color: #F5F7FA !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        h3 {
            font-weight: 600 !important;
            color: #F5F7FA !important;
            font-size: 0.95rem !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        h4 {
            font-weight: 600 !important;
            color: #F5F7FA !important;
            font-size: 0.875rem !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.2rem !important;
        }
        p, div, span, label {
            color: #AAB4C3;
        }
        .stCaption, caption {
            color: #718096 !important;
            font-size: 0.8rem !important;
        }
        strong, b {
            color: #F5F7FA;
        }

        /* === SIDEBAR NAV RADIO === */
        section[data-testid="stSidebar"] .stRadio > label {
            display: none !important;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 4px !important;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 7px 12px;
            font-weight: 500;
            font-size: 0.85rem;
            color: #718096;
            transition: all 0.15s ease;
            cursor: pointer;
            width: 100%;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            color: #AAB4C3;
            background-color: #1A2431;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
            background-color: rgba(22,131,255,0.15) !important;
            color: #1683FF !important;
            border-color: rgba(22,131,255,0.3) !important;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] span,
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] p {
            color: #1683FF !important;
        }

        /* === BUTTONS — DARK === */
        .stButton > button {
            background-color: #101B27;
            color: #AAB8C8;
            border: 1px solid #213447;
            border-radius: 6px;
            padding: 0.4rem 0.85rem;
            font-weight: 500;
            font-size: 0.8rem;
            transition: all 0.15s ease;
            box-shadow: none !important;
            width: 100%;
        }
        .stButton > button:hover {
            border-color: #168BFF;
            background-color: #142333;
            color: #F5F7FA;
        }
        .stButton > button:active, .stButton > button:focus {
            background-color: #142333;
            color: #F5F7FA;
            border-color: #168BFF;
        }
        /* Primary button */
        button[kind="primary"] {
            background-color: #168BFF !important;
            color: #FFFFFF !important;
            border: 1px solid #168BFF !important;
            font-weight: 600 !important;
        }
        button[kind="primary"]:hover {
            background-color: #329CFF !important;
            border-color: #329CFF !important;
        }

        /* === DARK CARD === */
        .cl-card {
            background-color: #101B27;
            border: 1px solid #213447;
            border-radius: 8px;
            padding: 1rem;
            transition: border-color 0.15s ease, background-color 0.15s ease;
        }
        .cl-card:hover {
            border-color: #2E4760;
            background-color: #142333;
        }

        /* === SELECTBOX / INPUTS — DARK === */
        .stSelectbox > div > div,
        .stTextInput > div > div > input {
            background-color: #101B27 !important;
            color: #F5F7FA !important;
            border-color: #213447 !important;
        }
        .stSelectbox label, .stTextInput label, .stSlider label {
            color: #AAB8C8 !important;
            font-size: 0.8rem !important;
        }

        /* === SLIDER — DARK === */
        .stSlider [data-baseweb="slider"] {
            padding-top: 0.5rem !important;
        }
        .stSlider div[data-baseweb="slider"] div {
            color: #AAB4C3 !important;
        }

        /* === TOGGLE === */
        .stToggle label span { color: #AAB4C3 !important; }

        /* === TABS — DARK === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #111722;
            border-bottom: 1px solid #263241;
            gap: 0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #718096;
            font-size: 0.8rem;
            padding: 6px 14px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #1683FF !important;
            border-bottom-color: #1683FF !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 0.75rem !important;
        }

        /* === DATAFRAME / TABLES — DARK === */
        .stDataFrame, [data-testid="stTable"] {
            border: 1px solid #263241 !important;
            border-radius: 6px !important;
        }

        /* === EXPANDER — DARK === */
        .stExpander {
            border: 1px solid #263241 !important;
            border-radius: 6px !important;
            background-color: #151D28 !important;
        }
        .stExpander summary { color: #AAB4C3 !important; }

        /* === INFO/SUCCESS/WARNING/ERROR BANNERS === */
        .stAlert { border-radius: 6px !important; font-size: 0.85rem !important; }

        /* === HIDE DEFAULTS === */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}

        /* === RADIO (inline) — DARK === */
        .stRadio div[role="radiogroup"] label { color: #AAB4C3 !important; }
        .stRadio div[role="radiogroup"] label[data-checked="true"] span { color: #1683FF !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inr_indian(value):
    """Format a number as Indian Rupees with exact Lakh/Crore grouping (1,23,45,67,890)."""
    if value is None:
        return "₹0"
    try:
        val = round(float(value))
    except (ValueError, TypeError):
        return f"₹{value}"
    sign = "-" if val < 0 else ""
    val = abs(val)
    s = str(int(val))
    if len(s) <= 3:
        return f"{sign}₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return f"{sign}₹{','.join(groups)},{last3}"


def inr(value):
    """Format currency amount with Indian comma grouping."""
    return inr_indian(value)


def section_header(title, subtitle=None, right_html=None):
    """Compact dark section header with optional right-side content."""
    right = f'<div style="display:flex;align-items:center;gap:8px;">{right_html}</div>' if right_html else ""
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:0.75rem;border-bottom:1px solid #263241;padding-bottom:0.5rem;">
            <div>
                <h1 style="margin:0;padding:0;line-height:1.2;">{title}</h1>
                {f'<div style="color:#718096;font-size:0.825rem;margin-top:0.15rem;">{subtitle}</div>' if subtitle else ''}
            </div>
            {right}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, delta=None, help_text=None):
    """Compact dark KPI metric card — standardized height."""
    delta_html = ""
    if delta:
        is_danger = "risk" in label.lower() or "exposure" in label.lower()
        color = "#FF4D5A" if is_danger and "↑" in delta else "#35D39A"
        delta_html = f'<div style="color:{color};font-size:0.75rem;font-weight:500;margin-top:0.3rem;">{delta}</div>'

    help_html = f'<div style="color:#718096;font-size:0.7rem;margin-top:0.5rem;border-top:1px solid #263241;padding-top:0.35rem;">{help_text}</div>' if help_text else ""

    st.markdown(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:0.85rem 1rem;">
            <div>
                <div style="color:#718096;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.35rem;">{label}</div>
                <div style="color:#F5F7FA;font-size:1.65rem;font-weight:700;letter-spacing:-0.03em;line-height:1.1;">{value}</div>
                {delta_html}
            </div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cri_gauge(score, target=70):
    """Compact semi-circular CR-I gauge — standardized height."""
    score_val = max(0.0, min(float(score), 100.0))
    angle = (score_val / 100.0) * 180.0 - 90.0

    if score_val < 40:
        arc_color, status_label, status_color = "#FF4D5A", "Low Resilience", "#FF4D5A"
    elif score_val < 70:
        arc_color, status_label, status_color = "#FFB547", "Moderate", "#FFB547"
    else:
        arc_color, status_label, status_color = "#35D39A", "High Resilience", "#35D39A"

    st.markdown(
        f"""
        <div class="cl-card" style="text-align:center;height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:0.85rem 1rem;">
            <div style="color:#718096;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;text-align:left;">Cyber Resilience Index (CR-I)</div>
            <div style="position:relative;width:130px;margin:0 auto;">
                <svg viewBox="0 0 200 115" style="width:100%;height:auto;">
                    <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#263241" stroke-width="14" stroke-linecap="round"/>
                    <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="{arc_color}" stroke-width="14" stroke-linecap="round"
                          stroke-dasharray="251.2" stroke-dashoffset="{251.2*(1-score_val/100.0)}"/>
                    <g transform="translate(100,100) rotate({angle})">
                        <line x1="0" y1="0" x2="0" y2="-58" stroke="#F5F7FA" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="0" cy="0" r="4" fill="#F5F7FA"/>
                    </g>
                </svg>
                <div style="font-size:1.4rem;font-weight:700;color:#F5F7FA;margin-top:-6px;line-height:1;">
                    {score_val:.0f}<span style="font-size:0.8rem;color:#718096;font-weight:400;">/100</span>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #263241;padding-top:0.35rem;">
                <span style="color:{status_color};font-size:0.7rem;font-weight:600;">{status_label}</span>
                <span style="font-size:0.7rem;color:#718096;">Target: ≥{target}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compliance_gauge(percentage, target=90):
    """Compact circular RBI compliance gauge — standardized height."""
    pct = max(0.0, min(float(percentage), 100.0))
    dashoffset = 282.7 * (1 - pct / 100.0)
    arc_color = "#35D39A" if pct >= 90 else ("#FFB547" if pct >= 60 else "#FF4D5A")

    st.markdown(
        f"""
        <div class="cl-card" style="text-align:center;height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:0.85rem 1rem;">
            <div style="color:#718096;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;text-align:left;">RBI Compliance</div>
            <div style="position:relative;width:80px;height:80px;margin:0 auto;">
                <svg viewBox="0 0 100 100" style="width:100%;height:100%;">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="#263241" stroke-width="8"/>
                    <circle cx="50" cy="50" r="42" fill="none" stroke="{arc_color}" stroke-width="8"
                            stroke-dasharray="263.9" stroke-dashoffset="{263.9*(1-pct/100.0)}"
                            stroke-linecap="round" transform="rotate(-90 50 50)"/>
                </svg>
                <div style="position:absolute;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:1.3rem;font-weight:700;color:#F5F7FA;">
                    {pct:.0f}%
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #263241;padding-top:0.35rem;">
                <span style="color:#718096;font-size:0.7rem;">Regulatory compliance</span>
                <span style="font-size:0.7rem;color:#718096;">Target: ≥{target}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(val):
    """Return dark-theme status pill badge html accepting string or numeric EAL value."""
    if isinstance(val, (int, float)):
        if val >= 10000000:
            lvl = "CRITICAL"
        elif val >= 5000000:
            lvl = "HIGH"
        elif val >= 1000000:
            lvl = "MEDIUM"
        elif val >= 500000:
            lvl = "LOW"
        else:
            lvl = "MINIMAL"
    else:
        lvl = str(val).upper()

    styles = {
        "CRITICAL": ("rgba(255,77,90,0.15)", "#FF4D5A", "● CRITICAL"),
        "HIGH": ("rgba(255,181,71,0.15)", "#FFB547", "● HIGH"),
        "MEDIUM": ("rgba(22,131,255,0.15)", "#1683FF", "● MEDIUM"),
        "LOW": ("rgba(53,211,154,0.15)", "#35D39A", "● LOW"),
        "MINIMAL": ("rgba(113,128,150,0.15)", "#718096", "● MINIMAL"),
    }
    bg, fg, txt = styles.get(lvl, styles["MINIMAL"])
    return f'<span style="background-color:{bg};color:{fg};padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600;letter-spacing:0.03em;">{txt}</span>'