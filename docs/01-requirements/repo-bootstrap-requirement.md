# Requirements: Repository Bootstrap

## Document Control

| Field | Value |
|---|---|
| Slice | `repo-bootstrap` |
| Status | Draft — P0 proposal |
| Date | 2026-07-26 |
| Product version | Quarry KB v0.1 |
| Source | `docs/01-requirements/quarry-kb-product-spec-v0.1.md` |
| Related ADRs | ADR-0002, ADR-0004, ADR-0005 |

## Goal Contract

**Goal:** A developer can start the Quarry KB foundation locally, observe a truthful API/database readiness state, and load the frontend shell through the documented Compose flow without hard-coded secrets or gateway assumptions.

**Included scope:** Compose services, FastAPI application shell, Vue application shell, PostgreSQL/pgvector connection, migration baseline, environment template, gateway endpoint policy, health probes, and foundation smoke verification.

**Excluded scope:** Authentication, user/role management, document upload, parsing, OCR execution, embeddings, retrieval, chat, provider CRUD, audit records, and production deployment automation.

**Acceptance:** The slice satisfies the acceptance criteria below and produces the implementation-ready artifacts listed in the traceability document.

**Verification:** Compose config validation, backend tests, migration upgrade smoke, frontend production build, and a frontend-to-backend health smoke path once scaffolding exists.

## Upstream Traceability

| Upstream item | How this slice uses it |
|---|---|
| `AC-10` | Establishes the documented Compose startup path. |
| `NFR-05` | Uses the locked `web` + `api` + `postgres` topology and does not add on-host OCR/embedding containers. |
| `NFR-07` / `NFR-08` | Keeps database and upload-volume boundaries explicit for later persistence slices. |
| `SEC-02`, `SEC-03`, `SEC-08`, `SEC-09`, `SEC-11` | Establishes secret, upload, and gateway configuration boundaries before code exists. |
| `D-01` through `D-07` | Records provider-neutral chat configuration and strict internal-only embedding/OCR boundaries; later slices implement user behavior. |

## Requirements

### Runtime Foundation

- **REQ-BOOT-001:** The repository shall document and provide a Compose topology containing `web`, `api`, and `postgres` services.
- **REQ-BOOT-002:** PostgreSQL shall be configured for the locked PostgreSQL + pgvector stack, with a migration baseline that validates the required database capability for later vector storage.
- **REQ-BOOT-003:** The API shall expose separate liveness and readiness probes. Liveness shall not require the database or model gateway. Readiness shall report database, migration, and configuration readiness without calling the model gateway.
- **REQ-BOOT-004:** The frontend shell shall load through the Compose web service and reach the API through one typed HTTP client boundary.

### Configuration And Boundary Safety

- **REQ-BOOT-005:** An English `.env.example` shall document runtime, database, upload-root, internal chat, embedding, and OCR configuration placeholders without containing real secrets.
- **REQ-BOOT-006:** Embedding and OCR base URLs shall be validated against the configured intranet/gateway allowlist using literal hostname (or `host:port`) matching of the URL host. Validation shall not perform DNS resolution. Empty embedding/OCR URLs are invalid. Public hosts shall be rejected before any outbound request is made. Local placeholder hosts documented in `.env.example` must be present on the default allowlist so bootstrap verification does not require a live gateway.
- **REQ-BOOT-007:** Chat configuration shall support an internal gateway placeholder and later Admin-configured public OpenAI-compatible providers without hard-coding a vendor. Bootstrap shall not implement provider CRUD.
- **REQ-BOOT-008:** Real passwords, API keys, JWT signing material, uploaded files, internal screenshots, and runtime logs shall remain outside Git.

### Verification And Operability

- **REQ-BOOT-009:** The documented local verification path shall cover Compose configuration, API tests, migration smoke, frontend build, and a frontend-to-backend health check.
- **REQ-BOOT-010:** Startup and readiness failures shall expose actionable, secret-safe diagnostics and shall not claim gateway health when no gateway call was made.

## Acceptance Criteria

1. **AC-BOOT-01:** **Given** the repository's documented prerequisites are installed, **when** a developer runs the documented Compose startup command (`docker compose -f deploy/docker-compose.yml up --build`), **then** `web`, `api`, and `postgres` start with health checks and no source-controlled secret is required.
2. **AC-BOOT-02:** **Given** the API process is running but PostgreSQL is unavailable, **when** the liveness probe is called, **then** it reports process liveness without falsely reporting database readiness.
3. **AC-BOOT-03:** **Given** PostgreSQL is available and the baseline migration has completed, **when** the readiness probe is called, **then** it returns HTTP 200 with ready component states for configuration, database, migration, and vector capability, without making an external gateway request.
4. **AC-BOOT-04:** **Given** an embedding or OCR URL host is outside the configured intranet/gateway allowlist, **when** configuration is loaded or validated, **then** readiness fails with a safe configuration error and no public request is attempted.
5. **AC-BOOT-05:** **Given** a developer opens the web service, **when** the shell requests API readiness, **then** the shell displays a typed ready, needs-attention (HTTP 503), or unreachable state rather than logging raw credentials or silently swallowing the error.
6. **AC-BOOT-06:** **Given** the migration baseline is applied twice, **when** the second migration run occurs, **then** it completes idempotently without creating duplicate application state.
7. **AC-BOOT-07:** **Given** only mock or placeholder configuration from `.env.example` is present, **when** the verification commands run, **then** they do not require live gateway credentials or real company documents.

## Assumptions

- The repository remains greenfield; no existing application API, table, component, or runtime behavior is inherited.
- The local Compose deployment is the first supported environment; staging and production hardening are later work.
- Health probes are infrastructure probes and are an explicit exception to product `SEC-01`. They remain unauthenticated and must be reachable only through the Compose/service network boundary (not published as a public business route). See ADR-0005.
- Exact gateway URLs, models, OCR path, and rate limits remain OQ-09 deployment inputs. Bootstrap uses documented placeholder hosts on the default allowlist.
- The Compose file path is `deploy/docker-compose.yml`.
- Plain Vue + CSS variables is used until a UI library ADR exists.
- The Alembic baseline enables and verifies the PostgreSQL `vector` extension; it creates no business tables.

## Dependencies

- ADR-0002 for the technology and runtime boundary.
- ADR-0004 for gateway configuration and egress rules.
- ADR-0005 for allowlist matching, SEC-01 probe exception, and readiness HTTP semantics.
- Backend and frontend standards.
- Docker and a PostgreSQL/pgvector-compatible image available to the local environment.

## Out Of Scope

- Login, JWT issuance, passwords, roles, or account lifecycle.
- User-facing Ask, Knowledge, Admin, or document-management behavior beyond a non-functional shell placeholder.
- Real OCR, embedding, chat, provider CRUD, or external gateway smoke calls.
- Async worker infrastructure, queues, object storage, and production observability.
- Any real company corpus or secret.

## Open Questions

| ID | Question | Owner | Impact |
|---|---|---|---|
| OQ-BOOT-01 | Should health probes be exposed on a private management port in the pilot, or only on the API port with network restriction? | Platform | Changes deployment exposure, not application behavior. |
| OQ-BOOT-02 | What exact PostgreSQL/pgvector image tag is approved for the pilot? | Platform | Needed to pin Compose reproducibly. |
| OQ-09 | What are the internal gateway base URLs, model IDs, OCR path, and rate limits? | Platform / Model gateway owner | Needed for real adapter smoke tests in later slices; placeholders are sufficient for bootstrap. |

