# Quarry KB Repository Bootstrap — API Implementation Guide

| Field | Value |
|---|---|
| Version | 0.1 draft |
| Base path | `/api/v1` |
| Backend | FastAPI |
| Authentication | Infrastructure probes only; explicit `SEC-01` exception; business authentication is deferred to `auth-password-jwt` |
| Response envelope | `success`, `data`, `error`, `meta` |

## Overview

This guide defines the two infrastructure health endpoints required by `repo-bootstrap`. They expose no business data and do not call the model gateway.

## Authentication

The health endpoints are deployment probes and are unauthenticated in this slice. This is an explicit exception to product `SEC-01` (session token required for non-authentication endpoints). The exception applies only to:

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

These probes must be restricted by the Compose/service network boundary for local bootstrap. They must not be treated as public business routes. All future business endpoints remain subject to `SEC-01` and must not reuse this exception. Decision record: ADR-0005.

## Error Response Format

### Ready success

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

### Not-ready failure

Not-ready always uses HTTP 503. `data` remains populated with overall status and component diagnostics so operators and the frontend can see which local dependency failed. `error` carries one stable primary code.

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

Messages must not include credentials, authorization headers, raw connection strings, API keys, document content, or unredacted stack traces.

There is no HTTP 200 response with `status=not_ready`.

## API Endpoints Summary

| Operation | Method | Endpoint | Auth |
|---|---|---|---|
| Liveness | GET | `/api/v1/health/live` | Deployment / Compose network boundary only |
| Readiness | GET | `/api/v1/health/ready` | Deployment / Compose network boundary only |

## Endpoint Reference

### Liveness

- **Method/path:** `GET /api/v1/health/live`
- **Purpose:** Confirm that the API process can accept requests.
- **Request:** No path, query, or body parameters.
- **Success response:** HTTP 200, `data.status = "alive"`.
- **Error cases:** No HTTP response when the process is not serving; do not perform dependency checks here.
- **Side effects:** None.

### Readiness

- **Method/path:** `GET /api/v1/health/ready`
- **Purpose:** Confirm local configuration, database, migration, and vector capability readiness.
- **Request:** No path, query, or body parameters.
- **Success response:** HTTP 200 with the ready payload shown above.
- **Not-ready response:** HTTP 503 with the not-ready payload shape shown above.
- **Error cases:**

| HTTP | Code | Condition |
|---|---|---|
| 503 | `CONFIGURATION_INVALID` | Required value missing/malformed, embedding/OCR host empty, or host not on allowlist. |
| 503 | `DATABASE_NOT_READY` | PostgreSQL connection unavailable. |
| 503 | `MIGRATION_NOT_CURRENT` | Baseline migration is missing or not current. |
| 503 | `VECTOR_CAPABILITY_UNAVAILABLE` | PostgreSQL `vector` extension is unavailable. |

- **Component fields:** Always include `configuration`, `database`, `migration`, and `vector_capability` with values `ready` or `not_ready`.
- **Primary error code selection:** Use the first failing dependency in this order: configuration → database → migration → vector capability.
- **Explicit non-behavior:** The endpoint does not call chat, embedding, or OCR integrations and therefore does not report their health.
- **Side effects:** Read-only database/configuration checks.

## State Reference

```text
not_ready (HTTP 503) ── all local checks pass ──► ready (HTTP 200)
         ▲                                         │
         └──────── any local check fails ◄─────────┘
```

Frontend mapping:

| API result | Frontend state |
|---|---|
| HTTP 200 ready | `ready` |
| HTTP 503 not-ready | `needs_attention` |
| Transport failure | `unreachable` |

## Concurrency

Readiness checks must be read-only and safe for concurrent probes. Database connection handling must use the configured application pool boundary; a probe must not create an unbounded connection per request.

## Integration Dependencies

- PostgreSQL/pgvector connection settings from runtime environment.
- Alembic migration tool state and `vector` extension availability.
- Intranet/gateway allowlist configuration for embedding/OCR settings (literal host match; no DNS lookup).
- No live model gateway dependency.
