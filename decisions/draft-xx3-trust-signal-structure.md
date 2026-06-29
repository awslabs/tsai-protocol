<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR XXX: Trust Signal Structure

**Status:** Proposed  
**Date:** 2026-06-26  
**Deciders:** TSAI Working Group (pending)  
**Relationship to ADR 004:** may supersede [ADR 004 — Tiered Trust Model (T0-T3)](./004-tiered-trust-model.md), depending on the option chosen (see Consequences)

---

## Context

ADR 004 defined a four-tier model, T0 to T3, each tier adding to the one below: T0 identity, T1 reputation, T2 economic stake, T3 constraints and real-time verification. Tiers do two jobs: they group signals, and they act as a shorthand for assurance level that a Service Provider uses to set policy ("require T2").

Two tensions with that model are the inputs to this decision.

First, the assurances are not cumulative. An operator can carry insured recourse from day one with no reputation history, and an established operator may decline to post stake. The consolidated strategy proposal already treats the tiers as independent assurances, so the numbering implies an order the model no longer holds.

Second, the tier label is coarse relative to the decision a Service Provider makes. "Require T3" does not say how much insurance coverage or which certification, and that decision is a predicate over specific signals. The credential also carries redundant tier markers, a `type` entry, a `tsaiTier` field, and an in-block level, that duplicate the structure and can become inconsistent with it.

This ADR examines how to structure the signals: keep the tiers, make them independent, or replace them with a flat list of typed signals. It concerns only signal structure and content. It is orthogonal to the credential format (draft-xx2) and the holder-binding decision (draft-xx1), each decided in its own ADR in this branch.

---

## Decision Criteria

1. **Faithfulness to the model.** The structure represents assurances that are independently present or absent, without implying a false order.
2. **Policy expressiveness.** A Service Provider can express its admission rule directly against the signals it cares about.
3. **Extensibility.** New signal types are addable without restructuring the credential or renumbering anything.
4. **Validation tractability.** The structure is straightforward to validate, including per-signal provenance.
5. **Continuity.** The change preserves the substance of the existing signals and maps cleanly from the current tiers.
6. **Implementer simplicity.** The structure minimises ambiguity, redundancy, and implementation effort.
7. **Portability across Trust Authorities.** A Service Provider can consume and compare credentials from different authorities without per-authority logic.
8. **Adoption and communicability.** How much effort a newcomer needs to integrate, and how readily policy-setters and badge-readers understand what an agent has.

---

## Options Considered

### Option 1: Cumulative tiers (status quo, ADR 004)

Retain T0-T3 as a cumulative sequence.

**Pros.** Lowest integration cost and highest communicability (8): one field checked against one threshold, and "T2" is understood immediately, like a hotel star rating or an SSL validation level (DV, OV, EV). Where authorities share the tier definitions, the scale compares directly across them with no per-authority logic (7). Policy is a single comparison (2).

**Cons.** The cumulative assumption fails: insurance without reputation, or accreditation without stake, cannot be expressed (1). Cross-authority comparison holds only while authorities agree on the scale, which is hard to sustain (7). The label is coarse (2), a new assurance cannot be added without redefining the scale (3), and the redundant markers can become inconsistent (6).

### Option 2: Independent tiers (T0-T3, present or absent)

Keep the four tiers but treat them as independent flags, as the consolidated proposal frames them.

**Pros.** Keeps the existing T0-T3 vocabulary, badges, and integrations, so migration is cheap (5, 8). A bounded four-name set is easy to standardise across authorities without a type registry (7). It drops the cumulative assumption, so insurance without reputation is now expressible (1).

**Cons.** The names are still arbitrary and the numbering still implies an order (1). It does not capture that the tiers differ in kind, a verified fact versus an assessment versus a backed promise (1). It stays coarse for policy (2), and a fifth kind of assurance means extending the fixed set (3).

### Option 3: Flat list of typed signals

Replace tiers with a `signals` array. Each signal is an object with a `type` and value, independently present or absent, and a Service Provider's policy is a predicate over the signals. The two variants differ only in whether each signal also declares the nature of its assurance.

**Shared pros.** Represents independence directly, with no false order (1). Extensible: any authority adds a type without restructuring or a central scale (3), the open-vocabulary approach of W3C VC `type` arrays and OAuth scopes.

**Shared cons.** The single ordinal label is gone, so the immediate communicability of a tier is lost and any human-facing progression moves to Trust Authority product naming (8).

#### Variant 3a: type only

The signal carries a `type` and value, nothing more.

**Pros.** Lowest governance: a new type needs no taxonomy decision, and the interoperability contract is just namespaced type names (3, 7, 8).

**Cons.** The list is heterogeneous with nothing to tell a verifier how to treat each signal, so a Service Provider must know every type name, and portability rests on names rather than shared meaning (2, 7). Validation is harder without a discriminator (4).

#### Variant 3b: classified by category

Each signal also carries a `category` naming the nature of the assurance. The `category` is a closed set of three values:

- **attribute** — a fact the authority verified (domain control, KYC level, a certification); the verifier could re-check it.
- **attestation** — the authority's own assessment (a reputation score) that the verifier cannot reproduce, so it carries provenance such as method and window.
- **guarantee** — a commitment backed by a liable party, whether self-posted collateral or third-party insurance or buyer protection, carrying coverage and provider; a promise about recourse rather than a fact.

