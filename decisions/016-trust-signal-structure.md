<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 016: Trust Signal Structure

**Status:** Accepted  
**Date:** 2026-07-02  
**Deciders:** TSAI Working Group  
**Relationship to ADR 004:** supersedes [ADR 004 — Tiered Trust Model (T0-T3)](./004-tiered-trust-model.md)


---

## Context

ADR 004 defined a four-tier model, T0 to T3, each tier adding to the one below: T0 identity, T1 reputation, T2 economic stake, T3 constraints and real-time verification. Tiers do two jobs: they group signals, and they act as a shorthand for assurance level that a Service Provider uses to set policy ("require T2").

Two tensions with that model are the inputs to this decision.

First, the assurances are not cumulative. An operator can carry insured recourse from day one with no reputation history, and an established operator may decline to post stake. The consolidated strategy proposal already treats the tiers as independent assurances, so the numbering implies an order the model no longer holds.

Second, the tier label is coarse relative to the decision a Service Provider makes. "Require T3" does not say how much insurance coverage or which certification, and that decision is a predicate over specific signals. The credential also carries redundant tier markers, a `type` entry, a `tsaiTier` field, and an in-block level, that duplicate the structure and can become inconsistent with it.

This ADR decides only the structure of the signals: how they are shaped and discriminated. It deliberately does not define the set of categories or the per-type fields, which are left to a later decision, either a separate ADR or the implementation JSON schema. It is orthogonal to the credential format (ADR 015) and the holder-binding decision (ADR 014), each decided in its own ADR in this branch.

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

**Pros.** Lowest integration cost and highest communicability (8): one field checked against one threshold, and "T2" is understood immediately, like an SSL validation level (DV, OV, EV). Where authorities share the tier definitions, the scale compares directly across them with no per-authority logic (7). Policy is a single comparison (2).

**Cons.** The cumulative assumption fails: insurance without reputation, or accreditation without stake, cannot be expressed (1). Cross-authority comparison holds only while authorities agree on the scale, which is hard to sustain (7). The label is coarse (2), a new assurance cannot be added without redefining the scale (3), and the redundant markers can become inconsistent (6).

### Option 2: Independent tiers (T0-T3, present or absent)

Keep the four tiers but treat them as independent flags, as the consolidated proposal frames them.

**Pros.** Keeps the existing T0-T3 vocabulary, badges, and integrations, so migration is cheap (5, 8). A bounded four-name set is easy to standardise across authorities without a type registry (7). It drops the cumulative assumption, so insurance without reputation is now expressible (1).

**Cons.** The names are still arbitrary and the numbering still implies an order (1). It does not capture that the tiers differ in kind (1). It stays coarse for policy (2), and a fifth kind of assurance means extending the fixed set (3).

### Option 3: Flat list of typed signals

Replace tiers with a flat list of signals. Each signal is an object, independently present or absent, and a Service Provider's policy is a predicate over the signals. The two variants differ only in whether each signal declares the nature of its assurance.

**Shared pros.** Represents independence directly, with no false order (1). Extensible: any authority adds a type without restructuring or a central scale (3), the open-vocabulary approach of W3C VC `type` arrays and OAuth scopes.

**Shared cons.** The single ordinal label is gone, so the immediate communicability of a tier is lost and any human-facing progression moves to Trust Authority product naming (8).

#### Variant 3a: type only

Each signal carries a `type` and its value, nothing more.

**Pros.** Lowest governance: a new type needs no taxonomy decision, and the interoperability contract is just namespaced type names (3, 7, 8).

**Cons.** The list is heterogeneous with nothing to tell a verifier how to treat each signal, so a Service Provider must know every type name, and portability rests on names rather than shared meaning (2, 7). Validation is harder without a discriminator (4).

#### Variant 3b: category, type, and type-specific fields

Each signal is an object carrying a `category` that names the nature of the assurance, a `type` that names the specific signal, and whatever type-specific fields that type needs. This ADR fixes that three-part shape only. It does not define which categories exist, which types exist, or which fields each type carries; those are a separate decision, taken later in their own ADR or in the implementation JSON schema.

The value of the category discriminator, independent of what the categories turn out to be, is that a verifier can decide how to treat a signal from its `category` before it knows the specific `type`. That is what gives category-level policy and cross-authority portability: a Service Provider can act on a signal's category even when two authorities name the underlying type differently, and a new type is usable by existing policy as long as it declares a category.

**Pros.** Strongest cross-authority portability, because the category carries meaning above the type names (7). Category-level policy keeps working when new types appear, provided each declares a category (2, 3). The discriminator gives clean per-category validation and tells a consumer how to treat each signal (4). The shape is the type-and-subtype arrangement of MIME types (`text/plain`, `text/html`), which is familiar.

