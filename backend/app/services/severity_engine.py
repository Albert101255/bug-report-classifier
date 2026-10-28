import re
from datetime import UTC, datetime, timedelta

SEVERITY_RULES = [
    {
        "level": "P0 - Blocker",
        "sla_hours": 1,
        "keywords": [
            r"\b(oomkilled|segfault|data loss|security breach|cve|rce|sql injection|zero-day|outage|all workers dead|database corruption)\b"
        ],
        "impact": "System Outage or Severe Security Vulnerability (Immediate Page)",
    },
    {
        "level": "P1 - Critical",
        "sla_hours": 4,
        "keywords": [
            r"\b(payment failed|checkout down|deadlock|500 internal server error|auth failed|token expired|login loop|connection pool exhausted|unhandled exception)\b"
        ],
        "impact": "Core Business Functionality Impaired (High Urgency)",
    },
    {
        "level": "P2 - Major",
        "sla_hours": 24,
        "keywords": [
            r"\b(timeout|slow query|dropdown clipped|filter broken|validation error|missing webhook|export incomplete|retry exhausted)\b"
        ],
        "impact": "Degraded Feature Performance with Workaround Available",
    },
]


def calculate_severity(description: str, subject: str = "") -> dict:
    full_text = f"{subject} {description}".lower()

    for rule in SEVERITY_RULES:
        for kw_pattern in rule["keywords"]:
            if re.search(kw_pattern, full_text, re.IGNORECASE):
                now = datetime.now(UTC)
                deadline = (now + timedelta(hours=rule["sla_hours"])).isoformat()
                return {
                    "severity": rule["level"],
                    "sla_hours": rule["sla_hours"],
                    "sla_deadline": deadline,
                    "impact_summary": rule["impact"],
                }

    now = datetime.now(UTC)
    deadline = (now + timedelta(hours=72)).isoformat()
    return {
        "severity": "P3 - Minor",
        "sla_hours": 72,
        "sla_deadline": deadline,
        "impact_summary": "Standard Bug / Cosmetic or Low-Impact Defect",
    }
