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
Password Adapter
        │ verify supplied password against stored hash
        ▼
Active-status check
        │ active only
        ▼
JWT Adapter
        │ sign sub=user_id, iat, exp, auth_version
        ▼
Safe auth response
        │ token + current user summary
        ▼
Browser session state
```

### Login Field Mapping

| Input / output | Destination | Rule |
|---|---|---|
| Account identifier | User lookup key | Normalize according to approved identifier rule. |
| Password | Password adapter only | Never persist, log, or include in response. |
| User ID | JWT subject and current-user summary | Internal ID; not an external provider subject. |
| Current role | Safe profile and authorization lookup | Current DB value is authoritative. |
| JWT | Browser session state | Never write to logs or render as UI content. |

## Flow 2: Protected Request

```text
HTTP bearer token
        ▼
Token validation
  malformed/expired/invalid ──► 401 TOKEN_INVALID
        │ valid subject
        ▼
Current-user repository lookup
  missing/inactive ────────────► 401 ACCOUNT_INACTIVE / TOKEN_INVALID
        │ active user
        ▼
Current role authorization
  role not allowed ────────────► 403 FORBIDDEN
        │ allowed
        ▼
Future business use case
```

The role claim, if present for display convenience, is not used as the authorization source of truth. A role update is therefore visible on the next protected request.

## Flow 3: Admin Account Lifecycle

```text
Admin request
        ▼
Authenticate current Admin
        ▼
Validate identifier / role / password / target state
        ▼
Transactional user mutation
        ├── create active user
        ├── change role
        ├── deactivate user and advance auth version
        └── reactivate user
        ▼
Safe response (no hash/token)
        ▼
Next request reads committed current state
```

## Flow 4: Frontend Session Lifecycle

| Event | Client action | API behavior |
|---|---|---|
| App start with session | Restore token and call `/auth/me`. | Return current safe user or `401`. |
| Login success | Store approved session state and route to authenticated shell. | Return token and safe profile. |
| Login failure | Show generic error; retain no password. | Return `401 AUTHENTICATION_FAILED`. |
| Protected `401` | Clear token and return to login. | Reject invalid/inactive session. |
| Protected `403` | Keep session; show forbidden state. | Reject insufficient current role. |
| Explicit logout | Clear token/session state. | No server session record is required by this slice. |

## Data Lifecycle

1. A password enters memory only for the duration of login or an Admin account operation.
2. The password adapter produces or verifies a hash.
3. PostgreSQL stores the hash and non-secret identity metadata.
4. JWT signing produces an access token with bounded lifetime and auth version.
5. Protected requests use the token to locate the current user; the token is not persisted as a session row.
6. Deactivation increments the auth version and causes both version-mismatched and inactive-user tokens to fail.

## Failure Boundaries

- Password verification failure is indistinguishable from unknown identifier.
- User lookup/database failure fails closed and is mapped to a safe server/dependency error.
- Token parser errors do not echo raw token content.
- Role denial does not reveal unrelated user records.
- No flow sends identity data to the model gateway, public provider, OCR, embedding, or external SSO.

## Data Safety Checks

- [ ] Hash and token values are absent from API response models.
- [ ] Redaction covers password, bearer, authorization, token, and secret-shaped values.
- [ ] Admin list/current-user shapes are allowlisted fields rather than ORM serialization.
- [ ] Deactivation behavior is covered by an integration test using an unexpired token.
- [ ] Role change behavior is covered by a next-request authorization test.
