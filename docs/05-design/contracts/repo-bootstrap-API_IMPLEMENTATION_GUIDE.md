# Quarry KB Repository Bootstrap — API Implementation Guide

| Field | Value |
|---|---|
| Version | 0.1 draft |
| Base path | `/api/v1` |
| Backend | FastAPI |
| Authentication | Infrastructure probes only; business authentication is deferred to `auth-password-jwt` |
| Response envelope | `success`, `data`, `error`, `meta` |

## Overview

This guide defines the two infrastructure health endpoints required by `repo-bootstrap`. They expose no business data and do not call the model gateway.

## Authentication

The health endpoints are deployment probes and are unauthenticated in this slice. They must be restricted by the service/deployment network boundary. All future business endpoints remain subject to the product authentication requirement and must not reuse this exception.

## Error Response Format

### Success

```json
{
  "success": true,
  "data": {
    "status": "ready"
  },
  "error": null,
  "meta": null
}
```

### Failure

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "DATABASE_NOT_READY",
    "message": "Database is not ready."
  },
  "meta": null
}
```

Messages must not include credentials, authorization headers, raw connection strings, API keys, document content, or unredacted stack traces.

## API Endpoints Summary

| Operation | Method | Endpoint | Auth |
|---|---|---|---|
| Liveness | GET | `/api/v1/health/live` | Deployment boundary only |
| Readiness | GET | `/api/v1/health/ready` | Deployment boundary only |

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
- **Success response:** HTTP 200 with:

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

- **Not-ready response:** HTTP 503 with the failing component state and one stable error code.
- **Error cases:**

| HTTP | Code | Condition |
|---|---|---|
| 503 | `CONFIGURATION_INVALID` | Required value missing, malformed, or endpoint policy rejected. |
| 503 | `DATABASE_NOT_READY` | PostgreSQL connection unavailable. |
| 503 | `MIGRATION_NOT_CURRENT` | Baseline migration is missing or not current. |
| 503 | `VECTOR_CAPABILITY_UNAVAILABLE` | Required PostgreSQL vector capability is unavailable. |

- **Explicit non-behavior:** The endpoint does not call chat, embedding, or OCR integrations and therefore does not report their health.
- **Side effects:** Read-only database/configuration checks.

## State Reference

```text
not-ready ── local checks pass ──► ready
    ▲                              │
    └──── database/config fails ◄──┘
```

## Concurrency

Readiness checks must be read-only and safe for concurrent probes. Database connection handling must use the configured application pool boundary; a probe must not create an unbounded connection per request.

## Integration Dependencies

- PostgreSQL/pgvector connection settings from runtime environment.
- Migration tool state.
- Intranet/gateway allowlist configuration for embedding/OCR settings.
- No live model gateway dependency.

