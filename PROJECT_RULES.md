# PROJECT_RULES.md

Hard rules for Quarry KB contributors and coding agents.

Detail belongs in linked docs. This file stays short and enforceable.

## Agent Startup

Before non-trivial work, read:

1. This file
2. Recent items under `docs/lessons/inherited/` and `docs/lessons/observed/`
3. Layer standards when coding: `docs/standards/frontend.md` / `docs/standards/backend.md`
4. `docs/00-context/handoff-playbook.md` when the work crosses sessions or agents

## SDD Is Mandatory For Non-Trivial Work

- Non-trivial changes must travel through a `docs/01`–`docs/06` slice (plus profile chain stages as required) and be review-confirmed before implementation.
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

- Use the document chain in `docs/00-context/sdd-profile.md` (orders 0–13, including bootstrap and traceability).
- For full slice SDD generation, start from `wwa-sdd-generate-all` via `docs/SDD-BOOTSTRAP.md` and pass `docs/00-context/checklists/sdd-generation-gate.md`.
- Do not invent a parallel `docs/sdd/` single-file template system that replaces the `00`–`06` chain.

## Language

- Project rules and SDD documents are English-only.
- Do not create `.zh-CN.md` companions for SDD unless explicitly requested.

## Hand-Off And Execution Manifest

Authority for procedure: `docs/00-context/handoff-playbook.md`. Decision record: ADR-0003.

- No execution manifest → no asynchronous or cross-session implementation.
- Chat-only hand-off is forbidden for mandatory hand-off cases.
- Apply only after `freshness-gate` passes.
- After verify completes, write `archive.md` and set manifest `status` to `archived`.
- Validate manifests against `docs/00-context/execution-manifest.schema.json`.
- On archive, record new pitfalls under `docs/lessons/observed/` when applicable.

## Product And Stack Boundaries

- Follow `docs/00-context/product-positioning.md` and ADR-0002.
- Stack is FastAPI + Vue 3 + PostgreSQL/pgvector + Docker Compose.
- Greenfield only: do not fork WeKnora.
- Uploaded knowledge files stay out of Git (local volume / later object storage).
- Do not introduce Java/Spring/Oracle defaults.
- Do not commit secrets, real company documents, internal screenshots, logs, or uploaded knowledge corpora.

## Standards And Lessons

- Coding conventions: `docs/standards/frontend.md`, `docs/standards/backend.md`.
- Lessons process: `docs/lessons/README.md`.
- Promote lessons into this file or standards when the same class repeats ≥2 times, or when security / data correctness is involved.

## Related ADRs

- ADR-0001 — context engineering + ADRs + SDD skills
- ADR-0002 — technology stack and auth evolution
- ADR-0003 — execution-manifest hand-off
