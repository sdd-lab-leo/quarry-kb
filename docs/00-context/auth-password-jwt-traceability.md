# Traceability: Password Authentication and JWT Authorization

## Slice Contract

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Goal | Establish local identity, JWT access sessions, Admin account lifecycle, and current-role server authorization. |
| Status | Draft; Major review findings remediated in docs; awaiting owner/security acceptance of proposed ADR-0006 and implementation handoff manifest. |
| Upstream | Product specification v0.1.5, ADR-0002, ADR-0005, proposed ADR-0006, verified `repo-bootstrap`. |
| Downstream | `knowledge-ingest`, `ask-rag`, `chat-providers`, and `audit-minimal`. |

## SDD Generation Gate Evidence

| Check | Evidence |
|---|---|
| SDD skill chain used | yes |
| Entry skill | `.agents/skills/wwa-sdd-generate-all/SKILL.md` (original generation); remediation guided by `review-doc-quality` findings |
| Downstream skills read during generation/remediation | `req-to-user-story`, `user-story-to-spec`, `spec-to-architecture`, `architecture-to-design`, `design-to-tasks`, `review-doc-quality`, `context-engineering-adr` |
| ADR created/updated | ADR-0006 proposed and extended to encode OQ-AUTH-001 through OQ-AUTH-005, UUID `user_id`, `INTERNAL_ERROR`, and JWT-key/bootstrap fail-closed semantics; ADR-0002/0005 reused |
| `review-doc-quality` result | Independent audit was **PASS WITH FIXES**. Remediation of Major findings is recorded in [`docs/reviews/auth-password-jwt-sdd-quality.md`](../reviews/auth-password-jwt-sdd-quality.md). Remains Draft; does **not** approve implementation or mark ADR-0006 Accepted. |

## Source → Requirements

| Source | Requirements |
|---|---|
| FR-01 | REQ-AUTH-001 |
| FR-02 / SEC-02 | REQ-AUTH-002, REQ-AUTH-012 |
| FR-03 | REQ-AUTH-003, REQ-AUTH-005 |
| FR-04 | REQ-AUTH-004 |
| FR-05 | REQ-AUTH-005, REQ-AUTH-006 |
| FR-06 / ADR-0002 | REQ-AUTH-007 |
| FR-07 / backend standard | REQ-AUTH-008, REQ-AUTH-013 |
| FR-50 | REQ-AUTH-009 |
| FR-51 | REQ-AUTH-010 |
| SEC-01 / ADR-0005 | REQ-AUTH-011 |
| ADR-0006 / operational safety | REQ-AUTH-014, REQ-AUTH-015 |

## Requirements → Stories

| Requirements | Stories |
|---|---|
| REQ-AUTH-001, 002, 012, 013 | US-AUTH-001 |
| REQ-AUTH-003, 004, 005, 009, 014, 015 | US-AUTH-002 |
| REQ-AUTH-006, 008, 010, 011 | US-AUTH-003 |
| REQ-AUTH-007 | US-AUTH-004 |

## Stories → Specification

| Stories | Specification sections |
|---|---|
| US-AUTH-001 | FR-AUTH-001 to FR-AUTH-003; login workflow; error contract |
| US-AUTH-002 | FR-AUTH-004, FR-AUTH-007 to FR-AUTH-010, FR-AUTH-014, FR-AUTH-015; account data/state |
| US-AUTH-003 | FR-AUTH-006, FR-AUTH-011 to FR-AUTH-013; protected-request flow |
| US-AUTH-004 | FR-AUTH-005; identity data requirements; SSO boundary |

## Specification → Architecture / Design

| Specification area | Architecture / design output |
|---|---|
| Login and protected request | `auth-password-jwt-architecture.md`, `auth-password-jwt-data-flow.md`, `auth-password-jwt-design.md` |
| User identity and lifecycle | `auth-password-jwt-data-model.md`, design §Data Design |
| API/error contract | `../05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md` |
| Role, bootstrap, and SSO boundaries | Architecture §Security / Related ADRs; design §Security / Audit / Reliability; ADR-0006 |

