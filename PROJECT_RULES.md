# PROJECT_RULES.md

Hard rules for Quarry KB contributors and coding agents.

This Step 1 skeleton covers SDD discipline only. Coding standards, lessons, and hand-off playbook details arrive in Step 2.

## SDD Is Mandatory For Non-Trivial Work

- Non-trivial changes must travel through a `docs/01`–`docs/06` slice and be review-confirmed before implementation.
- Non-trivial or user-facing changes must update SDD first.
- Do not implement feature code without an approved slice.

### Non-trivial examples

- Adding or changing APIs
- Adding or changing data models / migrations
- Auth, JWT, SSO, roles, or permission behavior
- Introducing new dependencies
- Changing architecture boundaries (services, storage, retrieval pipeline, compose topology)

### Trivial examples

- Typos
- Comments
- Pure style tweaks with no behavior change
- Documentation wording that does not change scope or behavior

## Backfill Policy

- If code already exists without matching SDD docs, backfill the chain immediately.
- Mark backfilled documents explicitly as `Backfilled`.
- Never present backfilled docs as if they preceded the code.

## Traceability

- Code, tests, and changelog entries must be traceable to tasks, spec, and design.
- Reviews should reject non-trivial changes that cannot point to their SDD slice.

## Document Chain Integrity

- Use the `docs/00-context` → `docs/06-tasks` (+ reviews) chain defined by `docs/00-context/sdd-profile.md`.
- Do not invent a parallel `docs/sdd/` single-file template system that replaces the `00`–`06` chain.

## Execution Manifest Gate

- Before asynchronous agent work or cross-session implementation, create or reference an execution manifest.
- Validate manifests against `docs/00-context/execution-manifest.schema.json`.
- Detailed hand-off playbook content is deferred to Step 2.

## Product And Stack Boundaries

- Follow `docs/00-context/product-positioning.md` and ADR-0002.
- Stack is FastAPI + Vue 3 + PostgreSQL/pgvector + Docker Compose.
- Do not introduce Java/Spring/Oracle defaults.
- Do not commit secrets, real company documents, internal screenshots, logs, or uploaded knowledge corpora.

## Deferred To Step 2

- `docs/standards/*`
- `docs/lessons/*`
- Hand-off playbook body
