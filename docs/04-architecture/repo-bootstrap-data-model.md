# Data Model: Repository Bootstrap

## Overview

The `repo-bootstrap` slice establishes the database and migration boundary but intentionally creates no business entities. This prevents later user, document, chunk, session, message, citation, and audit schemas from being invented before their own SDD slices.

## Entity Relationship Diagram

```text
┌──────────────────────────────┐
│ Migration Metadata            │
│ tool-owned revision state     │
└──────────────────────────────┘

No application business entities or relationships are owned by repo-bootstrap.
```

## Entity Definitions

### Migration Metadata

- **Logical table:** Tool-owned migration metadata.
- **Purpose:** Records the applied migration revision so startup and readiness can distinguish a fresh, current, or incomplete database.
- **Logical attributes:**
  - `revision_identifier`: non-empty migration revision value.
  - `applied_state`: current applied/revision state reported by the migration tool.
- **Ownership:** Migration tooling, not application business logic.
- **Application contract:** The API may read migration readiness but must not edit migration metadata directly.

The physical table name and vendor-specific columns are intentionally left to the selected migration tool and its approved version. No business entity is inferred from this operational state.

## State Models

### Migration Readiness

```text
MISSING ── baseline migration ──► CURRENT
   │                                 │
   └──────── validation failure ◄────┘
                    │
                    ▼
                 BLOCKED
```

| State | Meaning | Allowed transition |
|---|---|---|
| `MISSING` | Fresh database has no foundation revision | `CURRENT` after baseline migration; `BLOCKED` on failure. |
| `CURRENT` | Required foundation revision is applied | `BLOCKED` if capability/readiness validation fails. |
| `BLOCKED` | Migration or required capability is unavailable | `CURRENT` after corrective migration/configuration. |

## Configuration Entities

Configuration is environment-owned rather than persisted as application data in this slice.

| Configuration group | Logical values | Constraint |
|---|---|---|
| Runtime | Environment, ports, log level | No secret values in Git. |
| Database | Connection URL, migration target | Must resolve to the configured local database. |
| Storage | Upload root placeholder | Must be outside the Git corpus boundary. |
| Chat | Internal base URL/model and secret placeholder | Provider-neutral; public chat setup is later Admin scope. |
| Embedding | Base URL, model, dimension, secret placeholder | Internal/gateway allowlist only. |
| OCR | Base URL, model/path, timeout, secret placeholder | Internal/gateway allowlist only. |

## Audit Entities

None. Business audit records belong to `audit-minimal` and the slices that emit auditable actions.

## Field Mapping

| Source | Destination | Transformation |
|---|---|---|
| Environment variable | Validated runtime setting | Parse, validate, and redact on diagnostics. |
| Database migration output | Migration readiness | Normalize into `current`, `missing`, or `blocked`. |
| API readiness result | Frontend typed state | Normalize into `ready`, `degraded`, or `error`. |

