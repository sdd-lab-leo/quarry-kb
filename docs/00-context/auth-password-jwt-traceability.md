# Traceability: Password Authentication and JWT Authorization

## Slice Contract

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Goal | Establish local identity, JWT access sessions, Admin account lifecycle, and current-role server authorization. |
| Status | Draft; awaiting owner/security confirmation and implementation handoff manifest. |
| Upstream | Product specification v0.1.5, ADR-0002, ADR-0005, verified `repo-bootstrap`. |
| Downstream | `knowledge-ingest`, `ask-rag`, `chat-providers`, and `audit-minimal`. |

## Source → Requirements

| Source | Requirements |
|---|---|
| FR-01 | REQ-AUTH-001 |
| FR-02 / SEC-02 | REQ-AUTH-002, REQ-AUTH-012 |
| FR-03 | REQ-AUTH-003, REQ-AUTH-005 |
| FR-04 | REQ-AUTH-004 |
| FR-05 | REQ-AUTH-006 |
| FR-06 / ADR-0002 | REQ-AUTH-007 |
| FR-07 / backend standard | REQ-AUTH-008, REQ-AUTH-013 |
| FR-50 | REQ-AUTH-009 |
| FR-51 | REQ-AUTH-010 |
| SEC-01 / ADR-0005 | REQ-AUTH-011 |

## Requirements → Stories

| Requirements | Stories |
|---|---|
| REQ-AUTH-001, 002, 012, 013 | US-AUTH-001 |
| REQ-AUTH-003, 004, 005, 009 | US-AUTH-002 |
| REQ-AUTH-006, 008, 010, 011 | US-AUTH-003 |
| REQ-AUTH-007 | US-AUTH-004 |

## Stories → Specification

| Stories | Specification sections |
|---|---|
| US-AUTH-001 | FR-AUTH-001 to FR-AUTH-003; login workflow; error contract |
| US-AUTH-002 | FR-AUTH-004, FR-AUTH-007 to FR-AUTH-010; account data/state |
| US-AUTH-003 | FR-AUTH-006, FR-AUTH-011 to FR-AUTH-013; protected-request flow |
| US-AUTH-004 | FR-AUTH-005; identity data requirements; SSO boundary |

## Specification → Architecture / Design

| Specification area | Architecture / design output |
|---|---|
| Login and protected request | `auth-password-jwt-architecture.md`, `auth-password-jwt-data-flow.md`, `auth-password-jwt-design.md` |
| User identity and lifecycle | `auth-password-jwt-data-model.md`, design §Data Design |
| API/error contract | `../05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md` |
| Role and SSO boundaries | Architecture §Security / Related ADRs; design §Security / Audit / Reliability |

## Design → Tasks

| Design area | Tasks |
|---|---|
| Accepted auth defaults | TASK-AUTH-001 |
| User schema/repository | TASK-AUTH-002 |
| Password/JWT adapters | TASK-AUTH-003 |
| Login/current-user boundary | TASK-AUTH-004 |
| Admin lifecycle/role checks | TASK-AUTH-005 |
| Frontend session/login | TASK-AUTH-006 |
| Integrated verification | TASK-AUTH-007 |
| Cross-session handoff | TASK-AUTH-008 |

## Requirement → Verification Mapping

| Requirement / acceptance | Verification |
|---|---|
| REQ-AUTH-001/002; AC-AUTH-001/002 | Password/JWT unit tests, login API tests, redaction tests |
| REQ-AUTH-003/004/005/009; AC-AUTH-003/004 | Admin API role matrix and account lifecycle integration tests |
| REQ-AUTH-006/010; AC-AUTH-005 | Unexpired-token deactivation test and next-request role-change test |
| REQ-AUTH-007; AC-AUTH-007 | Migration/schema test; no SSO network dependency |
| REQ-AUTH-008/011; AC-AUTH-004 | Protected-route tests, health exception smoke, forbidden checks |
| REQ-AUTH-012/013; AC-AUTH-006/008 | Safe projections, frontend build/UI tests, `401`/`403` session mapping |

## Product Boundary and Naming Note

- Current delivery language calls verified `repo-bootstrap` P0.
- `docs/00-context/project-plan.md` labels engineering foundation P1 and identity P2; its status table predates the completed bootstrap runtime verification.
- This slice follows the product specification's explicit downstream order and is the next identity slice after `repo-bootstrap`.
- No project-wide stage status is changed by this document-only session; owner acceptance and implementation evidence remain separate gates.

## ADR Status

- ADR-0002 is reused for stack, phase-one password/JWT auth, roles, and future SSO reservation.
- ADR-0005 is reused for health-probe authorization exception.
- No new ADR is created in this document-only pass. If the owner changes the proposed JWT algorithm/key-rotation or token invalidation defaults, create/update an auth security ADR before implementation.

## Handoff Gate

Implementation is not approved by this document set alone. Before a coding session:

1. Resolve OQ-AUTH-001 through OQ-AUTH-005.
2. Run freshness-gate against the accepted docs, ADRs, and current commit.
3. Create and validate a change-package execution manifest.
4. Implement strictly against `docs/03-spec/auth-password-jwt-spec.md` and `docs/06-tasks/auth-password-jwt-tasks.md`.
