<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 011: Trust Authority Operational Transparency

**Status:** Proposed  
**Date:** 2026-03-17  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

The threat model identifies TA signing key compromise and TA insider fraudulent issuance as critical and high-severity findings. Current mitigations include HSM key storage, multiple competing TAs, and audit logging.

Three mitigations in the threat model depend on governance body oversight. The governance body is a working group that stewards the specification — it has no operational capabilities, monitoring infrastructure, or enforcement mechanisms.

Credential transparency logs (Section 5.12.3) require a log operator ecosystem with no clear business model, and raise privacy concerns that conflict with the protocol's privacy requirements.

The protocol needs a TA accountability mechanism that works without an operational governance body, requires no new infrastructure operators, preserves credential-level privacy, and adds minimal operational burden to TAs.

---

## Options Considered

### Option 1: Credential Transparency Logs

Public append-only logs of all credential issuances. Detects individual fraudulent credentials but requires a log operator ecosystem (no business model identified) and exposes credential metadata.

**Decision:** Deferred. Privacy concerns and ecosystem bootstrapping problems make this impractical for v1.0.

### Option 2: Governance Body Operational Role

Governance body operates TA registry, monitors TA behavior, enforces accreditation.

**Decision:** Rejected. Does not match the governance body's current role or capabilities.

### Option 3: TA Self-Attestation via Operational Status Reports

TAs publish signed, machine-readable operational status reports at a well-known endpoint. Reports contain aggregate statistics, not individual credential data. Platforms consume reports as part of TA trust evaluation.

**Decision:** Accepted.

---

## Decision

Require TAs to publish signed operational status reports at `/.well-known/tsai-ta-status`. Reports use aggregate statistics to enable platform-driven TA accountability without compromising credential-level privacy or requiring new infrastructure.

See Architecture Section 7.7 for the normative specification.

---

## Rationale

- Aggregate statistics reveal TA operational patterns (issuance spikes, zero revocations, stale key rotation) without exposing individual credential data
- Self-attestation is the only mechanism requiring no new infrastructure or actors
- A compromised TA could falsify reports, but: falsified reports create verifiable discrepancies if platforms collectively observe more credentials than reported; a TA that stops publishing or publishes stale reports is itself a signal
- Aligns with "TSAI signals, platforms decide" — platforms already choose which TAs to trust (ADR 002); status reports give them data for informed decisions

---

## Consequences

### Positive

- Platforms gain data for TA trust decisions without new infrastructure
- Privacy preserved (aggregate data only)
- Minimal TA burden (report generation from existing operational data)
- Detects systemic TA compromise or misbehavior

### Negative

- Self-reported data can be falsified by a compromised TA
- Cannot detect individual fraudulent credentials
- Effectiveness depends on platforms consuming and acting on reports

### Accepted Residual Risks

- A single fraudulent credential from an otherwise well-behaved TA remains undetectable at the protocol level
- A TA that falsifies both behavior and reports consistently can evade detection until external evidence surfaces

---

## References

- ADR 002: Centralized Trust Authorities
- Architecture Section 5.8: Trust Authority Security
- Architecture Section 7.7: Operational Transparency (normative)
- Threat Model: TA signing key compromise, TA insider fraudulent issuance, TA standards lowering

> Note: architecture section numbers in this ADR refer to the pre-2026-08 structure, before the specification was renumbered.
