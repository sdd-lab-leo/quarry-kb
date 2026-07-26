# System Architecture: Repository Bootstrap

## Overview

- **Architecture Summary:** A small layered foundation runs a Vue web shell, a FastAPI API, and PostgreSQL/pgvector through Docker Compose. The API owns safe configuration and readiness evaluation; the web shell consumes health state through a single typed HTTP boundary. External model gateways are configuration boundaries only in this slice.
- **Design Objective:** Make local startup, database readiness, and integration boundaries explicit and reproducible before business slices add identity, ingestion, and RAG behavior.
- **Architectural Style:** Layered modular application with a containerized local runtime and adapter-ready external integration boundaries.

## Source Specification

- **Feature / System Name:** `repo-bootstrap`
- **Scope Summary:** Compose foundation, FastAPI/Vue shells, PostgreSQL/pgvector migration baseline, health probes, environment template, and gateway host-policy validation.

## Architectural Drivers

### Key Functional Drivers

- Start `web`, `api`, and `postgres` together through the documented local flow.
- Distinguish process liveness from database/migration/configuration readiness.
- Provide a migration boundary for later application data.
- Keep chat provider configuration vendor-neutral.
- Reject public embedding/OCR endpoints before outbound use.

### Key Non-Functional Drivers

- Secrets and uploaded content stay outside Git.
- Browse and future application startup must not depend on an uncalled model gateway.
- Runtime configuration is externalized.
- The stack remains FastAPI + Vue 3 + PostgreSQL/pgvector + Docker Compose.

### Constraints and Assumptions

- The repository is greenfield; there are no existing application components to reuse.
- The first supported environment is local Docker Compose.
- `[ASSUMPTION]` Health probes are restricted to the service/deployment boundary and do not require user authentication.
- Exact gateway URLs, model IDs, OCR path, and rate limits are deployment inputs under OQ-09.

## System Context

### Primary Actors

| Actor | Role |
|---|---|
| Developer | Starts services, runs migrations, and verifies the foundation. |
| Platform maintainer | Supplies environment configuration and inspects readiness. |

### External Systems

| System | Integration Purpose |
|---|---|
| PostgreSQL/pgvector | Foundation database and later vector storage capability. |
| Internal model gateway | Future chat, embedding, and OCR target; configuration boundary only here. |

### System Boundary

The slice includes the local web shell, API, database connection, migration baseline, configuration validation, and deployment probes. It excludes business data and model execution. Uploaded files, secrets, and runtime logs are outside the Git boundary; later upload storage uses a configured volume.

## High-Level Architecture

### Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────┐
│  Developer / Platform Maintainer                             │
│  Compose command · browser · readiness probe                  │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTP / Compose
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  Web Shell                                                   │
│  Vue 3 · Vite · TypeScript · typed health client              │
└─────────────────────────┬────────────────────────────────────┘
                          │ REST / JSON
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  API Foundation                                              │
│  FastAPI · settings · liveness/readiness · safe diagnostics   │
├──────────────────────────────────────────────────────────────┤
│  Foundation Services                                         │
│  configuration policy · migration readiness · API boundary    │
└──────────────┬───────────────────────────────┬───────────────┘
               │ database protocol             │ config only
               ▼                               ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│  PostgreSQL + pgvector    │       │  Internal Model Gateway   │
