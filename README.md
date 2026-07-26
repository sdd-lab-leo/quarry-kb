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

## Stack

- Frontend: Vue 3 + Vite + TypeScript + Pinia (`frontend/`)
- Backend: FastAPI (`backend/`)
- Data: PostgreSQL + pgvector
- Uploads: local disk via Docker volume (not in Git)
- Auth: deferred to `auth-password-jwt` (not in `repo-bootstrap`)
- Runtime: Docker Compose (`web` + `api` + `postgres`) under `deploy/`

## Repository Layout

```text
.agents/skills/          Canonical SDD / Agentic SDLC skills
docs/00-context/         Durable context, profile, registry, ADRs, hand-off
docs/01-requirements/    Requirements slices
docs/02-user-stories/    User stories
docs/03-spec/            Specifications
docs/04-architecture/    Architecture / data flow / data model
docs/05-design/          Design + API contracts
docs/06-tasks/           Implementation tasks
frontend/                Vue 3 foundation shell
backend/                 FastAPI foundation + Alembic baseline
deploy/                  Compose topology
samples/                 Mock samples only
```

## Samples Policy

`samples/` is for **mock** examples only.

Do **not** place real company documents, internal screenshots, secrets, production exports, or personal data here.

## Local Startup (`repo-bootstrap`)

1. Copy `.env.example` to an untracked `.env` and adjust only local placeholders.
2. Start the foundation:

```sh
docker compose -f deploy/docker-compose.yml up --build
```

3. Open `http://localhost:8080` for the Vue shell. It calls `GET /api/v1/health/ready` through the web proxy.

### Separate local processes

```sh
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install --no-package-lock
npm run dev
```

### Verification

```sh
python3 scripts/validate_execution_manifest.py docs/00-context/changes/20260726-repo-bootstrap/manifest.yaml
git diff --check
cd backend && .venv/bin/python -m pytest
cd frontend && npm run build
python3 -c "import yaml; yaml.safe_load(open('deploy/docker-compose.yml')); print('compose yaml OK')"
# optional when Docker is available:
docker compose -f deploy/docker-compose.yml config
```

### Open risks still tracked in SDD

- `OQ-BOOT-02`: PostgreSQL/pgvector image tag used in Compose is a development pin (`pgvector/pgvector:0.8.0-pg16`), not a pilot-approved tag.
- `OQ-BOOT-01`: probe management port undecided; API remains on the Compose network.
- `OQ-09`: concrete gateway URLs/models unresolved; placeholders only.

## Language

Documentation bodies are written in English. Chinese mirrors, if needed, should be stored as `*.zh-CN.md`.
