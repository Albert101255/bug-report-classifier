import re
from typing import Any

DEFAULT_RULES = [
    {
        "id": "rule-sec-01",
        "name": "Security & CVE Auto-Escalation",
        "pattern": r"(?:cve-\d+|sql injection|xss|rce|zero-day|credential leak|privilege escalation)",
        "target_team": "BL-110 (Security & Compliance)",
        "forced_severity": "P0 - Blocker",
        "enabled": True,
        "description": "Any security vulnerability or exploit is immediately directed to Security queue with P0 priority.",
    },
    {
        "id": "rule-bill-02",
        "name": "Payment Gateway Hard Failure",
        "pattern": r"(?:stripe webhook dropped|chargeback error|credit card processor down|checkout 500)",
        "target_team": "BL-104 (Payment Gateway & Billing)",
        "forced_severity": "P1 - Critical",
        "enabled": True,
        "description": "Payment and checkout interruptions route straight to Billing engineering.",
    },
    {
        "id": "rule-k8s-03",
        "name": "Kubernetes OOMKilled Emergency",
        "pattern": r"(?:oomkilled|exit code 137|crashloopbackoff|ingress 502)",
        "target_team": "BL-105 (Cloud Infrastructure & K8s)",
        "forced_severity": "P0 - Blocker",
        "enabled": True,
        "description": "Cluster worker pod crashes route immediately to Cloud Infrastructure.",
    },
]


def evaluate_rules(description: str, subject: str = "") -> dict[str, Any] | None:
    full_text = f"{subject} {description}".lower()
    for rule in DEFAULT_RULES:
        if not rule["enabled"]:
            continue
        if re.search(rule["pattern"], full_text, re.IGNORECASE):
            return {
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "target_team": rule["target_team"],
                "forced_severity": rule["forced_severity"],
                "reason": rule["description"],
            }
    return None
