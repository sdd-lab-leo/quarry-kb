# Quarry KB v0.1 Evaluation Question Set

## Document Control

| Field | Value |
|---|---|
| Status | Draft — pending product-owner acceptance |
| Version | 0.1 |
| Purpose | Fixed evaluation set for P0 and the later pilot gate |
| Scope | Mock corpus and non-production evaluation only |
| Product source | `docs/01-requirements/quarry-kb-product-spec-v0.1.md` |
| Prototype source | `docs/01-requirements/prototypes/index.html` |

## Evaluation Contract

This set fixes the question text, question type, and expected source boundary before implementation. It is not a collection of real company content. The corpus used with it must contain mock or explicitly approved pilot documents only.

The first ten questions are positive-grounding questions. A passing answer must be supported by one or more relevant citations that a reviewer can open and trace to the named mock source family. Wording may vary; unsupported claims may not.

The negative question must produce an explicit no-basis response and must not be answered from general model knowledge.

## Mock Source Contract

The evaluation corpus should include mock documents using these source identities, which already appear in the static prototype:

| Source ID | Mock source |
|---|---|
| SRC-01 | Change Management Handbook (mock) |
| SRC-02 | Weekly Release Process (mock) |
| SRC-03 | Emergency Change Policy (mock) |
| SRC-04 | Onboarding Checklist (mock) |
| SRC-05 | Incident Review Template (mock) |
| SRC-06 | Scanned Vendor Form (mock) |
| SRC-07 | Weekly Ops Notes (mock) |

The exact mock corpus text is a later pilot-preparation input. The source identities and question wording below are fixed now so retrieval and citation quality can be compared across implementations.

## Positive Questions

| ID | Question | Type | Expected source boundary | Pass condition |
|---|---|---|---|---|
| EQ-01 | Who approves a change request for the payment module? | Cross-source policy | SRC-01, SRC-02, optionally SRC-03 for the emergency branch | Answer identifies the normal approval chain and cites the relevant source locations. |
| EQ-02 | When does the release manager confirm approved changes? | Process timing | SRC-02 | Answer cites the weekly release process and states the relevant confirmation point or cut-off. |
| EQ-03 | How is an emergency change approved and what follow-up is required? | Exception policy | SRC-03 | Answer includes the emergency approval rule and retrospective requirement with a citation. |
| EQ-04 | What must a new joiner complete during the first week? | Checklist lookup | SRC-04 | Answer cites the onboarding checklist and does not substitute an uncited generic onboarding list. |
| EQ-05 | Which template should be used to record an incident review? | Template lookup | SRC-05 | Answer identifies the mock incident review template and cites the source. |
| EQ-06 | What information must be recorded after a change is approved? | Recordkeeping policy | SRC-01, SRC-02 | Answer cites the relevant change-management or release-process content. |
| EQ-07 | What is the weekly release cut-off rule? | Process rule | SRC-02 | Answer cites the cut-off rule and distinguishes it from emergency handling. |
| EQ-08 | What operating detail is captured in the weekly operations notes? | Operational context | SRC-07 | Answer cites the weekly operations notes rather than inventing a status update. |
| EQ-09 | Which fields are required on the scanned vendor form before submission? | OCR-backed lookup | SRC-06 | Answer cites the OCR-indexed source and exposes the document/page location. |
| EQ-10 | How can I tell whether a document was parsed from native text or OCR? | Source inspection | SRC-06 plus document metadata | Answer explains the visible parse-mode metadata and cites or opens the document detail. |

## Negative Question

| ID | Question | Expected behavior | Fail condition |
|---|---|---|---|
| EQ-11 | What is the budget for next year's team offsite? | Return an explicit no-basis response because the mock corpus does not cover offsite budgets. | Any numeric budget, guessed policy, or uncited answer is a failure. |

## Operational Evaluation Scenarios

These scenarios are evaluated alongside the questions because P0 fixes the product's trust and degradation boundaries.

| ID | Scenario | Expected result |
|---|---|---|
| OPS-01 | Viewer attempts to upload or delete a document | API denies the operation; hiding the button alone is insufficient. |
| OPS-02 | Internal gateway is unavailable while opening Knowledge | Knowledge list and already-indexed document detail remain readable. |
| OPS-03 | Internal gateway is unavailable during upload | File is accepted and recorded; ingest later exposes a visible failure or stalled state with a retry/reindex path. |
| OPS-04 | Internal gateway is unavailable and Internal Gateway is selected for Ask | Clear provider error with retry; no silent provider switch and no fabricated answer. |
| OPS-05 | Embedding path is unavailable and a public chat provider is selected | Keyword-only retrieval notice is visible; citations remain required when evidence exists. |
| OPS-06 | Public chat provider is selected | Ask shows a short warning that retrieved snippets may leave the intranet. |
| OPS-07 | OCR or embedding endpoint is configured as public | Configuration is rejected; no public fallback is attempted. |

## Scoring Rules

1. `EQ-01` through `EQ-10` form the positive set. At least eight of ten must receive relevant, traceable citations for the v0.1 acceptance gate `AC-04`.
2. `EQ-11` must satisfy `AC-05` and may not be scored as a normal retrieval miss.
3. `EQ-09` is the required scanned-document question for `AC-03a`; its source must report OCR or mixed parsing.
4. A citation is relevant only when the reviewer can open the cited document/chunk and confirm that it supports the claim.
5. Model fluency, answer length, and uncited general knowledge do not increase the score.

## Open Questions

| ID | Question | Impact |
|---|---|---|
| OQ-EVAL-01 | Which department owns the first approved pilot corpus? | Determines whether the mock source contract is replaced or supplemented for pilot evaluation. |
| OQ-EVAL-02 | What quality bar should be used for citation relevance beyond the 8/10 gate? | Needed for pilot reporting and later retrieval tuning. |

## Traceability

| This document | Upstream source |
|---|---|
| Positive citation set | `AC-04`, `FR-32` to `FR-35` |
| Negative question | `AC-05`, `FR-35` |
| OCR-backed question | `AC-03a`, `FR-14a`, `FR-19` |
| Operational scenarios | `AC-01`, `AC-02`, `AC-18` to `AC-21`, `D-07` |

