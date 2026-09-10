"""CyberLens 2.0 - Executive View (Dark Banking Dashboard).
High-level cyber risk overview with financial impact and investment recommendations.
"""

import streamlit as st
import pandas as pd
import altair as alt

from risk_engine import (
    compute_overall_cr_i,
    optimize_budget,
    enrich_controls_with_reduction,
    total_exposure,
)
from components.widgets import (
    section_header,
    metric_card,
    render_cri_gauge,
    render_compliance_gauge,
    inr,
    risk_badge,
)


def compliance_pct(rows):
    """Share of vuln-rows that map to a known RBI clause."""
    if not rows:
        return 100.0
    mapped = sum(1 for r in rows if r.get("rbi_clause") and r["rbi_clause"] != "Unmapped")
    return round(mapped / len(rows) * 100, 1)


def render(session):
    rows = session.get("risk_matrix", [])
    assets = session.get("assets", [])
    vulns_by_asset = session.get("vulns_by_asset", {})

    overall_cr_i = compute_overall_cr_i(assets, vulns_by_asset)
    exposure = total_exposure(assets, vulns_by_asset)
    comp_pct = compliance_pct(rows)

    # Scenario indicator
    is_demo = len(assets) <= 5
    scenario_html = f'<span style="color:{"#35D39A" if is_demo else "#718096"};font-size:0.8rem;font-weight:500;">● {"Demo Scenario Active" if is_demo else "Baseline Portfolio"}</span>'
    section_header(
        "Executive View",
        "High-level cyber risk overview with financial impact and investment recommendations.",
        right_html=scenario_html,
    )

    # === KPI ROW ===
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        delta_str = "↑ vs baseline (demo subset)" if is_demo else "Full portfolio assessment"
        metric_card(
            "Total Annual Cyber Risk Exposure",
            inr(exposure) + " /yr",
            delta=delta_str,
            help_text="Expected Annual Loss across all active assets",
        )
    with kpi2:
        render_cri_gauge(overall_cr_i, target=70)
    with kpi3:
        render_compliance_gauge(comp_pct, target=90)

    # === TOP 3 CYBER RISKS ===
    st.markdown(
        """<div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:0.5rem;">
            <h2 style="margin:0;color:#F5F7FA;">Top 3 Cyber Risks</h2>
            <span style="color:#718096;font-size:0.75rem;">Highest financial impact</span>
        </div>""",
        unsafe_allow_html=True,
    )

    top_risks = sorted(rows, key=lambda r: r["eal_inr"], reverse=True)[:3]
    risk_cols = st.columns(3)
    for idx, (col, r) in enumerate(zip(risk_cols, top_risks), 1):
        with col:
            severity = "CRITICAL" if r["eal_inr"] >= 100_00_000 else ("HIGH" if r["eal_inr"] >= 50_00_000 else "MEDIUM")
            st.markdown(
                f"""
                <div class="cl-card" style="height:165px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:0.85rem 1rem;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                            <span style="background:#1683FF;color:#fff;font-weight:700;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:0.75rem;">{idx}</span>
                            {risk_badge(severity)}
                        </div>
                        <div style="font-weight:600;font-size:0.9rem;color:#F5F7FA;margin-bottom:0.2rem;">{r['asset_name']}</div>
                        <div style="font-size:1.2rem;font-weight:700;color:#F5F7FA;margin-bottom:0.25rem;">{inr(r['eal_inr'])} <span style="font-size:0.7rem;font-weight:400;color:#718096;">/year</span></div>
                        <div style="font-size:0.775rem;color:#AAB4C3;margin-bottom:0.15rem;">{r['category']}</div>
                    </div>
                    <div style="font-size:0.725rem;color:#718096;border-top:1px solid #263241;padding-top:0.35rem;">{r['rbi_clause']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View Details →", key=f"tr_{idx}_{r['asset_id']}"):
                session["current_view"] = "Technical View"
                session["selected_asset"] = r["asset_name"]
                st.rerun()

    # === BUDGET + INVESTMENT PLAN (SIDE BY SIDE) ===
    st.markdown('<div style="border-top:1px solid #263241;margin-top:0.5rem;padding-top:0.5rem;"></div>', unsafe_allow_html=True)
    budget_col, plan_col = st.columns([1, 1.4])

    with budget_col:
        st.markdown('<h2 style="margin:0;color:#F5F7FA;">Budget Allocator</h2><div style="color:#718096;font-size:0.75rem;margin-bottom:0.4rem;">Set your available budget for security controls</div>', unsafe_allow_html=True)

        budget_crores = st.slider(
            "Budget (₹ Crore)",
            min_value=0.0,
            max_value=10.0,
            value=float(session.get("budget_crores", 1.0)),
            step=0.1,
            format="₹%.1f Cr",
            key="budget_slider",
        )
        session["budget_crores"] = budget_crores
        budget_inr = budget_crores * 1_00_00_000

        st.markdown(
            f"""<div class="cl-card" style="text-align:center;padding:0.6rem;">
                <div style="font-size:0.65rem;color:#718096;text-transform:uppercase;font-weight:600;">Selected Budget</div>
                <div style="font-size:1.2rem;font-weight:700;color:#1683FF;margin-top:0.15rem;">₹{budget_crores:.1f} Crore</div>
            </div>""",
            unsafe_allow_html=True,
        )
        show_plan = st.button("Show Optimal Investment Plan →", type="primary", key="show_plan_btn")
        if "show_plan_clicked" not in session:
            session["show_plan_clicked"] = True
        if show_plan:
            session["show_plan_clicked"] = True

    with plan_col:
        if session.get("show_plan_clicked"):
            st.markdown('<h2 style="margin:0;color:#F5F7FA;">Optimal Investment Plan</h2><div style="color:#718096;font-size:0.75rem;margin-bottom:0.4rem;">Maximum risk reduction per rupee</div>', unsafe_allow_html=True)

            enriched = enrich_controls_with_reduction(session["controls"], assets, vulns_by_asset)
            plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

            if plan["controls"]:
                # Build HTML table for compact dark display
                table_html = '<table style="width:100%;border-collapse:collapse;font-size:0.8rem;">'
                table_html += '<tr style="border-bottom:1px solid #263241;color:#718096;font-weight:600;text-transform:uppercase;font-size:0.65rem;letter-spacing:0.05em;">'
                table_html += '<td style="padding:6px 8px;">Control</td><td style="padding:6px 8px;text-align:right;">Cost (₹)</td><td style="padding:6px 8px;text-align:right;">Reduction (₹/yr)</td><td style="padding:6px 8px;text-align:right;">ROSI</td></tr>'

                for c in sorted(plan["controls"], key=lambda x: x["cost_inr"], reverse=True):
                    cost = c["cost_inr"]
                    red = c.get("risk_reduction_inr", 0.0)
                    rosi = ((red - cost) / cost * 100) if cost > 0 else 0.0
                    rosi_color = "#35D39A" if rosi > 0 else "#FF4D5A"
                    table_html += f'<tr style="border-bottom:1px solid #1A2431;color:#AAB4C3;">'
                    table_html += f'<td style="padding:5px 8px;color:#F5F7FA;font-weight:500;">{c["name"]}</td>'
                    table_html += f'<td style="padding:5px 8px;text-align:right;">{inr(cost)}</td>'
                    table_html += f'<td style="padding:5px 8px;text-align:right;">{inr(red)}</td>'
                    table_html += f'<td style="padding:5px 8px;text-align:right;color:{rosi_color};font-weight:600;">{rosi:.0f}%</td></tr>'

                total_cost = plan["total_cost"]
                total_red = plan["total_reduction"]
                overall_rosi = ((total_red - total_cost) / total_cost * 100) if total_cost > 0 else 0.0

                table_html += f'<tr style="border-top:2px solid #263241;color:#F5F7FA;font-weight:700;">'
                table_html += f'<td style="padding:6px 8px;">Total</td>'
                table_html += f'<td style="padding:6px 8px;text-align:right;">{inr(total_cost)}</td>'
                table_html += f'<td style="padding:6px 8px;text-align:right;">{inr(total_red)}</td>'
                table_html += f'<td style="padding:6px 8px;text-align:right;color:#35D39A;">{overall_rosi:.0f}%</td></tr>'
                table_html += '</table>'

                st.markdown(f'<div class="cl-card" style="padding:0.5rem 0.75rem;">{table_html}</div>', unsafe_allow_html=True)

                remaining = plan["remaining_budget"]
                st.markdown(
                    f'<div style="display:flex;gap:1rem;margin-top:0.35rem;font-size:0.725rem;color:#718096;">'
                    f'<span>Remaining: <strong style="color:#AAB4C3;">{inr(remaining)}</strong></span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("No controls fit within the selected budget. Increase the slider.")

    # === IMPACT VISUALIZATION (SIDE BY SIDE) ===
    if session.get("show_plan_clicked"):
        enriched = enrich_controls_with_reduction(session["controls"], assets, vulns_by_asset)
        plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

        if plan["controls"]:
            st.markdown('<div style="border-top:1px solid #263241;margin-top:0.5rem;padding-top:0.5rem;"></div>', unsafe_allow_html=True)
            st.markdown('<h2 style="margin:0;color:#F5F7FA;">Projected Risk Reduction</h2><div style="color:#718096;font-size:0.75rem;margin-bottom:0.25rem;">Before and after implementing recommended controls</div>', unsafe_allow_html=True)

            total_red = plan["total_reduction"]
            viz1, viz2 = st.columns(2)

            with viz1:
                post_exposure = max(0.0, exposure - total_red)
                pct_reduction = (total_red / exposure * 100) if exposure > 0 else 0.0

                chart_df = pd.DataFrame([
                    {"State": "Before", "Exposure": round(exposure / 1_00_00_000, 2)},
                    {"State": "After", "Exposure": round(post_exposure / 1_00_00_000, 2)},
                ])

                bar_chart = alt.Chart(chart_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=50).encode(
                    x=alt.X("State:N", sort=None, axis=alt.Axis(labelAngle=0, title=None, labelColor="#71869A", tickColor="#213447")),
                    y=alt.Y("Exposure:Q", title="₹ Crore", axis=alt.Axis(labelColor="#71869A", titleColor="#71869A", gridColor="#142333", tickColor="#213447")),
                    color=alt.Color("State:N", scale=alt.Scale(domain=["Before", "After"], range=["#FF4D5A", "#168BFF"]), legend=None),
                ).properties(height=180, background="#101B27").configure_view(strokeWidth=0)

                st.altair_chart(bar_chart, width="stretch")
                st.markdown(
                    f'<div style="text-align:center;background:rgba(50,214,160,0.1);color:#32D6A0;padding:5px 10px;border-radius:4px;font-weight:600;font-size:0.8rem;">↓ {pct_reduction:.1f}% · {inr(total_red)}/yr reduction</div>',
                    unsafe_allow_html=True,
                )

            with viz2:
                cat_dict = {}
                for c in plan["controls"]:
                    for cat in c["affected_categories"]:
                        cat_dict[cat] = cat_dict.get(cat, 0.0) + c.get("risk_reduction_inr", 0.0)
                if not cat_dict:
                    cat_dict = {"Controls": total_red}

                pie_data = pd.DataFrame([
                    {"Category": k, "Reduction": round(v / 1_00_00_000, 2)}
                    for k, v in cat_dict.items()
                ])

                donut = alt.Chart(pie_data).mark_arc(innerRadius=45, outerRadius=70).encode(
                    theta=alt.Theta("Reduction:Q"),
                    color=alt.Color("Category:N", scale=alt.Scale(range=["#168BFF", "#329CFF", "#71869A", "#32D6A0", "#AAB8C8"]), legend=alt.Legend(orient="bottom", labelColor="#AAB8C8", titleColor="#71869A")),
                    tooltip=["Category", "Reduction"]
                ).properties(height=180, background="#101B27").configure_view(strokeWidth=0)

                st.altair_chart(donut, width="stretch")