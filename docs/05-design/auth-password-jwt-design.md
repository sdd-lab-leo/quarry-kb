# Detailed Design: Password Authentication and JWT Authorization

## Status

Approved — Implementation Ready

## Overview

This design turns the `auth-password-jwt` behavior into implementation-facing module, data, API, UI, and verification boundaries. It extends the verified P0 foundation; it does not implement code in this document-remediation session.

## Source Architecture

- `docs/04-architecture/auth-password-jwt-architecture.md`
- `docs/04-architecture/auth-password-jwt-data-flow.md`
- `docs/04-architecture/auth-password-jwt-data-model.md`
- `docs/03-spec/auth-password-jwt-spec.md`
- ADR-0002, ADR-0005, and Accepted ADR-0006

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

- `[DEFAULT]` Use an internal UUID `user_id` (ADR-0006).
- `[DEFAULT]` Use an access JWT with `sub`, `iat`, `exp`, and mandatory `auth_version`; do not emit a `role` claim; current role/status are loaded from PostgreSQL for authorization.
- `[DEFAULT]` Use HS256 with runtime environment secret `JWT_SIGNING_KEY`. When `APP_ENV` is not `local`, missing/blank key fails closed at settings/startup validation; auth routes are not served. Do not add a JWT component to ADR-0005 readiness.
- `[DEFAULT]` Use 30-minute access-token lifetime and no refresh-token endpoint.
- `[DEFAULT]` Store the browser token in memory with `sessionStorage` fallback; never `localStorage`.
- `[DEFAULT]` Admin supplies an initial password when creating an account; password reset is out of scope.
- `[DEFAULT]` New account/bootstrap passwords use Argon2id and the 12-character/non-whitespace policy (`422` on create/bootstrap). After login request-shape validation, all credential failures use generic `401 AUTHENTICATION_FAILED`.
- `[DEFAULT]` First Admin is created from `AUTH_BOOTSTRAP_ADMIN_*` env vars only when zero Admins exist; optional display name defaults to the normalized identifier; missing/invalid required values fail closed at startup.
- `[DEFAULT]` Last active Admin cannot be deactivated or demoted.
- `[DEFAULT]` Unexpected server/dependency failures use HTTP 500 / `AUTH_INTERNAL_ERROR` in the P0 envelope.

These defaults are recorded in Accepted ADR-0006 (2026-07-26), including Confirmed OQ-AUTH-001 through OQ-AUTH-005, UUID `user_id`, and `AUTH_INTERNAL_ERROR`.

## Design Scope

### Modules

- Authentication API and request/response models.
- Account administration API and safe user projections.
- Authentication and authorization service layer.
- First-Admin bootstrap path at startup.
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
- Return `401 AUTHENTICATION_FAILED` for structurally valid unknown, invalid, or inactive credentials; request-shape failures use `422 VALIDATION_ERROR` in the same P0 envelope.
- Never pass raw password values into logs, exception text, or response models.

### Current-user and authorization dependency

- Read the bearer token from the `Authorization` header.
- Verify signature, algorithm, expiry, subject, and `auth_version`.
- Load the current User row by internal ID.
- Reject missing subjects with `401 TOKEN_INVALID`.
- Reject inactive or version-mismatched users with `401 ACCOUNT_INACTIVE`.
- Return an internal authenticated-user context containing `user_id` and current role.
- Role checks compare the current database role to the required role set.

### First-Admin bootstrap

- On startup, serialize the zero-Admin check and create so concurrent starts have one winner; if zero Admin accounts exist and bootstrap env vars are present, create one active Admin.
- Validate the password and identifier policy before create. When zero Admins exist and required bootstrap values are missing or invalid, create no Admin and fail closed at startup.
- If any Admin already exists (active or deactivated), ignore bootstrap env vars.
- Optional `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` defaults to the normalized identifier.
- Never commit default bootstrap passwords.

### Account administration service

- Create: normalize identifier, validate password/role, hash password, create active User transactionally.
- List: return a bounded list (maximum 200 items) of `UserSummary` projections; no pagination in this slice.
- Update: permit display name, role, and status changes under an Admin check; update timestamps atomically.
- Deactivate: set status/time and increment `auth_version`.
- Reactivate: set active status, clear deactivation time, and keep pre-change tokens invalid through the incremented version.
- Last-Admin guard: reject deactivate/demote when it would leave zero active Admins (`409 LAST_ADMIN_REQUIRED`).
- No delete operation is included; deactivation is the v0.1 lifecycle control.

### Repository boundary

- Own user lookup by normalized identifier and internal ID.
- Own unique-conflict handling and transaction boundaries.
- Do not perform password hashing, JWT signing, or FastAPI request parsing.

### Password adapter

