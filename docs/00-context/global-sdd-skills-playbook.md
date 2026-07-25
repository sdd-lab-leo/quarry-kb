# Global SDD Skills Playbook

This playbook describes how to make the repository's Spec Driven Development skills available across Codex, Claude Code, OpenCode, and GitHub Copilot.

## Goal

Keep one portable SDD workflow library available globally so projects can reuse the same requirements, story, spec, architecture, design, task, implementation, review, and ADR workflows.

## Canonical Skill Set

| Skill | Purpose |
|---|---|
| `agentic-sdlc-orchestrator` | Coordinate propose/apply/verify/archive across SDD, process, and discipline layers |
| `agentic-sdlc-doctor` | Check global Agentic SDLC installation and routing health |
| `req-to-user-story` | Convert raw requirements into structured user stories |
| `user-story-to-spec` | Convert user stories into a structured specification |
| `spec-to-architecture` | Convert a specification into architecture |
| `architecture-to-design` | Convert architecture into detailed design |
| `design-to-tasks` | Convert design into implementation tasks |
| `tasks-to-implementation` | Implement from a task breakdown |
| `tasks-to-code` | Convert tasks into code-oriented implementation guidance |
| `review-doc-quality` | Review SDD artifacts for quality and readiness |
| `review-code-against-design` | Review code changes against intended design |
| `review-docs-against-code` | Review documentation against actual code |
| `context-engineering-adr` | Capture durable context and architecture decisions |
| `sdd-profile-manager` | Define or choose the right SDD profile for a project |
| `sdd-slice-bootstrap` | Create or audit a complete SDD slice document set |
| `wwa-sdd-generate-all` | Orchestrate full English SDD generation via the project skill chain |
| `execution-manifest` | Pin agent handoff context, inputs, outputs, constraints, and verification |
| `freshness-gate` | Check whether docs, code, tests, or approvals are stale |
| `cross-ide-skill-router` | Expose the same skill library across Codex, Claude Code, OpenCode, and similar tools |

The `_shared/` directory contains grounding rules used by the SDD skill family.

## Global Installation Targets

| Tool | Global Location |
|---|---|
| Codex | `~/.codex/skills/` |
| Shared OpenAI-style agents | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| OpenCode command entry | `~/.config/opencode/commands/sdd.md` |
| GitHub Copilot repository bridge | `.github/copilot-instructions.md` |
| GitHub Copilot Agentic SDLC instructions | `.github/instructions/agentic-sdlc.instructions.md` |

## OpenCode Usage

OpenCode may not load `SKILL.md` folders natively in every setup. The portable fallback is the global `/sdd` command:

```text
/sdd turn docs/03-spec/spec.md into architecture
/sdd review docs/05-design/design.md
/sdd implement docs/06-tasks/tasks.md
```

The command routes the request to the relevant skill under `~/.config/opencode/skills/`.

## GitHub Copilot Usage

GitHub Copilot uses repository custom instructions rather than this repository's
`SKILL.md` folders as native skills in every surface. The bridge files are:

```text
.github/copilot-instructions.md
.github/instructions/agentic-sdlc.instructions.md
```

Keep both files short. They should route Copilot to `AGENTS.md`,
`.agents/skills/`, `docs/00-context/sdd-profile.md`, and the doctor script
instead of duplicating workflow bodies.

Note: Copilot bridge files and doctor/CI scripts are not part of Step 1
bootstrap for Quarry KB; add them when enforceability assets are introduced.

## Sync Procedure

From this repository, sync the SDD skills with:

```sh
repo=/path/to/quarry-kb
for dest in ~/.codex/skills ~/.agents/skills ~/.claude/skills ~/.config/opencode/skills; do
  mkdir -p "$dest"
  cp -R "$repo/.agents/skills/_shared" "$dest/"
  cp -R "$repo/.agents/skills"/{agentic-sdlc-doctor,agentic-sdlc-orchestrator,architecture-to-design,context-engineering-adr,cross-ide-skill-router,design-to-tasks,execution-manifest,freshness-gate,req-to-user-story,review-code-against-design,review-doc-quality,review-docs-against-code,sdd-profile-manager,sdd-slice-bootstrap,spec-to-architecture,tasks-to-code,tasks-to-implementation,user-story-to-spec,wwa-sdd-generate-all} "$dest/"
done
mkdir -p ~/.config/opencode/commands
cp "$repo/.opencode/commands/sdd.md" ~/.config/opencode/commands/sdd.md
```

## Maintenance Rules

- Treat `.agents/skills/` as the canonical source for the SDD skill family in this repository.
- Mirror changes to `.claude/skills/` when the project-local Claude skill set should stay aligned.
- Re-sync global directories after changing a skill.
- Update `docs/00-context/agentic-sdlc-registry.md` after adding or changing global assets.
- Run `scripts/agentic-sdlc-doctor.sh` after sync once that script exists; CI should also run the doctor when CI is introduced.
- Keep OpenCode's `/sdd` command aligned with the skill list.
- Keep GitHub Copilot instruction files aligned with the shared skill routes when those bridges exist.
- Do not fork skill behavior per tool unless a tool has a genuine compatibility requirement.

## Enforceability Assets

| Asset | Path | Purpose | Step 1 status |
|---|---|---|---|
| Registry | `docs/00-context/agentic-sdlc-registry.md` | Skill versions, sources, sync targets, and supporting assets | Present |
| Execution manifest schema | `docs/00-context/execution-manifest.schema.json` | Machine-checkable execution manifest contract | Present |
| SDD bootstrap | `docs/SDD-BOOTSTRAP.md` | Full-slice SDD generation entry | Present |
| SDD generation gate | `docs/00-context/checklists/sdd-generation-gate.md` | Skill-chain evidence checklist | Present |
| CI template | `.github/workflows/agentic-sdlc.yml` | Doctor, secret scan, backend test, and frontend build | Deferred |
| GitHub Copilot bridge | `.github/copilot-instructions.md` | Repository-wide Copilot route into Agentic SDLC | Deferred |
| GitHub Copilot Agentic SDLC instructions | `.github/instructions/agentic-sdlc.instructions.md` | Path-specific and agent Copilot route into shared skills | Deferred |

## Current Global Batch

The current global batch contains 19 skills: the original 11 SDD skills, 5 Agentic SDLC primitives, 2 control-plane utilities, and the full-slice orchestrator:

- `agentic-sdlc-orchestrator`
- `agentic-sdlc-doctor`

- `sdd-profile-manager`
- `sdd-slice-bootstrap`
- `wwa-sdd-generate-all`
- `execution-manifest`
- `freshness-gate`
- `cross-ide-skill-router`
