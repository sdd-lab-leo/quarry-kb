# L-002: Uploaded files stay out of GitHub

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | ingest-storage |
| Symptom | Knowledge binaries or exports committed into the repository |
| Root cause | Convenience path during local demos; unclear ownership of blob storage |
| Correct practice | Store uploads on local disk volume (or later object storage). Git holds code and metadata docs only |
| Promoted? | yes → `PROJECT_RULES.md`, `docs/standards/backend.md` (File Uploads) |
| Related | ADR-0002, backend standards |
| Source | inherited-decision |
