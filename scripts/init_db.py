#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from serving.database import engine, SessionLocal
from serving.models import Base, Team

Base.metadata.create_all(bind=engine)

session = SessionLocal()

teams_data = [
    ("BL-101", "BL-101 (Authentication & AuthZ)"),
    ("BL-102", "BL-102 (Database & ORM)"),
    ("BL-103", "BL-103 (UI Components & Design System)"),
    ("BL-104", "BL-104 (Payment Gateway & Billing)"),
    ("BL-105", "BL-105 (Cloud Infrastructure & K8s)"),
    ("BL-106", "BL-106 (API Gateway & Microservices)"),
    ("BL-107", "BL-107 (Search & Indexing Engine)"),
    ("BL-108", "BL-108 (Notification & Webhooks)"),
    ("BL-109", "BL-109 (Analytics & Telemetry)"),
    ("BL-110", "BL-110 (Security & Compliance)")
]

for backlog_id, name in teams_data:
    existing = session.query(Team).filter(Team.backlog_id == backlog_id).first()
    if not existing:
        t = Team(backlog_id=backlog_id, name=name, description=f"Engineering team managing {name}")
        session.add(t)

session.commit()
print("Database initialized & seeded successfully!")
