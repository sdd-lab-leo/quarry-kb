# L-007: Parsing and model access go through adapters

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | backend-architecture |
| Symptom | Vendor parser/SDK types leak into services and routers |
| Root cause | Fastest path couples domain logic to one implementation |
| Correct practice | Isolate parsers, LLM clients, and storage behind `adapters/`; services depend on interfaces |
| Promoted? | yes → `docs/standards/backend.md` |
| Related | backend standards |
| Source | inherited-decision |
