# Change Packages

Per-change hand-off packages for Quarry KB. Procedure: `docs/00-context/handoff-playbook.md`.

## Naming

```text
YYYYMMDD-{slice-key}/
```

Examples:

- `20260725-repo-bootstrap/`
- `20260801-auth-password-jwt/`

Use the SDD slice slug as `{slice-key}` when one exists.

## Required Files

| File | Purpose |
|---|---|
| `proposal.md` | Intent, scope, risks, acceptance |
| `manifest.yaml` | Schema-valid execution manifest |
| `review.md` | Freshness + verification notes |
| `archive.md` | Final outcome after verify |

Copy from `_templates/` when starting a change. Do not leave active work only in chat.

## Rules

- `manifest.yaml` must conform to `docs/00-context/execution-manifest.schema.json`.
- No async / cross-session implementation without a manifest (`status` at least `accepted` before apply).
- Pass freshness-gate before apply; write archive after verify.
- This directory may contain only `_templates/` until the first real change is opened.