- `hash(plaintext) -> password_hash`
- `verify(plaintext, password_hash) -> bool`
- Use Argon2id through a maintained password-hashing library; pin the dependency version in implementation review.
- Treat malformed hashes as verification failure, not an internal error containing the hash.

### JWT adapter

- `issue(user_id, auth_version, now, expiry) -> encoded_token`
- `verify(encoded_token, now) -> token_claims`
- Issue/verify required `sub`, `iat`, `exp`, and `auth_version` claims using HS256 and `JWT_SIGNING_KEY`; do not emit a `role` claim; reject algorithm confusion, invalid signature, missing subject, missing/invalid `auth_version`, invalid UTC timestamps, and expired token.
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

Errors preserve `success=false`, safe `data` when useful, typed `error.code`, safe `error.message`, and optional `meta`. Framework request-validation and auth-dependency failures must be normalized into this envelope; raw FastAPI error bodies are not part of the auth contract. Unexpected server/dependency failures use HTTP 500 with `error.code = AUTH_INTERNAL_ERROR` and a safe message.

### Endpoint set

| Method | Path | Auth | Success status | Purpose |
|---|---|---|---:|---|
| POST | `/api/v1/auth/login` | Public | 200 | Issue access token. |
| GET | `/api/v1/auth/me` | Active user | 200 | Return `UserSummary`. |
| GET | `/api/v1/admin/users` | Admin | 200 | List safe users (bounded, max 200). |
| POST | `/api/v1/admin/users` | Admin | 201 | Create an account. |
| PATCH | `/api/v1/admin/users/{user_id}` | Admin | 200 | Change display name, role, or active status. |
| GET | `/api/v1/health/live` | Infrastructure exception | 200 | Existing liveness probe. |
| GET | `/api/v1/health/ready` | Infrastructure exception | 200/503 | Existing readiness probe. |

### Request and response decisions

- Login request: `identifier`, `password`.
- Login response: `access_token`, `token_type="bearer"`, `expires_at`, `user` as `UserSummary`.
- User create request: `identifier`, `display_name`, `password`, `role`.
- User update request: optional `display_name`, `role`, `status`; at least one field required.
- User list response: `{ "items": UserSummary[] }` with at most 200 items; no pagination metadata in this slice.
- Shared `UserSummary`: `user_id`, `identifier`, `display_name`, `role`, `status`, `created_at`, `updated_at`.
- No endpoint accepts or returns `external_subject`, `password_hash`, or `auth_version` in phase one.

### Authorization and error mapping

| Condition | Status | Code |
|---|---:|---|
| Missing/malformed/expired/unknown-subject token | 401 | `TOKEN_INVALID` |
| Inactive user or auth-version mismatch | 401 | `ACCOUNT_INACTIVE` |
| Invalid login | 401 | `AUTHENTICATION_FAILED` |
| Non-Admin calling Admin endpoint | 403 | `FORBIDDEN` |
| Duplicate normalized identifier | 409 | `ACCOUNT_CONFLICT` |
| Last-Admin demotion/deactivation | 409 | `LAST_ADMIN_REQUIRED` |
| Invalid role/password/field/identifier | 422 | `VALIDATION_ERROR` |
| Target user absent | 404 | `USER_NOT_FOUND` |
| Unexpected server/dependency failure | 500 | `AUTH_INTERNAL_ERROR` |

## Data Design

Use the logical User model in `auth-password-jwt-data-model.md`. The implementation must add one Alembic migration from revision `20260726_0001`, with no unrelated business tables.

### Transaction rules

- Account creation commits User row and hash together.
- Status/role changes commit as one transaction.
- Bootstrap zero-Admin check/create and last-Admin protection must be serialized with the account mutation so concurrent starts or Admin updates cannot create duplicate first Admins or leave zero active Admins.
- Duplicate identifiers map to a stable conflict response.
- User list reads use the shared `UserSummary` projection, not full entity serialization.
- Last-Admin checks occur inside the same transaction as the mutation.

### Token invalidation rules

- Deactivation increments `auth_version` and sets status deactivated.
- A protected request rejects a token whose `auth_version` differs from the current User row.
- Reactivation does not restore pre-deactivation tokens.
- `auth_version` validation is mandatory, not optional.

## UI / User Flow Design

### Login view

- Fields: account identifier and password.
- States: idle, submitting, authenticated, generic authentication error, API unavailable.
- On success: store session in memory/`sessionStorage`, fetch current user, route to authenticated shell.
- On `401`: show generic credentials error and clear any partial session.
- Password field is never included in telemetry or client logs.

### Authenticated shell

- Displays safe current-user name and role.
- Provides logout that clears token/session state.
- `401` from any protected call clears session and returns to login.
- `403` shows forbidden state without clearing a valid session.

### Admin user view

