"""CyberLens 2.0 - SIH-specific features: demo scenario loader and summary generator.

Dataset-agnostic: the demo scenario is built dynamically from whichever
dataset is loaded (original UPI/CBS dataset or the SWIFT/IMPS/FOREX testing
dataset), so counts and asset picks are always correct.
"""

import datetime
import time
import streamlit as st

from risk_engine import total_exposure, compute_overall_cr_i, expected_annual_loss


def _top_risk_assets(assets, vulns_by_asset, n=5):
    """Return the assets with the highest Expected Annual Loss, desc order."""
    scored = sorted(
        (
            {
                **a,
                "_eal": sum(
                    expected_annual_loss(v, a) for v in vulns_by_asset.get(a["asset_id"], [])
                ),
            }
            for a in assets
        ),
        key=lambda a: a["_eal"],
        reverse=True,
    )
    return scored[:n]


def load_demo_scenario(session):
    """Filter the session to a high-risk subset of dynamic assets + their top vulns.

    Picks the `n` highest-EAL assets in the loaded dataset and, for each,
    keeps its highest-severity vulnerability (falling back to all if fewer).
    Uses the server-side copy of the full dataset so the demo always targets
    real asset IDs in the current CSV.
    """
    # Audit: log scenario load action
    audit = session.get("audit_log", [])
    audit.append({"action": "load_demo_scenario", "timestamp": time.time()})
    session["audit_log"] = audit[:1000]

    import data_loader
    all_assets = data_loader.get_assets()
    all_vulns = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in all_assets}

    top = _top_risk_assets(all_assets, all_vulns, n=5)
    selected_vulns = {}
    for a in top:
        candidate_vulns = all_vulns.get(a["asset_id"], [])
        # Highest-severity mapped vulnerabilities (top 2 by CVSS)
        kept = sorted(candidate_vulns, key=lambda v: v["cvss_base_score"], reverse=True)[:2]
        if kept:
            selected_vulns[a["asset_id"]] = kept

    session["vulns_by_asset"] = selected_vulns
    session["assets"] = [a for a in all_assets if a["asset_id"] in selected_vulns]

    # Trigger risk matrix recompute
    from risk_engine import compute_risk_matrix
    session["risk_matrix"] = compute_risk_matrix(
        session["assets"], session["vulns_by_asset"]
    )

    n_assets = len(session["assets"])
    n_vulns = sum(len(v) for v in session["vulns_by_asset"].values())
    st.success(
        f"Loaded Demo Scenario — high-risk subset: {n_assets} assets, "
        f"{n_vulns} vulnerabilities. "
        f"Target: {', '.join(a['name'] for a in session['assets'])}."
    )


def reset_full_portfolio(session):
    """Restore the full dataset from data_loader."""
    import data_loader
    from risk_engine import compute_risk_matrix
    from controls_library import CONTROLS
    assets = data_loader.get_assets()
    vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in assets}
    risk_matrix = compute_risk_matrix(assets, vulns_by_asset)
    session["assets"] = assets
    session["vulns_by_asset"] = vulns_by_asset
    session["risk_matrix"] = risk_matrix
    session["controls"] = list(CONTROLS.values())
    n_vulns = sum(len(v) for v in vulns_by_asset.values())
    st.success(f"Reset to full portfolio ({len(assets)} assets, {n_vulns} vulnerabilities).")


