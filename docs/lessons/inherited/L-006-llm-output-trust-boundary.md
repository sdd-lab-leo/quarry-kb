# L-006: LLM output has a trust boundary; do not treat it as approved knowledge by default

| Field | Value |
|---|---|
| Date | 2026-07-25 |
| Module | rag-knowledge |
| Symptom | Model answers or generated notes written straight into the knowledge corpus as authoritative |
| Root cause | Missing review/ingest gate between generation and durable knowledge |
| Correct practice | Keep a trust boundary: generated text is untrusted until an explicit review or wiki/knowledge approval path accepts it |
| Promoted? | yes → `docs/00-context/product-positioning.md` (knowledge evolution boundary); detailed wiki/ingest slice TBD |
| Related | product-positioning; future wiki / ingest slices |
| Source | inherited-decision |
