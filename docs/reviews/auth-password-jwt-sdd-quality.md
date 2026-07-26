# P2 auth-password-jwt SDD Review Report

## 1. Scope

This review audits the first P2 Identity and Authorization slice, `auth-password-jwt`, in docs-only mode. It covers the existing requirements, user stories, specification, architecture, data flow, data model, design, API guide, tasks, traceability record, and proposed ADR-0006. It also grounds claims against the implemented `repo-bootstrap` source tree and historical P1 archive evidence.

Explicitly excluded: `audit-minimal`, authentication code, database migration code, frontend implementation, dependency or lockfile changes, execution-manifest creation, commit, push, and PR.

The `sdd-slice-bootstrap` Audit mode and `review-doc-quality` review process were applied. Existing documents were preserved and minimally corrected; no full SDD generation was run.

## 2. Overall Verdict

- **Verdict:** PASS WITH FIXES
- **Documentation quality:** Good
- **Implementation readiness:** Pending Decisions
- **Rationale:** The complete SDD chain exists, is substantial, is English-only, and now has aligned role, status, token invalidation, endpoint, health-probe, migration-boundary, and scope contracts. The slice must remain Draft because ADR-0006 and OQ-AUTH-001 through OQ-AUTH-005 are still Proposed/Open. A small number of implementation-impacting details also remain unowned: missing/invalid bootstrap failure behavior, the stable generic 5xx envelope mapping, and the internal `user_id` type.

## 3. Document Inventory

| File | Current status | Complete? | Modified in this audit? | Main issue / note |
|---|---|---:|---:|---|
| `docs/01-requirements/auth-password-jwt-requirement.md` | Draft | Yes | Yes | OQ-AUTH-001 to OQ-AUTH-005 remain open; password/login and bootstrap defaults are now explicit as proposed. |
| `docs/02-user-stories/auth-password-jwt-user-stories.md` | Draft | Yes | Yes | Acceptance covers roles, lifecycle, last-Admin protection, and concurrent bootstrap; missing/invalid bootstrap behavior remains pending. |
| `docs/03-spec/auth-password-jwt-spec.md` | Draft | Yes | Yes | Functional, security, workflow, error, integration, and scope sections are present; 5xx code and internal ID type remain pending. |
| `docs/04-architecture/auth-password-jwt-architecture.md` | Draft | Yes | Yes | Component boundaries and current-role authorization are clear; proposed JWT/bootstrap decisions remain unaccepted. |
| `docs/04-architecture/auth-password-jwt-data-flow.md` | Draft | Yes | Yes | Login, protected request, lifecycle, bootstrap, session, and safety flows are present; bootstrap failure disposition remains pending. |
| `docs/04-architecture/auth-password-jwt-data-model.md` | Draft | Yes | Yes | User model and migration boundary are complete; current slice requires non-null `password_hash`, while `user_id` type is still proposed. |
| `docs/05-design/auth-password-jwt-design.md` | Draft | Yes | Yes | Concrete module/API/UI/error design exists; framework error normalization and UUID type need final pinning. |
| `docs/05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md` | Draft | Mostly | Yes | Endpoint/request/response/status/error contract is coherent; stable unexpected-5xx code/message is not yet selected. |
| `docs/06-tasks/auth-password-jwt-tasks.md` | Draft | Yes | Yes | Tasks are ordered and verifiable; TASK-AUTH-001 now owns the remaining contract decisions. |
| `docs/00-context/auth-password-jwt-traceability.md` | Draft | Yes | Yes | Bidirectional chain and verification mapping exist; this report is now linked as current evidence. |
| `docs/00-context/decisions/ADR-0006-pilot-auth-security-defaults.md` | Proposed | N/A | Yes | Proposed security defaults are concrete but not accepted. Status was intentionally not advanced. |
| `docs/00-context/changes/20260726-repo-bootstrap/archive.md` | Archived historical evidence | N/A | No | Confirms P1 foundation scope and that auth was not implemented; not an active auth handoff. |
| `docs/reviews/auth-password-jwt-sdd-quality.md` | Current audit record | Yes | New | This report; no prior final auth review file existed at audit start. |

## 4. Critical Findings

### C-01 — ADR-0006 and the five auth open questions still block approval

- **Why it matters:** Password policy, bootstrap, JWT lifetime, browser token storage, and identifier normalization affect security posture and implementation behavior. ADR-0006 remains `Proposed`, and OQ-AUTH-001 through OQ-AUTH-005 are not owner/security-confirmed.
- **Affected sections:** All slice status fields; `ADR-0006`; `TASK-AUTH-001`; traceability handoff gate.
- **Required action:** Obtain explicit confirmation or amendment. Do not mark the slice `Approved`, `Accepted`, or `Implementation Ready`, and do not create a new active execution manifest before that confirmation.

