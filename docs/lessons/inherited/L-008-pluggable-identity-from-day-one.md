# L-008: Design phase-1 password login as pluggable identity

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | auth |
| Symptom | Password tables and checks hard-wire the domain so SSO requires a rewrite |
| Root cause | Treating phase-1 auth as the final identity model |
| Correct practice | Password provider is an adapter. Reserve `external_subject`. Business logic uses internal `user_id` + roles |
| Promoted? | yes → `docs/standards/backend.md`, ADR-0002 |
| Related | ADR-0002 |
| Source | inherited-decision |
