---
name: wwa-sdd-generate-all
description: >
  Quarry KB project-local SDD orchestration skill. Use when the user asks to generate all
  SDD documents for a Quarry KB slice, bootstrap a feature slice, or prepare implementation-ready
  documentation. Produces the full English Quarry KB SDD set using PROJECT_RULES,
  docs/standards/frontend.md, docs/standards/backend.md, SDD-BOOTSTRAP, and project-local SDD skills.
  The directory name wwa-sdd-generate-all is retained for skill-set isomorphism with deployment-agent.
---

# wwa-sdd-generate-all

Generate the complete Quarry KB SDD document set for one product slice.

The skill **directory name** `wwa-sdd-generate-all` is kept for isomorphism with the shared Agentic SDLC skill set from deployment-agent. Behavior and paths in this file are Quarry KB–local.

This is a project-local orchestration skill. It coordinates smaller skills; it does not replace them.

## Mandatory Skill Chain

Use project-local skills in this order (do not hand-write the entire set in one ad hoc pass):

| Order | Skill | Output |
|---|---|---|
| 1 | `wwa-sdd-generate-all` | Slice contract, orchestration, final consistency gate |
| 2 | `req-to-user-story` | User stories + acceptance criteria |
| 3 | `user-story-to-spec` | Implementation-facing spec |
| 4 | `spec-to-architecture` | Architecture, data flow, data model |
| 5 | `architecture-to-design` | Design + contracts |
| 6 | `design-to-tasks` | Implementation tasks |
| 7 | `review-doc-quality` | Quality and traceability review |

When the slice materially changes architecture, API/persistence, security, auth/roles, retrieval boundaries, or data ownership: capture or update an ADR under `docs/00-context/decisions/` and ensure `review-doc-quality` covers the decision links. This repository has no `architecture-review` skill.

Use `review-code-against-design` only after implementation exists.

## When To Use

- "generate the full SDD for this slice"
- "generate SDD in one pass"
- "prepare SDD for implementation"
- "bootstrap a new Quarry KB feature slice"

## Required Context Before Generating

1. `PROJECT_RULES.md`
2. `AGENTS.md`
3. `docs/standards/frontend.md` and/or `docs/standards/backend.md` when the slice touches that layer
4. `docs/SDD-BOOTSTRAP.md`
5. `docs/00-context/sdd-profile.md`
6. Relevant ADRs under `docs/00-context/decisions/`
7. Existing slice docs under `docs/01-*` … `docs/06-*`
8. UI baseline when relevant (only if such artifacts exist in the repo)

## Language

English-only for project rules and SDD documents (`PROJECT_RULES.md`, `docs/00-context/sdd-profile.md`). Do not create `.zh-CN.md` companions unless the user explicitly asks.

## Document Set (Quarry KB Paths)

Aligned with `docs/00-context/sdd-profile.md` and `docs/SDD-BOOTSTRAP.md`:

1. `docs/01-requirements/{slice}-requirement.md`
2. `docs/02-user-stories/{slice}-user-stories.md`
3. `docs/03-spec/{slice}-spec.md`
4. `docs/04-architecture/{slice}-architecture.md`
5. `docs/04-architecture/{slice}-data-flow.md` when stateful workflows/integrations exist
6. `docs/04-architecture/{slice}-data-model.md` when persistence exists
7. `docs/05-design/{slice}-design.md`
8. `docs/05-design/contracts/{slice}-API_IMPLEMENTATION_GUIDE.md` when API contracts change
9. `docs/06-tasks/{slice}-tasks.md`
10. `docs/00-context/{slice}-traceability.md`

Keep historical filenames (`-requirement`, `-user-stories`) for chain isomorphism.

## Workflow

### Step 1 — Slice contract

Define slug, goal, in/out of scope, sources, acceptance, verification, constraints (security, auth/roles, upload/knowledge boundaries, data-safety).

### Step 2 — Requirements

Stable IDs such as `REQ-{SLICE}-001`. Then run `req-to-user-story`.

### Step 3 — User stories

IDs such as `US-{SLICE}-001` with Given/When/Then acceptance. Then `user-story-to-spec`.

### Step 4 — Spec

Happy path, empty/error states, acceptance matrix. `docs/03-spec/` is behavior source of truth.

### Step 5 — Architecture / data flow / data model

Call out auth/roles, upload vs metadata ownership, retrieval/RAG boundaries, persistence, and adapter seams. Use `spec-to-architecture`. Ground claims against the real codebase (`_shared/grounding-rules.md`); do not invent APIs, tables, or behaviors.

### Step 6 — Design

UX, components, API/integration, test hooks. Ground UI in an existing UI baseline when present. Use `architecture-to-design`.

### Step 7 — API guide

Only when backend/API is in scope. Otherwise document deferral in traceability.

### Step 8 — Tasks

Actionable, ordered, mapped to requirements/spec, with verification commands. Use `design-to-tasks`.

### Step 9 — Traceability

Link sources → requirements → stories → spec/design → tasks → verification.

### Step 10 — Quality gate

Apply `review-doc-quality` and `docs/00-context/checklists/sdd-generation-gate.md`.

## Quarry KB Constraints To Preserve

- Greenfield only; do not fork WeKnora
- Stack: FastAPI + Vue 3 + PostgreSQL/pgvector + Docker Compose (ADR-0002)
- Uploaded knowledge files stay out of Git; DB stores metadata/paths only
- Auth: phase-1 password provider is pluggable; reserve `external_subject`; business logic uses internal `user_id` + roles `Admin` | `Editor` | `Viewer`
- Parsers, LLM clients, and storage go through adapters (`docs/standards/backend.md`)
- LLM output has a trust boundary; do not treat it as approved knowledge by default
- Follow `docs/standards/frontend.md` and `docs/standards/backend.md`
- No Java/Spring/Oracle defaults

## Final Response Must Include

- Slice slug
- Files created/updated
- API guide included or deferred
- Assumptions / open questions
- **SDD skill chain used: yes** (list entry + downstream skill files read)
- ADR created/updated or explicit `not applicable`
- `review-doc-quality` result
- Recommended implementation handoff command

If the skill chain cannot be used, **stop** and report instead of generating ad hoc SDD.
