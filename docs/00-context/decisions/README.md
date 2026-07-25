# Architecture Decision Records

This directory stores durable Architecture Decision Records (ADRs) for decisions that shape system architecture, security posture, data ownership, integrations, or AI-agent working context for Quarry KB.

## Rules

- One ADR records one decision.
- Accepted ADRs are immutable except for typo fixes, link repairs, or status changes.
- Reversing a decision requires a new ADR that supersedes the old one.
- Architecture and design documents should link to ADRs instead of duplicating their rationale.
- Coding agents should read relevant ADRs before changing cross-cutting behavior.

## Index

| ADR | Status | Decision |
|---|---|---|
| [ADR-0001](ADR-0001-adopt-context-engineering-adr-and-sdd-skills.md) | Accepted | Adopt context engineering, ADRs, and SDD skills |
| [ADR-0002](ADR-0002-lock-technology-stack-and-auth-evolution.md) | Accepted | Lock technology stack and auth evolution (password → SSO) |
| [ADR-0003](ADR-0003-adopt-execution-manifest-handoff.md) | Accepted | Adopt execution-manifest based hand-off for multi-agent and multi-session work |
