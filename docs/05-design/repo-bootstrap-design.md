# Detailed Design: Repository Bootstrap

## Overview

`repo-bootstrap` creates the smallest runnable foundation for Quarry KB: a Compose topology, a FastAPI health boundary, a PostgreSQL/pgvector migration baseline, a Vue shell, and externalized configuration with strict embedding/OCR host policy.

## Source Architecture

- `docs/03-spec/repo-bootstrap-spec.md`
- `docs/04-architecture/repo-bootstrap-architecture.md`
- `docs/04-architecture/repo-bootstrap-data-flow.md`
- ADR-0002, ADR-0004, and ADR-0005

The source repository is a greenfield skeleton. No existing application methods, classes, endpoints, tables, or components are referenced as inherited behavior.

## Design Assumptions

- FastAPI, Vue 3, TypeScript, Pinia, Vue Router, PostgreSQL/pgvector, Alembic, and Docker Compose are the locked stack.
- Health probes are infrastructure interfaces, an explicit `SEC-01` exception, and network-restricted rather than user-authenticated in this slice.
- The migration tool is Alembic, as required by the backend standard.
- The Compose file path is `deploy/docker-compose.yml`.
- The web service serves the built Vue application and proxies or routes `/api` to the API service within the Compose network.
- Default local allowlist includes `gateway.internal`, and `.env.example` uses that host for embedding/OCR/chat placeholders.

## Design Scope

### Included

- Compose service definitions and health checks under `deploy/docker-compose.yml`.
- Runtime settings and secret-safe validation.
- Liveness and readiness API endpoints.
- Alembic baseline that enables the `vector` extension and records revision metadata.
- Vue shell, typed API client, and safe error presentation.
- Local verification hooks.

### Excluded

- Auth, JWT, roles, user tables, business routes, upload handling, OCR, embedding, chat, retrieval, provider CRUD, audit, and production monitoring.

## Module Design

### Compose Runtime

- Starts `postgres`, `api`, and `web` in dependency order from `deploy/docker-compose.yml`.
- Uses service health checks to distinguish container start from usable readiness.
- Publishes only the web entrypoint for developer browsers; API health probes are consumed on the Compose network (web→api and compose healthchecks), not as a public internet business route.
- Mounts the later upload volume boundary without adding sample or real corpus content to Git.

### API Configuration Boundary

- Loads environment settings through a typed settings object.
- Validates required local values and endpoint policy during application startup/readiness.
- Embedding/OCR host policy:
  - Parse URL host (hostname or `host:port`).
  - Reject empty hosts.
  - Match literally against the configured allowlist.
  - Do not perform DNS resolution.
  - Do not make an outbound request during validation.
- Keeps secret values available only to server-side integration boundaries.
- Emits stable safe error codes rather than raw connection strings or exception details.

### API Health Boundary

- Liveness answers whether the API process can serve requests.
- Readiness checks configuration, database connectivity, migration state, and vector capability.
- HTTP mapping:
  - `200` only when every required component is ready.
  - `503` when any required component is not ready; response includes all component states plus one stable error code.
- Readiness never calls chat, embedding, or OCR integrations and never reports gateway health.

### Migration Boundary

- Runs the baseline migration through Alembic.
- Baseline revision duty:
  1. Enable PostgreSQL extension `vector` if not already present.
  2. Record Alembic revision metadata.
  3. Create no business tables.
- Readiness validates vector capability by checking extension availability (for example `pg_extension` where `extname = 'vector'`).

### Frontend Shell

- Renders an application frame and foundation status.
- Uses one typed API client for readiness calls.
- Normalizes API results into `loading`, `ready`, `needs_attention`, or `unreachable`.
- Leaves auth and business-route guards for the `auth-password-jwt` slice.

## API / Interface Design

### Response Envelope