No other critical structural or code-grounding finding was found.

## 5. Major Findings

### M-01 — Bootstrap invalid/missing configuration behavior remains a decision

- **Why it matters:** The documents now consistently require a serialized zero-Admin check/create and define repeated/existing-Admin behavior. They recommend creating no Admin and failing closed when required bootstrap variables are missing or invalid, but this is not yet accepted. Without it, first-start failure behavior can diverge across implementations.
- **Affected sections:** OQ-AUTH-002; `auth-password-jwt-data-flow.md` Flow 4; API guide Bootstrap Contract; ADR-0006.
- **Recommended fix:** Accept the proposed fail-closed behavior or record an explicit alternative, including operator-visible safe error behavior.

### M-02 — Login password-policy boundary needs explicit confirmation

- **Why it matters:** The remediation now separates request-shape validation from credential verification and recommends generic `401 AUTHENTICATION_FAILED` for structurally valid login attempts. Whether a policy-invalid login password receives `422` or the generic `401` remains an owner/security decision under OQ-AUTH-001.
- **Affected sections:** Requirements OQ-AUTH-001; spec FR-AUTH-003 and validation rules; API guide Login validation/error cases.
- **Recommended fix:** Confirm the proposed account-creation/bootstrap-only policy enforcement and generic login-failure mapping, or amend all affected documents together.

### M-03 — Generic unexpected 5xx error contract is not fully pinned

- **Why it matters:** The SDD requires auth request-validation and dependency failures to use the P0 envelope and forbids raw exception leakage, but it does not select a stable 5xx `error.code` and safe operator-facing message. The current P1 code only implements the envelope helper and health-specific 503 codes; it does not provide an existing auth error mapping to inherit.
- **Affected sections:** Spec privacy/error contract; design Common envelope and validation/error handling; API guide Error Response Format.
- **Recommended fix:** Select a stable safe 5xx code/message convention before implementation and add it to the API guide, spec, design, tasks, and verification mapping.

### M-04 — Internal `user_id` type is proposed but not owned by an ADR or OQ

- **Why it matters:** The design and examples currently propose UUID identifiers, while the requirement only requires a stable internal identifier and ADR-0006 does not decide the type. The migration, API examples, repository interfaces, and future ownership references need one pinned type.
- **Affected sections:** Data model `user_id`; design assumptions; API examples; TASK-AUTH-001.
- **Recommended fix:** Confirm UUID as the design default in TASK-AUTH-001 or add a small explicit decision record. This audit does not treat the current UUID proposal as approved.

## 6. Minor Findings

### m-01 — Bootstrap display-name derivation is not normalized precisely

`AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME` is optional and is described as derived from the identifier, but the documents do not say whether derivation uses the raw submitted value or the normalized identifier. Recommend deriving from the normalized identifier, or state the chosen rule in the accepted contract.

### m-02 — Identifier length units and Unicode handling are implicit

The trim/lowercase/3–64/`[a-z0-9._@-]+` rule is consistent and has no obvious regex self-collision. The final contract could state that length is measured after normalization and that non-ASCII input is rejected by the allowlist, with edge-case tests.

### m-03 — Authentication performance target remains unspecified

The specification explicitly records that no product latency target exists. This is acceptable for the current draft, but a measurable target should be added before pilot hardening if authentication latency becomes an operational SLO.

## 7. ADR-0006 and Open-Question Decision Table

| Decision | Current status | Proposed default | Recommendation | Required approver / confirmation |
|---|---|---|---|---|
| OQ-AUTH-001: password policy and login handling | Open / Proposed | New account/bootstrap passwords: minimum 12 characters, at least one non-whitespace character, no forced complexity regex, case-sensitive. Structurally valid login mismatches use generic auth failure. | Accept as proposed or amend the login boundary consistently. | Explicit product/security confirmation; no approver identity is named in repository docs. |
| OQ-AUTH-002: first-Admin bootstrap | Open / Proposed | Runtime env vars only; zero-Admin check/create serialized; any existing Admin disables bootstrap; no committed default password; missing/invalid required values create no Admin and recommended fail-closed startup. | Accept the concurrency and failure semantics or amend them explicitly. | Explicit product/security/operations confirmation. |
| OQ-AUTH-003: JWT lifetime | Open / Proposed | 30-minute access JWT; UTC `iat`/`exp`; response `expires_at` mirrors `exp`; no refresh token. | Accept or amend before implementation. | Explicit security/product confirmation. |
| OQ-AUTH-004: browser token storage | Open / Proposed | In-memory token with `sessionStorage` reload fallback; never `localStorage`. | Accept as proposed or amend with XSS/reload tradeoff. | Explicit security/product confirmation. |
| OQ-AUTH-005: identifier normalization | Open / Proposed | Trim + lowercase; normalized length 3–64; `[a-z0-9._@-]+`; display name separate; password case-sensitive. | Accept or amend, including edge cases. | Explicit product/architecture confirmation. |
| ADR-0006: Argon2id, HS256, mandatory `auth_version`, current DB role/status, bootstrap, last-Admin protection | Proposed | As stated in ADR-0006; key env name aligned to `JWT_SIGNING_KEY`. | Accept ADR-0006 or publish a superseding/amended decision. | Explicit owner/security confirmation. |

