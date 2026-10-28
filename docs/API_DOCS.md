# Triage Platform API Reference

All requests must use JSON payloads where applicable. Protected endpoints require the `Authorization: Bearer <jwt_token>` header.

> [!IMPORTANT]
> **Negative Scope Notice**: Triage is strictly single-issue-first. All legacy batch routes (`/api/v1/predict/batch`, `/api/v1/issues/import`, and bulk endpoints) have been permanently decommissioned and return `404 Not Found`.

---

## 1. Authentication & Accounts

### `POST /api/v1/auth/register`
Create a new user account, organization workspace, default project, and seed engineering teams.
- **Request Body**:
  ```json
  {
    "email": "engineer@company.com",
    "password": "SecurePassword123!",
    "full_name": "Ada Lovelace",
    "organization_name": "Acme Engineering",
    "role": "ORG_ADMIN"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "c1f7a0b3-...",
      "email": "engineer@company.com",
      "full_name": "Ada Lovelace",
      "role": "ORG_ADMIN",
      "is_active": true
    }
  }
  ```

### `POST /api/v1/auth/login`
Authenticate with email and password to receive a JWT session token.
- **Request Body**:
  ```json
  {
    "email": "engineer@company.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response `200 OK`**: Returns `TokenResponse` with JWT access token.

### `GET /api/v1/auth/me`
Retrieve profile of currently authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: User profile object.

---

## 2. Organizations, Projects & Teams

### `GET /api/v1/orgs/me`
Retrieve organization profile, active members, and settings for the authenticated tenant.

### `GET /api/v1/orgs/projects`
List projects belonging to the current organization.

### `POST /api/v1/orgs/projects`
Create a new project workspace within the organization.
- **Request Body**:
  ```json
  {
    "name": "Billing Service",
    "key": "BILL",
    "description": "Payment workflows and subscription engine"
  }
  ```

### `GET /api/v1/orgs/teams`
List engineering teams configured for triage routing in this organization.

### `POST /api/v1/orgs/teams`
Create a new team.
- **Request Body**:
  ```json
  {
    "code": "BL-111",
    "name": "BL-111 (Mobile Platform)",
    "description": "iOS and Android client applications",
    "category": "Mobile"
  }
  ```

---

## 3. Issues (Single-Defect Workflow)

### `POST /api/v1/issues/`
Report and automatically triage an individual software defect.
- **Request Body**:
  ```json
  {
    "title": "PostgreSQL connection pool exhausted under concurrent load",
    "description": "Connections hit max 100 with timeout in auth service after 30000ms.",
    "project_id": "c71a39f0-...",
    "severity": "P0 - Blocker",
    "priority": "URGENT",
    "environment": "Production",
    "steps_to_reproduce": "1. Run 50 auth requests\n2. Observe pool timeout",
    "technical_logs": "sqlalchemy.exc.TimeoutError: QueuePool limit reached",
    "team_id": null
  }
  ```
- **Response `201 Created`**: Returns full `IssueOut` record including assigned team, calculated SLA hours, and initial audit trail.

### `GET /api/v1/issues/`
Query and filter individual bug reports.
- **Query Parameters**:
  - `project_id` (UUID, optional)
  - `status` (NEW, TRIAGE, IN_PROGRESS, FIXED, VERIFICATION, CLOSED, REOPENED)
  - `team_id` (UUID, optional)
  - `priority` (LOW, MEDIUM, HIGH, URGENT)
  - `search` (text search in title and description)
  - `skip` (int, default 0), `limit` (int, default 50)

### `GET /api/v1/issues/{issue_id}`
Retrieve complete detail of a single issue, including comments, recommendations, and audit history.

### `PATCH /api/v1/issues/{issue_id}`
Update issue status, assigned team, severity, or priority. Validates state machine rules and records audit events.
- **Request Body**:
  ```json
  {
    "status": "IN_PROGRESS",
    "team_id": "848e4266-..."
  }
  ```

### `POST /api/v1/issues/{issue_id}/comments`
Post an engineering note or investigation finding to the defect thread.
- **Request Body**:
  ```json
  {
    "content": "Root cause confirmed: connection overflow was set to 0."
  }
  ```

### `GET /api/v1/issues/{issue_id}/audit`
Retrieve the complete immutable timeline of actions for this defect.

---

## 4. Intelligent Triage & Review

### `POST /api/v1/triage/predict`
Perform real-time single-issue classification preview without persisting a defect record.
- **Request Body**:
  ```json
  {
    "subject": "Null pointer in payment stripe webhook parser",
    "description": "Exception raised on event handler processing invoice.payment_succeeded"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "predicted_team": "BL-104 (Payment Gateway & Billing)",
    "confidence_score": 0.824,
    "confidence_level": "HIGH",
    "uncertainty_score": 0.176,
    "engine": "tfidf-logreg",
    "processing_time_ms": 3.42,
    "sla_hours": 8,
    "potential_duplicates": [],
    "stacktrace_analysis": {
      "has_trace": true,
      "detected_exception": "NullPointerException",
      "source_file": "webhook.py",
      "line_number": 42
    }
  }
  ```

### `GET /api/v1/triage/review-queue`
Retrieve predictions marked as `PENDING` review due to low confidence or high uncertainty.

### `POST /api/v1/triage/review/{prediction_id}/approve`
Approve the model's recommended team. Updates issue routing and marks prediction verified.

### `POST /api/v1/triage/review/{prediction_id}/override`
Override the recommendation with an engineer-specified team and justification.
- **Request Body**:
  ```json
  {
    "corrected_team": "BL-106 (API Gateway & Microservices)",
    "reason": "Gateway deserialization bug rather than payment service defect"
  }
  ```

---

## 5. Analytics & Metrics

### `GET /api/v1/analytics/overview`
Returns real, computed database metrics for the organization.
- **Response `200 OK`**:
  ```json
  {
    "total_issues": 142,
    "open_issues": 38,
    "triaged_issues": 104,
    "pending_review_count": 6,
    "blocker_critical_count": 12,
    "team_distribution": [
      { "team_name": "BL-102 (Database & ORM)", "issue_count": 28 },
      { "team_name": "BL-101 (Authentication & AuthZ)", "issue_count": 24 }
    ],
    "volume_by_day": [
      { "date": "2026-10-22", "count": 14 },
      { "date": "2026-10-23", "count": 19 }
    ],
    "avg_confidence": 0.742,
    "human_override_rate": 0.083
  }
  ```

---

## 6. Workspace Settings & Integrations

### `GET /api/v1/settings/org` & `PATCH /api/v1/settings/org`
Fetch and persist organizational triage rules, confidence thresholds, and auto-assignment policies.

### `GET /api/v1/integrations/github/config` & `POST /api/v1/integrations/github/configure`
Configure target GitHub repository (`owner/repo`) and personal access token.

### `POST /api/v1/integrations/github/sync/{issue_id}`
Synchronize a single verified internal defect to the configured GitHub repository.
