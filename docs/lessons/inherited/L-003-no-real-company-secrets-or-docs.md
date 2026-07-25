# L-003: Never commit real company documents, secrets, or logs

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | repository-hygiene |
| Symptom | Real intranet docs, screenshots, tokens, or runtime logs appear in Git history |
| Root cause | Using production-like fixtures without a redaction policy |
| Correct practice | Use mock samples only under `samples/`. Keep secrets in untracked env files. Redact logs |
| Promoted? | yes → `PROJECT_RULES.md` |
| Related | README samples policy, `.gitignore` |
| Source | inherited-decision |
