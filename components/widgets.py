"""CyberLens 2.0 - Reusable Streamlit widgets."""

try:
    import streamlit as st
except ImportError:
    st = None


def metric_card(label, value, delta=None, help_text=None):
    """Small metric card with optional tooltip."""
    if not st:
        return
    delta_text = f"  \n**{delta}**" if delta else ""
    help_text = f"  \n{help_text}" if help_text else ""
    st.markdown(
        f"""
        <div style="background-color: #1f2937; padding: 16px; border-radius: 8px;
                    border-left: 4px solid #6366f1; margin-bottom: 8px;">
            <div style="color: #9ca3af; font-size: 0.85rem;">{label}</div>
            <div style="color: #f9fafb; font-size: 1.6rem; font-weight: bold;">{value}</div>
            {delta_text}{help_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def cr_i_gauge(cr_i):
    """CR-I gauge (0-100) shown as a colored progress bar."""
    if not st:
        return
    color = "#ef4444" if cr_i < 40 else ("#f59e0b" if cr_i < 70 else "#22c55e")
    st.markdown(
        f"""
        <style>
        .gauge-labels {{ display: flex; justify-content: space-between; color: #9ca3af; font-size: 0.75rem; }}
        .stProgress > div > div > div {{ background-color: {color} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.progress(max(0.0, min(float(cr_i) / 100.0, 1.0)))
    st.markdown('<div class="gauge-labels"><span>0 (High Risk)</span><span>100 (Resilient)</span></div>', unsafe_allow_html=True)


def section_header(title, subtitle=None):
    if not st:
        return
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def inr_indian(value):
    """Format a number as Indian Rupees with lakh/crore grouping (1,23,45,67,890)."""
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
    """Format a number as Indian Rupees with lakh/crore grouping."""
    return inr_indian(value)