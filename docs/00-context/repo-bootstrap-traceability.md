# Traceability: Repository Bootstrap

## Slice Contract

| Field | Value |
|---|---|
| Slice | `repo-bootstrap` |
| Goal | Start and verify the FastAPI/Vue/PostgreSQL foundation with safe gateway boundaries. |
| Status | Verified in workspace — product-owner acceptance and P1 runtime gate recorded |
| Implementation boundary | Initial code applied under change package `docs/00-context/changes/20260726-repo-bootstrap/` after freshness-gate pass; current review recheck includes a minimal Compose remediation. |

## Source → Requirement Mapping

| Source | Requirements |
|---|---|
| `AC-10` | `REQ-BOOT-001`, `REQ-BOOT-009` |
| `NFR-05` | `REQ-BOOT-001`, `REQ-BOOT-002`, `REQ-BOOT-006` |
| `NFR-07`, `NFR-08` | `REQ-BOOT-002`, `REQ-BOOT-008` |
| `SEC-01` (probe exception) | `REQ-BOOT-003`, ADR-0005 |
| `SEC-02`, `SEC-03`, `SEC-11` | `REQ-BOOT-005`, `REQ-BOOT-008`, `REQ-BOOT-010` |
| `SEC-08`, `SEC-09` | `REQ-BOOT-006` |
| `D-01` | `REQ-BOOT-007` |
| `D-03`, `D-04`, `D-05` | `REQ-BOOT-006` |
| `D-07` | `REQ-BOOT-010` |
| ADR-0002 | All runtime and stack requirements |
| ADR-0004 | Gateway host policy and no-gateway health behavior |
| ADR-0005 | Allowlist match rule, SEC-01 probe exception, readiness HTTP semantics, baseline vector duty |

## Requirements → Stories

| Requirement | Stories |
|---|---|
| `REQ-BOOT-001`, `REQ-BOOT-002`, `REQ-BOOT-009` | US-BOOT-001 |
| `REQ-BOOT-003`, `REQ-BOOT-010` | US-BOOT-002 |
| `REQ-BOOT-002`, `REQ-BOOT-003` | US-BOOT-003 |
| `REQ-BOOT-004`, `REQ-BOOT-009` | US-BOOT-004 |
| `REQ-BOOT-005` through `REQ-BOOT-008` | US-BOOT-005 |

## Stories → Specification

| Stories | Specification sections |
|---|---|
| US-BOOT-001 | Runtime Startup, FR-BOOT-01 to FR-BOOT-02 |
| US-BOOT-002 | Health And Readiness, FR-BOOT-03 to FR-BOOT-04 |
| US-BOOT-003 | Database Foundation, FR-BOOT-05 to FR-BOOT-07 |
| US-BOOT-004 | Frontend Shell, FR-BOOT-08 to FR-BOOT-09 |
| US-BOOT-005 | Configuration And Data Safety, FR-BOOT-10 to FR-BOOT-12 |

## Specification → Architecture / Design

| Specification | Architecture / design output |
|---|---|
| Runtime and health requirements | `repo-bootstrap-architecture.md`, `repo-bootstrap-design.md`, API guide |
| Database and migration requirements | `repo-bootstrap-data-flow.md`, `repo-bootstrap-data-model.md`, design §Data Design |
| Configuration and egress requirements | ADR-0004, ADR-0005, architecture §Integration Architecture, design §Integration Design |
| Frontend shell requirements | architecture §Frontend Components, design §UI / User Flow Design |

## Design → Tasks

| Design area | Tasks |
|---|---|
| Compose and configuration | TASK-001 |
| PostgreSQL/pgvector and migration | TASK-002 |
| API settings and health | TASK-003 |
| Vue shell and typed client | TASK-004 |
| Verification | TASK-005 |
| Documentation alignment | TASK-006 |

## Requirement → Verification Mapping

| Requirement / acceptance | Verification |
|---|---|
| `REQ-BOOT-001`, `AC-BOOT-01` | Compose config validation and startup smoke for `deploy/docker-compose.yml` |
| `REQ-BOOT-002`, `AC-BOOT-03`, `AC-BOOT-06` | Migration upgrade/reapply and vector capability smoke |
| `REQ-BOOT-003`, `AC-BOOT-02`, `AC-BOOT-03` | API liveness/readiness integration tests (200 ready / 503 not-ready) |
| `REQ-BOOT-004`, `AC-BOOT-05` | Frontend build and browser-to-API readiness smoke |
| `REQ-BOOT-005` to `REQ-BOOT-008`, `AC-BOOT-04`, `AC-BOOT-07` | Configuration validation, literal allowlist tests, secret scan, and repository hygiene review |
| `REQ-BOOT-009`, `REQ-BOOT-010` | Full documented verification loop and secret-safe error review |

## P0 Gate Evidence

- [x] v0.1 product specification and prototype exist.
- [x] Fixed evaluation question set created: `docs/00-context/evaluation-question-set-v0.1.md`.
- [x] Gateway contract and egress assumptions recorded in ADR-0004; bootstrap probe/allowlist/readiness clarifications recorded in ADR-0005.
- [x] First implementation slice has a complete draft SDD chain.
- [x] Independent document review findings remediated (readiness contract, allowlist rule, SEC-01 exception, traceability mappings, slice-order alignment).
- [x] Remediation review recorded in `docs/reviews/repo-bootstrap-sdd-quality.md`.
- [x] Execution manifest + freshness-gate evidence recorded in `docs/00-context/changes/20260726-repo-bootstrap/`.
- [x] Dockerless implementation verification passed (pytest, frontend build, compose YAML parse, local health smoke).
- [x] Product owner accepts v0.1 scope and this slice (accepted in the independent review session on 2026-07-26).
- [x] Docker/Postgres Compose migration smoke in a Docker-capable environment.
- [x] P0/P1 stage gates marked complete after owner acceptance + runtime smoke.

## Acceptance And Verification Recheck

| Field | Value |
|---|---|
| Recheck date | 2026-07-26 |
| Acceptance | Product owner accepted the v0.1 scope and `repo-bootstrap` slice in the review session. |
| Runtime evidence | Docker Compose started `web`, `api`, and `postgres`; all services reported healthy after the minimal Compose remediation. |
| Migration evidence | Alembic baseline applied and reapplied successfully; database contained only `alembic_version` and the `vector` extension. |
| API evidence | Web-proxied liveness returned HTTP 200; readiness returned HTTP 200 when ready and HTTP 503 with `DATABASE_NOT_READY` plus all four components when PostgreSQL was stopped. |
| Frontend evidence | Production build and web-to-API readiness HTTP smoke passed. |
| Scope evidence | No authentication, ingestion, retrieval, chat, provider, audit, real secrets, or real corpora were added. |

The archived manifest and original change review remain historical evidence for the earlier apply. This recheck records the later Docker-capable verification and does not convert the archived manifest into an active handoff.

## Scope Boundary

The next implementation handoff must implement only `docs/03-spec/repo-bootstrap-spec.md` and `docs/06-tasks/repo-bootstrap-tasks.md`. It must not add authentication, ingestion, retrieval, chat, provider administration, audit, or real data.