## Design → Tasks

| Design area | Tasks |
|---|---|
| Accepted auth defaults / ADR-0006 | TASK-AUTH-001 |
| Pre-coding handoff manifest | TASK-AUTH-008 |
| User schema/repository | TASK-AUTH-002 |
| Password/JWT adapters | TASK-AUTH-003 |
| Login/current-user/bootstrap boundary | TASK-AUTH-004 |
| Admin lifecycle/role checks | TASK-AUTH-005 |
| Frontend session/login/Admin UI | TASK-AUTH-006 |
| Integrated verification | TASK-AUTH-007 |
| Post-verify archive | TASK-AUTH-009 |

## Requirement → Verification Mapping

| Requirement / acceptance | Verification |
|---|---|
| REQ-AUTH-001/002; AC-AUTH-001/002 | Password/JWT unit tests, login API tests, redaction tests |
| REQ-AUTH-003/004/005/009; AC-AUTH-003/004 | Admin API role matrix and account lifecycle integration tests |
| REQ-AUTH-006/010; AC-AUTH-005 | Unexpired-token deactivation test, reactivation auth-version test, next-request role-change test |
| REQ-AUTH-007; AC-AUTH-007 | Migration/schema test; no SSO network dependency |
| REQ-AUTH-008/011; AC-AUTH-004 | Protected-route tests, health exception smoke, forbidden checks |
| REQ-AUTH-012/013; AC-AUTH-006/008 | Safe projections, frontend build/UI tests, `401`/`403` session mapping |
| REQ-AUTH-014; AC-AUTH-009 | Last-Admin demotion/deactivation rejection tests |
| REQ-AUTH-015; AC-AUTH-010 | Bootstrap-once, concurrent-start, existing-Admin, and missing/invalid-env tests |

## Product Boundary and Naming Note

- Current delivery language calls verified `repo-bootstrap` P0.
- `docs/00-context/project-plan.md` labels engineering foundation P1 and identity P2.
- This slice follows the product specification's explicit downstream order and is the next identity slice after `repo-bootstrap`.
- This slice does **not** satisfy the full plan P2 exit gate because audit persistence remains in `audit-minimal`.
- Project-plan stage statuses were updated in the same remediation pass to reflect that foundation scaffolding exists and Compose smoke remains residual.

## ADR Status

- ADR-0002 is reused for stack, phase-one password/JWT auth, roles, and future SSO reservation.
- ADR-0005 is reused for health-probe authorization exception and readiness component set.
- ADR-0006 is **Proposed** for pilot auth security defaults. It now encodes OQ-AUTH-001 through OQ-AUTH-005 (password policy + login generic failure, identifier normalization, JWT TTL/claims/no role claim, browser storage, bootstrap fail-closed), plus Argon2id, HS256/`JWT_SIGNING_KEY` settings/startup fail-closed without changing ADR-0005 readiness, mandatory `auth_version`, UUID `user_id`, `INTERNAL_ERROR`, and last-Admin protection. Owner/security acceptance is still required before TASK-AUTH-008 completes. Documented defaults are not approval.

## Handoff Gate

Implementation is not approved by this document set alone. Before a coding session:

1. Accept or amend proposed ADR-0006 (closes OQ-AUTH-001 through OQ-AUTH-005 for handoff).
2. Complete TASK-AUTH-001.
3. Run freshness-gate against the accepted docs, ADRs, and current commit.
4. Complete TASK-AUTH-008: create and validate a change-package execution manifest.
5. Implement strictly against `docs/03-spec/auth-password-jwt-spec.md` and `docs/06-tasks/auth-password-jwt-tasks.md`.
6. After verify, complete TASK-AUTH-009 archive.
