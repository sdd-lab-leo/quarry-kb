# Feature Specification: Password Authentication and JWT Authorization

> **Source stories:** US-AUTH-001 through US-AUTH-004
> **Spec status:** Draft — remediated after independent SDD review
> **Last updated:** 2026-07-26

---

## Overview

**Feature summary:**
The slice adds local account/password authentication, short-lived JWT access sessions, Admin-managed account lifecycle, and server-side authorization for the three product roles.

**Business objective:**
Establish trustworthy identity and ownership before knowledge upload, retrieval, chat, and audit slices are implemented.

**In-scope outcome:**
An Admin can provision accounts, active users can log in, protected APIs can resolve the current user and current role, deactivation is effective on the next request, and the frontend can display and discard a safe session.

## Source Documents

- `docs/01-requirements/auth-password-jwt-requirement.md`
- `docs/02-user-stories/auth-password-jwt-user-stories.md`
- `docs/01-requirements/quarry-kb-product-spec-v0.1.md` — FR-01 to FR-07, FR-50 to FR-51, SEC-01/02, AC-01 (role matrix foundation)
- `docs/00-context/decisions/ADR-0002-lock-technology-stack-and-auth-evolution.md`
- `docs/00-context/decisions/ADR-0005-bootstrap-probe-allowlist-and-readiness-contract.md`
- `docs/00-context/decisions/ADR-0006-pilot-auth-security-defaults.md` (Proposed)
- `docs/00-context/changes/20260726-repo-bootstrap/archive.md`
- `docs/standards/backend.md` and `docs/standards/frontend.md`

## Actors / Users

| Actor | Responsibility |
|---|---|
| Admin | Creates and manages accounts; can use authenticated product capabilities in later slices. |
| Editor | Authenticated role reserved for future knowledge ingestion. |
| Viewer | Authenticated role reserved for future browse/query/Ask capabilities. |
| Unauthenticated visitor | Can log in and reach infrastructure health probes only. |
| Future SSO provider | Not integrated; only the mapping field is reserved. |

## Functional Scope

### Authentication

- **FR-AUTH-001**: The system accepts structurally valid account identifier and password input at the login boundary and returns a bearer JWT only for an active account with a valid password. *(Source: FR-01)*
- **FR-AUTH-002**: The system stores a password hash using Argon2id, never plaintext password material. *(Source: FR-02; ADR-0006)*
- **FR-AUTH-003**: For structurally valid login input, authentication failures are intentionally non-distinguishing for unknown identifier, invalid password, inactive account, and passwords that would fail the create/bootstrap policy. *(Derived from account privacy / SEC-02; ADR-0006)*

### Identity and roles

- **FR-AUTH-004**: Every account has exactly one role from `Admin`, `Editor`, `Viewer`. *(Source: FR-04)*
- **FR-AUTH-005**: Every account has a stable internal `user_id`, a unique account identifier, display name, status, timestamps, and nullable `external_subject`. *(Source: FR-06 and domain concept User)*
- **FR-AUTH-006**: Authorization decisions use the current internal user record, not an untrusted role claim copied from an old token. *(Source: FR-07 and FR-51)*

### Account administration

- **FR-AUTH-007**: An Admin can create an active account with identifier, display name, initial password, and exactly one role. *(Source: FR-03 and product scope §4.1)*
- **FR-AUTH-008**: An Admin can list accounts with safe identity, role, status, and timestamps. *(Source: FR-50)*
- **FR-AUTH-009**: An Admin can assign a new role, deactivate an account, and reactivate an account. *(Source: FR-03 and FR-51)*
- **FR-AUTH-010**: A deactivated account cannot log in and an existing token is rejected on the next protected request. *(Source: FR-05)*
- **FR-AUTH-014**: The system rejects any operation that would deactivate or demote the last remaining active Admin. *(Source: REQ-AUTH-014; ADR-0006)*
- **FR-AUTH-015**: When zero Admin accounts exist and the approved bootstrap configuration is valid, a one-time runtime env bootstrap shall create exactly one active Admin; bootstrap is ignored afterward. When zero Admins exist and required bootstrap values are missing or invalid, create no Admin and fail closed at startup. *(Source: REQ-AUTH-015; ADR-0006)*

### Boundary enforcement

- **FR-AUTH-011**: Login is public; future business endpoints require a valid token associated with an active account. *(Source: SEC-01)*
- **FR-AUTH-012**: The P0 infrastructure health endpoints remain the explicit no-token exception from ADR-0005 and do not imply business authorization.
- **FR-AUTH-013**: Frontend guards may hide or redirect UI, but server-side authorization is the security boundary. *(Source: FR-07)*

## Non-Functional Requirements

