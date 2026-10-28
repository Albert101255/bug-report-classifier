# Security Architecture & Hardening Guide

## 1. Authentication & Session Security

- **JWT Tokens**: Authenticated sessions utilize HMAC-SHA256 signed JSON Web Tokens (`HS256`).
- **Signature Verification**: Tokens are cryptographically validated on every protected endpoint through FastAPI dependencies.
- **Expiration**: Standard token lifetime is 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`).
- **Password Storage**: Passwords are never stored in plaintext. They are salted and hashed using `bcrypt` (work factor 12).
- **Client Storage**: Tokens are stored in browser session storage/localStorage and dispatched via `Authorization: Bearer <token>` HTTP headers.

---

## 2. Role-Based Access Control (RBAC)

The platform enforces strict role boundaries:

| Role | Permissions |
|---|---|
| `ORG_ADMIN` | Full administrative control: manage organization settings, invite members, configure GitHub credentials, view all projects and audit events. |
| `TEAM_LEAD` | Create and edit issues, assign issues to teams, approve or override triage predictions in review queue, post comments, trigger retraining. |
| `ENGINEER` | Report new bugs, transition issue state (`IN_PROGRESS`, `FIXED`, `VERIFICATION`), add technical logs and comments. |
| `VIEWER` | Read-only access to issues, triage feeds, and analytics dashboards. |

Role enforcement is enforced server-side via `require_role(...)` dependency guards in `backend/app/auth/dependencies.py`.

---

## 3. Multi-Tenant Organization Isolation

- Every project, team, issue, comment, prediction, and audit event contains a mandatory foreign key to `organization_id`.
- The authenticated user's organization is extracted directly from the validated JWT payload.
- All database queries filter explicitly by `organization_id`, preventing cross-tenant information disclosure.

---

## 4. Elimination of Batch/CSV Attack Surfaces

Legacy bug tracking tools often suffer from serious vulnerability vectors tied to CSV processing:
1. **CSV Injection (Formula Injection)**: Untrusted bug descriptions starting with `=`, `+`, `-`, or `@` can execute arbitrary commands when exported to spreadsheet software.
2. **Denial of Service (DoS)**: Unbounded batch ingestion files consume worker memory, tie up database connections, and starve API threads.
3. **Audit Trail Evasion**: Bulk uploads frequently bypass per-issue validation and attribution.

**By eliminating CSV and batch workflows entirely**, Triage eliminates these attack surfaces at the architectural level. Every defect is validated individually through typed Pydantic schemas.

---

## 5. Kubernetes & Secret Hardening

- Plaintext credentials have been purged from Kubernetes manifests (`k8s/deployment.yaml`).
- All sensitive variables (`DATABASE_URL`, `JWT_SECRET_KEY`, `REDIS_URL`, `ADMIN_API_KEY`) are injected via Kubernetes `Secret` resources or container environment variables.
- Containers run as non-root users (`USER app`).
