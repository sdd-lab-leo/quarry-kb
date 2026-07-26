# ADR-0004: Internal Gateway Contract And Data-Egress Boundaries

## Status

Accepted

## Date

2026-07-26

## Context

Quarry KB uses an internal model gateway for embedding and multimodal OCR, while v0.1 also permits explicitly configured public OpenAI-compatible chat providers. The repository currently contains only placeholders, so the first implementation slice must preserve these boundaries without pretending that concrete gateway URLs, model IDs, or rate limits are known.

The product specification already settles decisions D-01 through D-07. This ADR records how those decisions constrain the application boundary and the bootstrap configuration.

## Decision

1. Chat/completion is accessed through a provider-neutral OpenAI-compatible adapter boundary. The internal gateway is the recommended pilot default. Public chat providers are opt-in through a later Admin configuration flow.
2. Embedding and multimodal OCR are internal-gateway-only integrations. Their configured base URLs must resolve to an approved intranet/gateway host. Public embedding or OCR URLs are invalid configuration, not fallback targets.
3. Health and readiness probes do not call the model gateway. They verify process health, database readiness, migration readiness, and configuration shape without sending document text, page images, or user prompts outside the application.
4. The bootstrap environment template uses placeholders for concrete gateway URLs, model identifiers, vector dimension, OCR path, and rate limits. These values are deployment configuration, not source-code constants.
5. When a public chat provider is enabled or selected, the later Admin and Ask surfaces must show the accepted data-egress warning: retrieved snippets may leave the intranet. Provider credentials remain server-side secrets.
6. Gateway outage behavior follows the product's surface-specific matrix: Browse remains available, Upload accepts files but ingest may fail visibly, and Ask reports provider/vector degradation without silent provider switching or fabricated answers.

## Consequences

### Positive

- The first slice can validate configuration and deployment without requiring live gateway credentials.
- Future parser, embedding, and chat implementations remain replaceable through adapter boundaries.
- The public-chat egress trade-off is visible and cannot be confused with the stricter embedding/OCR boundary.

### Negative

- Concrete gateway smoke tests remain blocked until OQ-09 values are supplied.
- Public-provider warnings and outage behavior must be implemented again in the relevant later slices; bootstrap only establishes the contract.

## Alternatives Considered

| Alternative | Why not |
|---|---|
| Use a public embedding/OCR fallback | Violates D-03, D-04, D-05, and SEC-08/09. |
| Make health checks depend on gateway availability | Would make deployment readiness and Browse unnecessarily dependent on an external integration. |
| Hard-code the internal gateway URL and model IDs | OQ-09 is unresolved and hard-coding would leak deployment assumptions into source. |

## Review Triggers

- The internal gateway changes from OpenAI-compatible contracts.
- The security boundary changes to permit external embedding or OCR.
- The product removes public chat providers or changes the accepted Ask-time egress trade-off.
- The deployment moves to multiple environments with different gateway allowlists.

## Related Documents

- [Product specification](../../01-requirements/quarry-kb-product-spec-v0.1.md)
- [Product positioning](../product-positioning.md)
- [ADR-0002](ADR-0002-lock-technology-stack-and-auth-evolution.md)
- [ADR-0005](ADR-0005-bootstrap-probe-allowlist-and-readiness-contract.md) (clarifies allowlist matching, SEC-01 probe exception, and readiness HTTP semantics)
- [repo-bootstrap architecture](../../04-architecture/repo-bootstrap-architecture.md)
