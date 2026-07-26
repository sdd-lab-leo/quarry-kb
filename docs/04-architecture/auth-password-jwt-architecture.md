# System Architecture: Password Authentication and JWT Authorization

## Overview

- **Architecture Summary:** A modular FastAPI authentication boundary backed by PostgreSQL user records, a pluggable password provider, and a runtime-configured JWT signer. Vue consumes typed authentication APIs and provides usability guards, while the API remains the authorization boundary.
- **Design Objective:** Establish one internal identity and role model that later knowledge, Ask, provider, and audit slices can reuse.
- **Architectural Style:** Layered modular monolith with API, application services, repositories, and adapters.

## Source Specification

- **Feature:** `auth-password-jwt`
- **Scope:** Login, JWT access sessions, current-user resolution, Admin account lifecycle, three roles, and future-SSO identity reservation.
- **Upstream:** `docs/03-spec/auth-password-jwt-spec.md`, ADR-0002, ADR-0005, and the verified `repo-bootstrap` chain.

## Architectural Drivers

### Functional Drivers

- Active users must log in with local credentials.
- Admins must manage account lifecycle and roles.
- Deactivation must affect unexpired tokens on the next protected request.
- Current role, not stale token content, controls authorization.
- Future SSO must map to the same internal user ownership model.

### Non-Functional Drivers

- Passwords, tokens, hashes, and authorization headers must not leak.
- Tests must run without SSO, paid services, or external model calls.
- All persistent changes use Alembic.
- Health probes preserve the explicit infrastructure exception from ADR-0005.

### Constraints and Assumptions

- FastAPI + Vue 3 + PostgreSQL/pgvector + Docker Compose remain fixed by ADR-0002.
- `[DEFAULT]` The pilot uses a short-lived bearer JWT and current-user database lookup for protected requests.
- `[DEFAULT]` The pilot uses HS256 runtime secret material unless a security review approves asymmetric keys.
- Audit persistence is a separate slice; this slice does not create audit tables.

## System Context

### Primary Actors

| Actor | Role |
|---|---|
| Admin | Provisions and manages local accounts. |
| Editor | Authenticated role reserved for future content operations. |
| Viewer | Authenticated role reserved for future read/query operations. |
| Unauthenticated visitor | Can log in and access health probes only. |

### External Systems

| System | Integration purpose |
|---|---|
| PostgreSQL | Durable user identity and role/status state. |
| Browser | Stores the approved client session state and calls the API. |
| Company SSO | Future mapping only; no integration in this slice. |

### System Boundary

The slice owns local account identity, password verification, JWT issuance/validation, role/status authorization, and Admin account operations. It does not own knowledge content, model providers, retrieval, or audit history. The API is the security boundary; the frontend cannot grant access.

## High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│ Users                                                        │
│ Admin · Editor · Viewer · Unauthenticated visitor            │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTPS / JSON
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ Vue Authentication Surface                                   │
│ Login · session bootstrap · role-aware navigation             │
└─────────────────────────┬────────────────────────────────────┘
                          │ REST / bearer token
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ FastAPI Authentication Boundary                              │
│ login · current user · Admin user operations · auth errors    │
└───────────────┬───────────────────────┬──────────────────────┘
                │                       │
                ▼                       ▼
┌──────────────────────────┐  ┌───────────────────────────────┐
│ Identity Services         │  │ Auth Adapters                 │
│ password verification     │  │ password hash · JWT signer    │
│ role/status authorization │  │ runtime key/config boundary   │
└──────────────┬───────────┘  └───────────────────────────────┘
               │ repository protocol
               ▼