def generate_sih_summary(session):
    """Write SIH_Submission.md with key metrics and impact framing."""
    assets = session["assets"]
    vulns_by_asset = session["vulns_by_asset"]
    exposure = total_exposure(assets, vulns_by_asset)
    cr_i = compute_overall_cr_i(assets, vulns_by_asset)
    num_vulns = sum(len(v) for v in vulns_by_asset.values())
    users_impacted = sum(a["daily_transaction_volume"] for a in assets)
    # MGNREGA-day equivalence: ~₹266/day wage (typical)
    mgnrega_days = int(exposure / 266) if exposure > 0 else 0

    content = f"""# Smart India Hackathon 2024 — CyberLens 2.0 Submission

## 1. Problem Statement
India's digital financial infrastructure processes over 350 million UPI
transactions daily (~₹3.5 lakh crore). Existing cyber-risk tools give
qualitative scores (Low/Medium/High) that do not translate into financial
impact or actionable budget decisions. RBI, SEBI, and NPCI require
quantifiable risk exposure in monetary terms for effective governance and
budget allocation.

## 2. Solution Overview
CyberLens 2.0 is an AI-enhanced Cyber Risk Quantification Platform that
transforms raw vulnerability, asset, and transaction data into RBI-aligned
financial risk metrics (in ₹) and produces an AI-optimized investment plan
that maximizes risk reduction per rupee spent.

## 3. Impact Metrics
- **Estimated Annual Risk Exposure:** ₹{exposure:,.0f}
- **Assets under assessment:** {len(assets)}
- **Vulnerabilities quantified:** {num_vulns}
- **Daily transactions represented:** {users_impacted:,}
- **Cyber Resilience Index (CR-I):** {cr_i:.1f}/100
- **MGNREGA-day equivalence:** {mgnrega_days:,} days of rural wage protected

## 4. Technical Stack
- **Frontend:** Streamlit (Executive + Technical dashboards)
- **Engine:** Python 3.11 — RBI-weighted CVSS, CR-I, EAL, ROSI knapsack optimizer
- **Data:** SQLite + sample CSV (zero-setup demo)
- **AI:** Few-shot remediation templates (Hindi/English), LLM-ready fallback

## 5. Compliance Alignment
Every vulnerability is auto-mapped to its exact regulatory clause under
RBI / NPCI / SEBI (e.g., RBI/SWIFT-CSP, NPCI/IMPS, SEBI/CSCRF), enabling
governance teams to audit and prioritize by mandate.

## 6. Future Scope
- Real-time CERT-In/NVD vulnerability feeds
- XGBoost-based scoring replacement for the rule-based model
- Exact integer optimization via PuLP
- Multi-language support (regional Indian languages)
- Kubernetes-ready micro-services deployment

## 7. Open-Source Pledge
Released under AGPL-3 to enable community audit and adoption by India's
public-sector banks and payment systems.
---
*Generated by CyberLens 2.0 on {datetime.date.today().isoformat()}.*
"""
    # Audit: log summary generation
    audit = session.get("audit_log", [])
    audit.append({"action": "generate_sih_summary", "timestamp": time.time(), "file": "SIH_Submission.md"})
    session["audit_log"] = audit[:1000]
    with open("SIH_Submission.md", "w", encoding="utf-8") as f:
        f.write(content)
    st.success("Generated `SIH_Submission.md` — ready for SIH portal upload.")
    st.download_button(
        label="Download SIH_Submission.md",
        data=content,
        file_name="SIH_Submission.md",
        mime="text/markdown",
    )


SUPPORTED_LANGUAGES = {
    "en": "en",
    "hi": "hi",
    "English": "en",
    "Hindi": "hi",
}

CYBER_LEXICON = {
    "Cyber Resilience Index": "साइबर लचीलापन सूचकांक (CR-I)",
    "Expected Annual Loss": "अपेक्षित वार्षिक वित्तीय हानि (EAL)",
    "Annual Risk Exposure": "वार्षिक जोखिम प्रभाव",
    "Authentication Bypass": "प्रमाणीकरण बाईपास",
    "Vulnerability": "सुरक्षा संवेदनशीलता / भेद्यता",
    "Remediation": "निवारण / सुधार उपाय",
    "Compliance Audit": "नियामक अनुपालन लेखापरीक्षा",
}


def translate_text(text: str, target_lang: str) -> str:
    """Translate cybersecurity terms into target language."""
    code = SUPPORTED_LANGUAGES.get(target_lang, target_lang)
    if code == "en":
        return text
    if code == "hi":
        for en_term, hi_term in CYBER_LEXICON.items():
            if en_term.lower() in text.lower():
                text = text.replace(en_term, hi_term)
        return text
    return text


def generate_ai_summary_report(session: dict, lang_code: str = "en"):
    """Generate executive summary in markdown and structured JSON format."""
    assets = session.get("assets", [])
    vulns_by_asset = session.get("vulns_by_asset", {})
    exposure = total_exposure(assets, vulns_by_asset)
    cr_i = compute_overall_cr_i(assets, vulns_by_asset)
    total_vulns = sum(len(v) for v in vulns_by_asset.values())

    md = f"""# Executive Cyber Risk Quantification Assessment
**Date:** {datetime.date.today().isoformat()}
**Regulatory Reference:** RBI Master Direction (RBI/2023-24/105)

### Summary Metrics
- **Overall Cyber Resilience Index (CR-I):** {cr_i:.1f}/100
- **Total Expected Annual Loss (EAL):** ₹{exposure:,.0f}
- **Assessed Assets:** {len(assets)}
- **Identified Vulnerabilities:** {total_vulns}

### Supervisory Recommendation
Prioritize immediate remediation and capital allocation towards critical payment infrastructure nodes (UPI Switch, CBS, ATM Switch) to avert catastrophic systemic operational loss.
"""
    if lang_code == "hi":
        md = translate_text(md, "hi")

    data = {
        "cr_i": cr_i,
        "total_exposure_inr": exposure,
        "asset_count": len(assets),
        "vulnerability_count": total_vulns,
        "compliance_framework": "RBI Master Direction / SEBI / NPCI",
        "generated_at": datetime.datetime.now().isoformat(),
    }
    return md, data