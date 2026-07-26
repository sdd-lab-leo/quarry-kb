# Detailed Design: Repository Bootstrap

## Overview

`repo-bootstrap` creates the smallest runnable foundation for Quarry KB: a Compose topology, a FastAPI health boundary, a PostgreSQL/pgvector migration baseline, a Vue shell, and externalized configuration with strict embedding/OCR host policy.

## Source Architecture

- `docs/03-spec/repo-bootstrap-spec.md`
- `docs/04-architecture/repo-bootstrap-architecture.md`
- `docs/04-architecture/repo-bootstrap-data-flow.md`
- ADR-0002 and ADR-0004

The source repository is a greenfield skeleton. No existing application methods, classes, endpoints, tables, or components are referenced as inherited behavior.

## Design Assumptions

- FastAPI, Vue 3, TypeScript, Pinia, Vue Router, PostgreSQL/pgvector, Alembic, and Docker Compose are the locked stack.
- Health probes are infrastructure interfaces and are network-restricted rather than user-authenticated in this slice.
- `[ASSUMPTION]` The migration tool is Alembic, as required by the backend standard.
- `[ASSUMPTION]` The web service serves the built Vue application and proxies or routes `/api` to the API service within the Compose network.

## Design Scope

### Included

- Compose service definitions and health checks.
- Runtime settings and secret-safe validation.
- Liveness and readiness API endpoints.
- Alembic baseline and pgvector capability validation.
- Vue shell, typed API client, and safe error presentation.
- Local verification hooks.

### Excluded

- Auth, JWT, roles, user tables, business routes, upload handling, OCR, embedding, chat, retrieval, provider CRUD, audit, and production monitoring.

## Module Design

### Compose Runtime

- Starts `postgres`, `api`, and `web` in dependency order.
- Uses service health checks to distinguish container start from usable readiness.
- Mounts the later upload volume boundary without adding sample or real corpus content to Git.

### API Configuration Boundary

- Loads environment settings through a typed settings object.
- Validates required local values and endpoint policy during application startup/readiness.
- Keeps secret values available only to server-side integration boundaries.
- Emits stable safe error codes rather than raw connection strings or exception details.

### API Health Boundary

- Liveness answers whether the API process can serve requests.
- Readiness checks configuration, database connectivity, migration state, and vector capability.
- Readiness never calls chat, embedding, or OCR integrations.

### Migration Boundary

- Runs the baseline migration through Alembic.
- Validates the PostgreSQL/pgvector capability needed by later chunk embeddings.
- Does not create placeholder business entities.

### Frontend Shell

- Renders an application frame and foundation status.
- Uses one typed API client for health calls.
- Normalizes API failures into a safe display state.
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

Failure responses set `success` to `false`, `data` to `null`, and include a stable error `code` and safe `message`.

### `GET /api/v1/health/live`

- **Purpose:** Deployment/process liveness.
- **Authentication:** None; infrastructure-only probe.
- **Dependencies:** API process only.
- **Success:** HTTP 200 with `data.status = "alive"`.
- **Failure:** No response if the process cannot serve requests.
- **Side effects:** None.

### `GET /api/v1/health/ready`

- **Purpose:** Local application readiness.
- **Authentication:** None; infrastructure-only probe.
- **Dependencies:** Valid configuration, PostgreSQL connection, current migration state, and pgvector capability.
- **Success:** HTTP 200 with component states for `configuration`, `database`, `migration`, and `vector_capability`.
- **Failure:** HTTP 503 with the same component categories and a safe code such as `DATABASE_NOT_READY`, `MIGRATION_NOT_CURRENT`, `VECTOR_CAPABILITY_UNAVAILABLE`, or `CONFIGURATION_INVALID`.
- **Explicit boundary:** Response does not include gateway health because the endpoint makes no gateway call.
- **Side effects:** Read-only checks only.

### Frontend API Client

- Base URL is configured once for the application.
- Health methods return typed success data or a normalized `ApiError` with `code`, `message`, and optional request ID.
- The client never logs authorization headers, passwords, API keys, or raw document content.

## Data Design

- Migration metadata is tool-owned and read indirectly through migration readiness.
- No application business tables are created in this slice.
- Runtime configuration is not persisted by the bootstrap application.
- Later slices own their entities, migrations, and data-model documents.