**Cons.** A category set has to be agreed at some point, even though it is deferred here, so the governance cost is postponed rather than removed (6). Slightly more structure than a bare list.

**Illustrative structure.** The shape only; the `category` and `type` values below are placeholders, and the vocabulary is defined elsewhere. Serialisation follows the format decision (ADR 015), so under SD-JWT VC these are claims. Variant 3a is the same without the `category` field.

```json
"signals": [
  { "category": "‹category›", "type": "‹type›", "value": "‹value›" },
  { "category": "‹category›", "type": "‹type›", "‹field›": "‹type-specific value›" }
]
```

**Mapping from the current tiers.** The substance of the T0-T3 signals is preserved as signals in this structure; T3's constraints and real-time verification are authorisation and verification concerns rather than trust signals and stay where the architecture places them. How the remaining tiers map onto specific categories and types is part of defining the category vocabulary, which is out of scope here.

---

## Comparison

The table summarises the per-criterion standing; the prose below gives the detail. Entries are relative, not absolute.

| Criterion | 1 cumulative | 2 independent | 3a typed | 3b category + type |
|---|---|---|---|---|
| 1 Faithfulness | fails (false order) | partial | yes | yes |
| 2 Policy expressiveness | coarse | coarse | by type | by category and type |
| 3 Extensibility | redefine the scale | fixed set | open | open |
| 4 Validation | simple | simple | harder; no discriminator | clean; discriminator |
| 5 Continuity | status quo | high | replaces tiers | replaces tiers |
| 6 Implementer simplicity | highest | high | high | a category set to agree, later |
| 7 Portability | only if the scale is agreed | bounded set | by type name | by shared category |
| 8 Adoption | highest | high; keeps badges | low issuing friction | moderate |

The options differ on three dimensions: faithfulness to independent assurances, how the set extends, and how it ports across authorities. Tiers (1, 2) are easiest to adopt and to read, and a small fixed vocabulary compares across authorities while they agree on it, but the scale is coarse and cannot be extended. A flat list (3) represents independence faithfully and any authority can extend it. Within the flat list, 3a leaves the assurance kind implicit, so a Service Provider must know each type and portability rests on names; 3b makes the kind explicit through the category, so policy and portability work by category, at the cost of agreeing a category set at some later point.

---

## Decision

Adopt **Variant 3b**: a flat list of signals in which each signal is an object carrying a `category`, a `type`, and type-specific fields.

This ADR fixes only that structure. It does not define the categories, the types, or the per-type fields. Those are a separate decision, taken later either as its own ADR or as the implementation JSON schema. What is decided here is that signals are a flat, independently-present list rather than tiers, and that each signal is discriminated by a `category` above its `type`.

The flat list is chosen over tiers because the assurances are not cumulative, so any ordered scale (Options 1 and 2) implies an order that does not hold and is too coarse for the predicate a Service Provider actually evaluates. Within the flat list, the category discriminator (3b) is chosen over a bare typed list (3a) because it lets a verifier treat a signal by its category before it knows the specific type, which is what gives cross-authority portability, category-level policy that survives new types, and clean validation. The cost accepted is that a category set must be agreed eventually; deferring it keeps this decision to the structural question and lets the vocabulary be settled with implementation experience rather than up front.

---

## Consequences

- Supersedes ADR 004. The tiered model and its redundant markers are replaced by the flat signal list.
- A signal is an object with a `category`, a `type`, and type-specific fields. A Service Provider's admission policy is a predicate over these signals.
- The category vocabulary, the set of types, and the fields each type carries are not decided here. They are deferred to a separate ADR or to the implementation JSON schema, and that later decision also settles how the current tier substance maps onto categories and types.
- Verification strength keyed to tiers must be re-expressed. ADR 004 and ADR 009 key verification rigour to tiers, an offline timestamp check for T0/T1 and stronger mechanisms for T2/T3. With no tiers, verification strength has to be expressed as a predicate over signals or categories, for example a signal carrying a status or verification reference that the Service Provider checks. Occasional checks against static or cached resources are inexpensive, so the offline-only constraint that motivated the low tiers is no longer decisive. This implies amending ADR 009 and is noted as a dependency, not settled here.
- Revocation stays atomic. A single credential carrying all signals is revoked as a whole, which fits the short-expiry-and-refresh model; per-signal revocation is not proposed.
- Reputation attribution, whether reputation accrues to the agent or the operator, is a separate open question and is not settled here.
- Serialisation follows ADR 015, which selects SD-JWT VC, so the signals are carried as claims in the credential.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 004 — Tiered Trust Model (T0-T3)](./004-tiered-trust-model.md)
- [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)
- ADR 014 — Holder Binding and Web Bot Auth Integration
- ADR 015 — Credential Serialisation Format
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc)