│  migration baseline       │       │  future chat/embed/OCR   │
└──────────────────────────┘       └──────────────────────────┘
```

### Layer Summary

- **Presentation Layer:** Vue shell renders the foundation status and provides the future route boundary.
- **API Layer:** FastAPI exposes deployment probes and loads validated runtime settings.
- **Foundation Services:** Configuration policy and migration readiness coordinate checks without owning future business domains.
- **Persistence Layer:** PostgreSQL/pgvector provides the database capability and migration state.
- **Integration Boundary:** Gateway settings are validated and recorded, but no gateway request is made by bootstrap probes.

## Component Breakdown

### Frontend Components

- **Shell:** Renders the initial application frame and foundation status.
- **Typed API client:** Owns health requests and normalized safe errors.
- **Route boundary:** Establishes the place where later authenticated views can be added; it does not implement auth.

### Backend Services

- **Configuration boundary:** Loads environment settings, validates required values, and enforces endpoint policy.
- **Health boundary:** Reports liveness and readiness with safe component statuses.
- **Migration boundary:** Reports whether the database has reached the required foundation revision and vector capability.

### Configuration / Administration Modules

- **Environment template:** Documents names and placeholder values; it is not a secret store.
- **Gateway policy:** Separates public-chat allowance from internal-only embedding/OCR configuration.

### Monitoring / Audit Modules

- **Deployment probes:** Provide liveness/readiness signals for local orchestration.
- **Structured diagnostics:** Emit request-safe outcome codes; business audit logging is deferred to later slices.

### Integration Adapters

- **Database adapter:** Connects the API readiness boundary to PostgreSQL/pgvector.
- **Model gateway adapters:** Not implemented in this slice; ADR-0004 defines their future boundary and allowed destinations.

## Data Architecture

### Conceptual Entities

| Entity | Description | Key Attributes |
|---|---|---|
| Migration state | Tool-owned record of the applied foundation revision | Revision identifier, applied state |
| Runtime configuration | Environment-owned settings | Environment, database URL, paths, gateway URLs, model IDs, allowlist |

No application business entities are owned by this slice.

### State / Status Models

- Process liveness: `alive` → `not-running` when the API process stops.
- Readiness: `not-ready` → `ready` when database, migration, and configuration checks pass; `ready` → `not-ready` when any required local dependency fails.
- Gateway status is intentionally not part of bootstrap readiness because no gateway call is made.

### Persistence Responsibilities

The migration tool owns migration metadata. Later slices own their business entities and migrations; bootstrap must not create placeholder user or knowledge tables that imply unapproved product behavior.

## Integration Architecture

### PostgreSQL/pgvector

- **Interaction Pattern:** Local database connection used for migration and readiness checks.
- **Triggered by:** Service startup, migration command, and readiness probe.
- **Data exchanged:** Connection metadata and migration/capability status; no model prompts or uploaded document content.

### Internal Model Gateway

- **Interaction Pattern:** Configuration-only boundary in bootstrap; future adapters use provider-specific contracts.
- **Triggered by:** None in this slice.
- **Data exchanged:** None in bootstrap.
- **Boundary:** Embedding and OCR remain internal-only; chat may later target internal or explicitly configured public providers.

## Workflow / Runtime Architecture

### Request Flow

1. The browser loads the web shell.
2. The shell calls the API health boundary through its typed client.
3. The API returns liveness/readiness state after local configuration and database checks.
4. The shell displays a ready or actionable failure state.

### State Transitions

- `not-ready → ready` when all required local checks pass.
- `ready → not-ready` when the database, migration state, or configuration becomes invalid.
- `alive → not-running` when the API process exits.

### Validation Flow

Configuration is validated before the API reports readiness. Embedding/OCR host policy is checked before any future adapter can make an outbound request. The health boundary never treats an uncalled gateway as healthy or unhealthy.

### Failure and Retry Handling

Compose restarts or manual developer retries are the bootstrap recovery path. The API reports dependency-specific readiness failure; bounded gateway retry behavior belongs to later ingestion and Ask slices.

## API / Interface Boundaries

### Major Inbound Interfaces

| Interface | Consumer | Purpose |
|---|---|---|
| `GET /api/v1/health/live` | Compose / operator | Process liveness probe. |
| `GET /api/v1/health/ready` | Compose / operator / web shell | Database, migration, and configuration readiness. |

### Internal Module Boundaries

- Web shell consumes health state through a typed HTTP client.
- Health boundary consumes configuration and database readiness abstractions.
- Future business services must not bypass the configuration or persistence boundaries.

### Outbound Integrations

| Target | Protocol | Triggered by |
|---|---|---|
| PostgreSQL/pgvector | Database protocol | Migration and readiness checks. |
| Internal model gateway | None in bootstrap | Later chat/embedding/OCR adapters only. |

### Event / Polling / Callback Patterns

- No asynchronous event or gateway callback is introduced in this slice.

## Deployment / Environment Considerations

- **Supported Environment:** Local Docker Compose first; later environments must inject their own configuration.
- **Runtime Assumptions:** `web`, `api`, and `postgres` are the only required services for bootstrap.
- **Configuration Separation:** `.env.example` documents names; real `.env` remains untracked.
- **Secrets Handling:** Keys are injected at runtime and never returned by probes.
- **Operational Concerns:** Readiness must remain truthful and independent of an uncalled gateway.

## Security / Reliability / Observability

### Access Control

Business authorization is deferred to `auth-password-jwt`. Infrastructure probes expose no business data and must be network-restricted.

### Secret Protection

Health responses, diagnostics, and logs redact passwords, tokens, API keys, authorization headers, and document bodies.

### Auditability

Business audit entries are deferred. Configuration validation and readiness outcomes are operational diagnostics, not user audit records.

### Resilience / Retry

Database readiness fails closed when the database or migration baseline is unavailable. No silent public fallback exists for embedding/OCR.

### Monitoring / Logging

Structured safe outcome codes are sufficient for bootstrap. Full metrics and tracing belong to the reliability slice.

## Risks / Tradeoffs

| # | Risk / Tradeoff | Notes |
|---|---|---|
| 1 | Gateway values are unresolved | Placeholder configuration enables bootstrap but postpones live adapter verification. |
| 2 | Probes are not yet on a dedicated management port | Network restriction is the interim boundary; deployment hardening must resolve OQ-BOOT-01. |
| 3 | No business schema is created | Later slices own their migrations, preventing placeholder data models from becoming accidental contracts. |

## Open Questions

1. Which PostgreSQL/pgvector image tag is approved for the pilot?
2. Should probes use a private management port?
3. What exact gateway values and rate limits will be used for later adapter smoke tests?

