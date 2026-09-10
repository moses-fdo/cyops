"""CyberLens 2.0 - Reusable Streamlit widgets."""

try:
    import streamlit as st
except ImportError:
    st = None


def metric_card(label, value, delta=None, help_text=None):
    """Small metric card with optional tooltip."""
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
    st.progress(cr_i / 100.0)
    st.markdown('<div class="gauge-labels"><span>0 (High Risk)</span><span>100 (Resilient)</span></div>', unsafe_allow_html=True)


def section_header(title, subtitle=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def inr_indian(value):
    """Format a number as Indian Rupees with lakh/crore grouping (1,23,45,67,890)."""
    if value is None:
        return "₹0"
    v = int(value)
    if v < 1000:
        return f"₹{v}"
    # Process in groups of 2 from right (Indian numbering system)
    s = str(v)
    # For values < 1 lakh (100,000), format with standard thousands commas
    if v < 100000:
        # Indian format: 12,34,567 = 12 lakh 34 thousand 567
        # Actually for 1k-99k, just use straightforward grouping
        # 25000 -> ₹25,000; 123456 -> ₹1,23,456
        if v < 1000:
            return f"₹{v}"
        # Group by 2 digits from right, but first group can be 1-3 digits
        groups = []
        temp = v
        # First group (leftmost) can be 1-3 digits
        first = temp % 1000 if temp >= 1000 else temp
        temp //= 1000
        groups.insert(0, f"{first:03d}" if first < 100 else f"{first}")
        while temp > 0:
            groups.insert(0, f"{temp % 100:02d}")
            temp //= 100
        # Actually simpler: for < 1 lakh, just standard comma
        s = f"{v:,}"  # western grouping is correct for 1k-99k
        return f"₹{s}"
    # 100,000+ — true Indian grouping
    if v >= 10000000:  # crores
        crore = v // 10000000
        lakh = (v // 100000) % 100
        thousand = (v // 1000) % 100
        units = v % 1000
        return f"₹{crore},{lakh:02d},{thousand:02d},{units:03d}"
    elif v >= 100000:  # lakhs
        lakh = v // 100000
        thousand = (v // 1000) % 100
        units = v % 1000
        return f"₹{lakh},{thousand:02d},{units:03d}"


def inr(value):
    """Format a number as Indian Rupees with lakh/crore grouping."""
    return inr_indian(value)