# L-009: Cross-session / cross-agent work needs an execution manifest

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | handoff |
| Symptom | Async or multi-session agents resume from chat memory and drift from approved scope |
| Root cause | Chat is not a durable, reviewable hand-off artifact |
| Correct practice | Create or reference an execution manifest before async / cross-session implementation; follow the hand-off playbook |
| Promoted? | yes → `PROJECT_RULES.md`, `docs/00-context/handoff-playbook.md`, ADR-0003 |
| Related | ADR-0003, execution-manifest schema |
| Source | inherited-decision |
