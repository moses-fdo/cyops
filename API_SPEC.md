# API Specification (API_SPEC.md) - CyberLens 2.0

This document describes the RESTful API endpoints for the CyberLens 2.0 risk engine.
The API is built with FastAPI and can be enabled by setting `ENABLE_API=true` in the environment
or by running the `api.py` entry point. The demo Streamlit app uses the engine in‑process,
but the same functions are exposed via these endpoints for scalability and integration.

## Base URL
`http://localhost:8000` (default when running via `docker compose` with the api service)

All endpoints return JSON. Errors return a JSON object with `{"detail": "error message"}` and appropriate HTTP status code.

## Authentication
For the demo and SIH submission, no authentication is required. In a production deployment,
you would add OAuth2/JWT middleware as needed.

## Endpoints

### Assets

#### GET /assets
Retrieve a list of assets, optionally filtered by asset_type or business_unit.

**Query Parameters**
- `asset_type` (string, optional): Filter by asset type (e.g., UPI_SWITCH, CBS_SERVER).
- `business_unit` (string, optional): Filter by business unit.

**Response**
- 200 OK: Array of asset objects.
  ```json
  [
    {
      "asset_id": "UPI_SWITCH_001",
      "name": "National UPI Switch",
      "asset_type": "UPI_SWITCH",
      "business_unit": "Payments",
      "criticality": 9.8,
      "daily_transaction_volume": 350000000,
      "replacement_cost": 50000000000,
      "downtime_cost_per_hour": 1000000000,
      "user_segments": ["retail", "corporate"]
    }
  ]
  ```

#### GET /assets/{asset_id}
Retrieve a specific asset by ID.

**Path Parameters**
- `asset_id` (string): The asset identifier.

**Response**
- 200 OK: Asset object (same structure as above).
- 404 Not Found: If asset does not exist.

### Vulnerabilities

#### GET /vulnerabilities
Retrieve a list of vulnerabilities, optionally filtered by asset_id, cve_id, or category.

**Query Parameters**
- `asset_id` (string, optional): Filter by asset ID.
- `cve_id` (string, optional): Filter by CVE identifier.
- `category` (string, optional): Filter by vulnerability category (e.g., Authentication Bypass).

**Response**
- 200 OK: Array of vulnerability objects.
  ```json
  [
    {
      "vuln_id": "V_UPI_001",
      "asset_id": "UPI_SWITCH_001",
      "cve_id": "CVE-2023-XXXX",
      "cvss_base_score": 8.1,
      "exploit_available": true,
      "days_unpatched": 60,
      "category": "Authentication Bypass",
      "affected_component": "UPI API Gateway"
    }
  ]
  ```

#### GET /vulnerabilities/{vuln_id}
Retrieve a specific vulnerability by ID.

**Path Parameters**
- `vuln_id` (string): The vulnerability identifier.

**Response**
- 200 OK: Vulnerability object (same structure as above).
- 404 Not Found: If vulnerability does not exist.

### Risk Calculations

#### POST /calculate/cr-i
Compute the Cyber Resilience Index (CR‑I) for a set of assets (or all assets if none specified).

**Request Body**
```json
{
  "asset_ids": ["UPI_SWITCH_001", "CBS_SERVER_002"] // optional; if empty or omitted, use all assets
}
```

**Response**
- 200 OK: Object containing the CR‑I score (0‑100) and optional metadata.
  ```json
  {
    "cr_i": 71.5,
    "asset_count": 2,
    "description": "Cyber Resilience Index (higher = more resilient)"
  }
  ```

#### POST /calculate/eal
Compute the Expected Annual Loss (EAL) in ₹/year for a specific vulnerability.

**Request Body**
```json
{
  "vuln_id": "V_UPI_001"
}
```

**Response**
- 200 OK: Object containing the EAL amount and intermediate values.
  ```json
  {
    "eal_inr": 1800000000.0, // ₹1.8 Crore per year
    "rbi_weighted_cvss": 9.1,
    "incident_probability": 0.82,
    "loss_per_incident_inr": 2195121951.0,
    "asset_id": "UPI_SWITCH_001"
  }
  ```

#### POST /calculate/total-exposure
Compute the total annual cyber risk exposure (sum of EAL) for a set of assets (or all assets).

**Request Body**
```json
{
  "asset_ids": ["UPI_SWITCH_001", "CBS_SERVER_002"] // optional
}
```

**Response**
- 200 OK: Object containing total exposure in ₹/year and per‑asset breakdown.
  ```json
  {
    "total_exposure_inr": 4200000000.0, // ₹4.2 Crore per year
    "asset_count": 2,
    "breakdown": [
      {
        "asset_id": "UPI_SWITCH_001",
        "eal_inr": 1800000000.0
      },
      {
        "asset_id": "CBS_SERVER_002",
        "eal_inr": 2400000000.0
      }
    ]
  }
  ```

### RBI Mappings

#### GET /rbi-mapping
Retrieve the RBI/SEBI/NPCI mapping for a given vulnerability category and asset type.

