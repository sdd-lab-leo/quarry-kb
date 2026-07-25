# ADR-0001: Adopt Context Engineering, ADRs, And SDD Skills

## Status

Accepted

## Date

2026-07-25

## Context

Quarry KB is a greenfield repository that will be operated by multiple coding agents and tools (Codex, Claude Code, OpenCode, and later CI/Copilot bridges). Without a shared durable memory and workflow contract, agents will invent competing documentation layouts, skip gates, or reconstruct decisions from chat.

The repository needs a lightweight, repo-local way to preserve:

- long-lived product/engineering context;
- architecture and cross-cutting decisions;
- a portable Spec Driven Development (SDD) skill chain aligned with proven Agentic SDLC practice.

## Decision

Adopt context engineering + ADRs + SDD skills as the operating system for this repository:

- Durable project background, boundaries, terminology, and agent working rules live under `docs/00-context/`.
- Architecture Decision Records live under `docs/00-context/decisions/`.
- The active SDD profile is `docs/00-context/sdd-profile.md` (`quarry-kb-fastapi-vue`).
- Canonical reusable workflows live under `.agents/skills/` (including `_shared/`), mirrored to `.claude/skills/` and routed via `.opencode/commands/sdd.md`.
- Non-trivial architectural or cross-cutting decisions must be captured as ADRs.
- Feature scope and implementation traceability remain in the `docs/01`–`docs/06` SDD chain; ADRs record the “why,” not a competing planning system.
- Do not invent a parallel single-file template system under `docs/sdd/` that replaces the `00`–`06` document chain.

## Alternatives Considered

| Alternative | Why Not |
|---|---|
| Keep decisions only in architecture docs or chat/PRs | Rationale becomes hard to find and is not durable across agents. |
| Skip skills and rely on free-form prompting | Workflow quality and gates become tool-specific and non-repeatable. |
| Replace SDD with ADRs only | ADRs capture decisions; they do not replace requirements, specs, designs, or tasks. |
| Invent a custom `docs/sdd/` mega-template | Breaks isomorphism with the shared Agentic SDLC skill family and harms reuse. |

## Consequences

### Positive

- Future maintainers and agents share one context and decision surface.
- SDD slices stay traceable from requirements through tasks and reviews.
- Skills can be synced globally without forking workflow behavior per tool.

### Negative

- Contributors must decide when a change deserves an ADR or a full SDD slice.
- Mirrored skill directories must be kept aligned after skill edits.

### Neutral / Operational

- Root agent instruction files (`AGENTS.md`, `PROJECT_RULES.md`) point to this contract instead of duplicating skill bodies.
- Execution manifests are required before asynchronous or cross-session implementation (detailed hand-off playbook comes in a later step).

## Review Triggers

Revisit this decision when:

- The repository adopts a dedicated ADR tooling platform.
- A different primary specification framework is intentionally chosen.
- Tooling standardizes a native skill format that removes the need for mirrored folders.

## Related Documents

- [SDD profile](../sdd-profile.md)
- [Global SDD skills playbook](../global-sdd-skills-playbook.md)
- [Agentic SDLC registry](../agentic-sdlc-registry.md)
- [Product positioning](../product-positioning.md)
- [AGENTS.md](../../../AGENTS.md)
- [PROJECT_RULES.md](../../../PROJECT_RULES.md)
