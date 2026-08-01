<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 021: Reputation Comparability, Support, and Attribution

**Status:** Accepted  
**Date:** 2026-08-01  
**Deciders:** TSAI Working Group  
**Relationship to ADR 016:** settles the reputation-attribution question [ADR 016 — Trust Signal Structure](./016-trust-signal-structure.md) left open

---

## Context

Reputation is the protocol's differentiator, and three gaps undermine it. The score is declared TA-specific and not comparable across Trust Authorities, so a Service Provider trusting several authorities must author a policy per private scale and an operator cannot tell what standing it needs. The behaviour a Trust Authority claims to observe has no specified supply: an authority has no visibility into an agent's conduct at a Service Provider it has no relationship with. And attribution is contradictory across the documents — agent-level in the architecture, operator-level in the concept document, open in ADR 016 — where the agent-level reading makes reputation washing structural, since an operator can register a fresh agent to shed a poor record for the cost of one key pair.

---

## Decision

**A portable band alongside the score.** A reputation signal carries a coarse ordinal `band`, one of `insufficient-history`, `established`, or `strong`, on the same pattern as `kyc`. The TA-specific `scr` remains as the fine-grained value. Each Trust Authority publishes how it maps its own scale to the band, under the published-criteria obligation (ADR 022 and §7.7). The band gives one statement a Service Provider can act on across authorities; the score stays available for authorities a Service Provider models directly.

**Mandatory support.** Whenever a reputation signal carries `scr` or `band`, it MUST also carry `cnt`, the number of interactions behind it, and the observation window, so a Service Provider can discount a score with thin support. The window is carried as `wdw` (an ISO 8601 duration) together with `asof` (the window end, per the per-signal currency rule), so the window is computable rather than a bare length.

**Attribution: agent-level, with an optional operator-level signal.** A reputation signal is about the specific agent by default. A Trust Authority MAY additionally include an operator-level reputation signal that aggregates across the operator's agents. A Service Provider evaluating a new agent, which by construction has thin agent-level history, weighs the operator-level standing. Reputation washing is not eliminated: a new agent under the same operator starts with no agent-level record while carrying the operator's identity, compliance, assurance, and any operator-level reputation. This is recorded as a known limitation in §5.11, and the operator-level signal is what lets a Service Provider see through it.

**Provenance.** A Trust Authority MUST assert only reputation it has a basis to observe, whether from its own relationship with the operator or from a feedback channel. The feedback channel — signed misbehaviour reports from Service Providers — is named in the roadmap phase that first ships a reputation signal; v1.0 does not specify its wire form, and until it does a Trust Authority's reputation rests on its own relationship, which the honesty obligation (§5.5, §7.6) already governs.

---

## Consequences

- A Service Provider can write one policy against `band` across authorities, and refine with `scr` where it models an authority directly.
- A thin-support score cannot masquerade as a strong one, because `cnt` and the window travel with it.
- Reputation washing is bounded, not closed; the operator-level signal and §5.11's note are the mitigation, and end-user-level Sybil resistance remains deferred (ADR 008).
- The reputation feedback channel is a named roadmap item rather than v1.0 wire format.

---

## References

- [ADR 008 — User Privacy and Sybil Prevention](./008-user-privacy-and-sybil-prevention.md)
- [ADR 016 — Trust Signal Structure](./016-trust-signal-structure.md)
- [ADR 022 — Holder-Directed Issuance and Type Metadata](./022-holder-directed-issuance-and-type-metadata.md)
