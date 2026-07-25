# L-005: Ground SDD claims; never invent existing APIs, tables, or behaviors

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | sdd-quality |
| Symptom | Specs describe endpoints, tables, or UX that do not exist and were never decided |
| Root cause | Generating docs from memory instead of repository evidence |
| Correct practice | Before writing SDD about existing code, ground every non-trivial claim against the codebase (`_shared/grounding-rules.md`). Mark unknowns explicitly |
| Promoted? | yes → `.agents/skills/_shared/grounding-rules.md`, review skills / `docs/reviews/` practice |
| Related | `review-doc-quality`, `review-docs-against-code` |
| Source | inherited-decision |
