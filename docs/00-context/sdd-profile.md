# SDD Profile: quarry-kb-fastapi-vue

## Status

Accepted

## Applies To

This profile applies to the Quarry KB repository: a department-scale living knowledge workbench built with FastAPI + Vue 3, PostgreSQL/pgvector, Docker Compose, and strict Spec Driven Development for APIs, auth/roles, retrieval/RAG flows, uploads, and knowledge evolution boundaries.

## Document Chain

| Order | Stage | Required | Default Path | Primary Skill |
|---|---|---|---|---|
| 0 | Bootstrap / orchestration | Yes for full slice SDD | `docs/SDD-BOOTSTRAP.md` | `wwa-sdd-generate-all` |
| 1 | Context | Yes | `docs/00-context/` | `context-engineering-adr` |
| 2 | Requirements | Yes | `docs/01-requirements/{slice}-requirement.md` | `req-to-user-story` |
| 3 | User Stories | Yes | `docs/02-user-stories/{slice}-user-stories.md` | `user-story-to-spec` |
| 4 | Specification | Yes | `docs/03-spec/{slice}-spec.md` | `user-story-to-spec` |
| 5 | Architecture | Yes | `docs/04-architecture/{slice}-architecture.md` | `spec-to-architecture` |
| 6 | Data Flow | Required when stateful workflows or integrations exist | `docs/04-architecture/{slice}-data-flow.md` | `spec-to-architecture` |
| 7 | Data Model | Required when persistence exists | `docs/04-architecture/{slice}-data-model.md` | `architecture-to-design` |
| 8 | Design | Yes | `docs/05-design/{slice}-design.md` | `architecture-to-design` |
| 9 | API Guide | Required when API contracts change | `docs/05-design/contracts/{slice}-API_IMPLEMENTATION_GUIDE.md` | `architecture-to-design` |
| 10 | Tasks | Yes | `docs/06-tasks/{slice}-tasks.md` | `design-to-tasks` |
| 11 | Traceability | Yes for full slice SDD | `docs/00-context/{slice}-traceability.md` | `wwa-sdd-generate-all` |
| 12 | Implementation | Yes for code changes | repository source tree | `tasks-to-implementation` |
| 13 | Review | Yes before handoff | review report or PR notes | `review-doc-quality`, `review-code-against-design`, `review-docs-against-code` |

For full SDD generation, start from `wwa-sdd-generate-all` and follow the mandatory skill chain in `docs/SDD-BOOTSTRAP.md`. Use `sdd-slice-bootstrap` to audit skeletons.

For change-level lifecycle operations, use `agentic-sdlc-orchestrator` as the entry point for `propose`, `apply`, `verify`, and `archive`.

Existing shared docs such as `docs/03-spec/spec.md`, `docs/04-architecture/architecture.md`, `docs/05-design/design.md`, and `docs/06-tasks/tasks.md` remain valid for cross-cutting project scope. New slices should prefer slice-specific filenames unless the change intentionally updates a shared artifact.

## Language

- Project rules and SDD documents are **English-only**.
- Do not create `.zh-CN.md` companions for SDD unless the user explicitly asks.

## Gates

- Non-trivial or user-facing changes must update the relevant SDD artifacts before implementation.
- Coding must not start from an incomplete slice unless the user explicitly approves a reduced scope.
- Full SDD generation must report skill-chain evidence per `docs/00-context/checklists/sdd-generation-gate.md`.
- Architecture, platform-boundary, security, integration, data ownership, or cross-tool workflow decisions require an ADR under `docs/00-context/decisions/`.
- Before handing work to an external or asynchronous agent, create or reference an execution manifest.
- Before approval, implementation, or release from changing docs/code, run a freshness check.
- Before relying on global tooling behavior, `agentic-sdlc-doctor` should pass or report only accepted warnings.

## Traceability

- Requirements use stable IDs where practical.
- User stories trace to requirements.
- Specs trace to user stories and become the implementation behavior source.
- Architecture and design trace to specs and ADRs.
- Tasks trace to design sections and verification commands.
- Code, tests, changelog entries, and release notes trace back to the relevant tasks/spec/design.

## Tool Routing

- Codex reads `.agents/skills/` and global skills under `~/.codex/skills/`.
- Claude Code reads `.claude/skills/` and global skills under `~/.claude/skills/`.
- OpenCode uses `/sdd` and global skills under `~/.config/opencode/skills/`.
- Shared OpenAI-style global skills are mirrored under `~/.agents/skills/`.

## Related ADRs

- [ADR-0001](decisions/ADR-0001-adopt-context-engineering-adr-and-sdd-skills.md)
- [ADR-0002](decisions/ADR-0002-lock-technology-stack-and-auth-evolution.md)
- [ADR-0003](decisions/ADR-0003-adopt-execution-manifest-handoff.md)
- [ADR-0006](decisions/ADR-0006-pilot-auth-security-defaults.md) (Proposed; pilot password/JWT security defaults)
