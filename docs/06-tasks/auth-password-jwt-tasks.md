# Implementation Task Breakdown: Password Authentication and JWT Authorization

## Overview

Implement the `auth-password-jwt` slice on top of the verified `repo-bootstrap` foundation. The outcome is local password login, JWT access sessions, Admin account lifecycle, server-side current-role authorization, and a minimal frontend session plus Admin account surface.

**Planning assumptions:**

- The slice is not approved for coding until OQ-AUTH-001 through OQ-AUTH-005 are accepted or explicitly defaulted, and proposed ADR-0006 is accepted or amended.
- No knowledge, model, upload, provider, audit, or SSO capability is added.
- All database changes use Alembic and start from revision `20260726_0001`.
- The health-probe exception from ADR-0005 remains intact.
- An execution manifest must exist before any async or cross-session coding session starts.

## Source Design

- `docs/05-design/auth-password-jwt-design.md`
- `docs/05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md`
- `docs/04-architecture/auth-password-jwt-data-model.md`
- `docs/03-spec/auth-password-jwt-spec.md`
- `docs/00-context/decisions/ADR-0006-pilot-auth-security-defaults.md`

## Workstreams

1. Resolve owner/security defaults and freeze the auth contract.
2. Create the execution-manifest handoff package before coding.
3. Add User migration and repository boundary.
4. Add password/JWT adapters and authentication services.
5. Add API routes and Admin lifecycle authorization.
6. Add frontend session, login, and Admin account surfaces.
7. Verify security, role matrix, migration, and Compose smoke.
8. Archive the change package after verify.

The critical path is TASK-AUTH-001 → TASK-AUTH-008 → TASK-AUTH-002 → TASK-AUTH-003 → TASK-AUTH-004 → TASK-AUTH-005 → TASK-AUTH-007. Frontend login work may begin after TASK-AUTH-004; Admin UI work requires TASK-AUTH-005. Verification follows backend and frontend completion. Archive is last.

## Task Breakdown by Domain

### Contract and Security

- Accept password, JWT, bootstrap, identifier, browser-storage, hasher, and last-Admin defaults.
- Accept or amend ADR-0006 before apply.

### Handoff

- Create a schema-valid execution manifest and freshness-gate record before coding.

### Persistence

- Add User schema, constraints, migration, and repository operations.

### Backend / API

- Add password/JWT adapters, authentication service, current-user dependency, Admin account service, bootstrap path, and routes.

### Frontend / UI

- Extend typed client, session store, login view, route guard, and Admin user view.

### Testing / Verification

- Cover success, failure, authorization, deactivation, role change, last-Admin protection, redaction, migration, build, and Compose smoke.

## Task Details

### TASK-AUTH-001: Accept and Pin Authentication Defaults

- **Objective:** Remove implementation ambiguity before code starts.
- **Scope:** Confirm or amend password policy and login-validation semantics, first-Admin bootstrap env/concurrency/failure contract, JWT lifetime/algorithm/key source/claims, browser token storage, identifier normalization, Argon2id hashing baseline, internal user ID type, mandatory `auth_version`, request-error envelope, and last-Admin protection; accept or amend ADR-0006; update this SDD set if amended.
- **Dependencies:** None.
- **Owner type:** product / security / architecture
- **Priority:** Must
- **Verification:** Written approval or accepted ADR-0006 references all OQ-AUTH decisions and the security defaults above.
- **Definition of done:** No implementation-impacting auth default remains unowned or deferred.

### TASK-AUTH-008: Prepare Implementation Handoff Package

- **Objective:** Make the approved slice durable for a separate implementation session before coding begins.
- **Scope:** Create a dated change package and schema-valid execution manifest referencing the approved auth documents, ADR-0006 (accepted/amended), allowed/forbidden paths, verification commands, out-of-scope list, and stop conditions. Record a freshness-gate pass against the pinned docs/code commit.
- **Dependencies:** TASK-AUTH-001; product-owner acceptance of the auth SDD set.
- **Owner type:** documentation / platform
- **Priority:** Must
- **Verification:** Manifest validates against `docs/00-context/execution-manifest.schema.json`; freshness-gate passes against the pinned docs/code commit.
- **Definition of done:** A future coding session can start from the manifest without chat-only context. No application code for this slice is written before this task completes for async/cross-session work.

### TASK-AUTH-002: Add User Migration and Repository Boundary

- **Objective:** Persist the local identity and current authorization state.
- **Scope:** User entity/table, role/status constraints, normalized identifier uniqueness, nullable external subject, mandatory auth version, timestamps, safe projections, and repository queries/mutations.
- **Dependencies:** TASK-AUTH-001, TASK-AUTH-008.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** Alembic upgrade/reapply from `20260726_0001`; repository tests for create/list/unique conflict/status/role changes; no unrelated business tables.
- **Definition of done:** User persistence is transactional, migration-aligned, and secret-safe.

### TASK-AUTH-003: Implement Password and JWT Adapters

- **Objective:** Isolate cryptographic/provider details behind replaceable boundaries.
- **Scope:** Argon2id password hash/verify adapter, JWT issue/verify adapter, runtime key configuration, expiry/`auth_version` claims, algorithm validation, and safe failure mapping.
- **Dependencies:** TASK-AUTH-001, TASK-AUTH-002.
- **Owner type:** backend / security
- **Priority:** Must
- **Verification:** Unit tests for valid/invalid password, malformed hash, expiry, signature, subject, algorithm, auth version mismatch, and missing key.
- **Definition of done:** No password/JWT library types leak into repositories or UI; no secret is logged.

