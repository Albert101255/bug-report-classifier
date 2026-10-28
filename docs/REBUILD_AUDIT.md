# Engineering Audit & Modernization Plan: Triage Platform Rebuild

**Date:** October 2026
**Repository:** `Albert101255/bug-report-classifier`
**Target Product Name:** **Triage** (Enterprise Bug Management & Intelligent Routing Platform)
**Initial Baseline Commit:** `8a3f86e970ca39fa434455a48f902ea18ea7ba8b`
**Development Branch:** `rebuild/enterprise-triage`

---

## 1. Executive Summary

This audit assesses the state of `bug-report-classifier` and outlines the comprehensive modernization into **Triage**, a production-ready engineering triage and issue management platform.

The original codebase combined elements of an early prototype (in `serving/`), a newer async FastAPI backend (in `backend/app/`), and a React frontend (`frontend/`). While the project demonstrated a useful machine learning baseline (TF-IDF + Logistic Regression), it suffered from pervasive simulation, lack of multi-tenancy, missing authentication/authorization, non-persisted user settings, hardcoded analytics, and an obsolete batch upload/CSV processing module that is fundamentally misaligned with daily single-issue engineering workflows.

In accordance with strict project guidelines, all batch/CSV processing is excluded. The rebuilt platform operates as an authentic, single-issue-first engineering system.

---

## 2. Comprehensive Inventory of Identified Problems

### 2.1 Pervasive Simulation & Fake Fallbacks
1. **Silent Client-Side Classification Fallback (`frontend/src/api.ts`):**
   When backend API calls fail or timeout, `api.ts` silently runs an in-browser keyword heuristic (`classifyInBrowser`) and writes results to `localStorage`. This completely masks backend failures, network disconnects, and server crashes from developers and users.
2. **Fabricated Integration Endpoints (`backend/app/routes/integrations.py`):**
   - The Jira export endpoint computes a fake issue key `f"BUG-{abs(hash(req.prediction_id)) % 9000 + 1000}"` and links to `https://jira.company.com/browse/...`. No outbound network request or Jira API call is made.
   - The Slack endpoint claims to dispatch a notification but merely returns a hardcoded `{ "success": True }` JSON payload.
3. **Fabricated Analytics Metrics (`backend/app/routes/analytics.py`):**
   - Fallback defaults for confidence and uncertainty (`0.88` and `0.038`) are returned when tables are empty.
   - Team accuracy is a completely static dictionary (`BL-101: 94.5%`, etc.) with no grounding in evaluation data.
   - The `daily_prediction_trend` returns static hardcoded data points for Monday through Sunday.
4. **Simulated Model Comparison (`backend/app/routes/compare.py`):**
   - The `/models/compare` endpoint passes an invalid argument `n_iter=20` to `model_manager.predict()`.
   - It synthetically adds `+0.04` to the confidence score and subtracts `0.01` from the uncertainty score to fabricate an improvement for a supposed "retrained active learning" model.
5. **Non-Persisted Settings (`frontend/src/pages/Settings/Settings.tsx`):**
   Toggles and thresholds give user feedback ("Saved!") via toast messages, but never make an HTTP request or persist to the database.

### 2.2 Machine Learning Misrepresentations & Inconsistencies
1. **Misleading Scientific Terminology:**
   - The UI, marketing text, and model metadata repeatedly reference "Monte Carlo Dropout variance" and deep learning uncertainty estimation.
   - In reality, the active production model is a linear `LogisticRegression` on TF-IDF features. Its probability outputs are standard softmax probabilities, not Monte Carlo dropout samples. The uncertainty score was simply `1.0 - confidence_score`.
2. **Inconsistent Team Catalogs:**
   - Frontend `api.ts` hardcodes a 6-team catalog (`BL-101`, `BL-102`, `BL-103`, `BL-106`, `BL-105`, `BL-110`).
   - Backend `model_manager.py` defines 10 teams (`BL-101` through `BL-110`).
   - Backend `models.py` contains a `Team` table with default seed values that may not match either.

### 2.3 Architecture & Security Deficits
1. **No Authentication or Authorization:**
   - No user login, registration, password hashing, session tokens, or JWTs.
   - Requests passed unvalidated dummy strings such as `user_id="user_1"`.
   - Anyone could access any route, trigger retraining, or override predictions without authentication.
2. **Missing Multi-Tenancy & Data Isolation:**
   - No concept of Organizations or Projects. All predictions were stored in a flat global table without tenant boundary isolation.
3. **Database Schema Evolution Debt:**
   - The application relied on `Base.metadata.create_all()` in `main.py` without Alembic migrations.
   - Foreign key constraints, audit trail tracking, and issue state transitions were either minimal or absent.
