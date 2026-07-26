# L-010: Keep Dockerless verification for repo-bootstrap

| Field | Value |
|---|---|
| Date | 2026-07-26 |
| Module | repo-bootstrap / verification |
| Symptom | Agent or constrained CI environments may lack Docker, so `docker compose … config` and live Compose/migration smoke cannot run |
| Root cause | Treating Docker runtime availability as an implicit hard gate for all bootstrap verification |
| Correct practice | Keep required gates Dockerless: pytest (with fakes for readiness dependencies), frontend build, Compose YAML parse, and local API process smoke. Mark Docker Compose/runtime and live Alembic-against-Postgres checks as optional when Docker/Postgres are unavailable, and record the skip with evidence |
| Promoted? | no |
| Related | ADR-0005, `docs/06-tasks/repo-bootstrap-tasks.md`, change `20260726-repo-bootstrap` |
| Source | observed-incident |

## Notes

During `repo-bootstrap` apply, the environment had Python/Node but no Docker CLI. Required verification still proved readiness contract behavior (HTTP 200/503 shapes) via unit/API tests and a local uvicorn smoke with database unavailable.
