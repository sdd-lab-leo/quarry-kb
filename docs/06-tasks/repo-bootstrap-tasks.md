# Implementation Task Breakdown: Repository Bootstrap

## Overview

Implement the first runnable Quarry KB foundation: Compose services, FastAPI health/readiness, PostgreSQL/pgvector migration baseline, Vue shell, and safe gateway configuration boundaries.

**Delivery objective:** A clean checkout can run the documented local smoke path without live model credentials or real documents.

**Planning assumptions:**

- The repository is greenfield.
- Alembic is the migration tool required by the backend standard.
- Plain Vue/CSS is used until a UI-library ADR exists.
- OQ-09 values are not needed for bootstrap-only tests; `.env.example` uses `gateway.internal` on the default allowlist.
- Compose path is `deploy/docker-compose.yml`.

## Source Design

- **System:** `repo-bootstrap`
- **Design:** `docs/05-design/repo-bootstrap-design.md`
- **API guide:** `docs/05-design/contracts/repo-bootstrap-API_IMPLEMENTATION_GUIDE.md`
- **Architecture:** `docs/04-architecture/repo-bootstrap-architecture.md`

## Workstreams

1. Runtime and configuration foundation.
2. Database and migration foundation.
3. API health boundary.
4. Frontend shell and typed client.
5. Integrated verification.

Tasks 001 and 002 can begin in parallel. Task 003 depends on 001 and 002. Task 004 depends on 003. Task 005 depends on 001–004.

## Task Breakdown by Domain

### Runtime / Configuration

- Compose topology and health checks.
- Environment template and secret-safe settings validation.
- Internal-only embedding/OCR host policy (literal allowlist match).

### Persistence / Migration

- PostgreSQL/pgvector service and baseline migration.
- Migration and vector readiness reporting.

### Backend / API

- FastAPI shell and liveness/readiness endpoints.
- Stable response envelope and safe failure codes.

### Frontend / UI

- Vue shell, typed readiness client, and status states.

### Testing / Verification

- Unit, integration, migration, build, and Compose smoke checks.

## Task Details

### TASK-001: Establish Runtime Configuration And Compose Topology

- **Objective:** Provide `web`, `api`, and `postgres` services with documented local startup and health-check wiring.
- **Scope:** `deploy/docker-compose.yml`, service environment wiring, local volume boundary, Compose-network probe consumption, and non-secret `.env.example` including default allowlist (`gateway.internal`) plus chat/embedding/OCR placeholders.
- **Dependencies:** None.
- **Owner type:** platform / devops
- **Priority:** Must
- **Notes:** Do not add real secrets, real documents, or a live gateway requirement. Traceability: `REQ-BOOT-001`, `REQ-BOOT-005`, `REQ-BOOT-006`, `REQ-BOOT-008`.
- **Definition of done:** Compose configuration validates; services have documented health behavior; `.env.example` contains placeholders only and an allowlist that accepts the placeholder host.

### TASK-002: Add PostgreSQL/pgvector Baseline And Migration Boundary

- **Objective:** Make the database capability and migration baseline repeatable.
- **Scope:** PostgreSQL/pgvector service choice, Alembic configuration, baseline migration that enables the `vector` extension and records revision metadata, vector capability validation, and migration command documentation. No business tables.
- **Dependencies:** None.
- **Owner type:** backend / platform
- **Priority:** Must
- **Notes:** Do not create user, document, chunk, session, message, citation, or audit tables. Traceability: `REQ-BOOT-002`, `REQ-BOOT-003`.
- **Definition of done:** Fresh database migration succeeds and enables `vector`; reapplication is safe; missing vector capability is surfaced; no business tables exist.

### TASK-003: Implement API Settings And Health Endpoints

- **Objective:** Expose truthful liveness and readiness using the API guide.
- **Scope:** Typed settings loading, literal embedding/OCR allowlist validation (no DNS), safe redaction, response envelope, `/api/v1/health/live`, and `/api/v1/health/ready` with HTTP 200 ready / HTTP 503 not-ready component payloads.
- **Dependencies:** TASK-001, TASK-002.
- **Owner type:** backend / security
- **Priority:** Must
- **Notes:** Readiness must not call chat, embedding, or OCR. Traceability: `REQ-BOOT-003`, `REQ-BOOT-006`, `REQ-BOOT-007`, `REQ-BOOT-010`.
- **Definition of done:** Endpoint behavior passes ready (200), database-down (503), migration-pending (503), vector-missing (503), and invalid-config (503) cases with component diagnostics and without leaking secrets.

### TASK-004: Implement Vue Shell And Typed Health Client

- **Objective:** Render the frontend shell and show normalized API foundation state.
- **Scope:** Vue application shell, single typed API client, `loading` / `ready` / `needs_attention` / `unreachable` states, and plain CSS variables.
- **Dependencies:** TASK-003.
- **Owner type:** frontend
- **Priority:** Must
- **Notes:** Do not implement login, auth guards, functional Ask/Knowledge/Admin views, or an unapproved UI library. Traceability: `REQ-BOOT-004`, `REQ-BOOT-009`.
- **Definition of done:** Production build succeeds; shell maps HTTP 200 → Ready, HTTP 503 → Needs attention, transport failure → Unable to reach API.

### TASK-005: Add Foundation Verification Loop

- **Objective:** Prove the vertical bootstrap path from Compose to browser readiness display.
- **Scope:** Backend tests, configuration policy tests, API integration tests, migration upgrade/reapply smoke, frontend build, Compose validation for `deploy/docker-compose.yml`, and frontend-to-backend readiness smoke.
- **Dependencies:** TASK-001, TASK-002, TASK-003, TASK-004.
- **Owner type:** QA / backend / frontend / devops
- **Priority:** Must
- **Notes:** Tests use fake/local dependencies and mock configuration; no paid model or real company data. Traceability: `REQ-BOOT-009`, `AC-BOOT-01` through `AC-BOOT-07`.
- **Definition of done:** All documented verification commands pass or failures are recorded with actionable evidence; no real secrets or corpora are introduced.

### TASK-006: Update Bootstrap Documentation And Traceability

- **Objective:** Keep runtime instructions, API guide, task mapping, and P0 context aligned.
- **Scope:** README/local startup references, task-to-requirement mapping, unresolved OQ status, and verification evidence placeholders.
- **Dependencies:** TASK-001 through TASK-005.
- **Owner type:** devops / documentation
- **Priority:** Should
- **Notes:** Do not mark P0 or P1 complete until the stage gate evidence exists. Traceability: `REQ-BOOT-001` through `REQ-BOOT-010`.
- **Definition of done:** A new contributor can follow the documented path and identify any unresolved OQ without relying on chat history.

## Dependency Plan

- **Critical path:** TASK-001 + TASK-002 → TASK-003 → TASK-004 → TASK-005 → TASK-006.
- **Prerequisite cluster:** TASK-001 and TASK-002 establish runtime and persistence foundations in parallel.
- **Parallel work:** Configuration and Compose work can proceed alongside the migration baseline; frontend shell work starts after the API contract is fixed.

## Risks / Blockers

- OQ-BOOT-02: unpinned PostgreSQL/pgvector image tag can weaken reproducibility.
- OQ-BOOT-01: probe exposure may require deployment changes after the initial local path.
- OQ-09: live gateway smoke tests remain outside bootstrap until concrete values are supplied.

## Open Questions

1. Which PostgreSQL/pgvector image tag is approved?
2. Should probes use a private management port?
3. When will exact gateway URLs, models, OCR path, and rate limits be available?
