"""
api.py - FastAPI REST Service for CyberLens 2.0 Risk Engine
Exposes risk calculation, optimization, multilingual translation, and AI report generation.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import data_loader
import risk_engine
from controls_library import CONTROLS
from components.sih_features import (
    translate_text,
    generate_ai_summary_report,
    SUPPORTED_LANGUAGES,
)

app = FastAPI(
    title="CyberLens 2.0 Risk Engine API",
    description="RESTful API for Cyber Risk Quantification, Controls Optimization, and Multilingual AI Summaries.",
    version="2.0.0",
)


# --- Helper Data Loaders ---

def get_current_data():
    data_loader.init_db()
    assets = data_loader.get_assets()
    vulns_by_asset = {a["asset_id"]: data_loader.get_vulnerabilities(a["asset_id"]) for a in assets}
    return assets, vulns_by_asset


# --- Pydantic Request/Response Models ---

class CRICalculateRequest(BaseModel):
    asset_ids: Optional[List[str]] = None

class EALCalculateRequest(BaseModel):
    vuln_id: str

class TotalExposureRequest(BaseModel):
    asset_ids: Optional[List[str]] = None

class BudgetOptimizeRequest(BaseModel):
    budget_inr: float = Field(gt=0, description="Budget in Indian Rupees")

class LLMRemediateRequest(BaseModel):
    vuln_id: str
    language: str = "en"

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"

class AISummaryRequest(BaseModel):
    total_exposure_inr: Optional[float] = None
    top_assets: Optional[List[str]] = None
    lang: str = "en"


# --- Endpoints ---

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok", "service": "CyberLens 2.0 API"}


@app.get("/assets", summary="List Assets")
def list_assets(asset_type: Optional[str] = None, business_unit: Optional[str] = None):
    assets, _ = get_current_data()
    if asset_type:
        assets = [a for a in assets if a.get("asset_type") == asset_type]
    if business_unit:
        assets = [a for a in assets if a.get("business_unit") == business_unit]
    return assets


@app.get("/assets/{asset_id}", summary="Get Asset Details")
def get_asset(asset_id: str):
    assets, _ = get_current_data()
    asset = next((a for a in assets if a.get("asset_id") == asset_id), None)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return asset


@app.get("/vulnerabilities", summary="List Vulnerabilities")
def list_vulnerabilities(asset_id: Optional[str] = None, category: Optional[str] = None):
    _, vulns_by_asset = get_current_data()
    all_vulns = [v for vulns in vulns_by_asset.values() for v in vulns]
    if asset_id:
        all_vulns = [v for v in all_vulns if v.get("asset_id") == asset_id]
    if category:
        all_vulns = [v for v in all_vulns if v.get("category") == category]
    return all_vulns


@app.post("/calculate/cr-i", summary="Calculate CR-I Score")
def calculate_cri(req: CRICalculateRequest):
    assets, vulns_by_asset = get_current_data()
    if req.asset_ids:
        assets = [a for a in assets if a["asset_id"] in req.asset_ids]
        vulns_by_asset = {k: v for k, v in vulns_by_asset.items() if k in req.asset_ids}
    score = risk_engine.compute_overall_cr_i(assets, vulns_by_asset)
    return {
        "cr_i": score,
        "asset_count": len(assets),
        "description": "Cyber Resilience Index (higher = more resilient)"
    }


@app.post("/calculate/eal", summary="Calculate EAL for Vulnerability")
def calculate_eal(req: EALCalculateRequest):
    assets, vulns_by_asset = get_current_data()
    for asset in assets:
        for v in vulns_by_asset.get(asset["asset_id"], []):
            if v["vuln_id"] == req.vuln_id:
                rbi_cvss = risk_engine.rbi_weighted_cvss(v, asset)
                prob = min(rbi_cvss / 10.0, 0.9)
                downtime_loss = float(asset["downtime_cost_per_hour"]) * risk_engine.AVG_INCIDENT_HOURS
                fraud_loss = float(asset["daily_transaction_volume"]) * risk_engine.FRAUD_LOSS_RATE
                loss = downtime_loss + fraud_loss
                eal = risk_engine.expected_annual_loss(v, asset)
                return {
                    "vuln_id": req.vuln_id,
                    "asset_id": asset["asset_id"],
                    "eal_inr": eal,
                    "rbi_weighted_cvss": rbi_cvss,
                    "incident_probability": prob,
                    "loss_per_incident_inr": loss
                }
    raise HTTPException(status_code=404, detail=f"Vulnerability {req.vuln_id} not found")


@app.post("/calculate/total-exposure", summary="Calculate Total Exposure")
def calculate_total_exposure(req: TotalExposureRequest):
    assets, vulns_by_asset = get_current_data()
    if req.asset_ids:
        assets = [a for a in assets if a["asset_id"] in req.asset_ids]
        vulns_by_asset = {k: v for k, v in vulns_by_asset.items() if k in req.asset_ids}
    
    total = risk_engine.total_exposure(assets, vulns_by_asset)
    matrix = risk_engine.compute_risk_matrix(assets, vulns_by_asset)
    breakdown = [{"asset_id": r["asset_id"], "eal_inr": r["eal_inr"]} for r in matrix]
    return {
        "total_exposure_inr": total,
        "asset_count": len(assets),
        "breakdown": breakdown
    }


@app.post("/optimize/budget", summary="Optimize Security Controls Budget")
def optimize_budget(req: BudgetOptimizeRequest):
    assets, vulns_by_asset = get_current_data()
    controls = list(CONTROLS.values())
    enriched = risk_engine.enrich_controls_with_reduction(controls, assets, vulns_by_asset)
    res = risk_engine.optimize_budget(enriched, req.budget_inr, assets, vulns_by_asset)
    return res


@app.post("/llm/remediate", summary="Get LLM Remediation Steps")
def llm_remediate_endpoint(req: LLMRemediateRequest):
    assets, vulns_by_asset = get_current_data()
    for asset in assets:
        for v in vulns_by_asset.get(asset["asset_id"], []):
            if v["vuln_id"] == req.vuln_id:
                res = risk_engine.llm_remediate(v, asset, language=req.language)
                return {
                    "vuln_id": req.vuln_id,
                    "remediation_steps": res["steps"],
                    "source": res.get("source", "rule_based")
                }
    raise HTTPException(status_code=404, detail=f"Vulnerability {req.vuln_id} not found")


@app.post("/translate", summary="Translate Text to Regional Language")
def translate_endpoint(req: TranslateRequest):
    if req.target_lang not in SUPPORTED_LANGUAGES.values() and req.target_lang not in SUPPORTED_LANGUAGES.keys():
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{req.target_lang}'"
        )
    translated = translate_text(req.text, req.target_lang)
    return {
        "translated_text": translated,
        "target_lang": req.target_lang,
        "source_lang": "en"
    }


@app.post("/ai/summary", summary="Generate Executive AI Risk Summary")
def ai_summary_endpoint(req: AISummaryRequest):
    assets, vulns_by_asset = get_current_data()
    if req.total_exposure_inr is None:
        req.total_exposure_inr = risk_engine.total_exposure(assets, vulns_by_asset)
    
    top = req.top_assets or [a["name"] for a in assets[:3]]
    session = {"risk_matrix": risk_engine.compute_risk_matrix(assets, vulns_by_asset), "assets": assets, "vulns_by_asset": vulns_by_asset}
    summary_md, summary_json = generate_ai_summary_report(session, lang_code=req.lang)
    return {
        "summary_markdown": summary_md,
        "summary_json": summary_json,
        "language": req.lang,
        "total_exposure_inr": req.total_exposure_inr
    }
