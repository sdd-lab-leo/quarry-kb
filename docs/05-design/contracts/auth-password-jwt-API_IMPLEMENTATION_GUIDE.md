# Quarry KB Authentication API Implementation Guide

| Field | Value |
|---|---|
| Slice | `auth-password-jwt` |
| Status | Draft; requires owner/security confirmation of listed defaults |
| Base path | `/api/v1` |
| Backend | FastAPI + PostgreSQL + Alembic |
| Auth model | Public login plus bearer JWT for active-user/business routes |
| Existing exception | `/health/live` and `/health/ready` remain infrastructure-only probes per ADR-0005 |

## Overview

This guide defines the HTTP contract for local password login, current-user resolution, and Admin account management. It preserves the P0 response envelope and never exposes password hashes, JWT secrets, provider credentials, or raw bearer tokens.

## Authentication

### Public and protected routes

| Route group | Authentication |
|---|---|
| `POST /auth/login` | Public credentials endpoint. |
| `GET /health/live`, `GET /health/ready` | Explicit infrastructure exception from ADR-0005. |
| `GET /auth/me` | Valid active bearer JWT. |
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
| `auth_version` | Yes | Reject tokens invalidated by account status changes. |
| `role` | No | Display convenience only; never authorization source of truth. |

Proposed defaults: 30-minute expiry, HS256 runtime secret, no refresh token. These are pending confirmation.

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
| `TOKEN_INVALID` | 401 | Token is missing, malformed, expired, or unverifiable. |
| `ACCOUNT_INACTIVE` | 401 | Current account cannot use the token. |
| `FORBIDDEN` | 403 | Current role cannot perform the operation. |
| `ACCOUNT_CONFLICT` | 409 | Normalized identifier already exists. |
| `VALIDATION_ERROR` | 422 | Request field validation failed. |
| `USER_NOT_FOUND` | 404 | Admin target does not exist. |

## API Endpoints Summary

| Operation | Method | Endpoint | Auth |
|---|---|---|---|
| Login | POST | `/auth/login` | Public |
| Current user | GET | `/auth/me` | Active user |
| List users | GET | `/admin/users` | Admin |
| Create user | POST | `/admin/users` | Admin |
| Update user | PATCH | `/admin/users/{user_id}` | Admin |

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
      "status": "active"
    }
  },
  "error": null,
  "meta": null
}
```

Validation/error cases:

- `422 VALIDATION_ERROR` for missing/empty fields or failed password policy input.
- `401 AUTHENTICATION_FAILED` for unknown, wrong, or inactive credentials.
- Never return password hash, raw password, or token diagnostics.

### Current user

**`GET /api/v1/auth/me`**

Request header: bearer token.

Success `data`:

```json
{
  "user_id": "<uuid>",
  "identifier": "alice",
  "display_name": "Alice",
  "role": "Viewer",
  "status": "active"
}
```

Errors: `401 TOKEN_INVALID` or `401 ACCOUNT_INACTIVE`.

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

The response must not include password hash, `external_subject`, auth version, JWT, or secret settings.

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

Success: HTTP 201 with the safe user projection; no credential is returned.

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

Success: HTTP 200 with safe user projection.

Errors: `401`, `403`, `404 USER_NOT_FOUND`, or `422 VALIDATION_ERROR`.

Deactivation must increment auth version and cause existing tokens to fail on their next protected request.

## State Reference

```text
active ── Admin deactivate ──► deactivated
active ◄─ Admin reactivate ─── deactivated
role: Admin | Editor | Viewer (one current value)
```

## Concurrency

- User updates are transactional.
- Duplicate identifiers are handled as a stable `409` conflict.
- If optimistic versioning is needed for concurrent Admin edits, use the user `updated_at`/version precondition rather than silently overwriting; the initial pilot may serialize by transaction.
- Authorization reads current role/status after the token is validated.

## Integration Dependencies

- PostgreSQL user table and Alembic migration from `20260726_0001`.
- Runtime JWT key and algorithm settings.
- Maintained password hashing adapter.
- P0 envelope and redaction behavior.
