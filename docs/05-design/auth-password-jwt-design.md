# Detailed Design: Password Authentication and JWT Authorization

## Overview

This design turns the approved `auth-password-jwt` behavior into implementation-facing module, data, API, UI, and verification boundaries. It extends the verified P0 foundation; it does not implement code in this document-generation session.

## Source Architecture

- `docs/04-architecture/auth-password-jwt-architecture.md`
- `docs/04-architecture/auth-password-jwt-data-flow.md`
- `docs/04-architecture/auth-password-jwt-data-model.md`
- `docs/03-spec/auth-password-jwt-spec.md`
- ADR-0002 and ADR-0005

## Grounding Evidence From P0

The following current-code claims were re-verified before writing this design:

| Claim | Evidence | Result |
|---|---|---|
| The FastAPI app currently registers only the health router under `/api/v1`. | `backend/app/main.py:14-28` | Verified. Auth routers are proposed additions, not existing behavior. |
| The existing response envelope has `success`, `data`, `error`, and `meta`. | `backend/app/core/envelope.py:8-24` | Verified. New auth responses must preserve it. |
| Health probes are marked as the infrastructure exception. | `backend/app/api/health.py:1-39` | Verified. Auth dependencies must not accidentally protect these probes. |
| The current frontend client is GET-only and has no token attachment. | `frontend/src/api/client.ts:19-52` | Verified. Auth requires an intentional client extension. |
| The current Vue shell only renders foundation readiness. | `frontend/src/App.vue:1-59` | Verified. Login/admin surfaces are not existing behavior. |

No existing User model, auth router, password adapter, JWT signer, or business migration was found in the current source tree.

## Design Assumptions

- `[DEFAULT]` Use an internal UUID user ID.
- `[DEFAULT]` Use an access JWT with `sub`, `iat`, `exp`, and `auth_version`; current role/status are loaded from PostgreSQL for authorization.
- `[DEFAULT]` Use HS256 with a runtime secret for the single-host pilot; do not expose the secret through settings APIs.
- `[DEFAULT]` Use 30-minute access-token lifetime and no refresh-token endpoint.
- `[DEFAULT]` Store the browser token in memory with session storage fallback; never localStorage.
- `[DEFAULT]` Admin supplies an initial password when creating an account; password reset is out of scope.

These defaults require owner/security confirmation before implementation handoff.

## Design Scope

### Modules

- Authentication API and request/response models.
- Account administration API and safe user projections.
- Authentication and authorization service layer.
- User repository and transaction boundary.
- Password and JWT adapter boundaries.
- Frontend session store, login view, route guard, and Admin user view.
- Migration, redaction, API, and browser verification.

### Exclusions

No business content routes, audit persistence, SSO, password recovery, provider setup, or external gateway call belongs in this design.

## Module Design

### Authentication API

- Accept credentials only at `POST /api/v1/auth/login`.
- Map the service result to the P0 envelope.
- Return `401 AUTHENTICATION_FAILED` for unknown, invalid, or inactive credentials.
- Never pass raw password values into logs, exception text, or response models.

### Current-user and authorization dependency

- Read the bearer token from the `Authorization` header.
- Verify signature, algorithm, expiry, subject, and auth version.
- Load the current User row by internal ID.
- Reject missing/inactive/version-mismatched users with `401`.
- Return an internal authenticated-user context containing `user_id` and current role.
- Role checks compare the current database role to the required role set.

### Account administration service

- Create: normalize identifier, validate password/role, hash password, create active User transactionally.
- List: return an allowlisted safe projection; never serialize ORM User directly.
- Update: permit display name, role, and status changes under an Admin check; update timestamps atomically.
- Deactivate: set status/time and increment `auth_version`.
- Reactivate: set active status, clear deactivation time, and keep pre-change tokens invalid through the incremented version.
- No delete operation is included; deactivation is the v0.1 lifecycle control.

### Repository boundary

- Own user lookup by normalized identifier and internal ID.
- Own unique-conflict handling and transaction boundaries.
- Do not perform password hashing, JWT signing, or FastAPI request parsing.

### Password adapter

- `hash(plaintext) -> password_hash`
- `verify(plaintext, password_hash) -> bool`
- Use a maintained password-hashing library; exact library/work factor must be recorded in implementation dependency review.
- Treat malformed hashes as verification failure, not an internal error containing the hash.

### JWT adapter

- `issue(user_id, auth_version, now, expiry) -> encoded_token`
- `verify(encoded_token, now) -> token_claims`
- Reject algorithm confusion, invalid signature, missing subject, invalid timestamps, and expired token.
- Never log the encoded token or raw authorization header.

## API / Interface Design

### Common envelope

