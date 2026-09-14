"""CyberLens 2.0 - Reusable UI Components & Dark Banking Dashboard Design System."""

import streamlit as st
import textwrap
import re


def render_html(html_str):
    """Safely render HTML in Streamlit by stripping indentation and blank lines so CommonMark never splits HTML blocks into code blocks."""
    cleaned = textwrap.dedent(html_str).strip()
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    st.markdown(cleaned, unsafe_allow_html=True)


THEMES = {
    "dark": {
        "canvas": "#07090E",
        "panel": "#0E131F",
        "panel-2": "#141A2B",
        "panel-3": "#1B2338",
        "hover": "#161E31",
        "button": "#121826",
        "button-hover": "#1C2438",
        "button-active": "#222D46",
        "border": "#1E293D",
        "border-2": "#283752",
        "border-3": "#334566",
        "border-4": "#3F567F",
        "border-hover": "#38BDF8",
        "track": "#121826",
        "text": "#F8FAFC",
        "text-2": "#F1F5F9",
        "text-3": "#E2E8F0",
        "text-4": "#CBD5E1",
        "muted": "#94A3B8",
        "faint": "#64748B",
        "accent-strong": "#38BDF8",
        "accent-glow": "rgba(56, 189, 248, 0.25)",
        "on-accent": "#03111C",
        "on-green": "#041F16",
        "shadow": "0 4px 24px -2px rgba(0, 0, 0, 0.55)",
        "shadow-hover": "0 8px 32px -2px rgba(0, 0, 0, 0.70)",
        "inset": "inset 0 1px 0 0 rgba(255, 255, 255, 0.05)",
        "inset-hover": "inset 0 1px 0 0 rgba(255, 255, 255, 0.08)",
        "buttonshadow": "0 1px 3px rgba(0, 0, 0, 0.4)",
        "glow": "0 0 16px -2px rgba(56, 189, 248, 0.35)",
        "input-shadow": "inset 0 1px 2px rgba(0, 0, 0, 0.4)",
    },
    "light": {
        "canvas": "#F6F8FC",
        "panel": "#FFFFFF",
        "panel-2": "#F1F5F9",
        "panel-3": "#E2E8F0",
        "hover": "#F8FAFC",
        "button": "#FFFFFF",
        "button-hover": "#F0F9FF",
        "button-active": "#E0F2FE",
        "border": "#E2E8F0",
        "border-2": "#CBD5E1",
        "border-3": "#94A3B8",
        "border-4": "#64748B",
        "border-hover": "#0284C7",
        "track": "#E2E8F0",
        "text": "#0F172A",
        "text-2": "#1E293B",
        "text-3": "#334155",
        "text-4": "#475569",
        "muted": "#64748B",
        "faint": "#94A3B8",
        "accent-strong": "#0284C7",
        "accent-glow": "rgba(2, 132, 199, 0.20)",
        "on-accent": "#FFFFFF",
        "on-green": "#041F16",
        "shadow": "0 4px 20px -4px rgba(15, 23, 42, 0.08)",
        "shadow-hover": "0 8px 28px -4px rgba(15, 23, 42, 0.14)",
        "inset": "inset 0 1px 0 0 rgba(255, 255, 255, 0.8)",
        "inset-hover": "inset 0 1px 0 0 rgba(255, 255, 255, 1)",
        "buttonshadow": "0 1px 2px rgba(15, 23, 42, 0.08)",
        "glow": "0 0 0 1px rgba(2, 132, 199, 0.30)",
        "input-shadow": "inset 0 1px 2px rgba(15, 23, 42, 0.05)",
    },
}


def _theme_root_css(theme):
    """Render the active theme's --cl-* custom properties for :root."""
    tokens = THEMES.get(theme, THEMES["dark"])
    lines = [f"        --cl-{k}: {v} !important;" for k, v in tokens.items()]
    return "\n".join(lines)


