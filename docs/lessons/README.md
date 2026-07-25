# Lessons Learnt

Capture durable engineering lessons for Quarry KB without turning chat noise into policy.

## Sources

| Source | Meaning | Directory |
|---|---|---|
| `inherited-decision` | Adopted boundary or operating decision brought in at bootstrap (not necessarily from a local incident) | `inherited/` |
| `observed-incident` | Real bug, outage, or process failure observed while building Quarry KB | `observed/` |

## Lifecycle

```text
Record → Retrospective → Promote (optional)
```

1. **Record** a lesson using `_template.md`.
2. **Retrospective**: fill root cause and correct practice; link ADR / SDD / PR when known.
3. **Promote** into `PROJECT_RULES.md` or `docs/standards/*` when the promotion rule triggers.

## Required Fields

| Field | Description |
|---|---|
| Date | ISO date (`YYYY-MM-DD`) |
| Module | Area (`auth`, `ingest`, `sdd`, `handoff`, …) |
| Symptom | What was seen |
| Root cause | Why it happened |
| Correct practice | What to do instead |
| Promoted? | `no` / `yes` + destination |
| Related | ADR / SDD / PR links |
| Source | `inherited-decision` or `observed-incident` |

## Promotion Rules

Promote a lesson into hard rules or standards when either:

- the same class of problem appears **≥ 2** times; or
- the issue involves **security** or **data correctness**.

Promotion targets:

- cross-cutting hard rules → `PROJECT_RULES.md`
- layer conventions → `docs/standards/frontend.md` or `docs/standards/backend.md`
- architecture “why” → new or updated ADR under `docs/00-context/decisions/`

## Agent Startup Reading

Before non-trivial work, agents must read:

1. `PROJECT_RULES.md`
2. Recent lessons in `docs/lessons/inherited/` and `docs/lessons/observed/` (newest first)

Do not treat lessons as a second policy encyclopedia: after promotion, the destination doc is authoritative; the lesson remains the narrative record.
