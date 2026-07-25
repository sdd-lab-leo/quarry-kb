# ADR-0003: Adopt Execution-Manifest Based Hand-Off For Multi-Agent And Multi-Session Work

## Status

Accepted

## Date

2026-07-25

## Context

Quarry KB will be built by multiple coding agents and humans across sessions. Chat transcripts are ephemeral, incomplete, and not schema-checked. Without a pinned hand-off artifact, async work drifts from approved SDD scope, skips freshness checks, and loses verification evidence.

The repository already has portable skills (`execution-manifest`, `freshness-gate`, `agentic-sdlc-orchestrator`) and `docs/00-context/execution-manifest.schema.json`.

## Decision

Adopt execution-manifest-based hand-off as a first-class operating practice:

- Mandatory for session switches, human/agent switches, async/remote agents, post-SDD-approval implementation start, and pre-release archive.
- Chat-only hand-off is forbidden for those cases.
- Lifecycle is `propose → accept → manifest → freshness → apply → verify → archive`.
- Change packages live under `docs/00-context/changes/YYYYMMDD-{slice-key}/` using the templates in `_templates/`.
- `manifest.yaml` must validate against `execution-manifest.schema.json` and carry Quarry fields: goal (`task.objective`), approved SDD inputs, `out_of_scope`, standards-aware constraints, outputs, verification, and `status` (`proposed` | `accepted` | `in_progress` | `verified` | `archived`).
- Apply requires a passed freshness-gate; verify completion requires an archive; new pitfalls go to `docs/lessons/observed/`.

Procedure detail lives in `docs/00-context/handoff-playbook.md`. Short hard rules live in `PROJECT_RULES.md` and `AGENTS.md`.

## Alternatives Considered

| Alternative | Why Not |
|---|---|
| Chat transcript as hand-off | Not durable, not reviewable, not schema-valid |
| PR description only | Missing pinned inputs/constraints before work starts; weak for async agents |
| Free-form NOTES.md without schema | Drifts per agent; cannot machine-check required fields |

## Consequences

### Positive

- Async agents receive explicit scope, paths, and verification.
- Freshness and archive become visible gates instead of folklore.
- Lessons from real changes have a clear write-back path.

### Negative

- Small multi-session chores gain a short package overhead.
- Contributors must keep manifest `status` current.

### Neutral / Operational

- Templates are seeded without creating a live change directory in this step.
- SDD remains the source of feature behavior; manifests pin execution context for a change.

## Review Triggers

Revisit when:

- CI gains automated manifest schema validation.
- A different orchestration tool replaces `agentic-sdlc-orchestrator`.
- Status vocabulary needs extension for release management.

## Related Documents

- [Hand-off playbook](../handoff-playbook.md)
- [Changes README](../changes/README.md)
- [Execution manifest schema](../execution-manifest.schema.json)
- [Lessons README](../../lessons/README.md)
- [PROJECT_RULES.md](../../../PROJECT_RULES.md)
- [AGENTS.md](../../../AGENTS.md)
- [L-009](../../lessons/inherited/L-009-execution-manifest-for-cross-session-work.md)