All bootstrap JSON responses use the repository envelope:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": null
}
```

### `GET /api/v1/health/live`

- **Purpose:** Deployment/process liveness.
- **Authentication:** None; infrastructure-only probe (`SEC-01` exception).
- **Dependencies:** API process only.
- **Success:** HTTP 200 with `data.status = "alive"`.
- **Failure:** No response if the process cannot serve requests.
- **Side effects:** None.

### `GET /api/v1/health/ready`

- **Purpose:** Local application readiness.
- **Authentication:** None; infrastructure-only probe (`SEC-01` exception).
- **Dependencies:** Valid configuration, PostgreSQL connection, current migration state, and pgvector capability.
- **Success:** HTTP 200 with `success=true` and component states all `ready`.
- **Not-ready:** HTTP 503 with `success=false`, `data.components` populated for all four components, and `error.code` set to one stable code identifying the primary failure.
- **Explicit boundary:** Response does not include gateway health because the endpoint makes no gateway call.
- **Side effects:** Read-only checks only.

Ready example:

```json
{
  "success": true,
  "data": {
    "status": "ready",
    "components": {
      "configuration": "ready",
      "database": "ready",
      "migration": "ready",
      "vector_capability": "ready"
    }
  },
  "error": null,
  "meta": null
}
```

Not-ready example:

```json
{
  "success": false,
  "data": {
    "status": "not_ready",
    "components": {
      "configuration": "ready",
      "database": "not_ready",
      "migration": "not_ready",
      "vector_capability": "not_ready"
    }
  },
  "error": {
    "code": "DATABASE_NOT_READY",
    "message": "Database is not ready."
  },
  "meta": null
}
```

### Frontend API Client

- Base URL is configured once for the application.
- Readiness method maps:
  - HTTP 200 → `ready`
  - HTTP 503 → `needs_attention` (surface safe component labels / error code)
  - transport failure → `unreachable`
- The client never logs authorization headers, passwords, API keys, or raw document content.

## Data Design

- Migration metadata is Alembic-owned and read indirectly through migration readiness.
- Baseline creates/enables only the `vector` extension plus revision metadata.
- No application business tables are created in this slice.
- Runtime configuration is not persisted by the bootstrap application.
- Later slices own their entities, migrations, and data-model documents.

## UI / User Flow Design

### Foundation Shell

- Header identifies Quarry KB and the bootstrap environment.
- Main status panel shows `Loading`, `Ready`, `Needs attention`, or `Unable to reach API`.
- The panel lists only safe dependency labels and stable messages from readiness components.
- Future navigation may show disabled placeholders, but no unauthenticated business action is implied.

### Error Feedback

- Configuration or database failures show a needs-attention / retry state from HTTP 503.
- No raw stack trace, URL credential, token, or password is rendered.
- An API 503 is displayed as local foundation not-ready; it is not labeled as a model-gateway outage.

## Workflow / Execution Design

1. Compose starts PostgreSQL from `deploy/docker-compose.yml`.
2. API loads settings and exposes liveness.
3. Migration command applies the baseline (`vector` extension + revision).
4. Readiness checks configuration, database, migration, and vector capability.
5. Web serves the shell.
6. Shell calls readiness and displays the normalized result.

If configuration fails, readiness returns 503. If the database fails, liveness can remain successful while readiness returns 503. If a gateway is down, bootstrap behavior is unchanged because no gateway call occurs.

## Integration Design

### PostgreSQL/pgvector

- **Pattern:** Local TCP/database connection from API/migration process.
- **Credentials:** Runtime-only database credentials.
- **Retry:** Compose dependency ordering and developer retry; business-level retries are later scope.
- **Failure:** Readiness returns 503 with a safe database or vector-capability code.

### Model Gateway

- **Pattern:** No live call in bootstrap; future adapter boundary is defined by ADR-0004 and host/probe contracts by ADR-0005.
- **Credentials:** Placeholder names only in `.env.example`; real keys remain untracked.
- **Failure:** Not represented in bootstrap readiness; later slices implement surface-specific degradation.

## Security / Audit / Reliability Design

- Keep `.env` and runtime volumes untracked.
- Reject non-allowlisted embedding/OCR hosts by literal match before any outbound request.
- Keep public chat as an explicit later configuration path and preserve the egress warning requirement.
- Restrict probes to the Compose/service network boundary as a `SEC-01` exception.
- Redact secrets and sensitive content from logs and errors.
- Do not create business audit records in bootstrap.

## Validation and Error Handling

| Validation | Failure code | Result |
|---|---|---|
| Required setting missing | `CONFIGURATION_INVALID` | HTTP 503; safe message identifies the setting category. |
| Embedding/OCR host empty or not allowlisted | `CONFIGURATION_INVALID` | HTTP 503 before any outbound request; no DNS lookup. |
| Database unavailable | `DATABASE_NOT_READY` | Liveness may pass; readiness returns 503. |
| Migration not current | `MIGRATION_NOT_CURRENT` | Readiness returns 503 and migration action is documented. |
| pgvector unavailable | `VECTOR_CAPABILITY_UNAVAILABLE` | Readiness returns 503. |
| Web cannot reach API | `API_UNREACHABLE` | Shell shows unreachable / retry state. |

### Edge Cases

1. API alive, database down: liveness passes, readiness returns 503.
2. Database available, migration pending: readiness returns 503 with migration code.
3. Public embedding/OCR URL host: configuration fails before an outbound request.
4. Host that would DNS-resolve privately but is absent from allowlist: rejected (literal match only).
5. Public chat placeholder present: bootstrap accepts provider-neutral configuration but does not enable a provider or make a chat call.
6. Gateway unavailable: bootstrap health remains local-only and does not misreport gateway state.
7. Placeholder config from `.env.example` with `gateway.internal` on the default allowlist: readiness can pass without live gateway credentials.

## Testing Considerations

- Unit coverage for configuration parsing, literal allowlist validation (including empty, public, allowlisted, and DNS-looking-but-unlisteds hosts), redaction, and readiness state mapping.
- API integration coverage for liveness, ready (200), not-ready (503 with components), migration-pending, and vector-capability failure states.
- Migration upgrade/reapply smoke coverage against PostgreSQL/pgvector, asserting `vector` extension exists and no business tables were created.
- Frontend build and typed API-client coverage for ready, needs-attention (503), and unreachable states.
- Compose smoke coverage for `deploy/docker-compose.yml` startup and frontend-to-backend readiness reachability.
- No live model gateway, paid provider, real company document, or secret is required.

## Risks / Design Tradeoffs

- No business schema in the baseline means later slices must own their migrations, but this avoids premature data contracts.
- Infrastructure probes are unauthenticated by design; Compose/service network restriction is the interim boundary until OQ-BOOT-01 decides on a private management port.
- Placeholder gateway configuration gives fast local feedback but postpones live adapter verification until OQ-09 is resolved.

## Open Questions

- Approved PostgreSQL/pgvector image tag (`OQ-BOOT-02`).
- Dedicated management port for probes (`OQ-BOOT-01`).
- Exact gateway values and rate limits for later smoke tests (`OQ-09`).
