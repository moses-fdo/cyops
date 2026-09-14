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
        "canvas": "#1A1A1A",
        "panel": "#232426",
        "panel-2": "#2A2C2F",
        "panel-3": "#353A3E",
        "hover": "#353A3E",
        "button": "#232426",
        "button-hover": "#2A2C2F",
        "button-active": "#353A3E",
        "border": "#2E3034",
        "border-2": "#353A3E",
        "border-3": "#434850",
        "border-4": "#555B62",
        "border-hover": "#E0E0E0",
        "track": "#232426",
        "text": "#E0E0E0",
        "text-2": "#D0D0D0",
        "text-3": "#BFBFBF",
        "text-4": "#A0A0A0",
        "muted": "#8E8E8E",
        "faint": "#6B6B6B",
        "accent-strong": "#E0E0E0",
        "accent-glow": "rgba(224, 224, 224, 0.12)",
        "on-accent": "#1A1A1A",
        "on-green": "#0D2818",
        "shadow": "0 1px 3px rgba(0, 0, 0, 0.45)",
        "shadow-hover": "0 3px 12px rgba(0, 0, 0, 0.6)",
        "inset": "inset 0 1px 0 0 rgba(255, 255, 255, 0.03)",
        "inset-hover": "inset 0 1px 0 0 rgba(255, 255, 255, 0.06)",
        "buttonshadow": "0 1px 2px rgba(0, 0, 0, 0.35)",
        "glow": "0 0 0 2px rgba(224, 224, 224, 0.18)",
        "input-shadow": "inset 0 1px 2px rgba(0, 0, 0, 0.35)",
    },
    "light": {
        "canvas": "#FFFFFF",
        "panel": "#F7F7F5",
        "panel-2": "#F1F1EF",
        "panel-3": "#EBEBEA",
        "hover": "#EFEFED",
        "button": "#FFFFFF",
        "button-hover": "#EFEFED",
        "button-active": "#E5E5E3",
        "border": "#E9E9E7",
        "border-2": "#E1E1DE",
        "border-3": "#D3D3D0",
        "border-4": "#C3C3C0",
        "border-hover": "#1A1A1A",
        "track": "#E9E9E7",
        "text": "#37352F",
        "text-2": "#45433D",
        "text-3": "#5A5A55",
        "text-4": "#6F6E69",
        "muted": "#787774",
        "faint": "#9B9A97",
        "accent-strong": "#1A1A1A",
        "accent-glow": "rgba(26, 26, 26, 0.12)",
        "on-accent": "#FFFFFF",
        "on-green": "#1C3829",
        "shadow": "0 1px 3px rgba(15, 15, 15, 0.06), 0 2px 8px rgba(15, 15, 15, 0.03)",
        "shadow-hover": "0 2px 6px rgba(15, 15, 15, 0.10), 0 4px 16px rgba(15, 15, 15, 0.06)",
        "inset": "inset 0 0 0 1px rgba(15, 15, 15, 0.05)",
        "inset-hover": "inset 0 0 0 1px rgba(15, 15, 15, 0.1)",
        "buttonshadow": "0 1px 2px rgba(15, 15, 15, 0.06)",
        "glow": "0 0 0 2px rgba(26, 26, 26, 0.18)",
        "input-shadow": "inset 0 1px 2px rgba(15, 15, 15, 0.04)",
    },
}


def _theme_root_css(theme):
    """Render the active theme's --cl-* custom properties for :root."""
    tokens = THEMES.get(theme, THEMES["dark"])
    lines = [f"        --cl-{k}: {v} !important;" for k, v in tokens.items()]
    return "\n".join(lines)


