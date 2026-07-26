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
        ├── validate embedding/OCR host allowlist
        └── redact secrets from diagnostics
        ▼
Validated runtime state
```

| Input | Validation | Output | Data-safety rule |
|---|---|---|---|
| Runtime environment | Required names and parseable values | Runtime settings | No secret value is returned in diagnostics. |
| Database URL | Parseable connection target | Database settings | Credentials are runtime-only. |
| Embedding/OCR URL | Intranet/gateway allowlist match | Approved integration target | Public target is rejected before request. |
| Chat URL | Provider-neutral placeholder/config | Chat target metadata | Public chat is permitted only through later explicit provider configuration. |

## Flow 2: Database Readiness

```text
API readiness request
        │
        ▼
Database connection check
        │
        ├── connection unavailable → database not-ready
        │
        ▼
Migration state check
        │
        ├── baseline missing → migration not-ready
        │
        ▼
Vector capability check
        │
        ├── unavailable → capability not-ready
        │
        ▼
Safe readiness response
```

The readiness path exchanges only connection and capability status with PostgreSQL. It does not send prompts, document text, page images, or model requests.

## Flow 3: Frontend Health Display

```text
Browser
  │
  │ GET /api/v1/health/ready
  ▼
Typed frontend API client
  │
  ├── success → normalized ready state
  └── failure → normalized safe error state
  ▼
Vue shell status panel
```

| API result | Frontend state | User-visible behavior |
|---|---|---|
| HTTP success + ready | `ready` | Show foundation ready. |
| HTTP success + not-ready | `degraded` | Show which local dependency needs attention without secrets. |
| HTTP failure | `error` | Show retry/actionable failure state. |

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
| Migration state | Migration tool | Missing → baseline applied | Database-owned; later slices add revisions. |
| Health result | API probe | Not-ready → ready or failure | Ephemeral operational response. |

## Edge-Case Trace

| Rule | Edge case | Expected result |
|---|---|---|
| Embedding/OCR allowlist | URL is empty | Configuration invalid; no request. |
| Embedding/OCR allowlist | URL is a public HTTPS host | Configuration invalid; no public fallback. |
| Embedding/OCR allowlist | URL is an approved intranet host with a path | Configuration valid; live call remains deferred. |
| Readiness does not call gateway | Gateway is down but database is ready | Readiness can still report local readiness; it does not claim gateway health. |
| Readiness depends on database | API is alive but database is down | Liveness succeeds; readiness fails. |

