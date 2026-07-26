# Requirements: Password Authentication and JWT Authorization

## Status

Draft — remediated after independent SDD review; not yet approved for implementation.

## Slice Contract

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Goal | Provide account/password login, JWT access sessions, server-side role authorization, and Admin-managed account lifecycle. |
| Upstream | `docs/01-requirements/quarry-kb-product-spec-v0.1.md`, FR-01 to FR-07 and FR-50 to FR-51 |
| Related decisions | ADR-0002; ADR-0005; proposed ADR-0006; the P0 `repo-bootstrap` SDD chain and API envelope |
| Verification | Backend unit/API tests, migration upgrade/reapply, frontend build, protected-route smoke, and role matrix checks |
| Stage naming note | The project plan calls engineering foundation P1 and identity P2, while current delivery language calls verified `repo-bootstrap` P0. This document follows the product-spec slice order: `auth-password-jwt` is the next slice after `repo-bootstrap`. Identity work in this slice does **not** include audit persistence; audit remains `audit-minimal` and is part of the broader plan P2 exit gate. |

## Context

`repo-bootstrap` provides the FastAPI/Vue/PostgreSQL foundation, readiness contract, migration baseline, and safe API envelope. It intentionally has no business tables or authentication. The next slice must establish a single internal identity model that later ingestion, retrieval, chat, provider, and audit slices can consume without redesigning ownership or role semantics.

The source product specification defines phase-one password authentication with JWT sessions, three roles (`Admin`, `Editor`, `Viewer`), Admin-created accounts, server-side authorization, and a reserved external identity field for a future SSO provider.

## Goals

- Allow an active user to log in with an account identifier and password and receive a bearer JWT access token.
- Store only password hashes and keep passwords, tokens, and authorization headers out of logs and API responses.
- Allow an Admin to create, list, deactivate, reactivate, and assign exactly one role to accounts.
- Make current account status and role authoritative at every protected API authorization check.
- Preserve an `external_subject` field for future company SSO without making SSO part of this slice.
- Provide a typed frontend login/session surface without putting authorization policy in Vue views.

## In Scope

- Login endpoint for account identifier plus password.
- JWT access-token issuance, validation, expiry, and current-user resolution.
- `Admin`, `Editor`, and `Viewer` role vocabulary shared by backend and frontend.
- User record and migration owned by this slice.
- Admin-only user list and account lifecycle operations.
- Server-side authentication and role dependencies for future business endpoints.
- Current-user endpoint for session bootstrap and frontend display.
- Client-side token storage and logout-by-token-discard for the pilot browser.
- One-time first-Admin bootstrap from runtime environment variables.
- Safe authentication failure envelopes and redaction tests.
- Health probe exception inherited from ADR-0005: `/api/v1/health/live` and `/api/v1/health/ready` remain infrastructure endpoints and are not business authorization evidence.

## Out Of Scope

- Company SSO, OIDC, SAML, or any external identity provider integration.
- Self-service registration, email verification, password reset, MFA, account recovery, or invitation email.
- Knowledge upload, parsing, OCR, chunking, embedding, retrieval, RAG, chat, or provider CRUD.
- Audit persistence and the Admin audit list; those belong to `audit-minimal` while this slice only defines account-operation boundaries.
- Shared sessions, workspaces, tenant isolation, or per-user private knowledge collections.
- Refresh-token rotation or a server-side session table. This slice uses a short-lived access JWT plus current-user state checks.

## Requirements

| ID | Requirement | Source | Priority |
|---|---|---|---|
| REQ-AUTH-001 | An active user can submit an account identifier and password and receive a bearer access token on valid credentials. | FR-01 | Must |
| REQ-AUTH-002 | Passwords are persisted only as one-way password hashes; plaintext passwords are never stored, returned, or logged. | FR-02, SEC-02 | Must |
| REQ-AUTH-003 | An Admin can create an account with identifier, display name, initial role, and initial password through a protected API. | FR-03, product scope §4.1 | Must |
| REQ-AUTH-004 | Each account has exactly one role: `Admin`, `Editor`, or `Viewer`. | FR-04 | Must |
| REQ-AUTH-005 | An Admin can deactivate and reactivate an account. A deactivated account cannot log in. | FR-03, FR-05 | Must |
| REQ-AUTH-006 | Existing tokens for a deactivated account are rejected on the next protected request. | FR-05 | Must |
| REQ-AUTH-007 | The user record contains a nullable, future-SSO-compatible `external_subject` field without requiring SSO now. | FR-06, ADR-0002 | Must |
| REQ-AUTH-008 | Authentication and authorization are enforced at the API boundary; frontend guards are usability only. | FR-07, backend standard | Must |
| REQ-AUTH-009 | An Admin can list users with identifier/display name, role, status, and safe timestamps; password hashes and secrets are never included. | FR-50, SEC-02 | Must |
| REQ-AUTH-010 | A role change is used on the next authorization check and does not depend on a stale role claim in an already-issued token. | FR-51 | Must |
| REQ-AUTH-011 | Only the login and infrastructure health endpoints are unauthenticated; future business endpoints require a valid active-user token. | SEC-01, ADR-0005 | Must |
| REQ-AUTH-012 | Authentication errors use the P0 response envelope and do not reveal whether a submitted identifier exists. | SEC-02, security baseline | Must |
| REQ-AUTH-013 | The frontend can restore a valid session, show the current user and role, and discard the token on logout or authentication failure. | FR-01, FR-07, frontend standard | Must |
| REQ-AUTH-014 | The system must reject any Admin operation that would deactivate or demote the last remaining active Admin. | Operational safety; ADR-0006 | Must |
| REQ-AUTH-015 | The first Admin shall be created by a one-time runtime env bootstrap that runs only when zero Admin accounts exist. | OQ-AUTH-002 / ADR-0006 | Must |

## Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-AUTH-001 | A valid active account receives a token; invalid identifier, invalid password, and inactive account all return the same safe authentication failure category. |
| AC-AUTH-002 | Password values, password hashes, JWT values, and `Authorization` headers are absent from response bodies, structured errors, and test-captured logs. |
| AC-AUTH-003 | An Admin can create one account in each role, list them, deactivate one, reactivate it, and assign a different role. |
| AC-AUTH-004 | A Viewer and Editor cannot call Admin-only user-management endpoints; the API returns a consistent forbidden response. |
| AC-AUTH-005 | A token issued before deactivation is rejected immediately after deactivation; a role update is reflected on the next protected request; tokens remain invalid after reactivation until a new login. |
| AC-AUTH-006 | The current-user response contains only safe identity fields and exactly one role; it never contains a password hash, token secret, or provider credential. |
| AC-AUTH-007 | The `external_subject` field is nullable and does not require an SSO integration or external network call. |
| AC-AUTH-008 | Login/session UI builds successfully, restores a valid session, handles `401`/`403` safely, and removes the local token on logout. |
| AC-AUTH-009 | Attempting to deactivate or demote the last active Admin fails with a typed validation/conflict error and leaves that Admin unchanged. |
| AC-AUTH-010 | Bootstrap env vars create exactly one Admin when none exist and are ignored once any Admin exists. |

## Open Questions

| ID | Question | Proposed default pending owner confirmation | Impact |
|---|---|---|---|
| OQ-AUTH-001 | What is the pilot password policy, and how should policy-invalid values be handled at login versus account creation/bootstrap? | Proposed default: minimum 12 characters, at least one non-whitespace character, no forced complexity regex, and case-sensitive passwords. Enforce the policy for new account/bootstrap credentials; for structurally valid login credentials, prefer the same generic authentication failure category rather than a policy-specific account-disclosure signal. | Validation, login error semantics, and onboarding UX |
| OQ-AUTH-002 | How is the first Admin bootstrapped, including concurrent startup and invalid/missing bootstrap configuration? | Proposed default: one-time startup bootstrap from runtime env vars `AUTH_BOOTSTRAP_ADMIN_IDENTIFIER`, `AUTH_BOOTSTRAP_ADMIN_PASSWORD`, and optional `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME`; the zero-Admin check and create must be serialized transactionally so concurrent starts produce at most one Admin; bootstrap is ignored after any Admin exists and never uses a committed default password. Recommended safe failure behavior is to create no Admin and fail closed when required bootstrap values are missing/invalid; owner/security confirmation is still required. | First-run operability, concurrency, and secret handling |
| OQ-AUTH-003 | How long should access JWTs live and how should expiry be represented? | Proposed default: 30-minute access token; required `iat`/`exp` claims use UTC time, `expires_at` mirrors `exp`, and no refresh token is provided in this slice. | Session UX and security posture |
| OQ-AUTH-004 | Where should the browser hold the access token? | In-memory state with `sessionStorage` as the reload fallback; never `localStorage`. | Reload behavior and XSS exposure |
| OQ-AUTH-005 | What account identifier normalization is required? | Trim and lowercase for lookup/uniqueness; length 3–64; allowed pattern `[a-z0-9._@-]+` after normalization; preserve display name separately; passwords remain case-sensitive. | Login and uniqueness behavior |

These open questions are also captured as proposed defaults in ADR-0006. Owner/security acceptance of ADR-0006 (or an amended ADR) closes them for implementation handoff.