All auth endpoints use the P0 envelope:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": null
}
```

Errors preserve `success=false`, safe `data` when useful, typed `error.code`, safe `error.message`, and optional `meta`.

### Endpoint set

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Public | Issue access token. |
| GET | `/api/v1/auth/me` | Active user | Return safe current-user projection. |
| GET | `/api/v1/admin/users` | Admin | List safe users. |
| POST | `/api/v1/admin/users` | Admin | Create active user. |
| PATCH | `/api/v1/admin/users/{user_id}` | Admin | Change display name, role, or active status. |
| GET | `/api/v1/health/live` | Infrastructure exception | Existing liveness probe. |
| GET | `/api/v1/health/ready` | Infrastructure exception | Existing readiness probe. |

### Request and response decisions

- Login request: `identifier`, `password`.
- Login response: `access_token`, `token_type="bearer"`, `expires_at`, `user` safe projection.
- User create request: `identifier`, `display_name`, `password`, `role`.
- User update request: optional `display_name`, `role`, `status`; at least one field required.
- User list response: safe user projections with pagination metadata if the implementation uses pagination; the initial pilot may return a bounded list.
- No endpoint accepts or returns `external_subject` in the phase-one Admin UI.

### Authorization and error mapping

| Condition | Status | Code |
|---|---:|---|
| Missing/malformed/expired token | 401 | `TOKEN_INVALID` |
| Inactive user or auth-version mismatch | 401 | `ACCOUNT_INACTIVE` |
| Invalid login | 401 | `AUTHENTICATION_FAILED` |
| Non-Admin calling Admin endpoint | 403 | `FORBIDDEN` |
| Duplicate normalized identifier | 409 | `ACCOUNT_CONFLICT` |
| Invalid role/password/field | 422 | `VALIDATION_ERROR` |
| Target user absent | 404 | `USER_NOT_FOUND` |

## Data Design

Use the logical User model in `auth-password-jwt-data-model.md`. The implementation must add one Alembic migration from revision `20260726_0001`, with no unrelated business tables.

### Transaction rules

- Account creation commits User row and hash together.
- Status/role changes commit as one transaction.
- Duplicate identifiers map to a stable conflict response.
- User list reads use a safe projection, not full entity serialization.

### Token invalidation rules

- Deactivation increments `auth_version` and sets status deactivated.
- A protected request rejects a token whose auth version differs from the current User row.
- Reactivation does not restore pre-deactivation tokens.

## UI / User Flow Design

### Login view

- Fields: account identifier and password.
- States: idle, submitting, authenticated, generic authentication error, API unavailable.
- On success: store session, fetch current user, route to authenticated shell.
- On `401`: show generic credentials error and clear any partial session.
- Password field is never included in telemetry or client logs.

### Authenticated shell

- Displays safe current-user name and role.
- Provides logout that clears token/session state.
- `401` from any protected call clears session and returns to login.
- `403` shows forbidden state without clearing a valid session.

### Admin user view

- Visible only to Admin users, but API remains authoritative.
- Lists identifier, display name, role, status, and timestamps.
- Create form requires identifier, display name, initial password, and one role.
- Edit form changes display name, role, or status; destructive deactivation requires confirmation.
- No password hash, token, external subject, or provider credential is shown.

## Workflow / Execution Design

### Login sequence

1. Validate request shape.
2. Normalize identifier.
3. Load user.
4. Verify password hash with constant-time adapter behavior.
5. Check status.
6. Issue JWT.
7. Return safe projection.

### Protected request sequence

1. Parse bearer header.
2. Verify JWT.
3. Load current user.
4. Check status and auth version.
5. Check current role when required.
6. Execute the future use case.

## Integration Design

- PostgreSQL: local repository connection only; no external network calls.
- Password adapter: local library boundary; no provider SDK leakage into services.
- JWT adapter: local signing boundary; key loaded from runtime configuration.
- SSO: deferred adapter boundary, no implementation or network call.

## Security / Audit / Reliability Design

- Use generic login errors to avoid account enumeration.
- Redact credential-shaped values using the existing P0 safety boundary and add auth-specific cases.
- Do not return ORM objects directly.
- Enforce role checks server-side.
- Reject deactivated/version-mismatched sessions immediately.
- Do not create audit persistence here; later `audit-minimal` must record account operations without secrets.

## Validation and Error Handling

- Empty/whitespace identifier: `422 VALIDATION_ERROR`.
- Invalid role: `422 VALIDATION_ERROR`.
- Password below approved minimum: `422 VALIDATION_ERROR`.
- Duplicate identifier: `409 ACCOUNT_CONFLICT`.
- Invalid login: `401 AUTHENTICATION_FAILED` with generic message.
- Invalid token: `401 TOKEN_INVALID`; do not echo token.
- Inactive/version-mismatched account: `401 ACCOUNT_INACTIVE`.
- Insufficient role: `403 FORBIDDEN`.
- Database failure: safe `5xx` envelope; no connection string, SQL, hash, or token in message.

### Edge Cases

1. Identifier differs only by case/whitespace: normalized uniqueness decision applies consistently.
2. User is deactivated between token validation and use-case authorization: current-user check occurs immediately before the use case; transaction boundaries must fail closed if the user mutation is observed.
3. Role changes while a browser holds an old token: current role is loaded from the database, so the next request uses the new role.
4. A malformed stored password hash: login fails generically and does not expose the hash.
5. A missing JWT key outside local mode: application/auth readiness fails closed; no token is issued.
6. Health probe request without a bearer token: remains allowed under ADR-0005 and is not treated as business-route bypass.

## Testing Considerations

- Unit tests for password adapter, JWT claims/expiry/version, normalization, and safe projections.
- API tests for login success/failure, current user, Admin CRUD lifecycle, `401`, `403`, conflict, and validation responses.
- Integration tests for migration upgrade/reapply and user uniqueness/status/role persistence.
- Security tests for log/response redaction and no secret-shaped values.
- Frontend tests/build for login states, session restore, logout, `401`, and `403` mapping.
- Compose smoke with seeded or documented first-Admin path, without real company documents or external identity services.

## Risks / Design Tradeoffs

- A database lookup on each protected request provides immediate deactivation/role effect at the cost of one indexed read; this is preferred for pilot correctness.
- No refresh token reduces surface area but requires re-login after access-token expiry.
- Admin-supplied initial passwords are operationally simple but require a secure bootstrap/runbook; confirm before implementation.

## Open Questions

- Resolve OQ-AUTH-001 through OQ-AUTH-005 and record accepted defaults before implementation.
- Decide whether the JWT algorithm/key rotation policy requires a new security ADR or is accepted under ADR-0002 for the pilot.