def inject_swiss_css(theme="dark"):
    """Inject the institutional command-center CSS using CSS variables.
    The active theme's tokens are emitted directly at :root (no JS required),
    so the light/dark switch re-paints on the next Streamlit rerun."""
    render_html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* === INSTITUTIONAL COMMAND CANVAS === */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: var(--cl-text) !important;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
        }

        .cl-mono {
            font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
            font-feature-settings: 'tnum' 1, 'zero' 1;
        }

        .stApp {
            background-color: var(--cl-canvas) !important;
            background: radial-gradient(circle at 50% -15%, rgba(56, 189, 248, 0.07) 0%, transparent 65%),
                        radial-gradient(circle at 10% 20%, rgba(16, 185, 129, 0.03) 0%, transparent 50%),
                        var(--cl-canvas) !important;
        }

        /* === CLEAN CANVAS MARGINS & TOP BAR === */
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

        /* Completely remove Streamlit's native header black banner */
        [data-testid="stHeader"],
        header[data-testid="stHeader"],
        .stApp > header,
        header {
            background-color: transparent !important;
            background: transparent !important;
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
            margin: 0 !important;
            visibility: hidden !important;
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
            padding-top: 1rem !important;
            width: 100% !important;
            max-width: 100% !important;
            background-color: var(--cl-canvas) !important;
        }

        .main .block-container {
            padding-top: 0.85rem !important;
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

        /* === TYPOGRAPHY === */
        h1 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            color: var(--cl-text) !important;
            font-size: 1.45rem !important;
            margin-bottom: 0.2rem !important;
            margin-top: 0 !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
            color: var(--cl-text-2) !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        h3 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: var(--cl-text-3) !important;
            font-size: 0.95rem !important;
            margin-top: 0.45rem !important;
            margin-bottom: 0.2rem !important;
        }
        h4 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: var(--cl-text-4) !important;
            font-size: 0.85rem !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.2rem !important;
        }
        p, div, span, label {
            color: var(--cl-muted);
        }
        .stCaption, caption {
            color: var(--cl-faint) !important;
            font-size: 0.775rem !important;
        }
        strong, b {
            color: var(--cl-text);
        }

        /* === BUTTONS & NAVBAR CONTROLS === */
        .stButton button,
        button[data-testid*="BaseButton"],
        button[data-testid*="baseButton"],
        button[data-testid*="stBaseButton"],
        button[kind="secondary"],
        div[data-testid="stButton"] button {
            background-color: var(--cl-button) !important;
            color: var(--cl-text) !important;
            border: 1px solid var(--cl-border-2) !important;
            border-radius: 6px !important;
            padding: 0.45rem 0.85rem !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            letter-spacing: -0.01em !important;
            box-shadow: var(--cl-buttonshadow) !important;
            transition: all 0.15s ease !important;
            width: 100% !important;
            outline: none !important;
        }

        .stButton button *,
        button[data-testid*="BaseButton"] *,
        button[data-testid*="baseButton"] *,
        button[data-testid*="stBaseButton"] *,
        button[kind="secondary"] *,
        div[data-testid="stButton"] button * {
            color: var(--cl-text) !important;
            font-weight: 600 !important;
            transition: color 0.15s ease !important;
        }

        /* Secondary Button Hover & Focus States */
        .stButton button:not([kind="primary"]):hover,
        .stButton button:not([kind="primary"]):focus,
        .stButton button:not([kind="primary"]):focus-visible,
        button[data-testid*="secondary"]:hover,
        button[data-testid*="secondary"]:focus,
        button[kind="secondary"]:hover,
        button[kind="secondary"]:focus {
            border-color: var(--cl-accent-strong) !important;
            background-color: var(--cl-button-hover) !important;
            color: var(--cl-accent-strong) !important;
            box-shadow: var(--cl-glow) !important;
            transform: translateY(-1px) !important;
            outline: none !important;
        }

        .stButton button:not([kind="primary"]):hover *,
        .stButton button:not([kind="primary"]):focus *,
        .stButton button:not([kind="primary"]):focus-visible *,
        button[data-testid*="secondary"]:hover *,
        button[data-testid*="secondary"]:focus *,
        button[kind="secondary"]:hover *,
        button[kind="secondary"]:focus * {
            color: var(--cl-accent-strong) !important;
        }

        .stButton button:not([kind="primary"]):active,
        button[data-testid*="secondary"]:active,
        button[kind="secondary"]:active {
            background-color: var(--cl-button-active) !important;
            border-color: var(--cl-accent-strong) !important;
            color: var(--cl-accent-strong) !important;
            transform: translateY(0px) !important;
        }

        .stButton button:not([kind="primary"]):active *,
        button[data-testid*="secondary"]:active *,
        button[kind="secondary"]:active * {
            color: var(--cl-accent-strong) !important;
        }

        /* Primary Button (Active View & Primary Actions) */
        button[kind="primary"],
        button[data-testid*="BaseButton-primary"],
        button[data-testid*="baseButton-primary"],
        button[data-testid*="stBaseButton-primary"],
        .stButton button[kind="primary"],
        .stButton button[data-testid*="primary"] {
            background: linear-gradient(180deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid #0284C7 !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 10px rgba(2, 132, 199, 0.35) !important;
            outline: none !important;
        }

        button[kind="primary"] *,
        button[data-testid*="BaseButton-primary"] *,
        button[data-testid*="baseButton-primary"] *,
        button[data-testid*="stBaseButton-primary"] *,
        .stButton button[kind="primary"] *,
        .stButton button[data-testid*="primary"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        button[kind="primary"]:hover,
        button[kind="primary"]:focus,
        button[data-testid*="primary"]:hover,
        button[data-testid*="primary"]:focus,
        .stButton button[kind="primary"]:hover,
        .stButton button[kind="primary"]:focus {
            background: linear-gradient(180deg, #0369A1 0%, #075985 100%) !important;
            border-color: #38BDF8 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.5) !important;
            transform: translateY(-1px) !important;
            outline: none !important;
        }

        button[kind="primary"]:hover *,
        button[kind="primary"]:focus *,
        button[data-testid*="primary"]:hover *,
        button[data-testid*="primary"]:focus *,
        .stButton button[kind="primary"]:hover *,
        .stButton button[kind="primary"]:focus * {
            color: #FFFFFF !important;
        }

        /* === REFINED DOUBLE-BEZEL CARDS === */
        .cl-card {
            background-color: var(--cl-panel) !important;
            border: 1px solid var(--cl-border) !important;
            border-radius: 6px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: var(--cl-shadow), var(--cl-inset) !important;
            position: relative !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease !important;
        }
        .cl-card:hover {
            border-color: var(--cl-border-hover) !important;
            box-shadow: var(--cl-shadow-hover), var(--cl-inset-hover) !important;
        }

        /* === LANDING & LOGIN PAGE ANIMATIONS & ELEVATED STYLES === */
        @keyframes clPulseDot {
            0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        .cl-login-card {
            background: var(--cl-panel) !important;
            border: 1px solid var(--cl-border-2) !important;
            border-top: 3px solid var(--cl-accent-strong) !important;
            border-radius: 12px !important;
            padding: 28px 32px !important;
            box-shadow: 0 16px 48px -12px rgba(0, 0, 0, 0.5), 0 0 32px -4px rgba(56, 189, 248, 0.15) !important;
            backdrop-filter: blur(12px) !important;
            transition: all 0.25s ease !important;
        }
        .cl-login-card:hover {
            border-color: var(--cl-accent-strong) !important;
            box-shadow: 0 20px 56px -12px rgba(0, 0, 0, 0.65), 0 0 40px -2px rgba(56, 189, 248, 0.25) !important;
        }
        .cl-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.725rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(16, 185, 129, 0.10);
            border: 1px solid rgba(16, 185, 129, 0.30);
            color: #10B981;
        }
        .cl-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10B981;
            display: inline-block;
            animation: clPulseDot 2s infinite;
        }
        .cl-feature-box {
            background: var(--cl-panel) !important;
            border: 1px solid var(--cl-border) !important;
            border-radius: 8px !important;
            padding: 18px 20px !important;
            transition: all 0.2s ease !important;
            box-shadow: var(--cl-shadow), var(--cl-inset) !important;
        }
        .cl-feature-box:hover {
            border-color: var(--cl-border-hover) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--cl-shadow-hover), var(--cl-inset-hover) !important;
        }

        /* === COMPACT HIGH-SECURITY PASSWORD INPUT FIELD === */
        div[data-testid="stForm"] {
            border: 1px solid var(--cl-border-2) !important;
            background: var(--cl-panel) !important;
            border-radius: 12px !important;
            padding: 24px 28px !important;
            max-width: 440px !important;
            margin: 0 auto !important;
            box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            border-top: 3px solid var(--cl-accent-strong) !important;
        }
        div[data-testid="stForm"] .stTextInput {
            max-width: 320px !important;
            margin: 0 auto 12px auto !important;
        }
        div[data-testid="stForm"] .stTextInput input {
            text-align: center !important;
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 0.18em !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            padding: 10px 16px !important;
            background-color: var(--cl-canvas) !important;
            border: 1px solid var(--cl-border-3) !important;
            border-radius: 8px !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stForm"] .stTextInput input:focus {
            border-color: var(--cl-accent-strong) !important;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.5) !important;
        }
        div[data-testid="stForm"] .stButton {
            max-width: 320px !important;
            margin: 0 auto !important;
        }
        div[data-testid="stForm"] label {
            text-align: center !important;
            width: 100% !important;
            font-size: 0.775rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: var(--cl-text-2) !important;
            font-family: 'JetBrains Mono', monospace !important;
            display: block !important;
            margin-bottom: 6px !important;
        }

        /* === HIDE STREAMLIT FORM INSTRUCTIONS ("Press enter to submit form") === */
        [data-testid="stFormInstructions"],
        div[data-testid="stFormInstructions"],
        small[data-testid="stFormInstructions"],
        .stForm [data-testid="stFormInstructions"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            min-height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* === CUSTOM MINIMALIST SCROLLBAR === */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--cl-canvas);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--cl-border);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--cl-accent-strong);
        }

        /* === INPUTS & SELECTBOXES === */
        .stSelectbox > div > div,
        .stTextInput > div > div > input {
            background-color: var(--cl-panel) !important;
            color: var(--cl-text) !important;
            border: 1px solid var(--cl-border) !important;
            border-radius: 5px !important;
            box-shadow: var(--cl-input-shadow) !important;
            font-size: 0.825rem !important;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within {
            border-color: var(--cl-accent-strong) !important;
            box-shadow: 0 0 0 1px var(--cl-accent-strong), 0 0 10px -2px rgba(56, 189, 248, 0.3) !important;
        }
        .stSelectbox label, .stTextInput label, .stSlider label {
            color: var(--cl-muted) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }

        /* === SLIDER === */
        .stSlider [data-baseweb="slider"] {
            padding-top: 0.5rem !important;
        }
        .stSlider div[data-baseweb="slider"] div {
            color: var(--cl-text-4) !important;
        }

        /* === TOGGLE === */
        .stToggle label span { color: var(--cl-text-4) !important; font-size: 0.825rem !important; }

        /* === TABS WITH ELECTRIC CYAN INDICATOR === */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 1px solid var(--cl-border) !important;
            gap: 4px !important;
            padding-bottom: 0 !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--cl-faint) !important;
            font-size: 0.825rem !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            border-radius: 5px 5px 0 0 !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.15s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--cl-text-3) !important;
            background: var(--cl-button) !important;
        }
        .stTabs [aria-selected="true"] {
            color: var(--cl-accent-strong) !important;
            border-bottom-color: var(--cl-accent-strong) !important;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1rem !important;
        }

        /* === TABLES & DATAFRAMES === */
        .stDataFrame, [data-testid="stTable"] {
            border: 1px solid var(--cl-border) !important;
            border-radius: 6px !important;
        }
        table tbody tr {
            transition: background-color 0.12s ease !important;
        }
        table tbody tr:hover td {
            background-color: var(--cl-hover) !important;
        }

        /* === EXPANDER === */
        .stExpander {
            border: 1px solid var(--cl-border) !important;
            border-radius: 6px !important;
            background-color: var(--cl-panel) !important;
        }
        .stExpander summary { color: var(--cl-text-4) !important; font-weight: 500 !important; }

        /* === ALERTS === */
        .stAlert {
            border-radius: 6px !important;
            font-size: 0.825rem !important;
            border: 1px solid var(--cl-border) !important;
            background-color: var(--cl-panel) !important;
        }

        /* === HIDE DEFAULTS === */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}

        /* === RADIO === */
        .stRadio div[role="radiogroup"] label { color: var(--cl-muted) !important; }
        .stRadio div[role="radiogroup"] label[data-checked="true"] span { color: var(--cl-accent-strong) !important; }

        /* === UNIFIED TOOLTIP DESIGN (SINGLE-BOX, ZERO NESTED BORDERS) === */
        #vg-tooltip-element,
        .vg-tooltip,
        div#vg-tooltip-element,
        #vg-tooltip-element.vg-tooltip,
        #vg-tooltip-element.dark-theme,
        #vg-tooltip-element.light-theme,
        div[data-baseweb="tooltip"],
        div[role="tooltip"],
        div[data-testid="stTooltipContent"],
        div[data-baseweb="popover"] {
            background-color: var(--cl-panel) !important;
            background: var(--cl-panel) !important;
            color: var(--cl-text) !important;
            border: 1px solid var(--cl-border-2) !important;
            box-shadow: var(--cl-shadow) !important;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
            font-size: 0.775rem !important;
            border-radius: 6px !important;
            padding: 7px 11px !important;
            z-index: 999999 !important;
            backdrop-filter: blur(8px) !important;
            overflow: hidden !important;
        }

        /* Reset all inner nested elements so they never render a second box or inner border */
        #vg-tooltip-element *,
        .vg-tooltip *,
        div[data-baseweb="tooltip"] *,
        div[role="tooltip"] *,
        div[data-testid="stTooltipContent"] *,
        div[data-baseweb="popover"] * {
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: var(--cl-text) !important;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
            font-size: 0.775rem !important;
            line-height: 1.35 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        #vg-tooltip-element table,
        .vg-tooltip table {
            border-collapse: collapse !important;
            margin: 0 !important;
        }

        #vg-tooltip-element table tr,
        .vg-tooltip table tr {
            background: transparent !important;
        }

        #vg-tooltip-element table tr td,
        .vg-tooltip table tr td {
            padding: 3px 6px !important;
            border: none !important;
            font-size: 0.775rem !important;
            line-height: 1.3 !important;
        }

        #vg-tooltip-element table tr td.key,
        .vg-tooltip table tr td.key {
            color: var(--cl-muted) !important;
            font-weight: 500 !important;
        }

        #vg-tooltip-element table tr td.value,
        .vg-tooltip table tr td.value {
            color: var(--cl-text) !important;
            font-weight: 700 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* === REMOVE CHART HOVER / SELECTION TOOLBAR & ACTIONS === */
        [data-testid="stElementToolbar"],
        div[data-testid="stElementToolbar"],
        [data-testid="stElementToolbarButton"],
        .vega-actions,
        details.vega-actions,
        summary.vega-actions-button,
        .vega-embed summary,
        div.vega-actions,
        button[title="View fullscreen"],
        .action-link {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
        }
        </style>
        """
    )
    # Emit the active theme's tokens at :root so light/dark re-paints on rerun.
    render_html(
        f"""
        <style>
        :root {{
{_theme_root_css(theme)}
        }}
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
        <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1.1rem;border-bottom:1px solid var(--cl-border);padding-bottom:0.75rem;">
            <div>
                <h1 style="margin:0;padding:0;line-height:1.2;font-size:1.45rem;font-weight:700;letter-spacing:-0.025em;color:var(--cl-text);">{title}</h1>
                {f'<div style="color:var(--cl-muted);font-size:0.8rem;margin-top:0.25rem;font-weight:400;">{subtitle}</div>' if subtitle else ''}
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

    help_html = f'<div style="color:var(--cl-faint);font-size:0.725rem;margin-top:0.5rem;border-top:1px solid var(--cl-border);padding-top:0.45rem;">{help_text}</div>' if help_text else ""

    render_html(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid #F43F5E;">
            <div>
                <div style="color:var(--cl-faint);font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;">{label}</div>
                <div class="cl-mono" style="color:var(--cl-text);font-size:1.75rem;font-weight:700;letter-spacing:-0.03em;line-height:1.1;">{value}</div>
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
                    <div style="color:var(--cl-faint);font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Cyber Resilience Index (CR-I)</div>
                    <span style="background:{status_bg};border:1px solid {status_border};color:{status_color};font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">
                        {status_label}
                    </span>
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-top:0.4rem;">
                    <span class="cl-mono" style="font-size:2rem;font-weight:700;color:var(--cl-text);line-height:1;">{score_val:.1f}</span>
                    <span style="font-size:0.875rem;color:var(--cl-faint);font-weight:500;">/ 100</span>
                </div>
            </div>
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:var(--cl-faint);margin-bottom:4px;font-family:\'JetBrains Mono\',monospace;">
                    <span style="color:#FB7185;">0 Critical</span>
                    <span style="color:#FBBF24;">40 Threshold</span>
                    <span style="color:#34D399;">70 Benchmark</span>
                    <span>100</span>
                </div>
                <div style="position:relative;height:8px;background:var(--cl-track);border-radius:4px;overflow:hidden;border:1px solid var(--cl-border-3);">
                    <div style="position:absolute;left:0;width:40%;height:100%;background:linear-gradient(90deg, #F43F5E, #FB7185);opacity:0.35;"></div>
                    <div style="position:absolute;left:40%;width:30%;height:100%;background:linear-gradient(90deg, #F59E0B, #FBBF24);opacity:0.35;"></div>
                    <div style="position:absolute;left:70%;width:30%;height:100%;background:linear-gradient(90deg, #10B981, #34D399);opacity:0.45;"></div>
                    <div style="position:absolute;left:{pct_pos}%;top:0;bottom:0;width:4px;background:var(--cl-accent-strong);box-shadow:0 0 8px var(--cl-accent-strong);border-radius:2px;"></div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--cl-border);padding-top:0.45rem;font-size:0.725rem;color:var(--cl-faint);">
                <span>Audit Benchmark: <strong style="color:var(--cl-muted);">RBI/2023-24/105</strong></span>
                <span>Target: <strong style="color:var(--cl-accent-strong);">≥{target}</strong></span>
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
                    <div style="color:var(--cl-faint);font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">RBI Master Direction Audit</div>
                    <span style="background:{status_bg};border:1px solid {status_border};color:{status_color};font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">
                        {status_label}
                    </span>
                </div>
                <div style="display:flex;align-items:baseline;gap:6px;margin-top:0.4rem;">
                    <span class="cl-mono" style="font-size:2rem;font-weight:700;color:var(--cl-text);line-height:1;">{pct:.0f}%</span>
                    <span style="font-size:0.875rem;color:var(--cl-faint);font-weight:500;">Clause Coverage</span>
                </div>
            </div>
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.65rem;color:var(--cl-faint);margin-bottom:4px;font-family:\'JetBrains Mono\',monospace;">
                    <span>17 of 17 Vulnerabilities Mapped</span>
                    <span style="color:var(--cl-accent-strong);">Target: ≥{target}%</span>
                </div>
                <div style="height:8px;background:var(--cl-track);border-radius:4px;overflow:hidden;border:1px solid var(--cl-border-3);">
                    <div style="width:{pct}%;height:100%;background:linear-gradient(90deg, #059669, #10B981);box-shadow:0 0 6px rgba(16, 185, 129, 0.4);transition:width 0.3s ease;"></div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--cl-border);padding-top:0.45rem;font-size:0.725rem;color:var(--cl-faint);">
                <span>Framework: <strong style="color:var(--cl-muted);">RBI · SEBI · NPCI</strong></span>
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
        "LOW": ("rgba(148, 163, 184, 0.08)", "var(--cl-muted)", "rgba(148, 163, 184, 0.25)", "LOW"),
        "MINIMAL": ("rgba(100, 116, 139, 0.06)", "var(--cl-faint)", "rgba(100, 116, 139, 0.20)", "MINIMAL"),
    }
    bg, fg, border, txt = styles.get(lvl, styles["MINIMAL"])
    return f'<span style="background-color:{bg};color:{fg};border:1px solid {border};padding:2px 8px;border-radius:4px;font-size:0.675rem;font-weight:700;letter-spacing:0.04em;font-family:\'JetBrains Mono\',monospace;white-space:nowrap;display:inline-flex;align-items:center;">{txt}</span>'


def render_quick_stat(label, value, icon="🛡️", badge=None, border_color="var(--cl-border)"):
    """Render a compact glassmorphic quick-stat telemetry block."""
    badge_html = f'<span style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.30);color:var(--cl-accent-strong);font-size:0.65rem;font-weight:700;padding:2px 6px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">{badge}</span>' if badge else ""
    render_html(
        f"""
        <div class="cl-card" style="padding:0.75rem 1rem;display:flex;align-items:center;justify-content:space-between;border-left:3px solid {border_color};min-height:68px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="font-size:1.2rem;line-height:1;">{icon}</div>
                <div>
                    <div style="color:var(--cl-faint);font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:2px;">{value}</div>
                </div>
            </div>
            {badge_html}
        </div>
        """
    )