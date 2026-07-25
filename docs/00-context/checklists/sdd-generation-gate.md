# SDD Generation Gate Checklist

Use before accepting any newly generated or materially updated Quarry KB SDD set.

## Required Evidence

The agent completion report must include:

- `SDD skill chain used: yes`
- Entry skill file read: `.agents/skills/wwa-sdd-generate-all/SKILL.md` (or `.claude/skills/…`)
- Downstream skill files read:
  - `req-to-user-story`
  - `user-story-to-spec`
  - `spec-to-architecture`
  - `architecture-to-design`
  - `design-to-tasks`
  - `review-doc-quality`
- ADR created/updated or explicit `not applicable` (no `architecture-review` skill in this repo)
- `review-doc-quality` result or explicit blocked reason

## Gate Checklist

| Check | Pass Criteria |
|---|---|
| Goal contract | Goal, slice, scope, exclusions, acceptance, verification, constraints are explicit |
| Required context | Project rules, SDD profile, bootstrap, and relevant docs were read or gaps reported |
| Skill chain | Full generation used the project-local chain; not entirely ad hoc |
| Language | SDD artifacts are English-only unless the user explicitly requested another language |
| Spec quality | Happy path, empty/error states, acceptance matrix present |
| Product boundaries | Auth/roles, upload/knowledge, and retrieval ownership explicit when relevant |
| Security / audit | Roles, JWT/SSO evolution, and data-safety expectations explicit when relevant |
| API guide | Present when API in scope, or deferral documented |
| Tasks | Ordered, verifiable, mapped to spec/requirements |
| Traceability | Sources → requirements → stories → spec/design → tasks → verification |

## Fail-Fast

Block handoff if:

- `SDD skill chain used` is missing or `no`
- Required project-local skill files were unavailable and SDD was generated anyway
- Spec and tasks disagree on scope
