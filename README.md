# Quarry KB

Department-scale living knowledge workbench for intranet teams (~60 people), optimized for fast iteration.

Value chain:

```text
Documents → Retrievable knowledge / RAG Q&A → (later) Agent → (later) Wiki
```

Quarry KB is greenfield. It does not fork WeKnora. Atlas Knowledge Hub is a different product (conversion/review); Quarry KB focuses on retrieval, Q&A, and knowledge evolution.

## Discipline Entry Points

| Document | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Agent contract: SDD gates, hand-off gates, skills, intended build/test |
| [PROJECT_RULES.md](PROJECT_RULES.md) | Hard rules for SDD, hand-off, product boundaries |
| [docs/00-context/sdd-profile.md](docs/00-context/sdd-profile.md) | Active SDD profile (`quarry-kb-fastapi-vue`) |
| [docs/SDD-BOOTSTRAP.md](docs/SDD-BOOTSTRAP.md) | Full-slice SDD generation entry (`wwa-sdd-generate-all`) |
| [docs/standards/frontend.md](docs/standards/frontend.md) | Frontend development standards |
| [docs/standards/backend.md](docs/standards/backend.md) | Backend development standards |
| [docs/lessons/README.md](docs/lessons/README.md) | Lessons learnt process (inherited / observed) |
| [docs/00-context/handoff-playbook.md](docs/00-context/handoff-playbook.md) | Execution-manifest hand-off procedure |
| [docs/00-context/checklists/sdd-generation-gate.md](docs/00-context/checklists/sdd-generation-gate.md) | Skill-chain evidence checklist |
| [docs/00-context/product-positioning.md](docs/00-context/product-positioning.md) | Product boundaries vs Atlas / WeKnora |
| [docs/00-context/decisions/](docs/00-context/decisions/) | Architecture Decision Records |

Non-trivial or user-facing changes must update the SDD chain before implementation. No approved slice means no feature code.

## Intended Stack (documented, not scaffolded yet)

- Frontend: Vue 3 + Vite + TypeScript + Pinia (`frontend/`)
- Backend: FastAPI (`backend/`)
- Data: PostgreSQL + pgvector
- Uploads: local disk via Docker volume (not in Git)
- Auth: phase 1 account/password + JWT; phase 2 company SSO with reserved `external_subject`
- Roles: Admin | Editor | Viewer
- Runtime: Docker Compose (`web` + `api` + `postgres`) under `deploy/`

## Repository Layout

```text
.agents/skills/          Canonical SDD / Agentic SDLC skills
.claude/skills/          Claude Code mirror of skills
.opencode/commands/      OpenCode /sdd router
docs/00-context/         Durable context, profile, registry, ADRs, hand-off
docs/01-requirements/    Requirements slices
docs/02-user-stories/    User stories
docs/03-spec/            Specifications
docs/04-architecture/    Architecture / data flow / data model
docs/05-design/          Design + API contracts
docs/06-tasks/           Implementation tasks
docs/07-prompts/         Prompt notes
docs/reviews/            Review reports
docs/standards/          Frontend / backend development standards
docs/lessons/            Inherited + observed lessons
frontend/                Vue 3 app (placeholder)
backend/                 FastAPI app (placeholder)
deploy/                  Compose / deploy assets (placeholder)
samples/input|output     Mock samples only
```

## Samples Policy

`samples/` is for **mock** examples only.

Do **not** place real company documents, internal screenshots, secrets, production exports, or personal data here.

## Local Startup (placeholder)

Application scaffolding is intentionally not part of Step 1. Intended later flow:

```sh
# after backend/frontend/deploy scaffolding exists
docker compose -f deploy/docker-compose.yml up --build
```

Or separately:

```sh
cd backend && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## Language

Documentation bodies are written in English. Chinese mirrors, if needed, should be stored as `*.zh-CN.md`.