def inject_swiss_css(theme="dark"):
    """Inject Notion-inspired clean UI design system using CSS variables.
    The active theme's tokens are emitted directly at :root (no JS required),
    so the light/dark switch re-paints on the next Streamlit rerun."""
    render_html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

        /* === NOTION CANVAS & TYPOGRAPHY === */
        html, body, [class*="css"] {
            font-family: 'Inter', ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: var(--cl-text) !important;
            letter-spacing: -0.011em;
            -webkit-font-smoothing: antialiased;
        }

        .cl-mono {
            font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
            font-feature-settings: 'tnum' 1, 'zero' 1;
        }

        .stApp {
            background-color: var(--cl-canvas) !important;
            background: var(--cl-canvas) !important;
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

        /* Completely remove Streamlit's native header banner */
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

        /* === NOTION HEADINGS === */
        h1 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.022em !important;
            color: var(--cl-text) !important;
            font-size: 1.45rem !important;
            margin-bottom: 0.2rem !important;
            margin-top: 0 !important;
            line-height: 1.25 !important;
        }
        h2 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.015em !important;
            color: var(--cl-text-2) !important;
            font-size: 1.1rem !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        h3 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            color: var(--cl-text-3) !important;
            font-size: 0.95rem !important;
            margin-top: 0.45rem !important;
            margin-bottom: 0.2rem !important;
        }
        h4 {
            font-family: 'Inter', sans-serif !important;
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

        /* === SMOOTH ANIMATIONS & KEYFRAMES === */
        @keyframes clFadeInUp {
            0% {
                opacity: 0;
                transform: translateY(12px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes clFadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        @keyframes clScaleUp {
            0% {
                opacity: 0;
                transform: scale(0.97);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }

        @keyframes clPulseDot {
            0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Enforce smooth animations on entrance for containers & card blocks */
        .cl-card,
        .cl-feature-box,
        .cl-login-card,
        div[data-testid="stForm"],
        div[data-testid="stMetric"],
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            animation: clFadeInUp 0.38s cubic-bezier(0.16, 1, 0.3, 1) ease-out both !important;
        }

        /* === NOTION BUTTONS WITH MICRO-INTERACTIONS === */
        .stButton button,
        button[data-testid*="BaseButton"],
        button[data-testid*="baseButton"],
        button[data-testid*="stBaseButton"],
        button[kind="secondary"],
        div[data-testid="stButton"] button {
            background-color: var(--cl-button) !important;
            color: var(--cl-text) !important;
            border: 1px solid var(--cl-border-2) !important;
            border-radius: 5px !important;
            padding: 0.42rem 0.85rem !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
            letter-spacing: -0.01em !important;
            box-shadow: var(--cl-buttonshadow) !important;
            transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
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
            font-weight: 500 !important;
            transition: color 0.18s ease !important;
        }

        /* Secondary Button Hover & Focus States */
        .stButton button:not([kind="primary"]):hover,
        .stButton button:not([kind="primary"]):focus,
        .stButton button:not([kind="primary"]):focus-visible,
        button[data-testid*="secondary"]:hover,
        button[data-testid*="secondary"]:focus,
        button[kind="secondary"]:hover,
        button[kind="secondary"]:focus {
            border-color: var(--cl-border-3) !important;
            background-color: var(--cl-button-hover) !important;
            color: var(--cl-text) !important;
            box-shadow: var(--cl-shadow) !important;
            transform: translateY(-1.5px) !important;
            outline: none !important;
        }

        .stButton button:not([kind="primary"]):hover *,
        .stButton button:not([kind="primary"]):focus *,
        .stButton button:not([kind="primary"]):focus-visible *,
        button[data-testid*="secondary"]:hover *,
        button[data-testid*="secondary"]:focus *,
        button[kind="secondary"]:hover *,
        button[kind="secondary"]:focus * {
            color: var(--cl-text) !important;
        }

        .stButton button:not([kind="primary"]):active,
        button[data-testid*="secondary"]:active,
        button[kind="secondary"]:active {
            background-color: var(--cl-button-active) !important;
            border-color: var(--cl-border-3) !important;
            color: var(--cl-text) !important;
            transform: translateY(0px) scale(0.985) !important;
        }

        /* Primary Button (Active View & Primary Actions) */
        button[kind="primary"],
        button[data-testid*="BaseButton-primary"],
        button[data-testid*="baseButton-primary"],
        button[data-testid*="stBaseButton-primary"],
        .stButton button[kind="primary"],
        .stButton button[data-testid*="primary"] {
            background-color: var(--cl-accent-strong) !important;
            background: var(--cl-accent-strong) !important;
            color: var(--cl-on-accent) !important;
            border: 1px solid var(--cl-accent-strong) !important;
            font-weight: 600 !important;
            border-radius: 5px !important;
            box-shadow: var(--cl-buttonshadow) !important;
            transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), filter 0.18s ease, opacity 0.18s ease, box-shadow 0.18s ease !important;
            outline: none !important;
        }

        button[kind="primary"] *,
        button[data-testid*="BaseButton-primary"] *,
        button[data-testid*="baseButton-primary"] *,
        button[data-testid*="stBaseButton-primary"] *,
        .stButton button[kind="primary"] *,
        .stButton button[data-testid*="primary"] * {
            color: var(--cl-on-accent) !important;
            font-weight: 600 !important;
        }

        button[kind="primary"]:hover,
        button[kind="primary"]:focus,
        button[data-testid*="primary"]:hover,
        button[data-testid*="primary"]:focus,
        .stButton button[kind="primary"]:hover,
        .stButton button[kind="primary"]:focus {
            filter: brightness(1.08) !important;
            opacity: 0.95 !important;
            transform: translateY(-1.5px) !important;
            outline: none !important;
        }

        button[kind="primary"]:active,
        button[data-testid*="primary"]:active,
        .stButton button[kind="primary"]:active {
            transform: translateY(0px) scale(0.985) !important;
        }

        /* === NOTION CARD / CALLOUT BLOCKS WITH SMOOTH HOVER LIFT === */
        .cl-card {
            background-color: var(--cl-panel) !important;
            border: 1px solid var(--cl-border) !important;
            border-radius: 6px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: var(--cl-shadow) !important;
            position: relative !important;
            transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.22s ease, background-color 0.22s ease, box-shadow 0.22s ease !important;
        }
        .cl-card:hover {
            border-color: var(--cl-border-2) !important;
            background-color: var(--cl-panel-2) !important;
            transform: translateY(-2.5px) !important;
            box-shadow: var(--cl-shadow-hover) !important;
        }

        .cl-login-card {
            background: var(--cl-panel) !important;
            border: 1px solid var(--cl-border-2) !important;
            border-top: 3px solid var(--cl-accent-strong) !important;
            border-radius: 12px !important;
            padding: 28px 32px !important;
            box-shadow: var(--cl-shadow) !important;
            backdrop-filter: blur(12px) !important;
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease !important;
            animation: clScaleUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) ease-out both !important;
        }
        .cl-login-card:hover {
            border-color: var(--cl-accent-strong) !important;
            transform: translateY(-2.5px) !important;
            box-shadow: var(--cl-shadow-hover) !important;
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
            background: rgba(224, 224, 224, 0.08);
            border: 1px solid rgba(224, 224, 224, 0.20);
            color: #E0E0E0;
            transition: all 0.2s ease !important;
        }
        .cl-status-badge:hover {
            background: rgba(224, 224, 224, 0.14);
        }
        .cl-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #E0E0E0;
            display: inline-block;
            animation: clPulseDot 2s infinite;
        }
        .cl-feature-box {
            background: var(--cl-panel) !important;
            border: 1px solid var(--cl-border) !important;
            border-radius: 8px !important;
            padding: 18px 20px !important;
            transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.22s ease, box-shadow 0.22s ease !important;
            box-shadow: var(--cl-shadow) !important;
        }
        .cl-feature-box:hover {
            border-color: var(--cl-border-2) !important;
            transform: translateY(-2.5px) !important;
            box-shadow: var(--cl-shadow-hover) !important;
        }

        /* === COMPACT HIGH-SECURITY PASSWORD INPUT FIELD === */
        div[data-testid="stForm"] {
            border: 1px solid var(--cl-border-2) !important;
            background: var(--cl-panel) !important;
            border-radius: 12px !important;
            padding: 24px 28px !important;
            max-width: 440px !important;
            margin: 0 auto !important;
            box-shadow: var(--cl-shadow) !important;
            border-top: 3px solid var(--cl-accent-strong) !important;
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease !important;
        }
        div[data-testid="stForm"]:hover {
            box-shadow: var(--cl-shadow-hover) !important;
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
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
            transition: border-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        div[data-testid="stForm"] .stTextInput input:focus {
            border-color: var(--cl-accent-strong) !important;
            box-shadow: 0 0 0 3px var(--cl-accent-glow) !important;
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
        delta_html = f'<div style="display:inline-flex;align-items:center;background:rgba(142, 142, 142, 0.12);border:1px solid rgba(142, 142, 142, 0.30);color:#A0A0A0;font-size:0.725rem;font-weight:600;padding:2px 8px;border-radius:4px;margin-top:0.5rem;font-family:\'JetBrains Mono\',monospace;">{delta}</div>'

    help_html = f'<div style="color:var(--cl-faint);font-size:0.725rem;margin-top:0.5rem;border-top:1px solid var(--cl-border);padding-top:0.45rem;">{help_text}</div>' if help_text else ""

    render_html(
        f"""
        <div class="cl-card" style="height:190px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid #8E8E8E;">
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
        status_bg = "rgba(142, 142, 142, 0.12)"
        status_color = "#A0A0A0"
        status_border = "rgba(142, 142, 142, 0.30)"
        accent_color = "#8E8E8E"
    elif score_val < 70:
        status_label = "Moderate Resilience"
        status_bg = "rgba(107, 107, 107, 0.12)"
        status_color = "#8E8E8E"
        status_border = "rgba(107, 107, 107, 0.30)"
        accent_color = "#6B6B6B"
    else:
        status_label = "High Resilience"
        status_bg = "rgba(224, 224, 224, 0.10)"
        status_color = "#BFBFBF"
        status_border = "rgba(224, 224, 224, 0.25)"
        accent_color = "#E0E0E0"

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
                    <span style="color:#A0A0A0;">0 Critical</span>
                    <span style="color:#8E8E8E;">40 Threshold</span>
                    <span style="color:#BFBFBF;">70 Benchmark</span>
                    <span>100</span>
                </div>
                <div style="position:relative;height:8px;background:var(--cl-track);border-radius:4px;overflow:hidden;border:1px solid var(--cl-border-3);">
                    <div style="position:absolute;left:0;width:40%;height:100%;background:linear-gradient(90deg, #8E8E8E, #A0A0A0);opacity:0.35;"></div>
                    <div style="position:absolute;left:40%;width:30%;height:100%;background:linear-gradient(90deg, #6B6B6B, #8E8E8E);opacity:0.35;"></div>
                    <div style="position:absolute;left:70%;width:30%;height:100%;background:linear-gradient(90deg, #E0E0E0, #BFBFBF);opacity:0.45;"></div>
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
    status_bg = "rgba(224, 224, 224, 0.10)" if is_compliant else "rgba(107, 107, 107, 0.12)"
    status_color = "#BFBFBF" if is_compliant else "#8E8E8E"
    status_border = "rgba(224, 224, 224, 0.25)" if is_compliant else "rgba(107, 107, 107, 0.30)"
    accent_color = "#E0E0E0" if is_compliant else "#6B6B6B"

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
                    <div style="width:{pct}%;height:100%;background:linear-gradient(90deg, #6B6B6B, #E0E0E0);box-shadow:0 0 6px rgba(16, 185, 129, 0.4);transition:width 0.3s ease;"></div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--cl-border);padding-top:0.45rem;font-size:0.725rem;color:var(--cl-faint);">
                <span>Framework: <strong style="color:var(--cl-muted);">RBI · SEBI · NPCI</strong></span>
                <span>Mandate Status: <strong style="color:#BFBFBF;">Verified</strong></span>
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
        "CRITICAL": ("rgba(142, 142, 142, 0.12)", "#A0A0A0", "rgba(142, 142, 142, 0.35)", "CRITICAL"),
        "HIGH": ("rgba(160, 160, 160, 0.12)", "#A0A0A0", "rgba(160, 160, 160, 0.30)", "HIGH"),
        "MEDIUM": ("rgba(142, 142, 142, 0.10)", "#8E8E8E", "rgba(142, 142, 142, 0.30)", "MEDIUM"),
        "LOW": ("rgba(107, 107, 107, 0.08)", "var(--cl-muted)", "rgba(107, 107, 107, 0.20)", "LOW"),
        "MINIMAL": ("rgba(53, 58, 62, 0.15)", "var(--cl-faint)", "rgba(53, 58, 62, 0.30)", "MINIMAL"),
    }
    bg, fg, border, txt = styles.get(lvl, styles["MINIMAL"])
    return f'<span style="background-color:{bg};color:{fg};border:1px solid {border};padding:2px 8px;border-radius:4px;font-size:0.675rem;font-weight:700;letter-spacing:0.04em;font-family:\'JetBrains Mono\',monospace;white-space:nowrap;display:inline-flex;align-items:center;">{txt}</span>'


def render_quick_stat(label, value, icon="", badge=None, border_color="var(--cl-border)"):
    """Render a compact glassmorphic quick-stat telemetry block."""
    badge_html = f'<span style="background:rgba(224,224,224,0.12);border:1px solid rgba(224,224,224,0.30);color:var(--cl-accent-strong);font-size:0.65rem;font-weight:700;padding:2px 6px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;">{badge}</span>' if badge else ""
    icon_html = f'<div style="font-size:1.2rem;line-height:1;">{icon}</div>' if icon else ""
    render_html(
        f"""
        <div class="cl-card" style="padding:0.75rem 1rem;display:flex;align-items:center;justify-content:space-between;border-left:3px solid {border_color};min-height:68px;">
            <div style="display:flex;align-items:center;gap:10px;">
                {icon_html}
                <div>
                    <div style="color:var(--cl-faint);font-size:0.675rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:2px;">{value}</div>
                </div>
            </div>
            {badge_html}
        </div>
        """
    )