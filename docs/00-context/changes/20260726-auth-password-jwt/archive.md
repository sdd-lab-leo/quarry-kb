# Change Archive: 20260726-auth-password-jwt

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Archived at | 2026-07-26 |
| Manifest | `manifest.yaml` → `archived` |
| Base commit at handoff | `f3de17826d9b9e1ce3aec67adcea3e5f6bf1d888` |

## What Shipped

- Accepted ADR-0006 and Confirmed OQ-AUTH-001 through OQ-AUTH-005, UUID `user_id`, and `AUTH_INTERNAL_ERROR`.
- Alembic migration `20260726_0002` adding only the `users` table.
- Argon2id password adapter and HS256 JWT adapter (`JWT_SIGNING_KEY`, `sub`/`iat`/`exp`/`auth_version`, no `role` claim).
- Auth APIs: `POST /auth/login`, `GET /auth/me`, Admin user list/create/update.
- First-Admin env bootstrap with serialized zero-Admin create and fail-closed missing/invalid config.
- Vue login/session/Admin UI with memory + `sessionStorage` token handling (no `localStorage`).
- Health probes remain anonymous ADR-0005 exceptions.

## Verification Evidence

| Command | Result |
|---|---|
| `python3 scripts/validate_execution_manifest.py …/manifest.yaml` | pass |
| `git diff --check` | pass |
| `cd backend && .venv/bin/python -m pytest` | pass (35 tests) |
| `cd frontend && npm run build` | pass |
| Compose YAML parse | pass |
| `docker compose … config` / live Alembic against Postgres | skipped (no Docker in environment; L-010) |
| no-`localStorage` scan | pass |
| no audit/knowledge tables in auth migration | pass |

## Residual Risks

- Live Compose/Postgres migration smoke was not run in this environment.
- First Compose boot after this slice requires valid `AUTH_BOOTSTRAP_ADMIN_*` when zero Admins exist (fail-closed).
- Audit persistence remains deferred to `audit-minimal` for full plan P2 exit.
- JWT HS256 remains single-host pilot posture.

## Lessons

None new beyond existing L-010 Dockerless verification guidance.