## 8. Contract Consistency

| Area | Result | Evidence / residual issue |
|---|---|---|
| Role vocabulary | Pass | `Admin`, `Editor`, `Viewer` is used consistently; semantics match backend/frontend standards. |
| Exactly one role | Pass | Requirement, story, spec, data model, API guide, tasks, and verification all state one current role. |
| Status and `auth_version` | Pass with pending approval | Deactivation increments `auth_version`; protected requests compare it and current status; reactivation does not revive old tokens; role changes use current DB role and do not need version increment in this slice. |
| Last-Admin protection | Pass with implementation verification pending | Demotion/deactivation is rejected and the check/mutation must be serialized; no code exists yet. |
| First-Admin bootstrap | Pass with pending decision | Concurrent, repeated, and existing-Admin behavior is now explicit; missing/invalid-env failure disposition remains Proposed. |
| JWT algorithm/key/claims/expiry | Pass with pending approval | Proposed HS256 + `JWT_SIGNING_KEY`, required `sub`/`iat`/`exp`/`auth_version`, UTC expiry, and no refresh token are aligned across the slice; ADR-0006 remains Proposed. |
| Error semantics | Partial | Login/authz codes and statuses are aligned; framework validation is required to use the P0 envelope, but stable generic 5xx code/message is not pinned. |
| Secret/token/password leakage | Pass at document level | Response allowlists and redaction requirements are explicit; code grounding confirms only baseline redaction exists, not auth behavior. |
| Health exception | Pass | Current code registers only health under `/api/v1`; health routes are explicit ADR-0005 infrastructure exceptions. Auth design must use opt-in protected dependencies, not a global guard that blocks probes. |
| Frontend responsibility | Pass as design | Route guards/session state are usability concerns; API authorization remains authoritative. Current frontend has no auth/session implementation. |
| Migration boundary | Pass | Auth migration is required to extend `20260726_0001` and add only the User schema; audit/knowledge tables remain excluded. |

## 9. Traceability Status

- Requirements → stories: complete for `REQ-AUTH-001` through `REQ-AUTH-015`.
- Stories → specification: complete for US-AUTH-001 through US-AUTH-004.
- Specification → architecture/data flow/data model/design/API guide: present and linked in the traceability document.
- Design → tasks: complete for TASK-AUTH-001 through TASK-AUTH-009; TASK-AUTH-001 now owns the remaining contract decisions.
- Requirement/acceptance → verification: present, including redaction, role matrix, deactivation/reactivation, bootstrap, health exception, migration, and frontend checks.
- Review evidence: this current report is linked from `auth-password-jwt-traceability.md`; no archived or active auth execution manifest exists, by request.
- Residual gaps: stable generic 5xx mapping and internal `user_id` type need explicit pinning before implementation.

## 10. Current-Code Grounding

Verified against the current workspace:

- `backend/app/main.py:14-28` creates the FastAPI app and currently includes only the health router under `/api/v1`; auth routers and auth middleware do not exist.
- `backend/app/core/envelope.py:8-24` provides the `success`, `data`, `error`, `meta` envelope helper.
- `backend/app/api/health.py:17-39` implements unauthenticated liveness/readiness behavior, including HTTP 200 ready and HTTP 503 not-ready.
- `backend/app/core/redaction.py:7-29` contains baseline secret-shaped redaction; it is not an auth implementation.
- `frontend/src/api/client.ts:19-52` currently issues GET-only requests and does not attach tokens; auth requires a future intentional extension.
- `frontend/src/App.vue:1-59` currently renders the foundation readiness shell; login, session restore, route guards, and Admin UI do not exist.
- `backend/alembic/versions/20260726_0001_enable_vector.py:14-22` is the current baseline and enables only the `vector` extension; it creates no User or other business table.
- The current source scan found no auth router, User model, password adapter, JWT signer, login route, or auth migration. Existing `password`/`token` matches are limited to baseline redaction/tests and placeholder database configuration.

Therefore, all auth behavior in this SDD is planned behavior, not existing behavior.