- Visible only to Admin users, but API remains authoritative.
- Lists identifier, display name, role, status, and timestamps from `UserSummary`.
- Create form requires identifier, display name, initial password, and one role.
- Edit form changes display name, role, or status; destructive deactivation requires confirmation.
- Surface `LAST_ADMIN_REQUIRED` as a non-destructive error.
- No password hash, token, external subject, auth version, or provider credential is shown.

## Workflow / Execution Design

### Login sequence

1. Validate request shape.
2. Normalize identifier.
3. Load user.
4. Verify password hash with constant-time adapter behavior.
5. Check status.
6. Issue JWT with current `auth_version`.
7. Return `UserSummary`.

### Protected request sequence

1. Parse bearer header.
2. Verify JWT including `auth_version` claim presence.
3. Load current user.
4. Check status and `auth_version` match.
5. Check current role when required.
6. Execute the future use case.

## Integration Design

- PostgreSQL: local repository connection only; no external network calls.
- Password adapter: local Argon2id library boundary; no provider SDK leakage into services.
- JWT adapter: local signing boundary; key loaded from runtime configuration.
- SSO: deferred adapter boundary, no implementation or network call.

## Security / Audit / Reliability Design

- Use generic login errors to avoid account enumeration.
- Redact credential-shaped values using the existing P0 safety boundary and add auth-specific cases.
- Do not return ORM objects directly.
- Enforce role checks server-side.
- Reject deactivated/version-mismatched sessions immediately.
- Enforce last-Admin protection server-side.
- Do not create audit persistence here; later `audit-minimal` must record account operations without secrets.
- Login rate limiting is deferred for the intranet pilot.

## Validation and Error Handling

- Empty/whitespace identifier or identifier outside 3–64 / pattern rules after trim+lowercase: `422 VALIDATION_ERROR`.
- Empty/whitespace display name or display name outside 1–128 after trim: `422 VALIDATION_ERROR`.
- Invalid role: `422 VALIDATION_ERROR`.
- New account/bootstrap password below 12 characters or containing only whitespace: `422 VALIDATION_ERROR`; no forced complexity regex; passwords remain case-sensitive.
- Login after request-shape validation: unknown identifier, wrong password, inactive account, and structurally valid passwords that fail create policy all return `401 AUTHENTICATION_FAILED` with the same safe category.
- Duplicate identifier: `409 ACCOUNT_CONFLICT`.
- Last-Admin violation: `409 LAST_ADMIN_REQUIRED`.
- Invalid/unknown-subject token: `401 TOKEN_INVALID`; do not echo token.
- Inactive/version-mismatched account: `401 ACCOUNT_INACTIVE`.
- Insufficient role: `403 FORBIDDEN`.
- Unexpected database/dependency failure: HTTP 500 / `AUTH_INTERNAL_ERROR`; no connection string, SQL, hash, or token in message.

### Edge Cases

1. Identifier differs only by case/whitespace: normalized uniqueness decision applies consistently.
2. User is deactivated between token validation and use-case authorization: current-user check occurs immediately before the use case; transaction boundaries must fail closed if the user mutation is observed.
3. Role changes while a browser holds an old token: current role is loaded from the database, so the next request uses the new role.
4. A malformed stored password hash: login fails generically and does not expose the hash.
5. A missing/blank `JWT_SIGNING_KEY` when `APP_ENV` is not `local`: settings/startup validation fails closed; auth routes are not served; no token is issued. ADR-0005 readiness components remain unchanged.
6. Health probe request without a bearer token: remains allowed under ADR-0005 and is not treated as business-route bypass.
7. Reactivation after deactivation: old tokens remain invalid because `auth_version` advanced.
8. Attempt to demote/deactivate the sole active Admin: rejected with `LAST_ADMIN_REQUIRED`.

## Testing Considerations

- Unit tests for password adapter, JWT claims/expiry/version, normalization, and safe projections.
- API tests for login success/failure, current user, Admin CRUD lifecycle, last-Admin guard, bootstrap-once, `401`, `403`, conflict, and validation responses.
- Integration tests for migration upgrade/reapply and user uniqueness/status/role persistence.
- Security tests for log/response redaction and no secret-shaped values.
- Frontend tests/build for login states, session restore, logout, Admin UI, `401`, and `403` mapping.
- Compose smoke with env bootstrap first-Admin path, without real company documents or external identity services.

## Risks / Design Tradeoffs

- A database lookup on each protected request provides immediate deactivation/role effect at the cost of one indexed read; this is preferred for pilot correctness.
- No refresh token reduces surface area but requires re-login after access-token expiry.
- Env-based first-Admin bootstrap is operationally explicit and avoids committed secrets; operators must remove bootstrap secrets after first success.
- Bounded list (max 200) avoids pagination complexity for a ~60-user department.

## Open Questions

None remaining for implementation.