**Pros.** Strongest cross-authority portability (7): the category carries meaning above the type names, so a Service Provider that requires "a guarantee of at least €100,000" interoperates across authorities even when one names the type `insurance` and another `buyerProtectionFund`. Category-level policy keeps working when new types appear, provided each declares a category (2, 3). The category discriminator gives clean per-category validation and tells a consumer how to treat each signal (4). It is the type-and-subtype arrangement of MIME types (text/plain, text/html).

**Cons.** Each signal type needs a category assignment, and the small closed category set must be agreed up front (6). Slightly more structure than a bare list.

**Illustrative structure (variant 3b).** Field names are for the schema to settle, and the serialisation depends on the format decision (draft-xx2). Variant 3a is the same without the `category` field.

```json
"signals": [
  { "category": "attribute",   "type": "domainControl", "value": "acme-corp.example" },
  { "category": "attribute",   "type": "kyc",           "value": "enhanced" },
  { "category": "attestation", "type": "reputationScore", "value": 0.87,
    "method": "https://trusted-shops.example/tsai/methods/reputation/v2", "window": "P90D" },
  { "category": "guarantee",   "type": "insurance", "provider": "did:web:trusted-shops.example",
    "coverage": { "value": 100000, "currency": "EUR" } }
]
```

**Mapping from the current tiers.** Each tier maps to one category: T0 identity becomes an **attribute** signal; T1 reputation becomes an **attestation** signal; T2 economic stake, including posted collateral and insurance, becomes a **guarantee** signal. T3 constraints and real-time verification are authorisation and verification concerns, not trust signals, and stay where the architecture places them.

---

## Comparison

The table summarises the per-criterion standing; the prose below gives the detail. Entries are relative, not absolute.

| Criterion | 1 cumulative | 2 independent | 3a typed | 3b typed + category |
|---|---|---|---|---|
| 1 Faithfulness | fails (false order) | partial | yes | yes |
| 2 Policy expressiveness | coarse | coarse | by type | by category |
| 3 Extensibility | redefine the scale | fixed set | open | open |
| 4 Validation | simple | simple | harder; no discriminator | clean; discriminator |
| 5 Continuity | status quo | high | replaces tiers | replaces tiers |
| 6 Implementer simplicity | highest | high | high | closed category set to agree |
| 7 Portability | only if the scale is agreed | bounded set | by type name | by shared category |
| 8 Adoption | highest | high; keeps badges | low issuing friction | moderate |

The options differ on three dimensions: faithfulness to independent assurances, how the set extends, and how it ports across authorities. Tiers (1, 2) are easiest to adopt and to read, and a small fixed vocabulary compares across authorities while they agree on it, but the scale is coarse and cannot be extended. A flat list (3) represents independence faithfully and any authority can extend it. Within the flat list, 3a leaves the assurance kind implicit, so a Service Provider must know each type and portability rests on names; 3b makes the kind explicit, so policy and portability work by category even across authorities that name types differently, at the cost of agreeing the closed category set.

---

## Decision

Open. This ADR recommends nothing. It records the current model, the options, and their pros and cons for the working group to weigh. The chosen option and its rationale will be recorded here on acceptance.

The trade runs across faithfulness, extensibility, portability, and adoption cost. Tiers are easiest to adopt and to compare while a shared scale holds, but coarse and fixed. A flat signal list is faithful and extensible; classifying each signal by category (3b) adds cross-authority portability and forward-compatible policy at the cost of agreeing the category set, while leaving it untyped (3a) keeps governance minimal but leaves type knowledge to the Service Provider.

---

## Consequences

The consequences depend on the option chosen.

- **Keeping tiers (1, 2).** No migration. The coarseness and limited extensibility remain, and under Option 1 the cumulative assumption and the redundant markers remain.
- **A flat signal list (3).** The credential represents independent assurances, policy is a predicate over signals, and the redundant tier markers and the single-label shorthand are gone, so go-to-market materials need rewording. Variant 3b adds a closed category set and discriminated-union validation; 3a keeps a heterogeneous list that a Service Provider resolves by type name.
- **Verification strength, when tiers are removed.** ADR 004 and ADR 009 key verification rigor to tiers: an offline timestamp check for T0/T1, and challenge-response or real-time verification for T2/T3. A flat list has no tiers to key this to, so verification strength has to be expressed independent of tiers, as a predicate over signals or categories. For example, an attestation or a guarantee signal may carry a status or verification reference that the Service Provider checks. Occasional checks against static, precalculated, or cached resources are inexpensive, so the offline-only constraint that motivated the low tiers is no longer decisive. This implies amending ADR 009 and is noted here as a dependency, not settled.

The following hold regardless of the option.

- **Revocation.** A single credential carrying all signals implies atomic, all-or-nothing revocation, which fits the short-expiry-and-refresh model. Per-signal revocation would reintroduce per-credential complexity and is not proposed.
- **Reputation attribution.** Whether reputation accrues to the agent or the operator is a separate open question and is not settled here.
- **Format.** Serialisation depends on the credential format decision (draft-xx2). The structures here hold whether the credential is a W3C VC or an SD-JWT VC.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 004 — Tiered Trust Model (T0-T3)](./004-tiered-trust-model.md)
- [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)
- draft-xx1 — Holder Binding and Web Bot Auth Integration (this branch)
- draft-xx2 — Credential Serialisation Format (this branch)
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc)