## 11. Scope Drift Check

Pass. The slice documents include only password login, access JWT sessions, current-user resolution, roles, Admin account lifecycle, first-Admin bootstrap, frontend session/Admin design, health exception, and the User migration design. Audit persistence/query APIs, upload, OCR execution, embedding, RAG, chat, provider management, SSO, refresh tokens, password recovery, MFA, real secrets/accounts, and implementation code remain excluded or deferred. References to `audit-minimal` are boundary/downstream references only and do not add audit design here.

## 12. Files Changed

- `docs/01-requirements/auth-password-jwt-requirement.md`
- `docs/02-user-stories/auth-password-jwt-user-stories.md`
- `docs/03-spec/auth-password-jwt-spec.md`
- `docs/04-architecture/auth-password-jwt-architecture.md`
- `docs/04-architecture/auth-password-jwt-data-flow.md`
- `docs/04-architecture/auth-password-jwt-data-model.md`
- `docs/05-design/auth-password-jwt-design.md`
- `docs/05-design/contracts/auth-password-jwt-API_IMPLEMENTATION_GUIDE.md`
- `docs/06-tasks/auth-password-jwt-tasks.md`
- `docs/00-context/auth-password-jwt-traceability.md`
- `docs/00-context/decisions/ADR-0006-pilot-auth-security-defaults.md`
- `docs/reviews/auth-password-jwt-sdd-quality.md` (new)

No backend, frontend, migration, dependency, lockfile, manifest, or runtime file was changed.

## 13. Verification Evidence

| Command / check | Result | Evidence or limitation |
|---|---|---|
| `git status --porcelain=v1 -b` at start | Pass | `## codex-leo...origin/codex-leo`; workspace was clean before this audit. |
| `git diff --stat` and `git diff` at start | Pass | No pre-existing diff; no user changes were overwritten. |
| `git branch --show-current` | Pass | `codex-leo`. |
| `git log -8 --oneline --decorate` | Pass | HEAD `ef42d68 fix: close repo-bootstrap P1 gate`; auth generation/remediation commits are `d8463c7` and `08af3ca`. |
| `git diff --check` | Pass | No whitespace errors after the documentation edits. |
| Markdown internal-link check | Pass | Repository Markdown link scan returned `Internal link issues: 0`. |
| Required `rg` terminology/decision scan | Pass | Checked OQ-AUTH-001..005, ADR-0006, status markers, unresolved language, JWT/refresh/storage terms, roles, auth_version, and excluded-scope terms. |
| Current-code grounding scan | Pass | Confirmed the auth capability is absent and P1 only provides foundation health/envelope/redaction/migration behavior. |
| Traceability inspection | Pass with residual gaps | All required chain stages and verification mappings are present; UUID type and stable 5xx mapping remain pending. |
| `pytest`, frontend build, Compose, migration runtime smoke | Not run | This was a docs-only audit; no auth implementation exists and the request explicitly excluded implementation/runtime work. |
| Execution manifest / freshness-gate | Not run | Correctly deferred; user explicitly requested no new active manifest in this session. |

## 14. Remaining Risks / Blockers

- ADR-0006 is still Proposed; OQ-AUTH-001 through OQ-AUTH-005 still require explicit confirmation or amendment.
- Missing/invalid bootstrap configuration behavior must be accepted, not inferred by an implementer.
- A stable generic 5xx envelope code/message must be selected before API implementation.
- The internal `user_id` type must be pinned; the current UUID shape is only proposed.
- No code-level proof exists yet for token invalidation, concurrent bootstrap, last-Admin serialization, redaction, frontend storage, or migration upgrade from `20260726_0001`.
- Overall plan P2 cannot be marked complete until the later independent `audit-minimal` slice is implemented and verified.

## 15. Final Decision

- **Can the documents be approved now?** No. They are suitable for decision review, but ADR-0006 and the open questions are not accepted.
- **Can the slice enter implementation handoff?** No. Do not create an active execution manifest yet.
- **What still needs confirmation?** OQ-AUTH-001 through OQ-AUTH-005, ADR-0006, the stable generic 5xx error mapping, and the internal `user_id` type.
- **What files must be updated after confirmation?** Update ADR-0006; the requirements OQ table; the spec; architecture/data flow/data model; detailed design; API guide; tasks; and traceability/status evidence. Update only the affected decisions if an amendment changes scope or behavior.
- **What is the next step after confirmation?** Run freshness-gate against the accepted docs and current code, then create a new active execution manifest for the implementation session. That manifest must remain separate from the archived `repo-bootstrap` manifest.

---

**Final verdict: PASS WITH FIXES — documentation quality is good, but implementation remains blocked pending explicit decisions.**
