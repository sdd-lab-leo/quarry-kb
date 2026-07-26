# Change Proposal: 20260726-repo-bootstrap

| Field | Value |
|---|---|
| Slice | `repo-bootstrap` |
| Date | 2026-07-26 |
| Proposed by | cloud-agent |
| Status | accepted |

## Goal

Deliver the first runnable Quarry KB foundation: Compose services (`web`, `api`, `postgres`), FastAPI health/readiness with secret-safe diagnostics, Alembic/pgvector baseline (no business tables), Vue shell with a typed health client, and externalized configuration with literal embedding/OCR host allowlist validation.

## In Scope

- `deploy/docker-compose.yml` topology and health wiring
- `.env.example` placeholders and default allowlist (`gateway.internal`)
- FastAPI settings, response envelope, `/api/v1/health/live`, `/api/v1/health/ready`
- Alembic baseline enabling PostgreSQL `vector` extension only
- Vue 3 + Vite + TypeScript shell and typed API client
- Verification tests and documented local smoke path
- Change-package review/archive evidence

## Out Of Scope

- Authentication, JWT, roles, account lifecycle
- Upload, parsing, OCR execution, embeddings, retrieval, RAG, chat
- Provider CRUD, Ask/Knowledge/Admin business views
- Audit records and real company/pilot corpora
- Live model-gateway calls or paid provider usage
- Java/Spring/Oracle or unapproved UI frameworks

## Inputs

- `docs/03-spec/repo-bootstrap-spec.md`
- `docs/06-tasks/repo-bootstrap-tasks.md`
- `docs/04-architecture/repo-bootstrap-architecture.md`
- `docs/04-architecture/repo-bootstrap-data-flow.md`
- `docs/04-architecture/repo-bootstrap-data-model.md`
- `docs/05-design/repo-bootstrap-design.md`
- `docs/05-design/contracts/repo-bootstrap-API_IMPLEMENTATION_GUIDE.md`
- `docs/00-context/repo-bootstrap-traceability.md`
- ADR-0002, ADR-0004, ADR-0005
- `docs/standards/backend.md`, `docs/standards/frontend.md`

## Risks / Constraints

- OQ-BOOT-02: PostgreSQL/pgvector image tag is not pilot-approved; implementation will pin a development tag and record the risk.
- OQ-BOOT-01: probe management port unresolved; local Compose network boundary is the interim control.
- OQ-09: concrete gateway values unresolved; placeholders only.
- Docker may be unavailable in the agent environment; Compose runtime smoke may be skipped with evidence.

## Acceptance

- Compose file and `.env.example` exist and validate structurally.
- Liveness/readiness match the API guide (200 ready / 503 not-ready with components).
- Baseline migration enables `vector` and creates no business tables.
- Frontend build succeeds and typed client maps ready / needs_attention / unreachable.
- Required tests pass without live gateway credentials or real secrets.

## Verification Plan

See `manifest.yaml` `verification.commands`.
