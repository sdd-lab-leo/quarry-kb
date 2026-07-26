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

These choices are security posture decisions and must be recorded before implementation handoff (`TASK-AUTH-001` / `TASK-AUTH-008`).

## Decision

For the department intranet pilot, adopt the following defaults unless this ADR is superseded:

1. **Password hashing:** Argon2id via a maintained Python password-hashing library. Persist only the encoded hash string. Treat malformed hashes as verification failure.
2. **JWT algorithm:** HS256 with the runtime environment secret `JWT_SIGNING_KEY`. Fail closed when the key is missing outside local development. Asymmetric keys and multi-host key distribution require a future ADR.
3. **Access-token lifetime:** 30 minutes. No refresh-token endpoint and no server-side session table in this slice.
4. **Token invalidation:** Every access token includes `auth_version`. Deactivation increments `auth_version`. Protected requests must reject tokens whose `auth_version` does not match the current User row, and must also reject inactive accounts. `auth_version` is mandatory, not optional.
5. **Authorization source of truth:** Current PostgreSQL `role` and `status` for the internal `user_id`. A JWT `role` claim, if present, is display convenience only and must never authorize.
6. **Browser storage:** Keep the access token in memory with `sessionStorage` as the reload fallback. Do not use `localStorage` for access tokens.
7. **First-Admin bootstrap:** One-time startup bootstrap from runtime environment variables:
   - `AUTH_BOOTSTRAP_ADMIN_IDENTIFIER` (required)
   - `AUTH_BOOTSTRAP_ADMIN_PASSWORD` (required)
   - `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` (optional; default derived from identifier)
   Bootstrap runs only when zero Admin accounts exist, creates exactly one active Admin, never commits default passwords, and is ignored once any Admin exists. The zero-Admin check and create must be serialized so concurrent starts have one winner. Missing/invalid required bootstrap values create no Admin; fail-closed startup is the recommended default pending owner/security confirmation.
8. **Last-Admin protection:** Reject any Admin operation that would deactivate or demote the last remaining active Admin account.

## Alternatives Considered

| Alternative | Why not |
|---|---|
| bcrypt only | Acceptable, but Argon2id is the stronger current default for new systems. |
| RS256 / asymmetric JWT now | Unnecessary key-distribution complexity for a single-host Compose pilot. |
| Refresh tokens + session table | Larger attack and migration surface than needed for v0.1. |
| Migration SQL seed with a committed password | Risks committing or sharing a default secret. |
| Status-only invalidation without `auth_version` | Reactivation would revive pre-deactivation tokens until expiry. |
| `localStorage` token persistence | Longer XSS exposure than memory/`sessionStorage`. |

## Consequences

### Positive

- Implementers receive one concrete security contract for hashing, JWT, bootstrap, storage, and invalidation.
- Deactivation and reactivation behavior is testable and not left to “optional” architecture wording.
- First-run operability does not require a committed admin password.

### Negative

- Owner/security must still accept this Proposed ADR (or amend it) before coding starts.
- Operators must supply bootstrap env vars on first boot and rotate/remove them afterward.
- HS256 remains a single-host pilot choice and must be revisited for multi-host rollout.

### Neutral / Operational

- `TASK-AUTH-001` accepts or amends this ADR; `TASK-AUTH-008` pins the accepted revision in the execution manifest.
- Audit persistence remains deferred to `audit-minimal`.

## Review Triggers

- Company security rejects Argon2id, HS256, 30-minute TTL, or browser storage choice.
- Multi-host or asymmetric JWT rollout begins.
- Refresh tokens or server-side sessions become required.
- SSO cutover changes bootstrap or identity linkage assumptions.

## Related Documents

- [ADR-0002](ADR-0002-lock-technology-stack-and-auth-evolution.md)
- [ADR-0005](ADR-0005-bootstrap-probe-allowlist-and-readiness-contract.md)
- [auth-password-jwt requirements](../../01-requirements/auth-password-jwt-requirement.md)
- [auth-password-jwt design](../../05-design/auth-password-jwt-design.md)
- [auth-password-jwt tasks](../../06-tasks/auth-password-jwt-tasks.md)