## UI / User Flow Design

### Foundation Shell

- Header identifies Quarry KB and the bootstrap environment.
- Main status panel shows `Loading`, `Ready`, `Needs attention`, or `Unable to reach API`.
- The panel lists only safe dependency labels and stable messages.
- Future navigation may show disabled placeholders, but no unauthenticated business action is implied.

### Error Feedback

- Configuration or database failures show a retry/instructions state.
- No raw stack trace, URL credential, token, or password is rendered.
- An API 503 is displayed as local foundation not-ready; it is not labeled as a model-gateway outage.

## Workflow / Execution Design

1. Compose starts PostgreSQL.
2. API loads settings and exposes liveness.
3. Migration command applies the baseline.
4. Readiness checks configuration, database, migration, and vector capability.
5. Web serves the shell.
6. Shell calls readiness and displays the normalized result.

If configuration fails, readiness stays not-ready. If the database fails, liveness can remain successful while readiness fails. If a gateway is down, bootstrap behavior is unchanged because no gateway call occurs.

## Integration Design

### PostgreSQL/pgvector

- **Pattern:** Local TCP/database connection from API/migration process.
- **Credentials:** Runtime-only database credentials.
- **Retry:** Compose dependency ordering and developer retry; business-level retries are later scope.
- **Failure:** Readiness returns 503 with a safe database code.

### Model Gateway

- **Pattern:** No live call in bootstrap; future adapter boundary is defined by ADR-0004.
- **Credentials:** Placeholder names only in `.env.example`; real keys remain untracked.
- **Failure:** Not represented in bootstrap readiness; later slices implement surface-specific degradation.

## Security / Audit / Reliability Design

- Keep `.env` and runtime volumes untracked.
- Reject public embedding/OCR targets before any outbound request.
- Keep public chat as an explicit later configuration path and preserve the egress warning requirement.
- Restrict probes to the deployment boundary.
- Redact secrets and sensitive content from logs and errors.
- Do not create business audit records in bootstrap.

## Validation and Error Handling

| Validation | Failure code | Result |
|---|---|---|
| Required setting missing | `CONFIGURATION_INVALID` | API remains not-ready; safe message identifies the setting category. |
| Embedding/OCR host not allowed | `CONFIGURATION_INVALID` | Startup/readiness fails before any outbound request. |
| Database unavailable | `DATABASE_NOT_READY` | Liveness may pass; readiness returns 503. |
| Migration not current | `MIGRATION_NOT_CURRENT` | Readiness returns 503 and migration action is documented. |
| pgvector unavailable | `VECTOR_CAPABILITY_UNAVAILABLE` | Readiness returns 503. |
| Web cannot reach API | `API_UNREACHABLE` | Shell shows retry/instructions state. |

### Edge Cases

1. API alive, database down: liveness passes, readiness fails.
2. Database available, migration pending: readiness fails with migration code.
3. Public embedding/OCR URL: configuration fails before an outbound request.
4. Public chat placeholder present: bootstrap accepts provider-neutral configuration but does not enable a provider or make a chat call.
5. Gateway unavailable: bootstrap health remains local-only and does not misreport gateway state.

## Testing Considerations

- Unit coverage for configuration parsing, intranet allowlist validation, redaction, and readiness state mapping.
- API integration coverage for liveness, ready, not-ready, migration-pending, and vector-capability failure states.
- Migration upgrade/reapply smoke coverage against PostgreSQL/pgvector.
- Frontend build and typed API-client coverage for ready, 503, and unreachable states.
- Compose smoke coverage for service startup and frontend-to-backend health reachability.
- No live model gateway, paid provider, real company document, or secret is required.

## Risks / Design Tradeoffs

- No business schema in the baseline means later slices must own their migrations, but this avoids premature data contracts.
- Infrastructure probes are unauthenticated by design; deployment must restrict their network exposure.
- Placeholder gateway configuration gives fast local feedback but postpones live adapter verification until OQ-09 is resolved.

## Open Questions

- Approved PostgreSQL/pgvector image tag.
- Dedicated management port for probes.
- Exact gateway values and rate limits for later smoke tests.

