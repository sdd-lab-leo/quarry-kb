# Change Archive: 20260726-repo-bootstrap

| Field | Value |
|---|---|
| Archived at | 2026-07-26 |
| Final manifest status | archived |
| Owner | cloud-agent |

## What Shipped

- Compose foundation (`deploy/docker-compose.yml`) with `web`, `api`, `postgres`, upload volume boundary, and Compose-network API exposure.
- `.env.example` with placeholder gateway settings and default allowlist host `gateway.internal`.
- FastAPI settings boundary with literal embedding/OCR host allowlist validation.
- Health probes: `GET /api/v1/health/live`, `GET /api/v1/health/ready` (200 ready / 503 not-ready + components).
- Alembic baseline `20260726_0001` enabling PostgreSQL `vector` extension only (no business tables).
- Vue 3 shell with typed API client and `loading` / `ready` / `needs_attention` / `unreachable` states.
- Dockerless verification suite and local uvicorn smoke evidence.
- Change package proposal/manifest/review/archive plus observed lesson L-010.

## Actual files modified / added

- `.env.example`
- `README.md`
- `deploy/docker-compose.yml`
- `backend/app/**`, `backend/alembic/**`, `backend/tests/**`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/alembic.ini`, `backend/pytest.ini`
- `frontend/src/**`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig*.json`, `frontend/index.html`, `frontend/Dockerfile`, `frontend/nginx.conf`
- `scripts/validate_execution_manifest.py`
- `docs/00-context/changes/20260726-repo-bootstrap/**`
- `docs/00-context/repo-bootstrap-traceability.md`
- `docs/lessons/observed/L-010-dockerless-verification-for-bootstrap.md`

## Verification Evidence

Passed:

- execution-manifest schema validation
- `git diff --check`
- `backend` pytest (21 passed)
- `frontend` `npm run build`
- Compose YAML parse
- local uvicorn health smoke (live 200, ready 503 DATABASE_NOT_READY with components)

Not run / skipped:

- `docker compose -f deploy/docker-compose.yml config` — Docker CLI unavailable
- live `alembic upgrade head` reapply against Postgres — no Postgres/Docker runtime
- full browser Compose frontend-to-backend path — depends on Docker Compose up

No git commit SHA for this apply was created (explicitly requested not to commit/push/PR).

## Scope Changes

None. Auth, upload, OCR execution, embedding calls, retrieval/RAG, chat, provider CRUD, and audit were not implemented.

## Residual Risks / Follow-Ups

- OQ-BOOT-02: Compose image tag is a development pin, not pilot-approved.
- OQ-BOOT-01: probe management port still open.
- OQ-09: concrete gateway values still unresolved.
- Docker/Postgres runtime smoke still required before claiming P1 stage gate complete.
- Product-owner acceptance of P0/slice remains a process gate outside this code change.

## Rollback / Recovery Notes

- Remove or revert the added `backend/`, `frontend/`, `deploy/`, `.env.example`, scripts, and change-package docs if the slice is abandoned.
- No production data migrations were applied in this environment.
- Do not delete Compose volumes that may later hold uploads/DB data without an explicit recovery plan.

## Lessons

| Lesson | Added? | Path |
|---|---|---|
| Dockerless verification for bootstrap | yes | `docs/lessons/observed/L-010-dockerless-verification-for-bootstrap.md` |

## Next recommended tasks

1. Product-owner acceptance of remediated P0 + `repo-bootstrap` docs/code.
2. Run Compose/Postgres migration smoke in a Docker-capable environment.
3. Start `auth-password-jwt` SDD/implementation only after owner acceptance and a fresh execution manifest for that slice.
