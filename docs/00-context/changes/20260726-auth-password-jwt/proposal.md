# Change Proposal: 20260726-auth-password-jwt

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Date | 2026-07-26 |
| Proposed by | cloud-agent |
| Status | accepted |

## Goal

Provide account/password login, JWT access sessions, server-side role authorization, Admin-managed account lifecycle, and a safe Vue session/Admin surface on top of the verified `repo-bootstrap` foundation.

## In Scope

- User schema migration from `20260726_0001`
- Argon2id password hashing and HS256 JWT adapters
- Login, current-user, and Admin user APIs
- First-Admin env bootstrap with fail-closed behavior
- Frontend memory/`sessionStorage` session, login, and Admin UI
- Tests and verification for the auth vertical slice

## Out Of Scope

- Refresh tokens, SSO/OIDC/LDAP, MFA, password reset, email verification
- Audit persistence/query APIs (`audit-minimal`)
- Upload, OCR, embedding, RAG, chat, provider tables/APIs
- Real secrets, default committed passwords, real corpora
- Lockfile or unrelated dependency changes beyond required auth libraries
- Git commit, push, or PR creation unless explicitly requested

## Inputs

- Approved `auth-password-jwt` SDD chain under `docs/01`–`docs/06` and traceability
- Accepted ADR-0006; ADR-0002; ADR-0005
- Confirmed OQ-AUTH-001 through OQ-AUTH-005
- Confirmed UUID `user_id` and `AUTH_INTERNAL_ERROR`

## Risks / Constraints

- Standards: `docs/standards/frontend.md`, `docs/standards/backend.md`
- Health probes remain ADR-0005 anonymous infrastructure exceptions
- No `localStorage` access tokens; no JWT `role` authorization
- Secrets stay outside Git

## Acceptance

- Active users can log in and receive a 30-minute access JWT
- Admin can create/list/update/deactivate/reactivate users with exactly one role
- Deactivation increments `auth_version` and rejects stale tokens
- Last active Admin cannot be deactivated or demoted
- Bootstrap creates at most one Admin and fails closed on missing/invalid config when zero Admins exist
- Frontend restores session from memory/`sessionStorage` only
- Verification commands in `manifest.yaml` pass

## Verification Plan

See `manifest.yaml` `verification.commands`.
