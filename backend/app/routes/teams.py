from typing import List
from fastapi import APIRouter
from app.schemas import TeamInfo

router = APIRouter(prefix="/teams", tags=["Teams"])

TEAMS_CATALOG: List[TeamInfo] = [
    TeamInfo(code="BL-101", name="BL-101 (Authentication & AuthZ)", description="OAuth, SSO, JWT tokens, user session state, and access permissions", category="Security & Identity", accuracy_rate=94.5, total_bugs_assigned=1420),
    TeamInfo(code="BL-102", name="BL-102 (Database & ORM)", description="PostgreSQL, connection pools, SQLAlchemy migrations, and slow SQL query optimization", category="Data & Storage", accuracy_rate=91.2, total_bugs_assigned=1180),
    TeamInfo(code="BL-103", name="BL-103 (UI Components & Design System)", description="React, CSS dark mode tokens, modal overlays, tables, and responsiveness", category="Frontend", accuracy_rate=96.0, total_bugs_assigned=1890),
    TeamInfo(code="BL-104", name="BL-104 (Payment Gateway & Billing)", description="Stripe API, subscription renewals, invoices, refund webhooks, and currency conversions", category="Finance & Core Business", accuracy_rate=89.8, total_bugs_assigned=950),
    TeamInfo(code="BL-105", name="BL-105 (Cloud Infrastructure & K8s)", description="Kubernetes pods, Helm charts, Docker containers, OOMKilled errors, and Terraform", category="DevOps & Cloud", accuracy_rate=93.4, total_bugs_assigned=1310),
    TeamInfo(code="BL-106", name="BL-106 (API Gateway & Microservices)", description="FastAPI, gRPC, rate limiters, HTTP 500 error handlers, and route proxies", category="Backend Infrastructure", accuracy_rate=92.1, total_bugs_assigned=1640),
    TeamInfo(code="BL-107", name="BL-107 (Search & Indexing Engine)", description="Elasticsearch, full-text search indexing, query analyzers, and ranking algorithms", category="Search & Discovery", accuracy_rate=88.5, total_bugs_assigned=780),
    TeamInfo(code="BL-108", name="BL-108 (Notification & Webhooks)", description="Email dispatches, SendGrid SMTP, Discord/Slack webhooks, and push notifications", category="Integrations", accuracy_rate=90.7, total_bugs_assigned=890),
    TeamInfo(code="BL-109", name="BL-109 (Analytics & Telemetry)", description="Prometheus metrics, Grafana dashboards, P50/P95 latency tracking, and event logs", category="Observability", accuracy_rate=95.2, total_bugs_assigned=1020),
    TeamInfo(code="BL-110", name="BL-110 (Security & Compliance)", description="XSS, CSRF, vulnerability scanning, input sanitization, and audit logs", category="Security & Identity", accuracy_rate=97.1, total_bugs_assigned=610)
]

@router.get("/list", response_model=List[TeamInfo])
async def list_teams():
    return TEAMS_CATALOG
