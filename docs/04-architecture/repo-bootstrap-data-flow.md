# Data Flow: Repository Bootstrap

## Scope

This document describes only bootstrap data movement. It does not define document ingestion, retrieval, chat, or user data flows.

## Flow 1: Startup Configuration

```text
Developer environment
        │
        │ local .env values / placeholders
        ▼
API configuration boundary
        │
        ├── validate required runtime settings
        ├── validate database URL shape
        ├── validate embedding/OCR hosts by literal allowlist match
        └── redact secrets from diagnostics
        ▼
Validated runtime state
```

| Input | Validation | Output | Data-safety rule |
|---|---|---|---|
| Runtime environment | Required names and parseable values | Runtime settings | No secret value is returned in diagnostics. |
| Database URL | Parseable connection target | Database settings | Credentials are runtime-only. |
| Embedding/OCR URL | URL host literally matches allowlist entry (hostname or `host:port`); empty host invalid; no DNS lookup | Approved integration target | Public or unknown host is rejected before request. |
| Allowlist | Non-empty list of approved hosts; default includes placeholder host `gateway.internal` | Host policy | Used only for embedding/OCR validation in this slice. |
| Chat URL | Provider-neutral placeholder/config | Chat target metadata | Public chat is permitted only through later explicit provider configuration. |

## Flow 2: Database Readiness

```text
API readiness request
        │
        ▼
Configuration validation
        │
        ├── invalid → configuration not-ready → HTTP 503
        │
        ▼
Database connection check
        │
        ├── connection unavailable → database not-ready → HTTP 503
        │
        ▼
Migration state check
        │
        ├── baseline missing → migration not-ready → HTTP 503
        │
        ▼
Vector capability check
        │
        ├── `vector` extension unavailable → vector_capability not-ready → HTTP 503
        │
        ▼
HTTP 200 ready response (all components ready)
```

The readiness path exchanges only connection, migration, and capability status with PostgreSQL. It does not send prompts, document text, page images, or model requests.

## Flow 3: Frontend Health Display

```text
Browser
  │
  │ GET /api/v1/health/ready
  ▼
Typed frontend API client
  │
  ├── HTTP 200 + ready → normalized ready state
  ├── HTTP 503 + not-ready → normalized needs_attention state
  └── transport / non-503 failure → normalized unreachable state
  ▼
Vue shell status panel
```

| API result | Frontend state | User-visible behavior |
|---|---|---|
| HTTP 200 + `status=ready` | `ready` | Show foundation ready. |
| HTTP 503 + component diagnostics | `needs_attention` | Show which local dependency needs attention without secrets. |
| Transport failure or unexpected non-503 error | `unreachable` | Show retry / unable-to-reach-API state. |

There is no `HTTP 200 + not-ready` success path. Not-ready is always HTTP 503.

## Flow 4: Future Gateway Boundary

```text
Future business slice
  │
  ├── chat request ───────────────► internal or explicitly enabled public chat provider
  ├── embedding request ──────────► internal gateway only
  └── OCR request ────────────────► internal gateway only
```

Bootstrap records this boundary and validates configuration policy. It does not execute any of the three calls.

## Lifecycle Summary

| Object | Created by | State changes | Retention/ownership |
|---|---|---|---|
| Runtime settings | Deployment environment | Unloaded → validated / invalid | Runtime-owned; not committed. |
| Migration state | Alembic baseline | Missing → baseline applied (`vector` enabled) | Database-owned; later slices add revisions. |
| Health result | API probe | Not-ready (503) → ready (200) or failure | Ephemeral operational response. |

## Edge-Case Trace

| Rule | Edge case | Expected result |
|---|---|---|
| Embedding/OCR allowlist | URL is empty | Configuration invalid; HTTP 503; no request. |
| Embedding/OCR allowlist | URL host is a public HTTPS host | Configuration invalid; HTTP 503; no public fallback; no DNS lookup. |
| Embedding/OCR allowlist | URL host is `gateway.internal` with a path and that host is on the default allowlist | Configuration valid; live call remains deferred. |
| Embedding/OCR allowlist | URL host would DNS-resolve to an intranet IP but is not listed | Configuration invalid; literal match only. |
| Readiness does not call gateway | Gateway is down but database/migration/vector are ready | Readiness can still return HTTP 200; it does not claim gateway health. |
| Readiness depends on database | API is alive but database is down | Liveness succeeds; readiness returns HTTP 503 with `DATABASE_NOT_READY`. |
| Vector capability | Extension missing after migration failure | Readiness returns HTTP 503 with `VECTOR_CAPABILITY_UNAVAILABLE`. |