4. **Codebase Duplication:**
   - The repository maintained two parallel backends: `serving/` (synchronous FastAPI, older SQLite/Pega integration) and `backend/app/` (async FastAPI). The root test suite imported `serving.main`.
5. **Hardcoded Secrets & Infrastructure Smells:**
   - `k8s/deployment.yaml` contains `postgresql://bug_user:secure_password_123@postgres:5432/bug_classifier`.
   - Frontend had a hardcoded `http://localhost:8000/api/v1` base URL.
6. **Visual Over-Decoration:**
   - The existing frontend was loaded with heavy neon gradients, glassmorphism filters, glowing cards, and demo-oriented flair rather than clean, high-density, accessible engineering tools (e.g., Linear, GitHub Issues, Sentry).

---

## 3. Scope Exclusion: Removal of Batch & CSV Workflows

In accordance with strict scope requirements, all bulk ingestion, multi-issue classification, and CSV parsing/exporting are systematically removed from every layer of the application.

### Removal Inventory
| Layer | Target File / Symbol | Action Taken |
|---|---|---|
| **Frontend Page** | `frontend/src/pages/BatchUpload/` | **Deleted completely** |
| **Frontend Route** | `frontend/src/App.tsx` (`/batch` route) | **Removed** |
| **Frontend Nav** | `frontend/src/components/layout/Sidebar.tsx` | **Removed batch nav link** |
| **Frontend Client** | `frontend/src/api.ts` (`predictBatch`, CSV export) | **Removed completely** |
| **Backend Route** | `backend/app/routes/predict.py` (`POST /batch`) | **Removed completely** |
| **Backend Schema** | `backend/app/schemas.py` (`BatchPredictRequest/Response`) | **Removed completely** |
| **Legacy Serving** | `serving/main.py` (`POST /api/v1/predict/batch`) | **Removed / Retired** |
| **Backend Tests** | `backend/tests/test_predict.py` (`test_batch_prediction`) | **Removed** |
| **Data Training** | `data/demo_bug_reports.csv` | **Migrated to `data/training_dataset.jsonl`**; raw CSV archived safely |
| **Documentation** | `README.md`, `docs/API_DOCS.md` | **All batch/CSV references purged** |

*Note: Issue attachments (e.g. single log files, screenshots) for individual bug reports are preserved as genuine single-issue features.*

---

## 4. Rebuilt Architecture ("Triage")

### 4.1 Backend Architecture (FastAPI + SQLAlchemy 2.0 Async + PostgreSQL)
A modular monolith with clear domain boundaries:

```
backend/
├── alembic/                      # Version-controlled database migrations
│   ├── env.py
│   └── versions/
├── app/
│   ├── auth/                     # Password hashing (bcrypt), JWT generation, dependencies
│   ├── core/                     # App settings (Pydantic Settings), security, database session
│   ├── models/                   # Clean SQLAlchemy 2.0 async models
│   │   ├── organization.py       # Organizations, Projects, Teams, Memberships
│   │   ├── user.py               # Users, Roles (Org Admin, PM, Team Lead, Dev, QA, Viewer)
│   │   ├── issue.py              # Bug reports, Lifecycle status, Severity, Priority, Assignee
│   │   ├── triage.py             # Prediction records, Feedback, Review decisions
│   │   ├── comment.py            # Issue discussion and internal notes
│   │   ├── audit.py              # Immutable audit trail of state/assignment/review changes
│   │   └── integration.py        # External integration configurations & sync logs
│   ├── schemas/                  # Pydantic v2 validation contracts
│   ├── routes/                   # Clean REST endpoints
│   │   ├── auth.py               # Register, Login, Refresh, Me
│   │   ├── organizations.py      # Org/Project/Team administration & membership
│   │   ├── issues.py             # Single-issue CRUD, status transitions, assignments
│   │   ├── triage.py             # Single-issue ML prediction, review queue, override/approve
│   │   ├── comments.py           # Issue comments and audit notes
│   │   ├── analytics.py          # Real aggregate queries across actual issue data
│   │   ├── settings.py           # Organization and user persistent settings
│   │   ├── integrations.py       # Real GitHub integration (with graceful "Not configured" state)
│   │   └── models.py             # Model metadata, performance evaluation, retrain dispatch
│   ├── services/
│   │   ├── model_manager.py      # TF-IDF + Logistic Regression inference & keyword extraction
│   │   ├── fallback_engine.py    # Transparent deterministic keyword routing when model degraded
│   │   ├── dedup_engine.py       # Real text-similarity duplicate detection for incoming reports
│   │   ├── severity_engine.py    # Stack trace and keyword-based SLA/Severity heuristics
│   │   ├── github_service.py     # Real GitHub REST client for issue synchronization
│   │   └── training_service.py   # Training pipeline consuming JSONL datasets
│   └── main.py                   # FastAPI entrypoint, middleware, health & Prometheus metrics
```