### TASK-AUTH-004: Implement Authentication and Current-User API

- **Objective:** Enable login, bootstrap, and protected current-user resolution.
- **Scope:** Login request/response, generic authentication failures, first-Admin env bootstrap path, bearer parsing, current-user endpoint, shared active-user dependency with mandatory `auth_version` check, P0 envelope integration, and health exception preservation.
- **Dependencies:** TASK-AUTH-003.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** API tests for login, request-validation envelope, bootstrap-once and concurrent-start behavior, missing/invalid bootstrap configuration, `/auth/me`, `401`, deactivation, token expiry, auth-version mismatch after reactivation, and health probe access without token.
- **Definition of done:** Active users can obtain and use a token; invalid/inactive/version-mismatched sessions fail closed; bootstrap cannot recreate Admin after one exists.

### TASK-AUTH-005: Implement Admin Account Lifecycle and Role Authorization

- **Objective:** Let Admins control account state and role without bricking the system.
- **Scope:** Admin list/create/update routes, role dependency, safe user projections, conflict/validation mapping, role change next-check behavior, deactivation `auth_version` invalidation, and last-Admin demotion/deactivation rejection.
- **Dependencies:** TASK-AUTH-004.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** Role matrix tests for Admin/Editor/Viewer, create/list/update/deactivate/reactivate flows, forbidden data access, serialized last-Admin protection, and exactly-one-role persistence.
- **Definition of done:** Admin operations are server-authorized and the current role/status is authoritative.

### TASK-AUTH-006: Add Frontend Session, Login, And Admin Surfaces

- **Objective:** Provide a safe browser session experience and Admin account UI.
- **Scope:** Typed auth API methods, in-memory/`sessionStorage` token handling (never `localStorage`), login view, current-user restore, logout, `401` session clearing, `403` forbidden state, role-aware route usability guards, and Admin user list/create/update UI that calls the Admin API only.
- **Dependencies:** TASK-AUTH-004 for login/session; TASK-AUTH-005 for Admin account UI.
- **Owner type:** frontend
- **Priority:** Must
- **Verification:** Typecheck/build and UI tests for loading, success, generic error, restore, logout, `401`, `403`, and Admin list/create/update happy paths with non-Admin route hiding.
- **Definition of done:** Frontend never logs/stores credentials in forbidden locations, does not use `localStorage` for access tokens, and does not claim authorization by hiding UI alone.

### TASK-AUTH-007: Add Security, Migration, and Integrated Verification

- **Objective:** Prove the complete identity vertical slice.
- **Scope:** Redaction regression tests, API integration tests, migration upgrade/reapply, Compose startup, browser smoke, last-Admin and auth-version tests, and scope-drift scan.
- **Dependencies:** TASK-AUTH-002 through TASK-AUTH-006.
- **Owner type:** QA / backend / frontend / security / devops
- **Priority:** Must
- **Verification:** `cd backend && pytest`; `cd frontend && npm run build`; Alembic upgrade twice; `docker compose -f deploy/docker-compose.yml config`; Compose live/ready; login/current-user/admin role smoke.
- **Definition of done:** All required checks pass, no secret/corpus is added, and evidence is recorded in the change review before archive.

### TASK-AUTH-009: Archive Implementation Change Package

- **Objective:** Freeze the verified outcome for later slices and audits.
- **Scope:** Write `archive.md`, set manifest status to `archived`, record residual risks, and add any new observed lessons.
- **Dependencies:** TASK-AUTH-007.
- **Owner type:** documentation / platform
- **Priority:** Must
- **Verification:** Archive links verification evidence; manifest status is `archived`; no chat-only closure.
- **Definition of done:** The change package is durable without relying on chat history.

## Dependency Plan

- **Critical path:** TASK-AUTH-001 → TASK-AUTH-008 → TASK-AUTH-002 → TASK-AUTH-003 → TASK-AUTH-004 → TASK-AUTH-005 → TASK-AUTH-007 → TASK-AUTH-009.
- **Parallel work:** Frontend login/session scaffolding may begin after TASK-AUTH-004; Admin UI requires TASK-AUTH-005; security test planning can run alongside TASK-AUTH-005.
- **Blocking decision:** Do not begin implementation if TASK-AUTH-001, TASK-AUTH-008, or freshness-gate is incomplete.

```text
TASK-AUTH-001
    └─► TASK-AUTH-008
            └─► TASK-AUTH-002
                    └─► TASK-AUTH-003
                            └─► TASK-AUTH-004 ─┬─► TASK-AUTH-005 ─┬─► TASK-AUTH-006
                                               │                 │
                                               └─────────────────┴─► TASK-AUTH-007
                                                                         └─► TASK-AUTH-009
```

## Risks / Blockers

- First-Admin bootstrap remains a high-impact operational dependency until ADR-0006 is accepted.
- Token algorithm/key rotation is a security decision recorded in ADR-0006, not a coding detail.
- Browser storage choice affects XSS/session persistence and must stay aligned with frontend standards.
- Audit records are required by the overall product but are intentionally deferred; later audit work must consume account-operation facts without secrets.

## Open Questions

- OQ-AUTH-001 through OQ-AUTH-005 in the requirements document.
- ADR-0006 must be accepted or amended before TASK-AUTH-008 completes.
