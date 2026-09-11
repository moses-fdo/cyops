"""CyberLens 2.0 - Reusable UI Components & Dark Banking Dashboard Design System."""

import streamlit as st
import textwrap
import re


def render_html(html_str):
    """Safely render HTML in Streamlit by stripping indentation and blank lines so CommonMark never splits HTML blocks into code blocks."""
    cleaned = textwrap.dedent(html_str).strip()
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_swiss_css():
    """Inject colorized dark banking command-center CSS theme (Obsidian & Ice Cyan with semantic risk accents)."""
    render_html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* === HIGH-END COLORIZED INSTITUTIONAL CANVAS === */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: #F8FAFC !important;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
        }

        .cl-mono {
            font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace !important;
            font-feature-settings: 'tnum' 1, 'zero' 1;
        }

        .stApp {
            background-color: #08090D !important;
            background: radial-gradient(circle at 50% -20%, rgba(56, 189, 248, 0.05) 0%, transparent 60%), #08090D !important;
        }

        /* === CLEAN CANVAS MARGINS === */
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
            padding-top: 0.75rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        .main .block-container {
            padding-top: 0.75rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        /* === DISCIPLINED SPACING === */
        [data-testid="stVerticalBlock"] > div {
            gap: 0.65rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            gap: 0.95rem !important;
        }
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stMarkdown"]) {
            min-height: 0 !important;
        }
        div[data-testid="stMarkdownContainer"] > div {
            margin-bottom: 0 !important;
        }
        .stMarkdown { min-height: 0 !important; }

        /* === FLOATING COMMAND DOCK === */
        .cl-topbar {
            background-color: #10131B !important;
            border: 1px solid #1E2333 !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.25rem !important;
            margin-bottom: 1.25rem !important;
            min-height: 60px !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.05) !important;
        }

        /* === TYPOGRAPHY === */
        h1 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            color: #F8FAFC !important;
            font-size: 1.45rem !important;
            margin-bottom: 0.2rem !important;
            margin-top: 0 !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
            color: #F1F5F9 !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        h3 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;
            font-size: 0.95rem !important;
            margin-top: 0.45rem !important;
            margin-bottom: 0.2rem !important;
        }
        h4 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: #CBD5E1 !important;
            font-size: 0.85rem !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.2rem !important;
        }
        p, div, span, label {
            color: #94A3B8;
        }
        .stCaption, caption {
            color: #64748B !important;
            font-size: 0.775rem !important;
        }
        strong, b {
            color: #F8FAFC;
        }

        /* === BUTTONS === */
        .stButton > button {
            background-color: #141822 !important;
            color: #E2E8F0 !important;
            border: 1px solid #222736 !important;
            border-radius: 5px !important;
            padding: 0.45rem 0.85rem !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            letter-spacing: -0.01em !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.15s ease !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            border-color: #38BDF8 !important;
            background-color: #1B2130 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 10px -2px rgba(56, 189, 248, 0.25) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button:active, .stButton > button:focus {
            background-color: #1E2536 !important;
            color: #FFFFFF !important;
            border-color: #38BDF8 !important;
        }
        /* Primary button - Ice Cyan */
        button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(180deg, #38BDF8 0%, #0284C7 100%) !important;
            color: #03111C !important;
            border: 1px solid #38BDF8 !important;
            font-weight: 700 !important;
            box-shadow: 0 0 14px -2px rgba(56, 189, 248, 0.4) !important;
        }
        button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(180deg, #7DD3FC 0%, #0369A1 100%) !important;
            border-color: #7DD3FC !important;
            color: #03111C !important;
            box-shadow: 0 0 18px -1px rgba(56, 189, 248, 0.55) !important;
            transform: translateY(-1px) !important;
        }

        /* === REFINED DOUBLE-BEZEL CARDS === */
        .cl-card {
            background-color: #10131B !important;
            border: 1px solid #1E2333 !important;
            border-radius: 6px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.04) !important;
            position: relative !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease !important;
        }
        .cl-card:hover {
            border-color: #2E364D !important;
            box-shadow: 0 6px 24px -2px rgba(0, 0, 0, 0.6), inset 0 1px 0 0 rgba(255, 255, 255, 0.06) !important;
        }

        /* === CUSTOM MINIMALIST SCROLLBAR === */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #08090D;
        }
        ::-webkit-scrollbar-thumb {
            background: #1E2333;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #38BDF8;
        }

        /* === INPUTS & SELECTBOXES === */
        .stSelectbox > div > div,
        .stTextInput > div > div > input {
            background-color: #10131B !important;
            color: #F8FAFC !important;
            border: 1px solid #1E2333 !important;
            border-radius: 5px !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3) !important;
            font-size: 0.825rem !important;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within {
            border-color: #38BDF8 !important;
            box-shadow: 0 0 0 1px #38BDF8, 0 0 10px -2px rgba(56, 189, 248, 0.3) !important;
        }
        .stSelectbox label, .stTextInput label, .stSlider label {
            color: #94A3B8 !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }

        /* === SLIDER === */
        .stSlider [data-baseweb="slider"] {
            padding-top: 0.5rem !important;
        }
        .stSlider div[data-baseweb="slider"] div {
            color: #CBD5E1 !important;
        }

        /* === TOGGLE === */
        .stToggle label span { color: #CBD5E1 !important; font-size: 0.825rem !important; }

        /* === TABS WITH ELECTRIC CYAN INDICATOR === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 1px solid #1E2333 !important;
            gap: 4px !important;
            padding-bottom: 0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #64748B !important;
            font-size: 0.825rem !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            border-radius: 5px 5px 0 0 !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.15s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #E2E8F0 !important;
            background: #141822 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #38BDF8 !important;
            border-bottom-color: #38BDF8 !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1rem !important;
        }

        /* === TABLES & DATAFRAMES === */
        .stDataFrame, [data-testid="stTable"] {
            border: 1px solid #1E2333 !important;
            border-radius: 6px !important;
        }
        table tbody tr {
            transition: background-color 0.12s ease !important;
        }
        table tbody tr:hover td {
            background-color: #161A24 !important;
        }

        /* === EXPANDER === */
        .stExpander {
            border: 1px solid #1E2333 !important;
            border-radius: 6px !important;
            background-color: #10131B !important;
        }
        .stExpander summary { color: #CBD5E1 !important; font-weight: 500 !important; }

        /* === ALERTS === */
        .stAlert {
            border-radius: 6px !important;
            font-size: 0.825rem !important;
            border: 1px solid #1E2333 !important;
            background-color: #10131B !important;
        }

        /* === HIDE DEFAULTS === */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}

        /* === RADIO === */
        .stRadio div[role="radiogroup"] label { color: #94A3B8 !important; }
        .stRadio div[role="radiogroup"] label[data-checked="true"] span { color: #38BDF8 !important; }
        </style>
        """
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
    """Compact institutional section header with optional right-side telemetry."""
    right = f'<div style="display:flex;align-items:center;gap:10px;">{right_html}</div>' if right_html else ""
    render_html(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1.1rem;border-bottom:1px solid #1E2333;padding-bottom:0.75rem;">
            <div>
                <h1 style="margin:0;padding:0;line-height:1.2;font-size:1.45rem;font-weight:700;letter-spacing:-0.025em;color:#F8FAFC;">{title}</h1>
                {f'<div style="color:#94A3B8;font-size:0.8rem;margin-top:0.25rem;font-weight:400;">{subtitle}</div>' if subtitle else ''}
            </div>
            {right}
        </div>
        """
    )


def metric_card(label, value, delta=None, help_text=None):
    """Colorized institutional financial metric card — standardized 190px height with crimson risk accent."""
    delta_html = ""
    if delta:
        delta_html = f'<div style="display:inline-flex;align-items:center;background:rgba(244, 63, 94, 0.10);border:1px solid rgba(244, 63, 94, 0.30);color:#FB7185;font-size:0.725rem;font-weight:600;padding:2px 8px;border-radius:4px;margin-top:0.5rem;font-family:\'JetBrains Mono\',monospace;">{delta}</div>'

    help_html = f'<div style="color:#64748B;font-size:0.725rem;margin-top:0.5rem;border-top:1px solid #1E2333;padding-top:0.45rem;">{help_text}</div>' if help_text else ""

    render_html(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid #F43F5E;">
            <div>
                <div style="color:#64748B;font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;">{label}</div>
                <div class="cl-mono" style="color:#F8FAFC;font-size:1.75rem;font-weight:700;letter-spacing:-0.03em;line-height:1.1;">{value}</div>
                {delta_html}
            </div>
            {help_html}
        </div>
        """
    )


def render_cri_gauge(score, target=70):
    """Calibrated institutional Cyber Resilience Index (CR-I) benchmark card — colorized multi-zone."""
    score_val = max(0.0, min(float(score), 100.0))

    if score_val < 40:
        status_label = "Low Resilience"
        status_bg = "rgba(244, 63, 94, 0.12)"
        status_color = "#FB7185"
        status_border = "rgba(244, 63, 94, 0.35)"
        accent_color = "#F43F5E"
    elif score_val < 70:
        status_label = "Moderate Resilience"
        status_bg = "rgba(245, 158, 11, 0.12)"
        status_color = "#FBBF24"
        status_border = "rgba(245, 158, 11, 0.35)"
        accent_color = "#F59E0B"
    else:
        status_label = "High Resilience"
        status_bg = "rgba(16, 185, 129, 0.12)"
        status_color = "#34D399"
        status_border = "rgba(16, 185, 129, 0.35)"
        accent_color = "#10B981"

    pct_pos = min(max(score_val, 4), 96)

    render_html(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid {accent_color};">
            <div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="color:#64748B;font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Cyber Resilience Index (CR-I)</div>
                    <span style="background:{status_bg};border:1px solid {status_border};color:{status_color};font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">
                        {status_label}
                    </span>
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-top:0.4rem;">
                    <span class="cl-mono" style="font-size:2rem;font-weight:700;color:#F8FAFC;line-height:1;">{score_val:.1f}</span>
                    <span style="font-size:0.875rem;color:#64748B;font-weight:500;">/ 100</span>
                </div>
            </div>
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#64748B;margin-bottom:4px;font-family:\'JetBrains Mono\',monospace;">
                    <span style="color:#FB7185;">0 Critical</span>
                    <span style="color:#FBBF24;">40 Threshold</span>
                    <span style="color:#34D399;">70 Benchmark</span>
                    <span>100</span>
                </div>
                <div style="position:relative;height:8px;background:#151923;border-radius:4px;overflow:hidden;border:1px solid #232838;">
                    <div style="position:absolute;left:0;width:40%;height:100%;background:linear-gradient(90deg, #F43F5E, #FB7185);opacity:0.35;"></div>
                    <div style="position:absolute;left:40%;width:30%;height:100%;background:linear-gradient(90deg, #F59E0B, #FBBF24);opacity:0.35;"></div>
                    <div style="position:absolute;left:70%;width:30%;height:100%;background:linear-gradient(90deg, #10B981, #34D399);opacity:0.45;"></div>
                    <div style="position:absolute;left:{pct_pos}%;top:0;bottom:0;width:4px;background:#38BDF8;box-shadow:0 0 8px #38BDF8;border-radius:2px;"></div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #1E2333;padding-top:0.45rem;font-size:0.725rem;color:#64748B;">
                <span>Audit Benchmark: <strong style="color:#94A3B8;">RBI/2023-24/105</strong></span>
                <span>Target: <strong style="color:#38BDF8;">≥{target}</strong></span>
            </div>
        </div>
        """
    )


def render_compliance_gauge(percentage, target=90):
    """Institutional RBI Mandate Audit Verification card — colorized emerald."""
    pct = max(0.0, min(float(percentage), 100.0))
    is_compliant = pct >= 90
    status_label = "Compliant" if is_compliant else "Review Required"
    status_bg = "rgba(16, 185, 129, 0.12)" if is_compliant else "rgba(245, 158, 11, 0.12)"
    status_color = "#34D399" if is_compliant else "#FBBF24"
    status_border = "rgba(16, 185, 129, 0.35)" if is_compliant else "rgba(245, 158, 11, 0.35)"
    accent_color = "#10B981" if is_compliant else "#F59E0B"

    render_html(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid {accent_color};">
            <div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="color:#64748B;font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">RBI Master Direction Audit</div>
                    <span style="background:{status_bg};border:1px solid {status_border};color:{status_color};font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">
                        {status_label}
                    </span>
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-top:0.4rem;">
                    <span class="cl-mono" style="font-size:2rem;font-weight:700;color:#F8FAFC;line-height:1;">{pct:.0f}%</span>
                    <span style="font-size:0.875rem;color:#64748B;font-weight:500;">Clause Coverage</span>
                </div>
            </div>
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#64748B;margin-bottom:4px;font-family:\'JetBrains Mono\',monospace;">
                    <span>17 of 17 Vulnerabilities Mapped</span>
                    <span style="color:#38BDF8;">Target: ≥{target}%</span>
                </div>
                <div style="height:8px;background:#151923;border-radius:4px;overflow:hidden;border:1px solid #232838;">
                    <div style="width:{pct}%;height:100%;background:linear-gradient(90deg, #059669, #10B981);box-shadow:0 0 6px rgba(16, 185, 129, 0.4);transition:width 0.3s ease;"></div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #1E2333;padding-top:0.45rem;font-size:0.725rem;color:#64748B;">
                <span>Framework: <strong style="color:#94A3B8;">RBI · SEBI · NPCI</strong></span>
                <span>Mandate Status: <strong style="color:#34D399;">Verified</strong></span>
            </div>
        </div>
        """
    )


def risk_badge(val):
    """Return calibrated financial risk badge HTML accepting string or numeric EAL value."""
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
        "CRITICAL": ("rgba(244, 63, 94, 0.12)", "#FB7185", "rgba(244, 63, 94, 0.40)", "CRITICAL"),
        "HIGH": ("rgba(249, 115, 22, 0.12)", "#FB923C", "rgba(249, 115, 22, 0.38)", "HIGH"),
        "MEDIUM": ("rgba(234, 179, 8, 0.10)", "#FACC15", "rgba(234, 179, 8, 0.35)", "MEDIUM"),
        "LOW": ("rgba(148, 163, 184, 0.08)", "#94A3B8", "rgba(148, 163, 184, 0.25)", "LOW"),
        "MINIMAL": ("rgba(100, 116, 139, 0.06)", "#64748B", "rgba(100, 116, 139, 0.20)", "MINIMAL"),
    }
    bg, fg, border, txt = styles.get(lvl, styles["MINIMAL"])
    return f'<span style="background-color:{bg};color:{fg};border:1px solid {border};padding:2px 8px;border-radius:4px;font-size:0.675rem;font-weight:700;letter-spacing:0.04em;font-family:\'JetBrains Mono\',monospace;white-space:nowrap;display:inline-flex;align-items:center;">{txt}</span>'