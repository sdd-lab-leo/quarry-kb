# User Stories: Password Authentication and JWT Authorization

## Actors

- **Admin** — manages accounts and roles and can use all authenticated product capabilities.
- **Editor** — authenticated user who will later manage knowledge content; this slice grants no upload capability yet.
- **Viewer** — authenticated read/query user; this slice grants no knowledge capability yet.
- **Unauthenticated visitor** — can access login and infrastructure health only.
- **Future SSO provider** — not integrated in this slice; represented only by the reserved `external_subject` field.

## Story US-AUTH-001: Log In To A Quarry KB Session

As an active Quarry KB user, I want to log in with my account identifier and password, so that I can receive an authenticated session for later product capabilities.

### Acceptance Criteria

1. **Given** an active account and correct password
   **When** the user submits the login form
   **Then** the API returns a bearer access token and safe current-user identity data.
2. **Given** an unknown identifier, wrong password, or deactivated account
   **When** the user submits credentials
   **Then** the API returns the same safe authentication failure category without revealing which condition occurred.
3. **Given** a successful login
   **When** the frontend stores the session
   **Then** it can restore the current user and role on page reload without logging the token.

### Notes / Assumptions

- The proposed default is a short-lived JWT access token with no refresh-token endpoint in this slice.
- Token claims do not become the authorization source of truth; current account status and role are resolved server-side.

### Dependencies

- `repo-bootstrap` API envelope and PostgreSQL/Alembic foundation.
- Password hashing and JWT signing configuration supplied at runtime.

### Out of Scope

- SSO, MFA, password reset, registration, email, and refresh tokens.

### Open Questions

- Confirm ADR-0006 / OQ-AUTH defaults for token lifetime, password policy, first-Admin bootstrap, and browser token storage.

## Story US-AUTH-002: Manage Accounts And Roles

As an Admin, I want to create, list, activate, deactivate, and assign roles to accounts, so that I can control who can use the knowledge workbench.

### Acceptance Criteria

1. **Given** an authenticated Admin
   **When** the Admin creates an account with a unique identifier, display name, password, and one valid role
   **Then** the account is created with an active status and no secret is returned.
2. **Given** an authenticated Admin
   **When** the Admin lists users
   **Then** the response includes safe identity, role, status, and timestamps but never password hashes or credentials.
3. **Given** an active account
   **When** an Admin changes its role or status
   **Then** the new value is used by the next authorization check.
4. **Given** a duplicate identifier or invalid role
   **When** an Admin submits the account operation
   **Then** the API rejects it with a typed validation/conflict error and leaves existing account data unchanged.
5. **Given** only one active Admin remains
   **When** an Admin attempts to deactivate or demote that Admin
   **Then** the API rejects the change and the last Admin remains active with role `Admin`.
6. **Given** zero Admin accounts exist and valid bootstrap env vars are configured
   **When** the application starts
   **Then** exactly one active Admin is created and later startups do not recreate bootstrap Admins.

### Notes / Assumptions

- Exactly one role is stored per account: `Admin`, `Editor`, or `Viewer`.
- Audit records are deferred to `audit-minimal`; this story does not imply an audit table.
- Admin-supplied initial password is used for ordinary account creation; bootstrap uses runtime env vars only for the first Admin.

### Dependencies

- `US-AUTH-001` authentication and Admin authorization.
- User migration and repository transaction boundary.

### Out of Scope

- Self-service registration, bulk import, SSO provisioning, and audit list.

### Open Questions

- Confirm ADR-0006 / OQ-AUTH-002 bootstrap env contract before implementation.

## Story US-AUTH-003: Enforce Current Server-Side Authorization

As a product owner, I want every business API request authorized against the current user record, so that hidden frontend controls cannot bypass role restrictions and deactivation takes effect immediately.

### Acceptance Criteria

1. **Given** a request to a future business endpoint without a valid token
   **When** the request reaches the API
   **Then** the API rejects it before business logic runs.
2. **Given** a valid token for a deactivated account
   **When** the account makes a protected request
   **Then** the API rejects the request even if the JWT has not expired.
3. **Given** an active user whose role changed
   **When** the user makes the next protected request
   **Then** authorization uses the new role rather than a stale token role claim.
4. **Given** a Viewer or Editor calling an Admin-only route
   **When** the API evaluates authorization
   **Then** it returns a safe forbidden response without leaking account data.

### Notes / Assumptions

- Health probes remain the explicit infrastructure exception defined by ADR-0005.
- Authorization uses internal `user_id` and current role; it does not scatter raw external identity subjects through business logic.

### Dependencies

- `US-AUTH-001` token validation.
- All future business routers must opt into the shared authorization dependency.

### Out of Scope

- Implementing future knowledge, Ask, provider, or audit routes.

### Open Questions

- None beyond the shared authentication defaults listed in the requirements document.

## Story US-AUTH-004: Preserve A Future SSO Identity Link

As an architect, I want the local user record to reserve an external identity subject, so that a later company SSO integration can map identities without redesigning ownership and authorization.

### Acceptance Criteria

1. **Given** a local password account
   **When** the account is persisted
   **Then** its external identity subject may remain null.
2. **Given** a future identity mapping value
   **When** it is stored
   **Then** it is separate from the local account identifier and does not replace internal `user_id` ownership.
3. **Given** this slice running without an SSO provider
   **When** the application starts
   **Then** no external identity network call is required.

### Notes / Assumptions

- The field is reserved for phase two and is not exposed as an editable Admin field in this slice.

### Dependencies

- ADR-0002 and the user data model.

### Out of Scope

- OIDC/SAML discovery, callback routes, account linking UI, and SSO provisioning.

### Open Questions

- The future SSO provider and subject format are intentionally not selected in this slice.
