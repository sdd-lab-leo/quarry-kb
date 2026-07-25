# Frontend Development Standards

Authority for Vue 3 application code under `frontend/`. Hard product rules remain in `PROJECT_RULES.md`. Stack lock: ADR-0002.

## Stack

- Vue 3 (Composition API + `<script setup>`)
- Vite
- TypeScript (strict mode preferred)
- Pinia for client state
- Vue Router for navigation

Do not introduce React, jQuery, or unapproved UI frameworks without an ADR.

## Project Layout (intended)

```text
frontend/src/
  api/                 # or services/ — HTTP clients only
  components/          # presentational / reusable UI
  views/               # route-level container pages
  composables/         # useXxx helpers
  stores/              # Pinia stores
  router/              # routes + guards
  types/               # shared TS types aligned to API contracts
  assets/
```

## API Access

- All HTTP calls live in `src/api/` or `src/services/`.
- Views and presentational components must not call `fetch` / `axios` directly.
- Prefer a single HTTP client wrapper that:
  - attaches auth token from session storage / memory;
  - normalizes errors into a typed `ApiError` (`code`, `message`, `requestId` when available);
  - never logs raw tokens or passwords.
- Page code consumes typed API functions; it does not assemble URLs ad hoc across files.

## Components And Composables

- Separate **container** (route/views, data loading, permissions) from **presentational** components (props in, events out).
- Composables are named `useXxx` (for example `useAuthSession`, `useKnowledgeSearch`).
- Vue SFCs and TS component names use PascalCase (`KnowledgeSearchPanel.vue`).
- Keep composables free of route-specific markup; return state and actions only.

## Routing, Auth, And Roles

- Roles: `Admin` | `Editor` | `Viewer` (same vocabulary as backend).
- Enforce role checks in Vue Router navigation guards and, where needed, in container components.
- Frontend stores **token/session metadata only**. Never store passwords, password hashes, or SSO secrets in `localStorage`, Pinia, or cookies beyond the agreed session token.
- On 401, clear session and redirect to login. On 403, show a non-destructive denial state.

## Errors And Feedback

- Surface API failures through one shared notification / toast path.
- Prefer server `message` + stable `code` when present; fall back to a generic user-safe string.
- Include a correlation id / request id in developer consoles or admin-only detail when the API provides one.
- Do not swallow errors in empty `catch` blocks.

## Types And Contracts

- Avoid unnecessary `any`. Use `unknown` + narrowing when the shape is uncertain.
- Keep request/response types aligned with backend contracts under `docs/05-design/contracts/` and generated or hand-maintained types in `src/types/`.
- When a contract changes, update types and SDD API guide in the same change set.

## UI Libraries

- Prefer the company’s existing approved UI component library when one is designated for intranet apps.
- If a new UI library is required, write an ADR before adding the dependency.
- Until a library ADR exists, keep UI plain Vue + CSS variables; do not silently adopt a new kit.

## State Management

- Server state: fetch via API modules; cache in Pinia only when multiple views share it.
- Do not mirror the entire backend database in Pinia.
- Derived UI state belongs in composables or local component state.

## Testing And Verification (when scaffolding exists)

- Prefer component tests for presentational logic and store/composable unit tests for state.
- Verification baseline: `cd frontend && npm run build` (typecheck + production build).
- Route-guard and role matrix changes need explicit test coverage or a manual verification checklist in the tasks doc.

## Related Docs

- `PROJECT_RULES.md`
- `docs/standards/backend.md`
- `docs/00-context/decisions/ADR-0002-lock-technology-stack-and-auth-evolution.md`
- `docs/00-context/handoff-playbook.md`
