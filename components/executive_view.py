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
    render_html,
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

    # Scenario indicator - Colorized
    is_demo = len(assets) <= 5
    scenario_html = (
        f'<div style="display:inline-flex;align-items:center;gap:7px;'
        f'background:rgba(56,189,248,0.08);'
        f'border:1px solid rgba(56,189,248,0.25);'
        f'padding:4px 11px;border-radius:4px;font-size:0.75rem;font-weight:600;'
        f'color:#38BDF8;font-family:\'JetBrains Mono\',monospace;">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;"></span>'
        f'{"Demo Scenario Active" if is_demo else "Baseline Portfolio"}</div>'
    )
    section_header(
        "Executive Summary",
        "Reserve Bank of India (RBI) Cyber Risk Quantification & Supervisory Capital Schedule",
        right_html=scenario_html,
    )

    # === KPI ROW ===
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        delta_str = "↑ vs baseline (demo subset)" if is_demo else "Full portfolio assessment"
        metric_card(
            "Total Annual Loss Exposure (EAL)",
            inr(exposure) + " /yr",
            delta=delta_str,
            help_text="Expected Annual Loss across all active banking and UPI infrastructure",
        )
    with kpi2:
        render_cri_gauge(overall_cr_i, target=70)
    with kpi3:
        render_compliance_gauge(comp_pct, target=90)

    # === TOP 3 CYBER RISKS ===
    render_html(
        """
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:0.85rem;margin-bottom:0.35rem;">
            <h2 style="margin:0;color:#F8FAFC;">Top 3 Systemic Risk Concentrations</h2>
            <span style="color:#64748B;font-size:0.725rem;font-family:'JetBrains Mono',monospace;">Highest Expected Annual Loss (₹)</span>
        </div>
        """
    )

    top_risks = sorted(rows, key=lambda r: r["eal_inr"], reverse=True)[:3]
    risk_cols = st.columns(3)
    for idx, (col, r) in enumerate(zip(risk_cols, top_risks), 1):
        with col:
            severity = "CRITICAL" if r["eal_inr"] >= 100_00_000 else ("HIGH" if r["eal_inr"] >= 50_00_000 else "MEDIUM")
            top_border = "#F43F5E" if severity == "CRITICAL" else ("#F59E0B" if severity == "HIGH" else "#38BDF8")
            render_html(
                f"""
                <div class="cl-card" style="height:175px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;border-top:2px solid {top_border};">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                            <span class="cl-mono" style="color:#38BDF8;font-size:0.75rem;font-weight:700;">#{idx:02d}</span>
                            {risk_badge(severity)}
                        </div>
                        <div style="font-weight:600;font-size:0.95rem;color:#F8FAFC;margin-bottom:0.25rem;">{r['asset_name']}</div>
                        <div class="cl-mono" style="font-size:1.35rem;font-weight:700;color:#FFFFFF;margin-bottom:0.35rem;">{inr(r['eal_inr'])} <span style="font-size:0.7rem;font-weight:400;color:#64748B;">/yr</span></div>
                        <div style="display:inline-block;background:#161A24;border:1px solid #232838;color:#CBD5E1;padding:2px 8px;border-radius:3px;font-size:0.7rem;font-weight:500;">{r['category']}</div>
                    </div>
                    <div class="cl-mono" style="font-size:0.675rem;color:#64748B;border-top:1px solid #1E2333;padding-top:0.45rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        Mandate: <span style="color:#94A3B8;">{r['rbi_clause']}</span>
                    </div>
                </div>
                """
            )
            if st.button("Inspect Asset →", key=f"tr_{idx}_{r['asset_id']}", width="stretch"):
                session["current_view"] = "Technical View"
                session["selected_asset"] = r["asset_name"]
                st.rerun()

    # === BUDGET + INVESTMENT PLAN ===
    render_html('<div style="border-top:1px solid #1E2333;margin-top:1rem;padding-top:0.85rem;"></div>')
    budget_col, plan_col = st.columns([1, 1.45])

    with budget_col:
        render_html(
            """
            <h2 style="margin:0;color:#F8FAFC;">Capital Allocation Parameter</h2>
            <div style="color:#94A3B8;font-size:0.75rem;margin-bottom:0.5rem;">Allocate defensive cybersecurity budget to minimize net portfolio liability</div>
            """
        )

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

        render_html(
            f"""
            <div class="cl-card" style="padding:0.85rem 1.15rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;border-left:3px solid #38BDF8;">
                <div style="font-size:0.75rem;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Allocated CapEx</div>
                <div class="cl-mono" style="font-size:1.35rem;font-weight:700;color:#38BDF8;">₹{budget_crores:.1f} Crore</div>
            </div>
            """
        )
        show_plan = st.button("Generate Allocation Schedule →", type="primary", key="show_plan_btn", width="stretch")
        if "show_plan_clicked" not in session:
            session["show_plan_clicked"] = True
        if show_plan:
            session["show_plan_clicked"] = True

    with plan_col:
        if session.get("show_plan_clicked"):
            render_html(
                """
                <h2 style="margin:0;color:#F8FAFC;">Optimal Security Investment Schedule</h2>
                <div style="color:#94A3B8;font-size:0.75rem;margin-bottom:0.5rem;">Knapsack ROSI-optimized controls minimizing aggregate expected loss</div>
                """
            )

            enriched = enrich_controls_with_reduction(session["controls"], assets, vulns_by_asset)
            plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

            if plan["controls"]:
                table_html = '<table style="width:100%;border-collapse:collapse;font-size:0.8rem;">'
                table_html += '<tr style="border-bottom:1px solid #1E2333;color:#64748B;font-weight:600;text-transform:uppercase;font-size:0.65rem;letter-spacing:0.06em;">'
                table_html += '<td style="padding:8px 10px;">Security Control Intervention</td><td style="padding:8px 10px;text-align:right;">CapEx (₹)</td><td style="padding:8px 10px;text-align:right;">Annual Risk Reduction (₹/yr)</td><td style="padding:8px 10px;text-align:right;">ROSI</td></tr>'

                for c in sorted(plan["controls"], key=lambda x: x["cost_inr"], reverse=True):
                    cost = c["cost_inr"]
                    red = c.get("risk_reduction_inr", 0.0)
                    rosi = ((red - cost) / cost * 100) if cost > 0 else 0.0
                    table_html += f'<tr style="border-bottom:1px solid #161924;color:#CBD5E1;">'
                    table_html += f'<td style="padding:7px 10px;color:#F8FAFC;font-weight:500;">{c["name"]}</td>'
                    table_html += f'<td class="cl-mono" style="padding:7px 10px;text-align:right;color:#94A3B8;">{inr(cost)}</td>'
                    table_html += f'<td class="cl-mono" style="padding:7px 10px;text-align:right;color:#F8FAFC;font-weight:600;">{inr(red)}</td>'
                    table_html += f'<td style="padding:7px 10px;text-align:right;"><span class="cl-mono" style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);color:#34D399;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.7rem;">+{rosi:.0f}%</span></td></tr>'

                total_cost = plan["total_cost"]
                total_red = plan["total_reduction"]
                overall_rosi = ((total_red - total_cost) / total_cost * 100) if total_cost > 0 else 0.0

                table_html += f'<tr style="border-top:1px solid #1E2333;color:#FFFFFF;font-weight:700;background:#161924;">'
                table_html += f'<td style="padding:9px 10px;">Total Allocated Portfolio</td>'
                table_html += f'<td class="cl-mono" style="padding:9px 10px;text-align:right;color:#38BDF8;">{inr(total_cost)}</td>'
                table_html += f'<td class="cl-mono" style="padding:9px 10px;text-align:right;color:#34D399;">{inr(total_red)}</td>'
                table_html += f'<td style="padding:9px 10px;text-align:right;"><span class="cl-mono" style="background:#10B981;color:#041F16;border:1px solid #10B981;font-weight:800;padding:2px 8px;border-radius:4px;font-size:0.725rem;">+{overall_rosi:.0f}%</span></td></tr>'
                table_html += '</table>'

                render_html(f'<div class="cl-card" style="padding:0.5rem 0.85rem;">{table_html}</div>')

                remaining = plan["remaining_budget"]
                render_html(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.45rem;font-size:0.75rem;color:#64748B;font-family:\'JetBrains Mono\',monospace;">'
                    f'<span>Surplus Budget: <strong style="color:#38BDF8;">{inr(remaining)}</strong></span>'
                    f'<span>Interventions Funded: <strong style="color:#34D399;">{len(plan["controls"])}</strong></span>'
                    f'</div>'
                )
            else:
                st.info("No controls fit within the selected budget. Increase the slider.")

    # === IMPACT VISUALIZATION ===
    if session.get("show_plan_clicked"):
        enriched = enrich_controls_with_reduction(session["controls"], assets, vulns_by_asset)
        plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

        if plan["controls"]:
            render_html('<div style="border-top:1px solid #1E2333;margin-top:1rem;padding-top:0.85rem;"></div>')
            render_html(
                """
                <h2 style="margin:0;color:#F8FAFC;">Net Risk Reduction Projection</h2>
                <div style="color:#94A3B8;font-size:0.75rem;margin-bottom:0.4rem;">Comparative loss profile before and after implementing recommended controls</div>
                """
            )

            total_red = plan["total_reduction"]
            viz1, viz2 = st.columns(2)

            with viz1:
                post_exposure = max(0.0, exposure - total_red)
                pct_reduction = (total_red / exposure * 100) if exposure > 0 else 0.0

                chart_df = pd.DataFrame([
                    {"State": "Current Exposure", "Exposure": round(exposure / 1_00_00_000, 2)},
                    {"State": "Mitigated Exposure", "Exposure": round(post_exposure / 1_00_00_000, 2)},
                ])

                bar_chart = alt.Chart(chart_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=55).encode(
                    x=alt.X("State:N", sort=None, axis=alt.Axis(labelAngle=0, title=None, labelColor="#94A3B8", labelFont="Plus Jakarta Sans", labelFontSize=11, tickColor="#1E2333")),
                    y=alt.Y("Exposure:Q", title="₹ Crore", axis=alt.Axis(labelColor="#64748B", titleColor="#64748B", gridColor="#161924", tickColor="#1E2333")),
                    color=alt.Color("State:N", scale=alt.Scale(domain=["Current Exposure", "Mitigated Exposure"], range=["#F43F5E", "#10B981"]), legend=None),
                ).properties(height=180, background="#10131B").configure_view(strokeWidth=0)

                st.altair_chart(bar_chart, width="stretch")
                render_html(
                    f'<div style="text-align:center;background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.30);color:#34D399;padding:6px 12px;border-radius:4px;font-weight:600;font-size:0.8rem;font-family:\'JetBrains Mono\',monospace;">'
                    f'↓ {pct_reduction:.1f}% Liability Reduction · <span class="cl-mono">{inr(total_red)}</span>/yr Averted</div>'
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

                donut = alt.Chart(pie_data).mark_arc(innerRadius=46, outerRadius=74).encode(
                    theta=alt.Theta("Reduction:Q"),
                    color=alt.Color("Category:N", scale=alt.Scale(range=["#38BDF8", "#818CF8", "#F43F5E", "#FB923C", "#10B981", "#A78BFA"]), legend=alt.Legend(orient="bottom", labelColor="#94A3B8", titleColor="#64748B", labelFont="Plus Jakarta Sans", labelFontSize=10)),
                    tooltip=["Category", "Reduction"]
                ).properties(height=180, background="#10131B").configure_view(strokeWidth=0)

                st.altair_chart(donut, width="stretch")