**Query Parameters**
- `category` (string, required): Vulnerability category (e.g., Authentication Bypass).
- `asset_type` (string, required): Asset type (e.g., UPI_SWITCH).

**Response**
- 200 OK: Object containing the mapping details.
  ```json
  {
    "category": "Authentication Bypass",
    "asset_type": "UPI_SWITCH",
    "rbi_clause": "RBI/2023-24/105.A.3",
    "nci_clause": null,
    "sebi_clause": "SEBI/HO/ISD/ISD/CIR/P/2020/168",
    "description": "Requires strong authentication for privileged access to payment systems."
  }
  ```
- 404 Not Found: If no mapping exists for the given inputs.

### Controls & Optimization

#### GET /controls
Retrieve the library of security controls with their cost and effectiveness.

**Response**
- 200 OK: Array of control objects.
  ```json
  [
    {
      "control_id": "CTRL_MFA_UPI",
      "name": "Deploy MFA for UPI Admin Access",
      "cost_inr": 800000, // ₹8 Lakhs
      "affected_categories": ["Authentication Bypass"],
      "effectiveness": 0.7 // Reduces risk by 70% for affected vulns
    },
    {
      "control_id": "CTRL_PATCH_MGMT",
      "name": "Automated Critical Patch Deployment (<7 days)",
      "cost_inr": 2000000, // ₹20 Lakhs
      "affected_categories": ["All"],
      "effectiveness": 0.8 // Reduces patch penalty by 80%
    }
  ]
  ```

#### POST /optimize/budget
Given a budget in ₹, return the optimal set of controls (using ROSI‑driven knapsack) that maximizes risk reduction.

**Request Body**
```json
{
  "budget_inr": 10000000 // ₹1 Crore
}
```

**Response**
- 200 OK: Object containing the selected controls, total cost, total risk reduction, remaining budget, and overall ROSI.
  ```json
  {
    "selected_controls": [
      {
        "control_id": "CTRL_MFA_UPI",
        "name": "Deploy MFA for UPI Admin Access",
        "cost_inr": 800000,
        "risk_reduction_inr": 4960000000.0, // ₹4.96 Crore/year
        "rosi": 520.0
      },
      {
        "control_id": "CTRL_PATCH_MGMT",
        "name": "Automated Critical Patch Deployment (<7 days)",
        "cost_inr": 2000000,
        "risk_reduction_inr": 3840000000.0, // ₹3.84 Crore/year
        "rosi": 480.0
      }
    ],
    "total_cost_inr": 2800000, // ₹28 Lakhs
    "total_risk_reduction_inr": 8800000000.0, // ₹8.8 Crore/year
    "remaining_budget_inr": 7200000, // ₹72 Lakhs
    "overall_rosi": 214.3 // (total_risk_reduction - total_cost) / total_cost * 100
  }
  ```

### LLM Remediation

#### POST /llm/remediate
Generate remediation steps in simple Hindi/English for a given vulnerability using the few‑shot LLM.

**Request Body**
```json
{
  "vuln_id": "V_UPI_001"
}
```

**Response**
- 200 OK: Object containing the remediation steps (array of strings) and optional metadata.
  ```json
  {
    "remediation_steps": [
      "Admin पैनल पर SMS‑OTP अनिवार्य करें।",
      "सभी privileged अकाउंट्स को 30 दिन में review करें।",
      "पुराने SSH keys को हटा दें।"
    ],
    "model_used": "TinyLlama-1.1B-Chat-v1.0 (4‑bit quantized)",
    "language": "Hindi/English mix"
  }
  ```
- 500 Internal Server Error: If the LLM fails to generate a response (fallback to rule‑based may be attempted internally).

### Health Check

#### GET /health
Simple health check endpoint.

**Response**
- 200 OK: `{"status": "ok"}`

## Data Types

- All monetary values are in Indian Rupees (₹) as floating point numbers (but represented as JSON numbers).
- Percentages and ratios are floating point numbers (e.g., 0.7 for 70%).
- Identifiers are strings.
- Timestamps are not used in the current demo but would be ISO 8601 strings if added.

## Versioning
This API is versioned implicitly via the FastAPI version (if needed, we can prefix with `/v1/`). For the SIH demo, we use the root path.

## Security & Rate Limiting
- The demo API does not implement authentication or rate limiting. In production, add:
  - OAuth2/JWT authentication.
  - Rate limiting (e.g., 100 requests/minute per IP).
  - Input validation and sanitization (FastAPI does this via Pydantic models).

## Example Usage (cURL)
```bash
# Get total exposure
curl -X POST "http://localhost:8000/calculate/total-exposure" \
  -H "Content-Type: application/json" \
  -d '{"asset_ids": ["UPI_SWITCH_001"]}'

# Optimize budget
curl -X POST "http://localhost:8000/optimize/budget" \
  -H "Content-Type: application/json" \
  -d '{"budget_inr": 10000000}'

# Get LLM remediation
curl -X POST "http://localhost:8000/llm/remediate" \
  -H "Content-Type: application/json" \
  -d '{"vuln_id": "V_UPI_001"}'
```

---
*Co‑Authored-By: Claude Code <noreply@anthropic.com>*