# Quarry KB Authentication API Implementation Guide

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Status | Draft; requires owner/security acceptance of ADR-0006 / OQ-AUTH defaults |
| Base path | `/api/v1` |
| Backend | FastAPI + PostgreSQL + Alembic |
| Auth model | Public login plus bearer JWT for active-user/business routes |
| Existing exception | `/health/live` and `/health/ready` remain infrastructure-only probes per ADR-0005 |

## Overview

This guide defines the HTTP contract for local password login, current-user resolution, and Admin account management. It preserves the P0 response envelope and never exposes password hashes, JWT secrets, provider credentials, `external_subject`, `auth_version`, or raw bearer tokens.

## Authentication

### Public and protected routes

| Route group | Authentication |
|---|---|
| `POST /auth/login` | Public credentials endpoint. |
| `GET /health/live`, `GET /health/ready` | Explicit infrastructure exception from ADR-0005. |
| `GET /auth/me` | Valid active bearer JWT with matching `auth_version`. |
| `/admin/users*` | Valid active bearer JWT with current role `Admin`. |
| Future business routes | Valid active bearer JWT plus route-specific current role. |

### Bearer header

```text
Authorization: Bearer <access_token>
```

The server must not echo or log the header value.

### Proposed token claims

| Claim | Required | Purpose |
|---|---:|---|
| `sub` | Yes | Internal `user_id`. |
| `iat` | Yes | Issue time. |
| `exp` | Yes | Expiry time. |
| `auth_version` | Yes | Mandatory invalidation claim; must match current User row. |
| `role` | No | Display convenience only; never authorization source of truth. |

Proposed defaults (ADR-0006): 30-minute expiry, HS256 with runtime environment secret `JWT_SIGNING_KEY`, UTC `iat`/`exp` claims, and no refresh token. Pending owner/security acceptance.

## Shared `UserSummary`

All user projections use the same allowlisted shape:

```json
{
  "user_id": "<uuid>",
  "identifier": "alice",
  "display_name": "Alice",
  "role": "Viewer",
  "status": "active",
  "created_at": "2026-07-26T10:00:00Z",
  "updated_at": "2026-07-26T10:00:00Z"
}
```

Never include `password_hash`, `external_subject`, `auth_version`, JWT values, or secret settings.

The `<uuid>` values in examples reflect the current proposed internal-ID shape only; the identifier type remains a TASK-AUTH-001 decision and is not an approval.

## Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials."
  },
  "meta": null
}
```

| Code | Status | Safe message intent |
|---|---:|---|
| `AUTHENTICATION_FAILED` | 401 | Do not distinguish unknown, wrong, or inactive credentials at login. |
| `TOKEN_INVALID` | 401 | Token is missing, malformed, expired, unverifiable, or subject unknown. |
| `ACCOUNT_INACTIVE` | 401 | Current account is deactivated or token `auth_version` mismatches. |
| `FORBIDDEN` | 403 | Current role cannot perform the operation. |
| `ACCOUNT_CONFLICT` | 409 | Normalized identifier already exists. |
| `LAST_ADMIN_REQUIRED` | 409 | Operation would deactivate or demote the last active Admin. |
| `VALIDATION_ERROR` | 422 | Request field validation failed. |
| `USER_NOT_FOUND` | 404 | Admin target does not exist. |

FastAPI request-validation failures and authentication-dependency failures must be normalized into this same P0 envelope. Unexpected server/dependency failures use a safe 5xx envelope; the stable 5xx code and operator-facing message must be pinned before implementation and must not expose raw exception details.

## API Endpoints Summary

| Operation | Method | Endpoint | Auth | Success |
|---|---|---|---|---:|
| Login | POST | `/auth/login` | Public | 200 |
| Current user | GET | `/auth/me` | Active user | 200 |
| List users | GET | `/admin/users` | Admin | 200 |
| Create user | POST | `/admin/users` | Admin | 201 |
| Update user | PATCH | `/admin/users/{user_id}` | Admin | 200 |

## Endpoint Reference

### Login

**`POST /api/v1/auth/login`**

Request:

```json
{
  "identifier": "alice",
  "password": "<write-only input>"
}
```

Success response, HTTP 200:

```json
{
  "success": true,
  "data": {
    "access_token": "<opaque JWT>",
    "token_type": "bearer",
    "expires_at": "2026-07-26T12:30:00Z",
    "user": {
      "user_id": "<uuid>",
      "identifier": "alice",
      "display_name": "Alice",
      "role": "Viewer",
      "status": "active",
      "created_at": "2026-07-26T10:00:00Z",
      "updated_at": "2026-07-26T10:00:00Z"
    }
  },
  "error": null,
  "meta": null
}
```

Validation/error cases:

- `422 VALIDATION_ERROR` for missing/empty request fields or identifier rule failures.
- For structurally valid non-empty credentials, unknown identifier, wrong password, and inactive account all return `401 AUTHENTICATION_FAILED` with the same safe category. Whether login should separately reject policy-invalid password values remains OQ-AUTH-001; new-account/bootstrap policy validation is distinct.
- Never return password hash, raw password, `auth_version`, or token diagnostics.

### Current user

**`GET /api/v1/auth/me`**

Request header: bearer token.

Success `data`: `UserSummary`.

Errors:

- `401 TOKEN_INVALID` for missing/malformed/expired/unverifiable/unknown-subject tokens.
- `401 ACCOUNT_INACTIVE` for deactivated accounts or `auth_version` mismatch.

### List users

**`GET /api/v1/admin/users`**

Auth: current role `Admin`.

Success `data`:

```json
{
  "items": [
    {
      "user_id": "<uuid>",
      "identifier": "alice",
      "display_name": "Alice",
      "role": "Viewer",
      "status": "active",
      "created_at": "2026-07-26T10:00:00Z",
      "updated_at": "2026-07-26T10:00:00Z"
    }
  ]
}
```

Bounded list only: maximum 200 items. No pagination query parameters in this slice.

The response must not include password hash, `external_subject`, `auth_version`, JWT, or secret settings.

### Create user

**`POST /api/v1/admin/users`**

Request:

```json
{
  "identifier": "alice",
  "display_name": "Alice",
  "password": "<write-only input>",
  "role": "Viewer"
}
```

Success: HTTP 201 with `UserSummary` in `data`; no credential is returned.

Errors: `401`, `403`, `409 ACCOUNT_CONFLICT`, or `422 VALIDATION_ERROR`.

### Update user

**`PATCH /api/v1/admin/users/{user_id}`**

Request:

```json
{
  "display_name": "Alice Chen",
  "role": "Editor",
  "status": "active"
}
```

At least one mutable field is required. Password change is intentionally not supported by this endpoint.

Success: HTTP 200 with `UserSummary`.

Errors: `401`, `403`, `404 USER_NOT_FOUND`, `409 LAST_ADMIN_REQUIRED`, or `422 VALIDATION_ERROR`.

Deactivation must increment `auth_version` and cause existing tokens to fail on their next protected request. Reactivation must not restore pre-deactivation tokens.

## State Reference

```text
active ── Admin deactivate ──► deactivated
active ◄─ Admin reactivate ─── deactivated
role: Admin | Editor | Viewer (one current value)
constraint: at least one active Admin must remain
```

## Bootstrap Contract

Runtime env vars (never committed with real secrets):

| Variable | Required | Purpose |
|---|---|---|
| `AUTH_BOOTSTRAP_ADMIN_IDENTIFIER` | Yes when bootstrapping | First Admin identifier |
| `AUTH_BOOTSTRAP_ADMIN_PASSWORD` | Yes when bootstrapping | First Admin password |
| `AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` | No | Display name; default derived from identifier |

Bootstrap runs only when zero Admin accounts exist and creates exactly one active Admin.

The zero-Admin check and create must be serialized transactionally. Concurrent starts have one winner; losing and repeated starts observe an existing Admin and ignore the bootstrap variables. If required bootstrap variables are missing or invalid, the recommended default is to create no Admin and fail closed; this behavior remains pending OQ-AUTH-002 confirmation.

## Concurrency

- User updates are transactional.
- Bootstrap and last-Admin checks are serialized with their mutations so concurrent starts cannot create duplicate Admins and concurrent Admin updates cannot leave zero active Admins.
- Duplicate identifiers are handled as a stable `409` conflict.
- Concurrent Admin edits rely on transaction serialization for the pilot; no client precondition header is required in this slice.
- Authorization reads current role/status/`auth_version` after the token is validated.

## Integration Dependencies

- PostgreSQL user table and Alembic migration from `20260726_0001`.
- Runtime `JWT_SIGNING_KEY` and HS256 algorithm settings.
- Argon2id password hashing adapter.
- P0 envelope and redaction behavior.
- Proposed ADR-0006 pilot auth security defaults.
