# ADR-0002: Lock Technology Stack And Auth Evolution

## Status

Accepted

## Date

2026-07-25

## Context

Quarry KB targets a department intranet (~60 users) with fast iteration around document ingest, retrieval/RAG Q&A, and later agent/wiki capabilities. Stack choices must stay lean for Docker Compose delivery and must leave a clear path from password authentication to company SSO without a second identity redesign.

Quarry KB is greenfield and must not inherit Java/Spring/Oracle assumptions from unrelated reference repositories, nor fork WeKnora.

## Decision

Lock the following technology and auth evolution path:

### Application stack

| Layer | Choice |
|---|---|
| Frontend | Vue 3 + Vite + TypeScript + Pinia |
| Backend | FastAPI |
| Database | PostgreSQL + pgvector |
| File storage | Local disk uploads via Docker volume |
| Runtime | Docker Compose services: `web`, `api`, `postgres` |

### Auth evolution

1. **Phase 1:** Account/password authentication with JWT session/token issuance.
2. **Phase 2:** Company SSO. Identity linkage must reserve an `external_subject` (or equivalent) field from the start so local accounts can map to SSO principals without rewriting ownership and audit models.
3. **Roles:** `Admin`, `Editor`, `Viewer`.

### Repository boundaries

- Application code and SDD documentation belong in Git.
- Uploaded knowledge files, real company documents, internal screenshots, secrets, and runtime logs must not be committed.
- Do not introduce Java, Spring, Maven, or Oracle as implementation dependencies or as documented defaults for this repository.

## Alternatives Considered

| Alternative | Why Not |
|---|---|
| Fork WeKnora as the starting codebase | Violates greenfield boundary and couples Quarry KB to another product’s architecture. |
| Start with SSO-only auth | Slows intranet MVP; password+JWT is enough for phase 1 if SSO fields are reserved. |
| Object storage first for uploads | Unnecessary for ~60-user intranet MVP; local Docker volume is simpler to operate initially. |
| Reuse Java/Spring/Oracle from Deployment Agent reference | Wrong stack for this product; would create permanent mismatch with FastAPI/Vue intent. |

## Consequences

### Positive

- Agents and contributors share one stack contract for architecture, design, and tasks.
- SSO migration remains possible without rewriting identity ownership.
- Repository hygiene stays aligned with knowledge-file sensitivity.

### Negative

- Later migration to remote object storage or additional IdPs will need explicit ADRs/slices.
- Phase 1 password auth requires careful secret handling and migration planning before SSO cutover.

### Neutral / Operational

- Coding conventions and language/framework standards will be added under `docs/standards/*` in a later step.
- No business application code is implied by this ADR alone; implementation still requires an approved SDD slice.

## Review Triggers

Revisit this decision when:

- Company SSO rollout forces a different identity model than `external_subject` mapping.
- Upload durability or multi-node deployment outgrows local Docker volumes.
- Retrieval/RAG requirements demand a different vector/data store than PostgreSQL + pgvector.

## Related Documents

- [Product positioning](../product-positioning.md)
- [SDD profile](../sdd-profile.md)
- [AGENTS.md](../../../AGENTS.md)
- [PROJECT_RULES.md](../../../PROJECT_RULES.md)
