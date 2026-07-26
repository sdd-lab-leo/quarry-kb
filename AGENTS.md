# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Required Reading

Before non-trivial changes, read:

- `PROJECT_RULES.md`
- Recent lessons in `docs/lessons/inherited/` and `docs/lessons/observed/`
- `docs/00-context/sdd-profile.md`
- `docs/SDD-BOOTSTRAP.md` when generating or updating slice SDD
- `docs/standards/frontend.md` and/or `docs/standards/backend.md` when touching that layer
- `docs/00-context/handoff-playbook.md` before async / cross-session work
- Relevant slice docs and ADRs

## Project Contract

## Build And Test

Placeholder until application scaffolding exists. Intended commands:

- Backend install/dev: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
- Backend test: `cd backend && pytest`
- Frontend install/dev: `cd frontend && npm install && npm run dev`
- Frontend build/typecheck: `cd frontend && npm run build`
- Compose (intended): `docker compose -f deploy/docker-compose.yml up --build`

Do not invent alternate Java/Maven/Oracle workflows for this repository.

## SDD Workflow Gate

This repository should be operated in strict Spec Driven Development mode for non-trivial or user-facing changes.

- The active project profile is `docs/00-context/sdd-profile.md` (`quarry-kb-fastapi-vue`).
- Before implementation, create or update the relevant SDD artifacts under `docs/01-requirements`, `docs/02-user-stories`, `docs/03-spec`, `docs/04-architecture`, `docs/05-design`, and `docs/06-tasks`.
- For full SDD generation, use `wwa-sdd-generate-all` (see `docs/SDD-BOOTSTRAP.md`) and report skill-chain evidence per `docs/00-context/checklists/sdd-generation-gate.md`.
- SDD and project-rule documents are English-only.
- Non-trivial or user-facing changes must update SDD first. Do not implement feature code without an approved slice.
- If a change has already been implemented without SDD artifacts, backfill the full SDD chain immediately and mark the documents as `Backfilled` rather than pretending they preceded the code.
- Treat SDD documents as the primary source of change intent and scope. Code, tests, and changelog entries must trace back to the SDD artifacts.
- For small bug fixes, copy edits, or metadata-only cleanup, update the nearest existing SDD artifact only when behavior or scope changes.
- Do not add a new user-facing feature as code-only work.

## Hand-Off Gate

Procedure: `docs/00-context/handoff-playbook.md`. Schema: `docs/00-context/execution-manifest.schema.json`. ADR: ADR-0003.

- Do **not** start asynchronous or cross-session implementation without an execution manifest.
- Do **not** hand off using chat history only for mandatory hand-off cases.
- Run `freshness-gate` and record a pass before **apply**.
- After **verify**, write `archive.md` and set manifest `status` to `archived`.
- New pitfalls discovered at archive time go to `docs/lessons/observed/`.
- Change packages use `docs/00-context/changes/YYYYMMDD-{slice-key}/` templates.

## Context Engineering And ADRs

- Use `docs/00-context/` as the durable project context layer for background, terminology, boundaries, onboarding knowledge, and cross-agent working rules.
- Use `docs/00-context/decisions/` for Architecture Decision Records (ADRs).
- Before changing architecture, platform boundaries, security posture, data ownership, integrations, or shared agent conventions, read the relevant context documents and ADRs.
- Capture significant new or reversed decisions as ADRs instead of leaving rationale only in chat, PRs, or implementation notes.
- Keep SDD artifacts as the source of feature scope; use ADRs for the "why" behind architecture and cross-cutting choices.
- For reusable ADR/context workflow guidance, use `.agents/skills/context-engineering-adr/`.

## Global Agentic SDLC Skills

- Treat `.agents/skills/` as the canonical project-local source for reusable SDD and Agentic SDLC workflows.
- Use `sdd-profile-manager` before applying SDD to a new project shape.
- Use `wwa-sdd-generate-all` for full slice SDD generation; use `sdd-slice-bootstrap` when auditing an existing skeleton.
- Use `execution-manifest` before handing work to a coding agent, remote agent, or automation.
- Use `freshness-gate` before approving, implementing, or releasing from potentially stale docs/code/tests.
- Use `cross-ide-skill-router` when keeping Codex, Claude Code, OpenCode, Gemini, or another tool aligned on the same workflow source.
- Use `agentic-sdlc-orchestrator` for propose/apply/verify/archive lifecycle work.
- Use `agentic-sdlc-doctor` after global skill sync or routing changes.
- Track global skill versions and supporting assets in `docs/00-context/agentic-sdlc-registry.md`.
- Validate execution manifests against `docs/00-context/execution-manifest.schema.json`.
- GitHub Copilot routing, when introduced, should live in thin bridge files under `.github/` that point back to this contract and `.agents/skills/`.