- **Security:** Password hashing uses Argon2id through a maintained library; plaintext password, password hash, JWT, bearer header, and secret-shaped values must not appear in logs or responses.
- **Security:** New account/bootstrap passwords use the 12-character minimum, must contain a non-whitespace character, and do not require a forced complexity regex. Passwords remain case-sensitive. Login never returns a policy-specific error after request-shape validation; it uses `401 AUTHENTICATION_FAILED` only. `[DEFAULT pending ADR-0006 acceptance]`
- **Security:** JWT signing uses HS256 with the runtime environment secret `JWT_SIGNING_KEY`. When `APP_ENV` is not `local`, missing/blank key fails closed at settings/startup validation and auth routes are not served. This does not add a JWT component to ADR-0005 readiness. `[DEFAULT pending ADR-0006 acceptance]`
- **Security:** Every issued access token has `sub`, `iat`, `exp`, and `auth_version`; `iat`/`exp` are UTC NumericDate values and `expires_at` in the response mirrors `exp` as ISO-8601 UTC. Pilot tokens must not include a `role` claim.
- **Security:** Access tokens must include `auth_version`. Deactivation increments `auth_version`. Protected requests reject version mismatches and inactive accounts. This invalidation mechanism is mandatory.
- **Reliability:** A deactivation must be observed on the next protected request without waiting for token expiry. A current-user lookup is therefore part of protected-request authorization.
- **Consistency:** A role change must be used on the next authorization check; the role claim in a previously issued token is not authoritative.
- **Privacy:** Login failures must not disclose whether an account exists. User list and current-user responses must exclude password hashes, tokens, external provider credentials, `external_subject` by default, `auth_version`, and internal secret values. Auth request-shape and dependency failures must use the P0 envelope; unexpected server failures must use HTTP 500 with `error.code = INTERNAL_ERROR` and a safe message without raw exception details.
- **Performance:** No product latency target is specified for authentication. The implementation should keep authorization lookup bounded and index-backed; a measurable target remains an open question.
- **Environment support:** Unit and API tests must run without live SSO, paid services, or external network calls. Compose/PostgreSQL migration smoke is required before implementation handoff is accepted.
- **Abuse controls:** Login rate limiting / lockout is deferred for the intranet pilot and is not required in this slice. `[DEFERRED]`

## Workflow / System Flow

```mermaid
flowchart TD
    A["User submits identifier and password"] --> B{"Credentials valid?"}
    B -- "No" --> E["Safe authentication error"]
    B -- "Yes" --> C{"Account active?"}
    C -- "No" --> E
    C -- "Yes" --> D["Issue short-lived bearer JWT"]
    D --> F["Frontend stores session safely"]
    F --> G["Protected request"]
    G --> H{"Token valid, auth_version matches, account active?"}
    H -- "No" --> I["401; discard session"]
    H -- "Yes" --> J{"Current role allowed?"}
    J -- "No" --> K["403; no business action"]
    J -- "Yes" --> L["Run protected use case"]
    M["Admin changes role/status"] --> N["Next check reads current user state"]
    N --> H
    style A fill:#dbeafe,stroke:#2563eb
    style D fill:#dcfce7,stroke:#16a34a
    style L fill:#dcfce7,stroke:#16a34a
    style E fill:#fee2e2,stroke:#dc2626
    style I fill:#fee2e2,stroke:#dc2626
    style K fill:#fef3c7,stroke:#d97706
```

### Main Flow

1. The user submits credentials to the public login endpoint.
2. The API normalizes the account identifier according to the approved identifier rule, loads the user, verifies the password hash, and checks active status.
3. On success, the API issues a short-lived JWT access token containing `sub`, `iat`, `exp`, and `auth_version`, plus safe current-user data. Structurally invalid input uses `VALIDATION_ERROR`; structurally valid credential mismatches use one generic authentication error.
4. The frontend keeps the token in memory with `sessionStorage` reload fallback and requests the current-user profile on startup.
5. A protected request validates the token, resolves the current internal user, checks active status and `auth_version`, and evaluates the current database role.
6. An Admin account operation commits atomically. Last-Admin demotion/deactivation is rejected. The next authorization check observes committed role/status.
7. Logout discards the browser token. Deactivation increments `auth_version` and rejects an unexpired token on the next protected request. Reactivation does not restore pre-deactivation tokens.
8. On first boot with zero Admins, the approved bootstrap transaction serializes the zero-Admin check and create so concurrent starts can create exactly one Admin; later starts ignore the bootstrap configuration.

## Data / Configuration Requirements

### Key Entities

| Entity | Description | Key attributes |
|---|---|---|
| User | Local account and authorization owner | `user_id`, identifier, display name, role, status, password hash, nullable `external_subject`, mandatory `auth_version`, timestamps |

### Configuration

- JWT signing key material: runtime environment secret `JWT_SIGNING_KEY`; required outside local development.
- JWT algorithm: `[DEFAULT]` HS256 for the single-host pilot (ADR-0006).
- Access token lifetime: `[DEFAULT]` 30 minutes; no refresh token; no `role` claim in issued tokens.
- Password hashing: Argon2id via a maintained library; encoded hash string persisted only.
- Password policy: `[DEFAULT]` minimum 12 characters, at least one non-whitespace character, no forced complexity regex, and case-sensitive passwords; create/bootstrap enforce with `422`; login uses generic `401` only after request-shape validation.
- First-Admin bootstrap env vars: `AUTH_BOOTSTRAP_ADMIN_IDENTIFIER`, `AUTH_BOOTSTRAP_ADMIN_PASSWORD`, optional `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` (default = normalized identifier). Missing/invalid required values with zero Admins fail closed at startup.
- Internal user ID: `[DEFAULT]` UUID.

