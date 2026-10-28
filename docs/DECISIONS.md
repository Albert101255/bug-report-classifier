# Architecture Decision Records (ADRs)

## ADR 001: Strict Single-Issue-First Architecture & Elimination of Batch Ingestion

### Status
Accepted & Implemented.

### Context
Legacy versions of the application included CSV upload wizards, bulk ingestion endpoints (`/api/v1/predict/batch`), and batch progress components. In practice, bulk uploading bypasses critical bug verification, floods engineering backlogs with unvetted noise, introduces severe security risks (CSV formula injection, denial of service), and dilutes triage quality.

### Decision
Permanently exclude all batch and bulk workflows. Remove all batch UI components, routes, client helpers, and database entities. Every issue in Triage must be reported and routed individually.

### Consequences
- Clean, focused user interface modeled on modern engineering standards (Linear, GitHub Issues).
- Every issue receives dedicated deduplication, stack trace extraction, SLA scoring, and audit tracking.
- Zero risk of CSV injection vulnerabilities.

---

## ADR 002: Modular Monolith with FastAPI and SQLAlchemy 2.0 Async

### Status
Accepted & Implemented.

### Context
The previous codebase had split functionality across two uncoordinated implementations (`backend/app/` and legacy `serving/main.py`), with synchronous SQLite drivers and fragmented schema migrations.

### Decision
Consolidate into a clean, modern FastAPI modular monolith in `backend/app/` with full async/await support using SQLAlchemy 2.0 (`asyncpg` for PostgreSQL, `aiosqlite` for local dev/testing) and versioned Alembic migrations.

### Consequences
- Non-blocking I/O performance suitable for real-time live typing predictions.
- Single source of truth for database models and API routes.
- Retired legacy `serving/` directory to historical archive.

---

## ADR 003: Multi-Tenant Scoping at Organization Boundary

### Status
Accepted & Implemented.

### Context
The legacy application lacked user accounts, access controls, and organization boundaries, allowing any user to view or modify all data.

### Decision
Introduce tenant organizations (`Organization`), role-based access control (`ORG_ADMIN`, `TEAM_LEAD`, `ENGINEER`, `VIEWER`), and enforce tenant isolation on all database queries.

### Consequences
- Supports multiple engineering teams and workspaces securely.
- Complete auditability of actions by actor.

---

## ADR 004: Scikit-Learn TF-IDF + Logistic Regression with Calibrated Entropy

### Status
Accepted & Implemented.

### Context
The legacy interface falsely claimed to run "Monte Carlo Dropout" deep neural networks despite executing a standard Logistic Regression model.

### Decision
Remove all fabricated Monte Carlo claims. Use a transparent scikit-learn TF-IDF + Logistic Regression pipeline with calibrated probabilities and Shannon entropy. Provide a deterministic keyword fallback when weights are unavailable.

### Consequences
- Fast inference ($< 5\text{ms}$) allowing real-time previews during typing.
- Honest, transparent telemetry.
- Low memory consumption ($< 2\text{MB}$ artifact footprint).

---

## ADR 005: Linear-Inspired Engineering Design System

### Status
Accepted & Implemented.

### Context
The original frontend featured distracting neon gradients, glowing animations, and demo-oriented layouts unsuitable for daily developer workflows.

### Decision
Rebuild the frontend from scratch with React 18, Vite, Tailwind CSS, TanStack Query, and Lucide icons, inspired by Linear, GitHub Issues, and Sentry.

### Consequences
- Restrained, typography-driven, high-contrast user interface.
- Full dark and light theme support.
- Streamlined information hierarchy.

---

## ADR 006: Training Data Format Migration to JSON Lines

### Status
Accepted & Implemented.

### Context
Active scripts read a CSV file for training, creating a contradiction with the non-negotiable rule excluding CSV handling.

### Decision
Migrate training dataset to `data/training_dataset.jsonl`. Safely preserve the original demo CSV in `data/archive/` as a static research asset.

### Consequences
- Unified JSON data serialization across API and ML training pipelines.
- Absolute compliance with the zero-CSV application scope.
