# Quarry KB Product Positioning

**Date:** 2026-07-25  
**Status:** Accepted  
**Owner:** Quarry KB direction  
**Gates:** Product scope, naming, architecture boundaries, and documentation that distinguish Quarry KB from related knowledge systems

---

## Decision

Quarry KB is a department-scale living knowledge workbench for roughly 60 people on an intranet, optimized for fast iteration.

Primary value chain:

```text
Documents → Retrievable knowledge / RAG Q&A → (later) Agent → (later) Wiki
```

Quarry KB is a greenfield product. It does not fork WeKnora. Application code belongs in Git; uploaded knowledge files do not.

---

## Naming

| Term | Definition |
|------|------------|
| **Quarry KB** | Department living knowledge workbench. Owns ingest, retrieval, RAG Q&A, roles, and knowledge evolution loops. |
| **Atlas Knowledge Hub** | Adjacent product focused on document conversion and review workflows. Not the same product as Quarry KB. |
| **WeKnora** | External/reference knowledge system. Quarry KB may learn from ideas but must not fork or inherit its codebase. |

---

## Boundary Rules

1. **Quarry vs Atlas:** Atlas Knowledge Hub emphasizes document conversion and review. Quarry KB emphasizes retrieval, Q&A, and knowledge evolution.
2. **Quarry vs WeKnora:** Greenfield implementation. Do not fork WeKnora into this repository.
3. **Code vs knowledge files:** Source code, SDD docs, and mock samples may be committed. Uploaded knowledge corpora, real company documents, screenshots of internal content, secrets, and runtime logs must not be committed.
4. **Auth evolution:** Phase 1 uses account/password + JWT. Phase 2 reserves company SSO via `external_subject` (or equivalent) without redesigning identity ownership.
5. **Roles:** `Admin`, `Editor`, and `Viewer` are the initial authorization model.
6. **Runtime shape:** Docker Compose with `web` + `api` + `postgres` (PostgreSQL + pgvector). Local disk uploads via Docker volume.

---

## Intended Stack (documented, not implemented in Step 1)

| Layer | Choice |
|---|---|
| Frontend | Vue 3 + Vite + TypeScript + Pinia |
| Backend | FastAPI |
| Data | PostgreSQL + pgvector |
| Files | Local disk upload storage (Docker volume) |
| Auth (phase 1) | Account/password + JWT |
| Auth (phase 2) | Company SSO (reserve `external_subject`) |
| Deploy | Docker Compose (`web`, `api`, `postgres`) |

---

## Implications

When naming, scoping, or designing features:

- Prefer retrieval/Q&A and knowledge lifecycle language over conversion/review language reserved for Atlas.
- Keep upload storage and knowledge corpora out of Git.
- Preserve SSO-ready identity fields even while shipping password auth first.
- Do not introduce Java/Spring/Oracle stack assumptions into this repository.
