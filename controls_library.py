"""CyberLens 2.0 - Security Controls Library
Defines available security controls for the ROSI-driven budget optimizer.

Controls are static definitions; their monetary risk reduction is computed
at runtime against actual vulnerabilities (which changes with the data).
"""

CONTROLS = {
    "CTRL_MFA_UPI": {
        "control_id": "CTRL_MFA_UPI",
        "name": "MFA for High-Value UPI Transactions",
        "cost_inr": 8_000_000,
        "affected_categories": ["Authentication Bypass"],
        "effectiveness": 0.75,
        "description": "Enforce multi-factor authentication for transactions above ₹50,000 (RBI/2023-24/105.A.3).",
    },
    "CTRL_WAF": {
        "control_id": "CTRL_WAF",
        "name": "Web Application Firewall",
        "cost_inr": 4_000_000,
        "affected_categories": ["SQL Injection", "Cross-Site Scripting", "Injection"],
        "effectiveness": 0.60,
        "description": "Deploy WAF to block injection and XSS attacks at the perimeter.",
    },
    "CTRL_PATCH": {
        "control_id": "CTRL_PATCH",
        "name": "Accelerated Patch Management Program",
        "cost_inr": 2_000_000,
        "affected_categories": ["SQL Injection", "Privilege Escalation", "Authentication Bypass",
                                "Insecure Storage", "Session Fixation", "Input Validation"],
        "effectiveness": 0.80,
        "description": "Patch critical vulnerabilities within 7 days (RBI expectation for critical systems).",
    },
    "CTRL_HARDEN": {
        "control_id": "CTRL_HARDEN",
        "name": "Section Hardening & Secure Storage",
        "cost_inr": 3_000_000,
        "affected_categories": ["Insecure Storage", "Data Exposure", "Weak Cryptography"],
        "effectiveness": 0.70,
        "description": "Move to hardware-backed keystores, enforce AES-256 and TLS 1.2+.",
    },
    "CTRL_EDR": {
        "control_id": "CTRL_EDR",
        "name": "EDR / Endpoint Monitoring",
        "cost_inr": 5_000_000,
        "affected_categories": ["Privilege Escalation", "Authentication Bypass", "Network Sniffing"],
        "effectiveness": 0.55,
        "description": "Endpoint detection and response with 24x7 SOC monitoring.",
    },
    "CTRL_RATE_LIMIT": {
        "control_id": "CTRL_RATE_LIMIT",
        "name": "Transaction Rate Limiting & Anomaly Detection",
        "cost_inr": 6_000_000,
        "affected_categories": ["Rate Limiting"],
        "effectiveness": 0.85,
        "description": "Velocity checks and ML anomaly detection on transaction flows.",
    },
    "CTRL_PENTEST": {
        "control_id": "CTRL_PENTEST",
        "name": "Annual Penetration Testing & Review",
        "cost_inr": 1_500_000,
        "affected_categories": ["SQL Injection", "Input Validation", "Session Fixation",
                                "Cross-Site Scripting", "Authentication Bypass"],
        "effectiveness": 0.45,
        "description": "Proactive identification and remediation of known vulnerability classes.",
    },
    "CTRL_BACKUP": {
        "control_id": "CTRL_BACKUP",
        "name": "Encrypted Offsite Backup & DR",
        "cost_inr": 7_000_000,
        "affected_categories": ["Ransomware", "Data Exposure"],
        "effectiveness": 0.65,
        "description": "Immutable, encrypted backups with tested disaster-recovery playbooks.",
    },
}