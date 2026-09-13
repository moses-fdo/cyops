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
import data_loader
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

    theme = session.get("theme", "dark") or "dark"
    is_light = theme == "light"
    chart = {
        "bg": "#FFFFFF" if is_light else "#10131B",
        "axis": "#64748B" if is_light else "#94A3B8",
        "title": "#94A3B8" if is_light else "#64748B",
        "grid": "#E2E8F0" if is_light else "#161924",
        "tick": "#CBD5E1" if is_light else "#1E2333",
    }

    # Scenario indicator - Colorized
    is_demo = len(assets) <= 5
    scenario_html = (
        f'<div style="display:inline-flex;align-items:center;gap:7px;'
        f'background:rgba(56,189,248,0.08);'
        f'border:1px solid rgba(56,189,248,0.25);'
        f'padding:4px 11px;border-radius:4px;font-size:0.75rem;font-weight:600;'
        f'color:var(--cl-accent-strong);font-family:\'JetBrains Mono\',monospace;">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;"></span>'
        f'{"Demo Scenario Active" if is_demo else "Baseline Portfolio"}</div>'
    )
    section_header(
        "Executive Summary",
        "Reserve Bank of India (RBI) Cyber Risk Quantification & Supervisory Capital Schedule",
        right_html=scenario_html,
    )

    # === MACRO TELEMETRY STATS RIBBON ===
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    total_txns = sum(a.get("daily_transaction_volume", 0) for a in assets)
    max_downtime = max((a.get("downtime_cost_per_hour", 0) for a in assets), default=0)
    total_vulns = sum(len(v) for v in vulns_by_asset.values())

    with r_col1:
        render_html(
            f"""
            <div class="cl-card" style="padding:0.65rem 0.95rem;display:flex;align-items:center;gap:10px;border-left:3px solid var(--cl-accent-strong);">
                <div style="font-size:1.15rem;">🏛️</div>
                <div>
                    <div style="color:var(--cl-faint);font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Assessed Systems</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:1px;">{len(assets)} <span style="font-size:0.7rem;font-weight:400;color:var(--cl-faint);">Nodes</span></div>
                </div>
            </div>
            """
        )
    with r_col2:
        render_html(
            f"""
            <div class="cl-card" style="padding:0.65rem 0.95rem;display:flex;align-items:center;gap:10px;border-left:3px solid #10B981;">
                <div style="font-size:1.15rem;">⚡</div>
                <div>
                    <div style="color:var(--cl-faint);font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Daily Txns Covered</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:1px;">{total_txns/1_000_000:.1f}M <span style="font-size:0.7rem;font-weight:400;color:var(--cl-faint);">txns/day</span></div>
                </div>
            </div>
            """
        )
    with r_col3:
        render_html(
            f"""
            <div class="cl-card" style="padding:0.65rem 0.95rem;display:flex;align-items:center;gap:10px;border-left:3px solid #F43F5E;">
                <div style="font-size:1.15rem;">⏱️</div>
                <div>
                    <div style="color:var(--cl-faint);font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Max Outage Liability</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:1px;">{inr(max_downtime)} <span style="font-size:0.7rem;font-weight:400;color:var(--cl-faint);">/hr</span></div>
                </div>
            </div>
            """
        )
    with r_col4:
        render_html(
            f"""
            <div class="cl-card" style="padding:0.65rem 0.95rem;display:flex;align-items:center;gap:10px;border-left:3px solid #F59E0B;">
                <div style="font-size:1.15rem;">🔍</div>
                <div>
                    <div style="color:var(--cl-faint);font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Quantified CVEs</div>
                    <div class="cl-mono" style="font-size:1.05rem;font-weight:700;color:var(--cl-text);margin-top:1px;">{total_vulns} <span style="font-size:0.7rem;font-weight:400;color:var(--cl-faint);">Active</span></div>
                </div>
            </div>
            """
        )

    render_html('<div style="margin-top:0.65rem;"></div>')

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
            <h2 style="margin:0;color:var(--cl-text);">Top 3 Systemic Risk Concentrations</h2>
            <span style="color:var(--cl-faint);font-size:0.725rem;font-family:'JetBrains Mono',monospace;">Highest Expected Annual Loss (₹)</span>
        </div>
        """
    )

    top_risks = sorted(rows, key=lambda r: r["eal_inr"], reverse=True)[:3]
    risk_cols = st.columns(3)
    for idx, (col, r) in enumerate(zip(risk_cols, top_risks), 1):
        with col:
            severity = "CRITICAL" if r["eal_inr"] >= 100_00_000 else ("HIGH" if r["eal_inr"] >= 50_00_000 else "MEDIUM")
            top_border = "#F43F5E" if severity == "CRITICAL" else ("#F59E0B" if severity == "HIGH" else "var(--cl-accent-strong)")
            render_html(
                f"""
                <div class="cl-card" style="min-height:195px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:1.1rem 1.25rem;margin-bottom:0.45rem;border-top:2px solid {top_border};">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                            <span class="cl-mono" style="color:var(--cl-accent-strong);font-size:0.75rem;font-weight:700;">#{idx:02d}</span>
                            {risk_badge(severity)}
                        </div>
                        <div style="font-weight:600;font-size:0.95rem;color:var(--cl-text);margin-bottom:0.25rem;">{r['asset_name']}</div>
                        <div class="cl-mono" style="font-size:1.35rem;font-weight:700;color:var(--cl-text);margin-bottom:0.35rem;">{inr(r['eal_inr'])} <span style="font-size:0.7rem;font-weight:400;color:var(--cl-faint);">/yr</span></div>
                        <div style="display:inline-block;background:var(--cl-hover);border:1px solid var(--cl-border-3);color:var(--cl-text-4);padding:2px 8px;border-radius:3px;font-size:0.7rem;font-weight:500;">{r['category']}</div>
                    </div>
                    <div class="cl-mono" style="font-size:0.725rem;color:var(--cl-faint);border-top:1px solid var(--cl-border);padding-top:0.5rem;margin-top:0.5rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        Mandate: <span style="color:var(--cl-muted);font-weight:500;">{r['rbi_clause']}</span>
                    </div>
                </div>
                """
            )
            if st.button("Inspect Asset →", key=f"tr_{idx}_{r['asset_id']}", width="stretch"):
                session["current_view"] = "Technical View"
                session["selected_asset"] = r["asset_name"]
                st.rerun()

    # === BUDGET + INVESTMENT PLAN ===
    render_html('<div style="border-top:1px solid var(--cl-border);margin-top:1rem;padding-top:0.85rem;"></div>')
    budget_col, plan_col = st.columns([1, 1.45])

    with budget_col:
        render_html(
            """
            <h2 style="margin:0;color:var(--cl-text);">Capital Allocation Parameter</h2>
            <div style="color:var(--cl-muted);font-size:0.75rem;margin-bottom:0.5rem;">Allocate defensive cybersecurity budget to minimize net portfolio liability</div>
            """
        )

        # Quick budget presets
        p_c1, p_c2, p_c3, p_c4 = st.columns(4)
        with p_c1:
            if st.button("₹50L", key="preset_50l", help="Set budget to ₹0.5 Crore"):
                session["budget_crores"] = 0.5
                st.rerun()
        with p_c2:
            if st.button("₹1.0 Cr", key="preset_1cr", help="Set budget to ₹1.0 Crore"):
                session["budget_crores"] = 1.0
                st.rerun()
        with p_c3:
            if st.button("₹2.5 Cr", key="preset_25cr", help="Set budget to ₹2.5 Crore"):
                session["budget_crores"] = 2.5
                st.rerun()
        with p_c4:
            if st.button("₹5.0 Cr", key="preset_5cr", help="Set budget to ₹5.0 Crore"):
                session["budget_crores"] = 5.0
                st.rerun()

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
            <div class="cl-card" style="padding:0.85rem 1.15rem;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;border-left:3px solid var(--cl-accent-strong);">
                <div style="font-size:0.75rem;color:var(--cl-faint);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">Allocated CapEx</div>
                <div class="cl-mono" style="font-size:1.35rem;font-weight:700;color:var(--cl-accent-strong);">₹{budget_crores:.1f} Crore</div>
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
                <h2 style="margin:0;color:var(--cl-text);">Optimal Security Investment Schedule</h2>
                <div style="color:var(--cl-muted);font-size:0.75rem;margin-bottom:0.5rem;">Knapsack ROSI-optimized controls minimizing aggregate expected loss</div>
                """
            )

            enriched = enrich_controls_with_reduction(session["controls"], assets, vulns_by_asset)
            plan = optimize_budget(enriched, budget_inr, assets, vulns_by_asset)

            if plan["controls"]:
                table_html = '<table style="width:100%;border-collapse:collapse;font-size:0.8rem;">'
                table_html += '<tr style="border-bottom:1px solid var(--cl-border);color:var(--cl-faint);font-weight:600;text-transform:uppercase;font-size:0.65rem;letter-spacing:0.06em;">'
                table_html += '<td style="padding:8px 10px;">Security Control Intervention</td><td style="padding:8px 10px;text-align:right;">CapEx (₹)</td><td style="padding:8px 10px;text-align:right;">Annual Risk Reduction (₹/yr)</td><td style="padding:8px 10px;text-align:right;">ROSI</td></tr>'

                for c in sorted(plan["controls"], key=lambda x: x["cost_inr"], reverse=True):
                    cost = c["cost_inr"]
                    red = c.get("risk_reduction_inr", 0.0)
                    rosi = ((red - cost) / cost * 100) if cost > 0 else 0.0
                    table_html += f'<tr style="border-bottom:1px solid var(--cl-hover);color:var(--cl-text-4);">'
                    table_html += f'<td style="padding:7px 10px;color:var(--cl-text);font-weight:500;">{c["name"]}</td>'
                    table_html += f'<td class="cl-mono" style="padding:7px 10px;text-align:right;color:var(--cl-muted);">{inr(cost)}</td>'
                    table_html += f'<td class="cl-mono" style="padding:7px 10px;text-align:right;color:var(--cl-text);font-weight:600;">{inr(red)}</td>'
                    table_html += f'<td style="padding:7px 10px;text-align:right;"><span class="cl-mono" style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);color:#34D399;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.7rem;">+{rosi:.0f}%</span></td></tr>'

                total_cost = plan["total_cost"]
                total_red = plan["total_reduction"]
                overall_rosi = ((total_red - total_cost) / total_cost * 100) if total_cost > 0 else 0.0

                table_html += f'<tr style="border-top:1px solid var(--cl-border);color:var(--cl-text);font-weight:700;background:var(--cl-hover);">'
                table_html += f'<td style="padding:9px 10px;">Total Allocated Portfolio</td>'
                table_html += f'<td class="cl-mono" style="padding:9px 10px;text-align:right;color:var(--cl-accent-strong);">{inr(total_cost)}</td>'
                table_html += f'<td class="cl-mono" style="padding:9px 10px;text-align:right;color:#34D399;">{inr(total_red)}</td>'
                table_html += f'<td style="padding:9px 10px;text-align:right;"><span class="cl-mono" style="background:#10B981;color:#041F16;border:1px solid #10B981;font-weight:800;padding:2px 8px;border-radius:4px;font-size:0.725rem;">+{overall_rosi:.0f}%</span></td></tr>'
                table_html += '</table>'

                render_html(f'<div class="cl-card" style="padding:0.5rem 0.85rem;">{table_html}</div>')

                remaining = plan["remaining_budget"]
                render_html(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.45rem;font-size:0.75rem;color:var(--cl-faint);font-family:\'JetBrains Mono\',monospace;">'
                    f'<span>Surplus Budget: <strong style="color:var(--cl-accent-strong);">{inr(remaining)}</strong></span>'
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
            render_html('<div style="border-top:1px solid var(--cl-border);margin-top:1rem;padding-top:0.85rem;"></div>')
            render_html(
                """
                <h2 style="margin:0;color:var(--cl-text);">Net Risk Reduction Projection</h2>
                <div style="color:var(--cl-muted);font-size:0.75rem;margin-bottom:0.4rem;">Comparative loss profile before and after implementing recommended controls</div>
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

                bar_chart = (
                    alt.Chart(chart_df)
                    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=80)
                    .encode(
                        x=alt.X(
                            "State:N",
                            sort=None,
                            axis=alt.Axis(
                                labelAngle=0,
                                title=None,
                                labelColor=chart["axis"],
                                labelFont="Plus Jakarta Sans",
                                labelFontSize=12,
                                labelFontWeight="bold",
                                tickColor=chart["tick"],
                                labelPadding=10,
                            ),
                        ),
                        y=alt.Y(
                            "Exposure:Q",
                            title="Exposure (₹ Cr)",
                            axis=alt.Axis(
                                labelColor=chart["axis"],
                                titleColor=chart["title"],
                                gridColor=chart["grid"],
                                tickColor=chart["tick"],
                                labelFont="JetBrains Mono",
                                labelFontSize=11,
                                titleFont="Plus Jakarta Sans",
                                titleFontSize=12,
                                titleFontWeight="bold",
                                titlePadding=12,
                            ),
                        ),
                        color=alt.Color(
                            "State:N",
                            scale=alt.Scale(
                                domain=["Current Exposure", "Mitigated Exposure"],
                                range=["#F43F5E", "#10B981"],
                            ),
                            legend=None,
                        ),
                        tooltip=[
                            alt.Tooltip("State:N", title="Scenario State"),
                            alt.Tooltip("Exposure:Q", title="Exposure (₹ Cr)"),
                        ],
                    )
                    .properties(height=320, background=chart["bg"])
                    .configure_view(strokeWidth=0)
                )

                render_html('<div class="cl-card" style="padding:1.1rem 1.25rem;">')
                st.altair_chart(bar_chart, width="stretch")
                render_html(
                    f'<div style="text-align:center;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);color:#34D399;padding:9px 16px;border-radius:6px;font-weight:700;font-size:0.875rem;font-family:\'JetBrains Mono\',monospace;margin-top:10px;">'
                    f'↓ {pct_reduction:.1f}% Liability Reduction · <span class="cl-mono">{inr(total_red)}</span>/yr Averted</div>'
                    f'</div>'
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

                donut = (
                    alt.Chart(pie_data)
                    .mark_arc(innerRadius=65, outerRadius=115)
                    .encode(
                        theta=alt.Theta("Reduction:Q"),
                        color=alt.Color(
                            "Category:N",
                            scale=alt.Scale(
                                range=[
                                    "#0284C7",
                                    "#6366F1",
                                    "#F43F5E",
                                    "#F59E0B",
                                    "#10B981",
                                    "#8B5CF6",
                                    "#06B6D4",
                                    "#EC4899",
                                ]
                            ),
                            legend=alt.Legend(
                                orient="right",
                                labelColor=chart["axis"],
                                titleColor=chart["title"],
                                labelFont="Plus Jakarta Sans",
                                labelFontSize=12,
                                titleFont="Plus Jakarta Sans",
                                titleFontSize=13,
                                titleFontWeight="bold",
                                symbolSize=120,
                                labelLimit=220,
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("Category:N", title="Vulnerability Category"),
                            alt.Tooltip("Reduction:Q", title="Reduction (₹ Cr)"),
                        ],
                    )
                    .properties(height=320, background=chart["bg"])
                    .configure_view(strokeWidth=0)
                )

                render_html('<div class="cl-card" style="padding:1.1rem 1.25rem;">')
                st.altair_chart(donut, width="stretch")
                render_html(
                    f'<div style="text-align:center;background:rgba(56,189,248,0.10);border:1px solid rgba(56,189,248,0.30);color:var(--cl-accent-strong);padding:9px 16px;border-radius:6px;font-weight:700;font-size:0.875rem;font-family:\'JetBrains Mono\',monospace;margin-top:10px;">'
                    f'ROSI Risk Mitigation Category Distribution</div>'
                    f'</div>'
                )