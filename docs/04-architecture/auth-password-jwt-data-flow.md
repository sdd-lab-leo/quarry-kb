# Data Flow: Password Authentication and JWT Authorization

## Scope

This document describes the identity, token, account lifecycle, and authorization data paths for `auth-password-jwt`. It does not describe document, retrieval, chat, provider, or audit data flows.

## Flow 1: Login

```text
Browser credentials
        │ identifier + password over HTTPS
        ▼
Authentication API
        │ normalize identifier
        ▼
User Repository ────────► PostgreSQL users
        │ user row or generic failure
        ▼
Password Adapter (Argon2id)
        │ verify supplied password against stored hash
        ▼
Active-status check
        │ active only
        ▼
JWT Adapter
        │ sign sub=user_id, iat, exp, auth_version
        ▼
Safe auth response
        │ token + UserSummary
        ▼
Browser session state (memory + sessionStorage)
```

### Login Field Mapping

| Input / output | Destination | Rule |
|---|---|---|
| Account identifier | User lookup key | Normalize according to approved identifier rule. |
| Password | Password adapter only | Never persist, log, or include in response. |
| User ID | JWT subject and current-user summary | Internal ID; not an external provider subject. |
| Current role | Safe profile and authorization lookup | Current DB value is authoritative. |
| `auth_version` | JWT claim only | Never returned in UserSummary. |
| JWT | Browser session state | Never write to logs, `localStorage`, or render as UI content. |

## Flow 2: Protected Request

```text
HTTP bearer token
        ▼
Token validation
  malformed/expired/invalid/unknown sub ──► 401 TOKEN_INVALID
        │ valid subject + claims
        ▼
Current-user repository lookup
  inactive or auth_version mismatch ──────► 401 ACCOUNT_INACTIVE
        │ active user and matching auth_version
        ▼
Current role authorization
  role not allowed ───────────────────────► 403 FORBIDDEN
        │ allowed
        ▼
Future business use case
```

The role claim, if present for display convenience, is not used as the authorization source of truth. A role update is therefore visible on the next protected request. `auth_version` comparison is mandatory on every protected request.

## Flow 3: Admin Account Lifecycle

```text
Admin request
        ▼
Authenticate current Admin
        ▼
Validate identifier / role / password / target state
        ▼
Last-Admin guard
  would remove/demote last active Admin ──► 409 LAST_ADMIN_REQUIRED
        ▼
Transactional user mutation
        ├── create active user
        ├── change role
        ├── deactivate user and advance auth_version
        └── reactivate user
        ▼
Safe UserSummary response (no hash/token/auth_version)
        ▼
Next request reads committed current state
```

## Flow 4: First-Admin Bootstrap

```text
Application startup
        ▼
Serialize bootstrap transaction and count any Admin accounts
  one or more Admins exist ──► ignore bootstrap env vars
        │ zero Admins
        ▼
Read AUTH_BOOTSTRAP_ADMIN_* env vars
  missing/invalid ──► create no Admin; safe startup failure behavior remains pending OQ-AUTH-002
        ▼
Create exactly one active Admin with Argon2id hash
        ▼
Later startups skip bootstrap
```

The serialized check/create is required so concurrent application starts have one winner; all losing starts re-read the committed state and skip creation. The recommended safe default for missing or invalid required bootstrap values is fail-closed startup, pending owner/security confirmation.

## Flow 5: Frontend Session Lifecycle

| Event | Client action | API behavior |
|---|---|---|
| App start with session | Restore token from memory/`sessionStorage` and call `/auth/me`. | Return current UserSummary or `401`. |
| Login success | Store approved session state and route to authenticated shell. | Return token and UserSummary. |
| Login failure | Show generic error; retain no password. | Return `401 AUTHENTICATION_FAILED`. |
| Protected `401` | Clear token and return to login. | Reject invalid/inactive/version-mismatched session. |
| Protected `403` | Keep session; show forbidden state. | Reject insufficient current role. |
| Explicit logout | Clear token/session state. | No server session record is required by this slice. |

## Data Lifecycle

1. A password enters memory only for the duration of login, bootstrap, or an Admin account operation.
2. The password adapter produces or verifies an Argon2id hash.
3. PostgreSQL stores the hash and non-secret identity metadata.
4. JWT signing produces an access token with bounded lifetime and mandatory `auth_version`.
5. Protected requests use the token to locate the current user; the token is not persisted as a session row.
6. Deactivation increments `auth_version` and causes both version-mismatched and inactive-user tokens to fail.
7. Reactivation clears `deactivated_at` but does not restore prior tokens.

## Failure Boundaries

- Password verification failure is indistinguishable from unknown identifier for structurally valid login input; request-shape validation remains a typed `VALIDATION_ERROR`.
- User lookup/database failure fails closed and is mapped to a safe server/dependency error.
- Token parser errors do not echo raw token content.
- Unknown token subject returns `TOKEN_INVALID`.
- Role denial does not reveal unrelated user records.
- No flow sends identity data to the model gateway, public provider, OCR, embedding, or external SSO.

## Data Safety Checks

- [ ] Hash, token, `external_subject`, and `auth_version` values are absent from API response models.
- [ ] Redaction covers password, bearer, authorization, token, and secret-shaped values.
- [ ] Admin list/current-user/login shapes use the shared `UserSummary` allowlist.
- [ ] Deactivation behavior is covered by an integration test using an unexpired token.
- [ ] Reactivation keeps pre-deactivation tokens invalid via `auth_version`.
- [ ] Role change behavior is covered by a next-request authorization test.
- [ ] Last-Admin demotion/deactivation is rejected.
- [ ] Access tokens are never written to `localStorage`.
