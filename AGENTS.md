# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

# Project Contract

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
- Non-trivial or user-facing changes must update SDD first. Do not implement feature code without an approved slice.
- If a change has already been implemented without SDD artifacts, backfill the full SDD chain immediately and mark the documents as `Backfilled` rather than pretending they preceded the code.
- Treat SDD documents as the primary source of change intent and scope. Code, tests, and changelog entries must trace back to the SDD artifacts.
- For small bug fixes, copy edits, or metadata-only cleanup, update the nearest existing SDD artifact only when behavior or scope changes.
- Do not add a new user-facing feature as code-only work.
- Before asynchronous agent work or cross-session implementation, create or reference an execution manifest validated against `docs/00-context/execution-manifest.schema.json`. Detailed hand-off playbook content arrives in a later step.

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
- Use `sdd-slice-bootstrap` when starting or auditing a feature slice.
- Use `execution-manifest` before handing work to a coding agent, remote agent, or automation.
- Use `freshness-gate` before approving, implementing, or releasing from potentially stale docs/code/tests.
- Use `cross-ide-skill-router` when keeping Codex, Claude Code, OpenCode, Gemini, or another tool aligned on the same workflow source.
- Use `agentic-sdlc-orchestrator` for propose/apply/verify/archive lifecycle work.
- Use `agentic-sdlc-doctor` after global skill sync or routing changes.
- Track global skill versions and supporting assets in `docs/00-context/agentic-sdlc-registry.md`.
- Validate execution manifests against `docs/00-context/execution-manifest.schema.json`.
- GitHub Copilot routing, when introduced, should live in thin bridge files under `.github/` that point back to this contract and `.agents/skills/`.

## Architecture Boundaries

Intended layout (not yet scaffolded as a full application in Step 1):

- Backend API and domain logic live under `backend/`
- Frontend Vue 3 application lives under `frontend/`
- Compose and deployment assets live under `deploy/`
- Uploaded knowledge files live outside Git (Docker volume / local data path); never commit corpora, secrets, or real company documents
- Do not put persistence or auth policy logic in Vue views
- Do not introduce Java/Spring/Oracle packages or modules into this repository

## Coding Conventions

Placeholder for Step 2.

- Detailed language and framework conventions will live under `docs/standards/*` and will be referenced from this section once created.
- Until those standards exist, prefer clear FastAPI + Vue 3 + TypeScript patterns consistent with ADR-0002 and do not invent a parallel convention system.

## Safety Rails

## NEVER

- Modify `.env`, lockfiles, or CI secrets without explicit approval
- Commit real company documents, internal screenshots, secrets, or runtime logs
- Commit uploaded knowledge corpora under `samples/` or elsewhere
- Implement feature code without an approved SDD slice for non-trivial work
- Remove feature flags without searching all call sites
- Commit without running the relevant verification commands once they exist

## ALWAYS

- Update SDD artifacts before non-trivial or user-facing changes
- Create or reference an execution manifest before async / cross-session implementation
- Show diff before committing
- Update changelog notes for user-facing changes once changelog practice is introduced

## Verification

Placeholder until scaffolding exists:

- Backend changes: `cd backend && pytest`
- API contract changes: update FastAPI tests and `docs/05-design/contracts/` guides
- UI changes: `cd frontend && npm run build`
- Schema/data model changes: keep migrations and SDD data-model docs aligned

## Compact Instructions

Preserve:

1. Architecture decisions (NEVER summarize)
2. Modified files and key changes
3. Current verification status (pass/fail commands)
4. Open risks, TODOs, rollback notes
