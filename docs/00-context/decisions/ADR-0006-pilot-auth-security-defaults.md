# ADR-0006: Pilot Auth Security Defaults For Password And JWT

## Status

Proposed

## Date

2026-07-26

## Context

ADR-0002 locked phase-one password authentication with JWT and reserved `external_subject` for later SSO. The `auth-password-jwt` SDD review found that several security parameters were still dual-proposed or labeled optional, which would force implementers to invent policy during coding:

- JWT algorithm and lifetime
- Password hashing library and work factor
- Whether `auth_version` is required for token invalidation
- Browser access-token storage
- First-Admin bootstrap mechanism
- Last-Admin lockout protection
- Password policy and login versus create/bootstrap validation
- Account identifier normalization
- Missing signing-key fail mode versus ADR-0005 readiness

These choices are security posture decisions and must be recorded before implementation handoff (`TASK-AUTH-001` / `TASK-AUTH-008`).

## Decision

For the department intranet pilot, adopt the following defaults unless this ADR is superseded:

1. **Password hashing:** Argon2id via a maintained Python password-hashing library. Persist only the encoded hash string. Treat malformed hashes as verification failure.
2. **Password policy (OQ-AUTH-001):** New account and bootstrap passwords require a minimum of 12 characters, at least one non-whitespace character, and no forced complexity regex. Passwords remain case-sensitive. Enforce this policy at Admin create and first-Admin bootstrap with `422 VALIDATION_ERROR`. At login, after request-shape validation, never return a policy-specific failure: unknown identifier, wrong password, inactive account, and structurally valid passwords that would fail the create/bootstrap policy all use the same `401 AUTHENTICATION_FAILED` category.
3. **Account identifier normalization (OQ-AUTH-005):** Trim surrounding whitespace and lowercase for lookup and uniqueness. After normalization, length must be 3–64 and match `[a-z0-9._@-]+`. Display name is stored separately and is not derived as the login key. Optional bootstrap display name defaults to the **normalized** identifier when `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` is omitted.
4. **Internal user ID:** Use UUID `user_id` values as the stable internal ownership identifier for this slice.
5. **JWT algorithm:** HS256 with the runtime environment secret `JWT_SIGNING_KEY`. When `APP_ENV` is not `local`, missing or blank `JWT_SIGNING_KEY` fails closed at settings/startup validation and the process must not serve auth routes. This does **not** add a JWT component to ADR-0005 readiness (`configuration`, `database`, `migration`, `vector_capability` remain unchanged). Asymmetric keys and multi-host key distribution require a future ADR.
6. **Access-token lifetime:** 30 minutes. Required JWT claims are `sub`, `iat`, `exp`, and `auth_version` (`iat`/`exp` are UTC NumericDate values; login response `expires_at` mirrors `exp` as an ISO-8601 UTC timestamp). No refresh-token endpoint and no server-side session table in this slice. Pilot tokens must **not** include a `role` claim; current role is always loaded from PostgreSQL.
7. **Token invalidation:** Every access token includes `auth_version`. Deactivation increments `auth_version`. Protected requests must reject tokens whose `auth_version` does not match the current User row, and must also reject inactive accounts. `auth_version` is mandatory, not optional.
8. **Authorization source of truth:** Current PostgreSQL `role` and `status` for the internal `user_id`. Token claims never authorize.
9. **Browser storage:** Keep the access token in memory with `sessionStorage` as the reload fallback. Do not use `localStorage` for access tokens.
10. **First-Admin bootstrap:** One-time startup bootstrap from runtime environment variables:
    - `AUTH_BOOTSTRAP_ADMIN_IDENTIFIER` (required when bootstrapping)
    - `AUTH_BOOTSTRAP_ADMIN_PASSWORD` (required when bootstrapping)
    - `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` (optional; default = normalized identifier)
    Bootstrap runs only when zero Admin accounts exist (counting any Admin row regardless of status), creates exactly one active Admin, never commits default passwords, and is ignored once any Admin exists. The zero-Admin check and create must be serialized so concurrent starts have one winner. When zero Admins exist and required bootstrap values are missing or invalid: create no Admin and **fail closed at startup** (process does not become ready for business use).
11. **Last-Admin protection:** Reject any Admin operation that would deactivate or demote the last remaining active Admin account. The count/check and mutation must run in one serialized transaction.
12. **Unexpected server errors:** Auth request-validation and auth-dependency failures use the P0 envelope. Unexpected server/dependency failures use HTTP 500 with `error.code = INTERNAL_ERROR` and a safe non-secret message; never return raw exception text, SQL, hashes, tokens, or connection strings.

## Alternatives Considered

| Alternative | Why not |
|---|---|
| bcrypt only | Acceptable, but Argon2id is the stronger current default for new systems. |
| RS256 / asymmetric JWT now | Unnecessary key-distribution complexity for a single-host Compose pilot. |
| Refresh tokens + session table | Larger attack and migration surface than needed for v0.1. |
| Migration SQL seed with a committed password | Risks committing or sharing a default secret. |
| Status-only invalidation without `auth_version` | Reactivation would revive pre-deactivation tokens until expiry. |
| `localStorage` token persistence | Longer XSS exposure than memory/`sessionStorage`. |
| Policy-specific login errors for short passwords | Creates an account/policy oracle; rejected for pilot. |
| Adding JWT key as a readiness component | Would change the ADR-0005 probe contract; settings/startup fail-closed is sufficient. |

## Consequences

### Positive

- Implementers receive one concrete security contract for hashing, password policy, identifiers, JWT, bootstrap, storage, and invalidation.
- Deactivation and reactivation behavior is testable and not left to “optional” architecture wording.
- First-run operability does not require a committed admin password.
- OQ-AUTH-001 through OQ-AUTH-005 are encoded here; owner/security acceptance of this ADR closes those questions for handoff.

### Negative

- Owner/security must still accept this Proposed ADR (or amend it) before coding starts.
- Operators must supply bootstrap env vars on first boot and rotate/remove them afterward.
- Fail-closed bootstrap/startup means Compose will not become healthy until required first-Admin values are present when zero Admins exist.
- HS256 remains a single-host pilot choice and must be revisited for multi-host rollout.

### Neutral / Operational

- `TASK-AUTH-001` accepts or amends this ADR; `TASK-AUTH-008` pins the accepted revision in the execution manifest.
- Audit persistence remains deferred to `audit-minimal`.

## Review Triggers

- Company security rejects Argon2id, HS256, 30-minute TTL, password policy, identifier rule, or browser storage choice.
- Multi-host or asymmetric JWT rollout begins.
- Refresh tokens or server-side sessions become required.
- SSO cutover changes bootstrap or identity linkage assumptions.
- Readiness probe contract needs a dedicated auth-config component.

## Related Documents

- [ADR-0002](ADR-0002-lock-technology-stack-and-auth-evolution.md)
- [ADR-0005](ADR-0005-bootstrap-probe-allowlist-and-readiness-contract.md)
- [auth-password-jwt requirements](../../01-requirements/auth-password-jwt-requirement.md)
- [auth-password-jwt design](../../05-design/auth-password-jwt-design.md)
- [auth-password-jwt tasks](../../06-tasks/auth-password-jwt-tasks.md)
