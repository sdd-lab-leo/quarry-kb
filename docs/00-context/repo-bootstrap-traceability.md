# Traceability: Repository Bootstrap

## Slice Contract

| Field | Value |
|---|---|
| Slice | `repo-bootstrap` |
| Goal | Start and verify the FastAPI/Vue/PostgreSQL foundation with safe gateway boundaries. |
| Status | Draft — awaiting review and acceptance |
| Implementation boundary | No application code until this SDD set is accepted and a hand-off manifest/freshness gate exists. |

## Source → Requirement Mapping

| Source | Requirements |
|---|---|
| `AC-10` | `REQ-BOOT-001`, `REQ-BOOT-009` |
| `NFR-05` | `REQ-BOOT-001`, `REQ-BOOT-002`, `REQ-BOOT-007` |
| `NFR-07`, `NFR-08` | `REQ-BOOT-002`, `REQ-BOOT-008` |
| `SEC-02`, `SEC-03`, `SEC-11` | `REQ-BOOT-005`, `REQ-BOOT-008`, `REQ-BOOT-010` |
| `SEC-08`, `SEC-09` | `REQ-BOOT-006`, `REQ-BOOT-007` |
| `D-01` through `D-07` | `REQ-BOOT-006`, `REQ-BOOT-007`, `REQ-BOOT-010` |
| ADR-0002 | All runtime and stack requirements |
| ADR-0004 | Gateway host policy and no-gateway health behavior |

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
| Configuration and egress requirements | ADR-0004, architecture §Integration Architecture, design §Integration Design |
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
| `REQ-BOOT-001`, AC-1 | Compose config validation and startup smoke |
| `REQ-BOOT-002`, `REQ-BOOT-007`, AC-3/6 | Migration upgrade/reapply and vector capability smoke |
| `REQ-BOOT-003`, AC-2/3 | API liveness/readiness integration tests |
| `REQ-BOOT-004`, AC-5 | Frontend build and browser-to-API health smoke |
| `REQ-BOOT-005` to `REQ-BOOT-008`, AC-4/7 | Configuration validation, secret scan, and repository hygiene review |
| `REQ-BOOT-009`, `REQ-BOOT-010` | Full documented verification loop and safe-error review |

## P0 Gate Evidence

- [x] v0.1 product specification and prototype exist.
- [x] Fixed evaluation question set created: `docs/00-context/evaluation-question-set-v0.1.md`.
- [x] Gateway contract and egress assumptions recorded in ADR-0004.
- [x] First implementation slice has a complete draft SDD chain.
- [ ] Product owner accepts v0.1 scope and this slice.
- [ ] `review-doc-quality` accepts the generated SDD set.
- [ ] Implementation hand-off manifest and freshness gate are created after slice acceptance.

## Scope Boundary

The next implementation handoff must implement only `docs/03-spec/repo-bootstrap-spec.md` and `docs/06-tasks/repo-bootstrap-tasks.md`. It must not add authentication, ingestion, retrieval, chat, provider administration, audit, or real data.

