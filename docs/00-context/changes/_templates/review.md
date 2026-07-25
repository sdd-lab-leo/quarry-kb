# Change Review: YYYYMMDD-{slice-key}

| Field | Value |
|---|---|
| Manifest | `manifest.yaml` |
| Manifest status | proposed \| accepted \| in_progress \| verified \| archived |
| Reviewer | human-or-agent |
| Date | YYYY-MM-DD |

## Freshness Gate

| Check | Result | Notes |
|---|---|---|
| SDD inputs current | pass \| fail | |
| ADRs current | pass \| fail | |
| Target code/docs current | pass \| fail \| n/a | |

Freshness skill: `freshness-gate`. **Apply must not start on fail.**

## Verification

| Command / gate | Result | Notes |
|---|---|---|
| | pass \| fail \| skipped | |

## Findings

- …

## Decision

- [ ] Ready to apply
- [ ] Apply blocked (reason below)
- [ ] Verified — proceed to archive

Blockers:
