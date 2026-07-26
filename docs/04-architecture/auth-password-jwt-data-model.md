# Data Model: Password Authentication and JWT Authorization

## Overview

This slice adds the durable local identity record required by authentication and future ownership checks. It intentionally does not add knowledge, session-history, provider, or audit entities.

## Entity Relationship Summary

```text
┌──────────────────────────────┐
│ User                         │
│ user_id (PK)                 │
│ identifier (unique)          │
│ role · status                │
│ password_hash                │
│ external_subject (nullable)  │
│ auth_version (mandatory)     │
└──────────────────────────────┘
```

There is no persisted Session entity in this slice. Access JWTs are short-lived and validated against the current User row, including mandatory `auth_version` comparison. Future session history is a separate product concept and must not be conflated with authentication tokens.

## Entity Definition: User

| Field | Logical type | Nullable | Constraints / purpose |
|---|---|---:|---|
| `user_id` | UUID | No | Primary key; internal ownership identifier. `[DEFAULT]` |
| `identifier` | String | No | Normalized, unique login identifier; length 3–64; pattern `[a-z0-9._@-]+`. |
| `display_name` | String | No | Safe human-readable name. |
| `role` | Enum | No | Exactly one of `Admin`, `Editor`, or `Viewer`. |
| `status` | Enum | No | `active` or `deactivated`; default `active` for Admin-created users. |
| `password_hash` | String | No for local accounts | Argon2id encoded hash only; never serialized to API responses. |
| `external_subject` | String | Yes | Reserved for future SSO mapping; unique when present. |
| `auth_version` | Integer | No | Starts at 0; incremented on deactivation; mandatory token claim check. |
| `created_at` | Timestamp UTC | No | Creation time. |
| `updated_at` | Timestamp UTC | No | Last mutation time. |
| `deactivated_at` | Timestamp UTC | Yes | Set when deactivated; cleared on reactivation. |

## Constraints and Indexes

- Primary key on `user_id`.
- Unique constraint on normalized `identifier`.
- Unique partial constraint on non-null `external_subject`.
- Index on `status` for active-user checks if query plans require it; the primary protected-request lookup is by `user_id`.
- Enum values are explicit and case-sensitive at the API boundary.
- Password hash column is never returned by repository-to-API mapping.
- Application rule: reject mutations that would leave zero active Admin accounts.

## State Models

```text
active ────────────────► deactivated
  ▲                         │
  └─────────────────────────┘
       Admin reactivation
```

| Transition | Trigger | Required effect |
|---|---|---|
| `active → deactivated` | Admin status update | Set status/time, increment `auth_version`, reject login and protected requests. Rejected if this is the last active Admin. |
| `deactivated → active` | Admin status update | Clear deactivation time; account may log in again. Existing pre-change tokens remain invalid because `auth_version` already advanced. |

Role changes do not transition account status. They update the current role atomically and are observed on the next authorization check. Demoting the last active Admin to a non-Admin role is rejected.

## Configuration Data

Authentication configuration is runtime-only, not persisted in this slice:

| Key | Purpose | Safety rule |
|---|---|---|
| JWT signing key | Sign/verify access tokens | Required outside local development; never committed or logged. |
| JWT algorithm | Select signer implementation | `[DEFAULT]` HS256 for pilot; must be explicit. |
| Access token lifetime | Bound token validity | `[DEFAULT]` 30 minutes. |
| Password policy | Validate new passwords | `[DEFAULT]` minimum 12 characters. |
| Bootstrap Admin env vars | First Admin creation | Used only when zero Admins exist; never commit defaults. |

## API Projection Rules

The public `UserSummary` projection contains exactly:

- `user_id`
- `identifier`
- `display_name`
- `role`
- `status`
- `created_at`
- `updated_at`

It must not contain `password_hash`, `external_subject`, JWT values, `auth_version`, or secret configuration.

Login, `/auth/me`, create, update, and list item responses all use this same `UserSummary` shape.

## Migration Boundary

- Add the User table and constraints through Alembic.
- Verify upgrade from the P0 vector-only baseline (`20260726_0001`) and safe reapplication.
- Do not create `documents`, `chunks`, `sessions`, `messages`, `citations`, `providers`, or `audit` tables.
- Record the migration revision in the auth traceability document once implementation exists.

## Open Questions

- Confirm ADR-0006 acceptance for UUID IDs, Argon2id, HS256, bootstrap env vars, and last-Admin protection.
- Confirm whether `external_subject` should later become Admin-visible; the phase-one default remains hidden from normal projections.