## Architecture Boundaries

Intended layout (application code not scaffolded in Steps 1–2):

- Backend API and domain logic live under `backend/`
- Frontend Vue 3 application lives under `frontend/`
- Compose and deployment assets live under `deploy/`
- Uploaded knowledge files live outside Git (Docker volume / local data path); never commit corpora, secrets, or real company documents
- Do not put persistence or auth policy logic in Vue views
- Do not introduce Java/Spring/Oracle packages or modules into this repository

## Coding Conventions

Do not fork a second convention system here. Follow:

- Frontend: `docs/standards/frontend.md` (Vue 3, Vite, TS, Pinia, Router; API modules; role guards; no password storage)
- Backend: `docs/standards/backend.md` (api → services → repositories → adapters; Alembic; pluggable identity; upload metadata; OpenAI-compatible LLM adapter)

## Safety Rails

## NEVER

- Modify `.env`, lockfiles, or CI secrets without explicit approval
- Commit real company documents, internal screenshots, secrets, or runtime logs
- Commit uploaded knowledge corpora under `samples/` or elsewhere
- Implement feature code without an approved SDD slice for non-trivial work
- Start async / cross-session implementation without an execution manifest
- Apply on a failed freshness-gate
- Remove feature flags without searching all call sites
- Commit without running the relevant verification commands once they exist

## ALWAYS

- Update SDD artifacts before non-trivial or user-facing changes
- Create or reference an execution manifest before async / cross-session implementation
- Pass freshness-gate before apply; write archive after verify
- Show diff before committing
- Update changelog notes for user-facing changes once changelog practice is introduced

## Verification

Placeholder until scaffolding exists:

- Backend changes: `cd backend && pytest` (see `docs/standards/backend.md`)
- API contract changes: update FastAPI tests and `docs/05-design/contracts/` guides
- UI changes: `cd frontend && npm run build` (see `docs/standards/frontend.md`)
- Schema/data model changes: Alembic migration + SDD data-model docs aligned
- Hand-off packages: manifest validates against `execution-manifest.schema.json`

## Compact Instructions

Preserve:

1. Architecture decisions (NEVER summarize)
2. Modified files and key changes
3. Current verification status (pass/fail commands)
4. Open risks, TODOs, rollback notes

## Cursor Cloud specific instructions

Current repo state: this is a docs / SDD governance repository. `backend/`, `frontend/`, and `deploy/` are intentionally empty (`.gitkeep` only) and there are **no** dependency manifests (`requirements.txt`, `package.json`, lockfiles), no CI, and no configured linters yet. The "Build And Test" / "Verification" commands above are placeholders that only apply once app scaffolding exists — do not expect them to run today, and do not scaffold the app without an approved SDD slice.

Preinstalled toolchain (no install step needed for current artifacts): Python 3.12, Node 22, npm 10, jq. The update script is effectively a no-op today; it only installs deps once `backend/requirements.txt` or `frontend/package.json` appear.

Runnable artifacts that exist today (all zero-dependency):

- Doc governance scanner (repo's core tooling): `python3 .agents/skills/review-docs-against-code/scripts/doc_consistency_scan.py --root . README.md AGENTS.md docs`. Pure stdlib; add `--json` for machine-readable output. Flagged "missing file-like references" are expected — docs reference intended/future files.
- Product prototype (static mock UI, no build/server framework): serve with `python3 -m http.server 8080` from `docs/01-requirements/prototypes/`, then open `http://localhost:8080/index.html`. It is a self-contained mock (login → Ask → Knowledge → Document detail → Admin); never wire it to real services.
- Execution-manifest schema is plain JSON: validate with `python3 -m json.tool docs/00-context/execution-manifest.schema.json`.