### 4.2 Database Design & Multi-Tenancy
- **Organizations & Projects:** Top-level tenancy boundary. Every Issue, Team, and Prediction belongs to an Organization and Project.
- **RBAC Matrix:**
  - `ORG_ADMIN`: Full management of org, members, teams, model retraining, and integrations.
  - `PROJECT_MANAGER`: Project configuration, issue assignment, SLA monitoring.
  - `TEAM_LEAD`: Team triage review approval/override, team assignments.
  - `DEVELOPER`: Issue status transitions, comments, resolution.
  - `QA_REPORTER`: Issue creation, verification, reopening.
  - `VIEWER`: Read-only access to authorized projects.
- **Issue Lifecycle State Machine:**
  `NEW` → `TRIAGE` → `IN_PROGRESS` → `FIXED` → `VERIFICATION` → `CLOSED` (with `REOPENED` transition allowed).

### 4.3 Honest Machine Learning Engineering
- **Active Model:** Scikit-learn TF-IDF Vectorizer (n-gram 1-2, sublinear tf) + `LogisticRegression` (multinomial, L2 penalty).
- **Probability & Uncertainty:**
  - Prediction probability = max softmax class probability.
  - Uncertainty = normalized entropy / margin-based score (explicitly documented as model output confidence, NOT Monte Carlo Dropout variance).
  - High confidence (`>= 0.75`), Medium (`0.50 - 0.74`), Low (`< 0.50`). Low/Medium routes to Triage Review Queue.
- **Degraded Fallback:** If model artifacts are missing or unreadable, the system operates in transparent "Deterministic Rule Fallback" mode, clearly logged in telemetry and surfaced in the UI. Manual assignment is always supported.

### 4.4 Modern Frontend Architecture (React 18 + Vite + Tailwind + TanStack Query)
- **Design Philosophy:** Modeled after Linear and GitHub Issues. High-contrast typography, slate neutral color palette, purposeful status indicators (Red for P0, Amber for P1, Green for Fixed/Verification, Slate for Closed).
- **Zero Simulation:** All UI interactions hit live FastAPI endpoints with proper loading, validation, error, and empty states. No client-side mock storage or fake fallback.
- **Primary Screens:**
  1. **Auth & Onboarding:** Login, registration, organization/project selector.
  2. **Operational Overview:** Live metrics (open bugs, unassigned, triage queue depth, team workload, recent activity).
  3. **Issue Explorer:** Filterable, searchable, sorted, paginated table of bugs.
  4. **Create Issue:** Single-issue report form with live stack trace parsing and instant duplicate detection warnings.
  5. **Issue Detail:** Full bug view, status transitions, assignee/team controls, ML suggestion vs human confirmation, comments, activity timeline.
  6. **Triage Inbox:** Dedicated queue for low-confidence routing suggestions requiring human approval or override.
  7. **Analytics:** Honest, real-database aggregations (volume trends, team distributions, triage latency, human override rate).
  8. **Teams & Projects:** Real management of teams, members, and project assignments.
  9. **Settings:** Persisted user profile, notification rules, organization settings, and GitHub integration credentials.
  10. **Model Management:** Transparent view of active model version, vocabulary size, trained timestamp, accuracy metrics, and retraining trigger.

---

## 5. Implementation Roadmap

1. **Phase 1: Database & Persistence Foundation**
   - Implement SQLAlchemy models with multi-tenant org/project hierarchy.
   - Configure Alembic migrations.
   - Implement JWT authentication and RBAC dependency guards.
2. **Phase 2: Core Issue Lifecycle & Services**
   - Implement Issue CRUD with validated state transitions.
   - Implement Duplicate Detection and Stack Trace parsing.
   - Implement Comments and Audit Trail logging.
3. **Phase 3: Machine Learning & Triage Workflow**
   - Refactor Model Manager to consume JSONL datasets.
   - Implement Single-issue Triage Prediction and Review Queue endpoints.
   - Connect human override feedback to audit logging.
4. **Phase 4: Real Analytics & Real Integrations**
   - Build live database aggregation queries for Analytics.
   - Implement real GitHub Issues integration with verified error handling.
5. **Phase 5: Frontend Rebuild**
   - Rebuild clean UI components using Tailwind CSS and Lucide icons.
   - Implement TanStack Query clients connected to real APIs.
   - Build all 10 core screens.
6. **Phase 6: Testing & Quality Assurance**
   - Backend unit and integration tests (Auth, Issues, Triage, RBAC, Multi-tenancy, Negative Batch check).
   - Frontend build and linting validation.
   - Playwright end-to-end user journeys.
7. **Phase 7: Production Hardening, Docker & Documentation**
   - Update Dockerfile, Docker Compose, and CI workflows.
   - Finalize complete documentation suite.
