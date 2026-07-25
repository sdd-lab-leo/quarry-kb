# Hand-Off Playbook

Durable hand-off rules for multi-session and multi-agent work on Quarry KB.

Policy owners:

- Hard gates → `PROJECT_RULES.md` and `AGENTS.md` (short rules only)
- Procedure detail → this playbook
- Machine contract → `docs/00-context/execution-manifest.schema.json`
- Change folder templates → `docs/00-context/changes/`

Related skills: `execution-manifest`, `freshness-gate`, `agentic-sdlc-orchestrator`.

## When Hand-Off Is Mandatory

Create or update a change package + execution manifest when any of the following is true:

- Switching chat sessions with unfinished implementation or SDD work
- Switching humans or coding agents mid-slice
- Starting **async / remote** agent work
- SDD for a slice is approved and implementation is about to start
- Pre-release archive of a completed change

## Forbidden

- Handing off with **chat history only**
- Starting async or cross-session implementation without an execution manifest
- Applying code from stale docs without a freshness check
- Closing a change after verify without an archive note

## Lifecycle

```text
propose → accept → manifest → freshness → apply → verify → archive
```

| Stage | Meaning | Primary artifact |
|---|---|---|
| propose | Describe intent, scope, and risks | `proposal.md` |
| accept | Human/owner accepts scope | proposal status + slice approval |
| manifest | Pin inputs/outputs/constraints | `manifest.yaml` (schema-valid) |
| freshness | Confirm docs/code/tests are not stale | freshness-gate result in `review.md` |
| apply | Implement within manifest constraints | code / docs per allowed paths |
| verify | Run verification commands and gates | verification section in `review.md` |
| archive | Freeze outcome; capture new lessons | `archive.md` + optional `docs/lessons/observed/` |

Use `agentic-sdlc-orchestrator` for propose/apply/verify/archive coordination.

## Change Folder Layout

Naming: `docs/00-context/changes/YYYYMMDD-{slice-key}/`

```text
YYYYMMDD-{slice-key}/
  proposal.md
  manifest.yaml
  review.md
  archive.md
```

Templates live in `docs/00-context/changes/_templates/`. Do not create a real change directory in Step 2 bootstrap; create one when a slice is ready to execute.

## Manifest Requirements

`manifest.yaml` **must** validate against `docs/00-context/execution-manifest.schema.json`.

In addition to schema-required fields, every Quarry KB manifest must make these explicit:

| Concern | Where in manifest |
|---|---|
| Goal | `task.objective` |
| Approved SDD inputs | `inputs.documents` (paths to approved slice docs) |
| Out of scope | top-level `out_of_scope` (array of strings; allowed by `additionalProperties`) |
| Constraints | `constraints` plus references to `docs/standards/*` in notes or `stop_conditions` |
| Outputs | `outputs.expected_artifacts` |
| Verification | `verification.commands` + `verification.quality_gates` |
| Status | top-level `status` |

### Status values

| Status | Meaning |
|---|---|
| `proposed` | Draft hand-off, not accepted |
| `accepted` | Scope accepted; ready for freshness/apply |
| `in_progress` | Apply underway |
| `verified` | Verification passed |
| `archived` | Change closed; archive written |

### Minimal content checklist

- [ ] `task.sdd_profile` is `quarry-kb-fastapi-vue`
- [ ] Approved SDD paths listed under `inputs.documents`
- [ ] `out_of_scope` non-empty or explicitly `["none"]` with rationale in proposal
- [ ] `constraints.allowed_paths` / `forbidden_paths` set (include `.env`, secrets, upload corpora as forbidden)
- [ ] Constraints cite `docs/standards/frontend.md` and/or `docs/standards/backend.md` when code changes are in scope
- [ ] `verification.commands` match AGENTS verification baselines
- [ ] `status` set and updated as the lifecycle advances

## Freshness Gate

Before **apply** (and before approval/release when docs or code moved):

1. Run the `freshness-gate` skill against the listed SDD inputs, ADRs, and target code paths.
2. Record the result in `review.md`.
3. If stale, update docs or re-accept scope before coding.

## Archive Rules

After **verify** completes:

1. Write `archive.md` (what shipped, verification evidence, residual risks).
2. Set manifest `status` to `archived`.
3. If a new pitfall was discovered, add a lesson under `docs/lessons/observed/` using `_template.md` (`Source: observed-incident`).
4. Promote to `PROJECT_RULES.md` / `docs/standards/*` when promotion rules in `docs/lessons/README.md` trigger.

## Related Docs

- ADR-0003
- `docs/00-context/changes/README.md`
- `docs/lessons/README.md`
- `.agents/skills/execution-manifest/`
- `.agents/skills/freshness-gate/`
- `.agents/skills/agentic-sdlc-orchestrator/`
