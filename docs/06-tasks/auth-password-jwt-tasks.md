# Implementation Task Breakdown: Password Authentication and JWT Authorization

## Overview

Implement the `auth-password-jwt` slice on top of the verified `repo-bootstrap` foundation. The outcome is local password login, JWT access sessions, Admin account lifecycle, server-side current-role authorization, and a minimal frontend session surface.

**Planning assumptions:**

- The slice is not approved for coding until OQ-AUTH-001 through OQ-AUTH-005 are accepted or explicitly defaulted.
- No knowledge, model, upload, provider, audit, or SSO capability is added.
- All database changes use Alembic and start from revision `20260726_0001`.
- The health-probe exception from ADR-0005 remains intact.

## Source Design

- `docs/05-design/auth-password-jwt-design.md`
- `docs/05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md`
- `docs/04-architecture/auth-password-jwt-data-model.md`
- `docs/03-spec/auth-password-jwt-spec.md`

## Workstreams

1. Resolve owner/security defaults and freeze the auth contract.
2. Add User migration and repository boundary.
3. Add password/JWT adapters and authentication services.
4. Add API routes and Admin lifecycle authorization.
5. Add frontend session and Admin account surfaces.
6. Verify security, role matrix, migration, and Compose smoke.

The critical path is TASK-AUTH-001 → TASK-AUTH-002 → TASK-AUTH-003 → TASK-AUTH-004 → TASK-AUTH-007. Frontend work can begin after the API guide is accepted; verification follows backend and frontend completion.

## Task Breakdown by Domain

### Contract and Security

- Accept password, JWT, bootstrap, identifier, and browser-storage defaults.
- Record any material change in an ADR before apply.

### Persistence

- Add User schema, constraints, migration, and repository operations.

### Backend / API

- Add password/JWT adapters, authentication service, current-user dependency, Admin account service, and routes.

### Frontend / UI

- Extend typed client, session store, login, route guard, and Admin user view.

### Testing / Verification

- Cover success, failure, authorization, deactivation, role change, redaction, migration, build, and Compose smoke.

## Task Details

### TASK-AUTH-001: Accept and Pin Authentication Defaults

- **Objective:** Remove implementation ambiguity before code starts.
- **Scope:** Confirm or amend password policy, first-Admin bootstrap, JWT lifetime/algorithm, browser token storage, and identifier normalization; update this SDD set and ADR if needed.
- **Dependencies:** None.
- **Owner type:** product / security / architecture
- **Priority:** Must
- **Verification:** Written approval or accepted ADR references all five OQ-AUTH decisions.
- **Definition of done:** No implementation-impacting auth default remains unowned or deferred.

### TASK-AUTH-002: Add User Migration and Repository Boundary

- **Objective:** Persist the local identity and current authorization state.
- **Scope:** User entity/table, role/status constraints, normalized identifier uniqueness, nullable external subject, auth version, timestamps, safe projections, and repository queries/mutations.
- **Dependencies:** TASK-AUTH-001.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** Alembic upgrade/reapply from `20260726_0001`; repository tests for create/list/unique conflict/status/role changes; no unrelated business tables.
- **Definition of done:** User persistence is transactional, migration-aligned, and secret-safe.

### TASK-AUTH-003: Implement Password and JWT Adapters

- **Objective:** Isolate cryptographic/provider details behind replaceable boundaries.
- **Scope:** Password hash/verify adapter, JWT issue/verify adapter, runtime key configuration, expiry/auth-version claims, algorithm validation, and safe failure mapping.
- **Dependencies:** TASK-AUTH-001, TASK-AUTH-002.
- **Owner type:** backend / security
- **Priority:** Must
- **Verification:** Unit tests for valid/invalid password, malformed hash, expiry, signature, subject, algorithm, auth version, and missing key.
- **Definition of done:** No password/JWT library types leak into repositories or UI; no secret is logged.

### TASK-AUTH-004: Implement Authentication and Current-User API