### Status and Role Models

- Account status: `active` ↔ `deactivated`; only Admin can trigger transitions.
- Roles: `Admin`, `Editor`, `Viewer`; exactly one value per account.
- Authorization transition: an account role/status change is effective on the next protected request.
- Last active Admin cannot be deactivated or demoted.

### Validation Rules

- Account identifier is trimmed and lowercased; after normalization length is 3–64 and matches `[a-z0-9._@-]+`.
- Display name is required, trimmed, length 1–128 after trim, and stored separately from the identifier.
- Role must be exactly one of the three role values.
- New account/bootstrap passwords must satisfy the policy (minimum 12 characters, at least one non-whitespace character, no forced complexity regex) and are never echoed in a response. Login does not return policy-specific errors after request-shape validation.
- An account identifier must be unique under normalized comparison.
- `external_subject` is nullable and not writable through the phase-one password UI.
- Updates that would leave zero active Admins are rejected.

## Integrations

### PostgreSQL / Alembic

- Persists the user record and migration metadata.
- User lifecycle changes are transactional.
- No upload, document, chunk, session, message, citation, provider, or audit tables are created by this slice.

### Browser frontend

- Calls login/current-user/admin-user APIs through the shared typed client.
- Attaches a bearer token only after a successful login.
- Never logs token or password values.
- Never stores access tokens in `localStorage`.

### External identity provider

- None in this slice. `external_subject` is a schema reservation only.

## Error Contract

The API uses the P0 envelope: `success`, `data`, `error`, and `meta`.

| Code | HTTP | Meaning |
|---|---:|---|
| `AUTHENTICATION_FAILED` | 401 | Identifier/password invalid or account inactive at login; intentionally non-distinguishing. |
| `TOKEN_INVALID` | 401 | Missing, malformed, expired, unverifiable bearer token, or token subject no longer maps to a user. |
| `ACCOUNT_INACTIVE` | 401 | Token maps to a currently deactivated account or `auth_version` mismatch. |
| `FORBIDDEN` | 403 | Authenticated account lacks the required current role. |
| `ACCOUNT_CONFLICT` | 409 | Normalized identifier already exists. |
| `LAST_ADMIN_REQUIRED` | 409 | Operation would remove or demote the last active Admin. |
| `VALIDATION_ERROR` | 422 | Request fields violate the approved input rules. |
| `USER_NOT_FOUND` | 404 | Admin target user does not exist; no secret data is disclosed. |
| `INTERNAL_ERROR` | 500 | Unexpected server/dependency failure; safe message only. |

Request-shape validation, authentication dependency failures, and business errors use the same P0 envelope (`success`, `data`, `error`, `meta`). A structurally invalid request returns `VALIDATION_ERROR`; an unexpected server/dependency failure returns HTTP 500 with `INTERNAL_ERROR` without credentials, tokens, connection strings, or raw exception details.

## Dependencies

### Upstream

- Verified `repo-bootstrap` runtime, migration, API envelope, and frontend client baseline.
- ADR-0002 role and password-to-SSO evolution decision.
- ADR-0005 health-probe authorization exception.
- Proposed ADR-0006 pilot auth security defaults.

### Downstream

- `knowledge-ingest` uses `user_id` and `Admin`/`Editor` authorization.
- `ask-rag` uses authenticated user ownership for sessions.
- `chat-providers` uses Admin authorization.
- `audit-minimal` records account and role/status operations.

## Risks / Ambiguities

| ID | Description | Type | Impact | Recommendation |
|---|---|---|---|---|
| R-AUTH-001 | First Admin bootstrap path depends on ADR-0006 acceptance. | Gap | High | Accept or amend ADR-0006 before implementation. |
| R-AUTH-002 | JWT lifetime, algorithm, password policy, identifier rules, and browser storage remain Proposed in ADR-0006. | Unclear | High | Accept ADR-0006 or record amendments before apply. |
| R-AUTH-003 | Audit requirements include account actions, but audit persistence is a later slice. | Boundary | Medium | Keep audit out of this slice and make `audit-minimal` the follow-up gate. |
| R-AUTH-004 | No user retention/deletion policy is defined. | Gap | Medium | Use deactivation only for v0.1 and defer deletion/retention to a later decision. |

## Out of Scope

- SSO and all external identity network behavior.
- Knowledge and model capabilities.
- Audit table/list and provider configuration.
- Password recovery, MFA, registration, invitations, and refresh tokens.
- Login rate limiting / account lockout for the intranet pilot.

## Open Questions

See `auth-password-jwt-requirement.md` OQ-AUTH-001 through OQ-AUTH-005. Their documented defaults are fully encoded in proposed ADR-0006 and must be accepted or explicitly amended before implementation handoff. Documentation of defaults is not owner approval.
