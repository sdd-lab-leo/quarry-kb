# User Stories: Repository Bootstrap

## Document Control

| Field | Value |
|---|---|
| Slice | `repo-bootstrap` |
| Status | Accepted |
| Date | 2026-07-26 |
| Source | `docs/01-requirements/repo-bootstrap-requirement.md` |

## User Story US-BOOT-001: Start The Foundation Locally

**Story:**  
As a developer,  
I want to start the documented Quarry KB services locally,  
so that I can verify the product foundation before feature work begins.

### Acceptance Criteria

1. **Given** the documented prerequisites are installed, **when** the developer runs `docker compose -f deploy/docker-compose.yml up --build`, **then** `web`, `api`, and `postgres` start and report their health state.
2. **Given** no real secret file is committed, **when** the services start with placeholder or local configuration, **then** startup does not require a source-controlled credential.
3. **Given** one service fails to start, **when** the developer inspects the documented verification output, **then** the failed dependency is identifiable without exposing secrets.

## Notes / Assumptions

- The repository is greenfield and has no existing service behavior to preserve.
- The local Compose flow is the first supported runtime.

## Dependencies

- `REQ-BOOT-001`, `REQ-BOOT-002`, `REQ-BOOT-009`
- ADR-0002

## Out of Scope

- Production rollout and orchestration.
- Authentication and business features.

## Open Questions

- Approved PostgreSQL/pgvector image tag remains open as `OQ-BOOT-02`.

## User Story US-BOOT-002: Inspect Truthful API Readiness

**Story:**  
As a developer or deployment probe,  
I want separate liveness and readiness checks,  
so that process failure is not confused with database or migration failure.

### Acceptance Criteria

1. **Given** the API process is alive and the database is unavailable, **when** liveness is checked, **then** liveness succeeds without claiming database readiness.
2. **Given** the database, baseline migration, and vector capability are ready, **when** readiness is checked, **then** readiness returns HTTP 200 with ready component states for configuration, database, migration, and vector capability.
3. **Given** the gateway has not been called, **when** readiness is checked, **then** the result does not include gateway health and does not claim that chat, embedding, or OCR is healthy.

## Notes / Assumptions

- Health probes are infrastructure interfaces and are not a substitute for authenticated business APIs.

## Dependencies

- `REQ-BOOT-003`, `REQ-BOOT-010`

## Out of Scope

- Gateway connectivity diagnostics.
- User authentication.

## Open Questions

- Management-port exposure is tracked by `OQ-BOOT-01`.

## User Story US-BOOT-003: Apply A Safe Database Baseline

**Story:**  
As a backend developer,  
I want a repeatable migration baseline for PostgreSQL/pgvector,  
so that later slices can add application data without hand-editing the database.

### Acceptance Criteria

1. **Given** a fresh database, **when** the baseline migration runs, **then** the PostgreSQL `vector` extension is enabled and Alembic records the foundation revision, with no business tables created.
2. **Given** the baseline migration has already run, **when** it runs again, **then** it does not duplicate application state or fail because of an already-applied revision.
3. **Given** the required vector capability is unavailable, **when** readiness or migration validation runs, **then** the failure identifies `vector_capability` as not ready and does not report overall readiness as ready.

## Notes / Assumptions

- No user, document, chunk, session, or audit tables belong to this slice.

## Dependencies

- `REQ-BOOT-002`, `REQ-BOOT-003`

## Out of Scope

- Feature-specific schemas and migrations.

## Open Questions

- The exact approved image tag is tracked by `OQ-BOOT-02`.

## User Story US-BOOT-004: Load The Frontend Shell

**Story:**  
As a frontend developer,  
I want a Vue shell with one typed API boundary,  
so that later user-facing slices can add routes without scattering HTTP behavior across views.

### Acceptance Criteria

1. **Given** the web service is running, **when** a developer opens it, **then** the frontend shell renders without requiring a business login implementation.
2. **Given** the shell checks API readiness, **when** the API returns HTTP 200 ready, HTTP 503 not-ready, or is unreachable, **then** the shell displays `Ready`, `Needs attention`, or `Unable to reach API` respectively.
3. **Given** an API request fails, **when** the shell handles the error, **then** it uses the shared safe error path and does not log tokens or passwords.

## Notes / Assumptions

- UI uses Vue 3, Vite, TypeScript, Pinia, and Router as defined by the project standards.
- No unapproved UI library is introduced in this slice.

## Dependencies

- `REQ-BOOT-004`, `REQ-BOOT-009`
- Frontend standard

## Out of Scope

- Functional Ask, Knowledge, Admin, or Login views.

## Open Questions

- Approved company UI library remains open as product OQ-04; this slice uses plain Vue/CSS.

## User Story US-BOOT-005: Configure Gateway Boundaries Safely

**Story:**  
As a platform maintainer,  
I want gateway configuration placeholders and host-policy validation,  
so that later model integrations cannot accidentally send embedding or OCR data to a public endpoint.

### Acceptance Criteria

1. **Given** the environment template is copied for local use, **when** a maintainer inspects it, **then** it contains placeholders for chat, embedding, OCR, and the default allowlist (including the placeholder gateway host) but no real secret.
2. **Given** an embedding or OCR base URL host is public or otherwise absent from the allowlist, **when** configuration validation runs, **then** it rejects the configuration by literal host match before an outbound request and without DNS resolution.
3. **Given** a public chat provider is configured for later use, **when** the configuration is documented, **then** it is distinguished from the stricter internal-only embedding/OCR boundary.

## Notes / Assumptions

- Concrete gateway values remain OQ-09 and are not required for local bootstrap verification.

## Dependencies

- `REQ-BOOT-005` to `REQ-BOOT-008`
- ADR-0004, ADR-0005

## Out of Scope

- Admin provider CRUD and Ask-time provider switching.
- Live gateway calls.

## Open Questions

- OQ-09 controls later adapter smoke-test values and rate limits.
