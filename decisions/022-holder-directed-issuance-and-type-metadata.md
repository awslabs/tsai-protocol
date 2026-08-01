<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 022: Holder-Directed Issuance and Type Metadata

**Status:** Accepted  
**Date:** 2026-08-01  
**Deciders:** TSAI Working Group  
**Relationship to ADR 015:** amends the purpose-issuance rationale in [ADR 015 — Credential Serialisation Format](./015-credential-serialisation-format.md)

---

## Context

ADR 015 treated selective disclosure as a retained but non-decisive capability, on the ground that "because credentials are short-lived and re-fetched per interaction, a Trust Authority can issue exactly the signals an interaction needs and omit the rest". That reasoning contradicts the privacy property in §5.7, that a Trust Authority does not learn which Service Provider an agent visits. A Trust Authority cannot issue exactly what an interaction needs without knowing the interaction. The two cannot both hold, and the issuance API has no field by which a purpose could be expressed, so purpose-issuance is not possible as specified.

Trust-Authority blindness is the more valuable property and the one both an operator and a Service Provider can reason about, so it is kept and purpose-issuance is dropped. That makes selective disclosure the only data-minimisation mechanism, and selective disclosure is holder-controlled, so an agent could withhold the very signals a Service Provider's policy needs to read, reputation above all. The protocol therefore needs a way to declare which signals an issuer may make disclosable and which are mandatory, and a cheaper minimisation path that does not depend on the holder suppressing signals after the fact.

---

## Decision

**Keep blindness, drop purpose-issuance.** §5.7's property stands. ADR 015's purpose-issuance sentence is withdrawn by this amendment.

**Holder-directed issuance.** `IssueRequest` gains an optional `signals` filter by which the agent requests a subset — for example identity only — without naming the Service Provider. The Trust Authority stays blind to the destination; it learns the agent's pattern of requests over time, which is far weaker than learning its destinations. This gives minimisation without the selective-disclosure machinery, and it supplies the field the `403 "does not meet the criteria for the requested signals"` response already refers to.

**Type metadata.** TSAI publishes a type-metadata document for each `vct`, per SD-JWT VC §4, carrying the per-type schema, display rules, and two controls per claim: `mandatory`, which declares a claim that must be present, and `sd`, which declares whether a claim may be selectively disclosed. Reputation signals are `sd: never`, so an issuer cannot make a score disclosable and an agent cannot withhold one it holds. The identity-floor signals (ADR 019) are `mandatory`. The document's integrity is protected by `vct#integrity` per SD-JWT VC §5. This document is where the required-field semantics live, replacing the `@context` and `type` role of the W3C model that ADR 015's consequences already assigned to it.

**Verifier surfacing.** Withheld array elements remain visible as digest objects until reconstruction, so a Service Provider can count how many signals were withheld even without seeing them. A verifier MUST surface that count and MAY fail closed above a policy threshold.

---

## Consequences

- Trust-Authority blindness holds; minimisation is available two ways, holder-directed issuance for the coarse case and selective disclosure for the fine case.
- A Service Provider can rely on reputation being present when a credential purports to carry it, because reputation is not disclosable and, under the floor, absence is a positive state rather than a suppression.
- TSAI now depends on a published type-metadata document per `vct`, which the credential-format and verification sections reference.
- The withheld-count surfacing gives a Service Provider a signal that disclosure was applied, which E.5's absence-ambiguity concern otherwise leaves silent.

---

## References

- [ADR 015 — Credential Serialisation Format](./015-credential-serialisation-format.md)
- [ADR 019 — Mandatory Identity Floor](./019-mandatory-identity-floor.md)
- [ADR 021 — Reputation Comparability, Support, and Attribution](./021-reputation.md)
- SD-JWT VC §4 (Type Metadata), §5 (Integrity), RFC 9901 §7.1
