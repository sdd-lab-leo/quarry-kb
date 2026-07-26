# ADR-0005: Bootstrap Probe Exception, Allowlist Matching, And Readiness HTTP Contract

## Status

Accepted

## Date

2026-07-26

## Context

ADR-0004 locked the internal-gateway and data-egress product boundary, but independent P0 review found three implementation-blocking gaps still open inside `repo-bootstrap`:

1. Embedding/OCR “allowlist / resolve to” wording did not commit a matching algorithm.
2. Unauthenticated health probes were described as network-restricted, but not as an explicit exception to product `SEC-01`.
3. Readiness success/failure semantics disagreed across data-flow, design, and the API guide (HTTP 200 not-ready vs HTTP 503; missing component payload shape; vector capability omitted from the spec component set).

These are still gateway/bootstrap boundary decisions, so they are recorded here as an amendment ADR rather than silently rewriting ADR-0004.

## Decision

1. Embedding/OCR allowlist validation uses literal hostname or `host:port` matching against the configured allowlist. Empty hosts are invalid. Validation must not perform DNS resolution and must not make an outbound request. A host that would resolve to a private IP but is absent from the allowlist is rejected.
2. The bootstrap `.env.example` default allowlist includes the documented placeholder host `gateway.internal`, and placeholder embedding/OCR/chat URLs use that host so local verification does not require a live gateway or OQ-09 values.
3. `GET /api/v1/health/live` and `GET /api/v1/health/ready` are an explicit exception to product `SEC-01`. They are unauthenticated infrastructure probes, expose no business data, and must remain reachable only through the Compose/service network boundary for local bootstrap. Future business endpoints must not reuse this exception. Whether probes later move to a private management port remains `OQ-BOOT-01`.
4. Readiness HTTP semantics for bootstrap are fixed:
   - HTTP 200 means all required local components are ready.
   - HTTP 503 means not-ready.
   - Not-ready responses include component diagnostics for `configuration`, `database`, `migration`, and `vector_capability`, plus one stable primary error code.
   - There is no HTTP 200 not-ready response.
5. The Alembic baseline enables the PostgreSQL `vector` extension and records revision metadata; it creates no business tables. Readiness reports vector capability from extension availability.

## Consequences

### Positive

- TASK-001/003/004 can implement host policy and readiness/frontend mapping without inventing security behavior.
- Probe auth exception is reviewable against `SEC-01` instead of being implied.
- Frontend and API share one not-ready contract.

### Negative

- Literal host matching is less convenient than DNS-based private-range checks.
- Local Compose network restriction is an interim control until OQ-BOOT-01 is resolved.

## Alternatives Considered

| Alternative | Why not |
|---|---|
| Validate allowlist via DNS resolution to private ranges | Environment-dependent and easy to get wrong; rejected for bootstrap. |
| Require JWT on health probes immediately | Conflicts with ordinary Compose probe practice; deferred in favor of explicit SEC-01 exception plus network restriction. |
| Return HTTP 200 with `not_ready` body | Forces clients to inspect payload shape for dependency failure; 503 is clearer for probes. |
| Rewrite ADR-0004 in place | Violates Accepted-ADR immutability; clarification belongs in a new ADR. |

## Review Triggers

- OQ-BOOT-01 chooses a private management port or different probe exposure model.
- Allowlist policy changes to support DNS, CIDR, or mTLS identity instead of host literals.
- Product `SEC-01` is revised to enumerate infrastructure probe exceptions centrally.

## Related Documents

- [ADR-0004](ADR-0004-gateway-contract-and-data-egress-boundaries.md)
- [Product specification](../../01-requirements/quarry-kb-product-spec-v0.1.md)
- [repo-bootstrap design](../../05-design/repo-bootstrap-design.md)
- [repo-bootstrap API guide](../../05-design/contracts/repo-bootstrap-API_IMPLEMENTATION_GUIDE.md)
- [repo-bootstrap traceability](../repo-bootstrap-traceability.md)