- **Objective:** Enable login and protected current-user resolution.
- **Scope:** Login request/response, generic authentication failures, bearer parsing, current-user endpoint, shared active-user dependency, P0 envelope integration, and health exception preservation.
- **Dependencies:** TASK-AUTH-003.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** API tests for login, `/auth/me`, `401`, deactivation, token expiry, and health probe access without token.
- **Definition of done:** Active users can obtain and use a token; invalid/inactive sessions fail closed.

### TASK-AUTH-005: Implement Admin Account Lifecycle and Role Authorization

- **Objective:** Let Admins control account state and role.
- **Scope:** Admin list/create/update routes, role dependency, safe user projections, conflict/validation mapping, role change next-check behavior, and deactivation auth-version invalidation.
- **Dependencies:** TASK-AUTH-004.
- **Owner type:** backend
- **Priority:** Must
- **Verification:** Role matrix tests for Admin/Editor/Viewer, create/list/update/deactivate/reactivate flows, and forbidden data access.
- **Definition of done:** Admin operations are server-authorized and the current role/status is authoritative.

### TASK-AUTH-006: Add Frontend Session and Login Surface

- **Objective:** Provide a safe browser session experience.
- **Scope:** Typed auth API methods, in-memory/session storage, login view, current-user restore, logout, `401` session clearing, `403` forbidden state, and role-aware route usability guards.
- **Dependencies:** TASK-AUTH-004; API contract accepted.
- **Owner type:** frontend
- **Priority:** Must
- **Verification:** Typecheck/build and UI tests for loading, success, generic error, restore, logout, `401`, and `403`.
- **Definition of done:** Frontend never logs/stores credentials in forbidden locations and does not claim authorization by hiding UI alone.

### TASK-AUTH-007: Add Security, Migration, and Integrated Verification

- **Objective:** Prove the complete identity vertical slice.
- **Scope:** Redaction regression tests, API integration tests, migration upgrade/reapply, Compose startup, browser smoke, and scope-drift scan.
- **Dependencies:** TASK-AUTH-002 through TASK-AUTH-006.
- **Owner type:** QA / backend / frontend / security / devops
- **Priority:** Must
- **Verification:** `cd backend && pytest`; `cd frontend && npm run build`; Alembic upgrade twice; `docker compose -f deploy/docker-compose.yml config`; Compose live/ready; login/current-user/admin role smoke.
- **Definition of done:** All required checks pass, no secret/corpus is added, and evidence is recorded in a change review before handoff.

### TASK-AUTH-008: Prepare Implementation Handoff Package

- **Objective:** Make the approved slice durable for a separate implementation session.
- **Scope:** Create a dated change package and schema-valid execution manifest referencing the approved auth documents, allowed/forbidden paths, verification commands, and stop conditions.
- **Dependencies:** TASK-AUTH-001 through TASK-AUTH-007; product-owner acceptance.
- **Owner type:** documentation / platform
- **Priority:** Must
- **Verification:** Manifest validates against `docs/00-context/execution-manifest.schema.json`; freshness-gate passes against the pinned docs/code commit.
- **Definition of done:** A future coding session can start from the manifest without chat-only context.

## Dependency Plan

- **Critical path:** TASK-AUTH-001 → TASK-AUTH-002 → TASK-AUTH-003 → TASK-AUTH-004 → TASK-AUTH-005 → TASK-AUTH-007 → TASK-AUTH-008.
- **Parallel work:** Frontend contract scaffolding may begin after TASK-AUTH-004 is accepted; security test planning can run alongside TASK-AUTH-005.
- **Blocking decision:** Do not begin implementation if TASK-AUTH-001 or freshness-gate is incomplete.

## Risks / Blockers

- First-Admin bootstrap is a high-impact operational dependency.
- Token algorithm/key rotation is a security decision, not a coding detail.
- Browser storage choice affects XSS/session persistence and must be accepted.
- Audit records are required by the overall product but are intentionally deferred; later audit work must consume account-operation facts without secrets.

## Open Questions

- OQ-AUTH-001 through OQ-AUTH-005 in the requirements document.
- Whether an explicit auth security ADR is needed after owner confirmation of JWT algorithm/key rotation.
