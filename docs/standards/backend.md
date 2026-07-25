# Backend Development Standards

Authority for FastAPI application code under `backend/`. Hard product rules remain in `PROJECT_RULES.md`. Stack and auth evolution: ADR-0002.

## Stack

- FastAPI + Python 3.11+ (intended)
- PostgreSQL + pgvector
- Alembic for schema migrations
- Local disk uploads via Docker volume
- OpenAI-compatible client for LLM calls

Do not introduce Java/Spring/Oracle modules or hard-wire a single proprietary LLM SDK into domain services.

## Layering

```text
api/            # HTTP routers, request/response models, auth dependencies
services/       # use-cases / domain orchestration
repositories/   # persistence queries and commands
adapters/       # external systems: LLM, parsers, object/file stores, SSO later
```

Rules:

- Routers must not open DB sessions for ad hoc SQL or write persistence logic inline.
- Services orchestrate repositories and adapters; they do not depend on FastAPI `Request` objects unless unavoidable for auth context already resolved.
- Repositories do not call LLMs or HTTP clients.
- Adapters isolate vendor SDKs so parsers, models, and storage can be swapped.

## Configuration

- Load settings from environment / settings module (for example pydantic-settings).
- Never hard-code secrets, JWT signing keys, intranet hostnames, or database passwords in source.
- Provide `.env.example` with placeholder keys only; real `.env` stays untracked.

## Database And Migrations

- PostgreSQL is the system of record; pgvector for embeddings.
- All schema changes go through Alembic migrations.
- Do not hand-edit production/dev schema outside migrations.
- Migrations and SDD data-model docs must stay aligned for the same slice.

## Auth And Identity

- Phase 1: Password provider + JWT (see ADR-0002).
- Reserve `external_subject` (or equivalent) on the user record for Phase 2 SSO mapping.
- Business logic authorizes on internal `user_id` and role, never on raw IdP subject strings scattered through services.
- Identity providers are pluggable adapters; password login must not paint the domain into a dead-end design.

## Authorization Roles

| Role | Intended capability |
|---|---|
| `Admin` | User/role admin, system configuration, full knowledge ops |
| `Editor` | Create/update knowledge content and ingest |
| `Viewer` | Read / query / RAG ask within allowed corpus |

Enforce roles in API dependencies; do not rely on frontend guards alone.

## File Uploads

- Store binary content on a local disk volume path configured by settings.
- Database stores metadata only (owner, path, hash, mime, size, timestamps, indexing status).
- Never commit uploaded corpora to Git.
- Validate size/mime before write; fail closed on path traversal.

## LLM And Prompts

- Call models through one OpenAI-compatible client adapter.
- Keep prompt templates outside business orchestration modules (for example `backend/app/prompts/` or `docs/07-prompts/` referenced by code loaders).
- Treat model output as untrusted until an explicit review/ingest path accepts it (see lessons L-006).
- Log model latency/error codes; do not log full prompts that contain secrets or raw confidential documents.

## Parsing / Models / Storage Adapters

- Document parsing, embedding/model access, and blob storage each go behind interfaces in `adapters/`.
- Domain services depend on protocols/interfaces, not concrete vendor types.
- New parser or model backends require an adapter implementation + tests; avoid rewriting services.

## Logging And Safety

- Redact tokens, passwords, `Authorization` headers, and sensitive document bodies from logs.
- Prefer structured logs with `request_id`, `user_id`, route, and outcome.
- Do not write secrets to stdout in Compose logs.

## Testing

- Critical paths must be testable without real intranet SSO or paid LLM calls (fake adapters / fixtures).
- Prefer service and repository tests for authz, ingest metadata, and retrieval plumbing.
- Verification baseline: `cd backend && pytest`.
- Schema changes: migration upgrade/downgrade smoke + updated SDD data-model notes.

## Related Docs

- `PROJECT_RULES.md`
- `docs/standards/frontend.md`
- `docs/00-context/decisions/ADR-0002-lock-technology-stack-and-auth-evolution.md`
- `docs/00-context/product-positioning.md`
- `docs/00-context/handoff-playbook.md`