┌──────────────────────────────────────────────────────────────┐
│ PostgreSQL User Store                                        │
│ users: identity · role · status · external_subject · times   │
└──────────────────────────────────────────────────────────────┘
```

## Layer Summary

- **Presentation:** Login/session and Admin account views; no security decisions.
- **API boundary:** Parses requests, applies authentication dependencies, maps errors, and exposes safe response shapes.
- **Application services:** Orchestrate login, current-user resolution, account lifecycle, and role checks.
- **Repository:** Owns user queries and transactional mutations; never hashes passwords or calls JWT libraries.
- **Adapters:** Isolate password hashing and JWT signing/verification so identity providers can evolve.
- **Persistence:** PostgreSQL stores the durable local identity record; no server session table is required for the proposed JWT model.

## Component Breakdown

### Frontend Components

- **Login surface:** Collects identifier/password and displays generic failures.
- **Session state:** Holds the current token/user state and clears it on logout or `401`.
- **Route/permission guard:** Redirects or hides unavailable screens for usability; never substitutes for API authorization.
- **Admin account surface:** Lists users and submits lifecycle/role changes only for Admin users.

### Backend Services

- **Authentication service:** Loads an account, verifies the password hash, checks active status, and issues a token.
- **Current-user service:** Resolves token subject to an active internal user and current role.
- **Account administration service:** Creates, lists, activates, deactivates, and changes role atomically.
- **Authorization dependency:** Requires a valid active account and optionally a current role.

### Integration Adapters

- **Password adapter:** Hashes and verifies passwords using a replaceable library boundary.
- **JWT adapter:** Signs and verifies access tokens using runtime key material and an explicitly configured algorithm.
- **Future identity adapter:** Reserved for a later SSO slice; not instantiated here.

## Data Architecture

### Conceptual Entity

| Entity | Description | Key attributes |
|---|---|---|
| User | Local identity and authorization owner | Internal ID, normalized identifier, display name, role, status, password hash, external subject, auth version, timestamps |

### State / Status Model

- `active → deactivated` — Admin action; protected requests fail immediately.
- `deactivated → active` — Admin action; login becomes possible again, subject to the approved session invalidation policy.
- Role is not a lifecycle state; it is a single current value used on every authorization check.

### Persistence Responsibilities

- PostgreSQL is authoritative for account status and current role.
- User mutations are transactional and unique-identifier constrained.
- No password, JWT, provider key, document, or audit payload is persisted by this slice.

## Integration Architecture

### PostgreSQL

- **Interaction pattern:** Repository queries and transactional writes through the application service boundary.
- **Data exchanged:** User identity, status, role, password hash, external subject, auth version, timestamps.
- **Failure behavior:** Authentication fails closed; protected requests return a safe dependency/authentication error without exposing database details.

### Browser

- **Interaction pattern:** REST/JSON with bearer authorization after login.
- **Data exchanged:** Credentials only to login; safe user profile and token response; never password hash or provider credentials.
- **Failure behavior:** `401` clears the session; `403` shows an authorization state without retrying credentials blindly.

### Future SSO

- **Interaction pattern:** Deferred.
- **Boundary:** A future adapter maps an external subject to internal `user_id`; domain authorization remains internal-role based.

## Workflow / Runtime Architecture

### Request Flow

1. Login reaches the public authentication operation.
2. The authentication service verifies credentials through the password adapter.
3. The JWT adapter issues a short-lived access token.
4. A protected request passes through token validation and current-user resolution.
5. The authorization dependency checks the current role before the target use case.

### Account Flow

1. Admin request is authenticated and authorized.
2. Input is normalized and validated.
3. Repository transaction creates or updates the user.
4. The next protected request reads the committed current status/role.

### Failure and Retry Handling

- Do not retry invalid credentials.
- A transient database failure fails closed with a safe server/dependency response.
- A malformed or expired token returns `401` and the frontend discards it.
- A valid token for a deactivated account returns `401`; no silent re-login occurs.
- Role denial returns `403`; the frontend must not treat it as an authentication failure.

## API / Interface Boundaries

### Major Inbound Interfaces

| Interface | Consumer | Purpose |
|---|---|---|
| `POST /api/v1/auth/login` | Browser | Issue a token for valid active credentials. |
| `GET /api/v1/auth/me` | Browser and future APIs | Resolve current safe user identity. |
| `GET /api/v1/admin/users` | Admin browser | List safe user records. |
| `POST /api/v1/admin/users` | Admin browser | Create an account. |
| `PATCH /api/v1/admin/users/{user_id}` | Admin browser | Change role/status/display name under the approved contract. |
| `/api/v1/health/*` | Infrastructure | Explicit P0 health exception; no business authorization. |

### Internal Module Boundaries

- API depends on application service protocols.
- Services depend on repository and adapter protocols.
- Repositories do not call hash/JWT libraries or external HTTP services.
- Frontend calls typed API functions and does not assemble authorization policy in views.

## Deployment / Environment Considerations

- Secrets and JWT key material are injected through runtime configuration and remain outside Git.
- Compose topology remains `web`, `api`, and `postgres`.
- The existing upload volume is not used by this slice.
- Local tests use fake password/JWT adapters where appropriate; no external identity provider is required.

## Security / Reliability / Observability

- **Access control:** Enforce authentication and role checks in the API layer.
- **Password protection:** Use a current password hashing scheme; never log or return plaintext/hash material.
- **Token protection:** Do not log or render bearer tokens; keep signing keys runtime-only.
- **Deactivation:** Resolve current status on every protected request so deactivation is immediate.
- **Role changes:** Resolve current role on every protected request so changes take effect without token refresh.
- **Logging:** Reuse the P0 redaction boundary and add auth-specific tests for credentials and bearer headers.
- **Audit:** No audit table in this slice; later audit integration must observe account operations without receiving secrets.

## Risks / Tradeoffs

| ID | Risk / Tradeoff | Decision / Mitigation |
|---|---|---|
| R-ARCH-AUTH-001 | Stateless JWT alone cannot revoke a token before expiry. | Current-user status lookup on every protected request; optional auth-version invalidation is part of the design default. |
| R-ARCH-AUTH-002 | HS256 is simpler for a single host but has symmetric-key distribution risk. | Use runtime secret only for the pilot; require an explicit security decision before multi-host rollout. |
| R-ARCH-AUTH-003 | Audit is required by the product but scheduled separately. | Keep audit out of this slice and trace account-operation hooks/boundaries to `audit-minimal`. |

## Related ADRs

- ADR-0002 — technology stack, phase-one password/JWT auth, roles, and future SSO reservation.
- ADR-0005 — health-probe exception and readiness boundary.
- `repo-bootstrap` SDD chain — existing envelope, migration, and frontend baseline.

## Open Questions

- First-Admin bootstrap, password policy, JWT lifetime/algorithm, browser token storage, and identifier normalization remain the OQ-AUTH set.
- Product owner must accept this slice before implementation handoff.
