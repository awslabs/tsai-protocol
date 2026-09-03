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

This ADR decides the signal structure and the baseline semantics that make a TSAI credential useful: the four categories and their typed fields, the mandatory operator-identity floor, and the TA-specific reputation score with its supporting evidence context. It remains orthogonal to the credential format (ADR 015) and holder binding (ADR 014).

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
9. **Accountability by default.** Every conforming credential identifies the accountable operator without requiring verifier configuration.
10. **Reputation evidence and attribution.** Reputation carries enough support and scope to be interpreted without hiding a thin history or making reputation washing invisible.

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

**Mapping from the current tiers.** The substance of the T0-T3 signals is preserved as signals in this structure; T3's constraints and real-time verification are authorisation and verification concerns rather than trust signals and stay where the architecture places them.

### Identity-floor alternatives

Three placements were considered. No floor maximises flexibility but permits a credential that identifies nobody. A verifier-side base profile keeps all policy in one place but makes the v1 identity guarantee depend on each Service Provider configuring that profile. An issuer obligation is chosen: every credential carries the operator's legal name, jurisdiction, verification depth, and a verified controlled domain. This applies before verifier policy and reintroduces no tier or ordering.

### Reputation alternatives

A TA-specific score preserves each authority's methodology but requires a Service Provider to model each scale. A shared band would simplify policy only if its labels had common evidence and thresholds; allowing each authority to map its own methodology would give equal labels different meanings and invite unsafe comparison. Genuine comparability would require domain-specific definitions of eligible interactions, outcomes, minimum history, calculation, and thresholds. TSAI v1 does not define that common evidence model and therefore removes the band.

A bare score plus mutable published criteria was also considered. It has the lowest wire cost, but an auditor or Service Provider cannot determine which methodology version produced a historical score after the criteria change. Standardising one range or calculation would solve that ambiguity by constraining TAs, but would recreate the premature comparability claim. TSAI therefore binds every registered score to a versioned HTTPS `mtd` and the exact methodology-document bytes through `mtd#integrity`. The small common document schema makes range, direction, semantics, calculation, evidence, and insufficient-history treatment inspectable while leaving their substance to the TA. The cost is two additional signal fields, an immutable document to publish and cache, and authority-specific policy keyed by `(iss, typ, mtd)`. A future derived type may define a comparable reputation profile with a shared evidence model.

Agent-level attribution is the default because behaviour belongs to the specific agent. An optional operator-level aggregate lets a Service Provider evaluate a new agent against the operator's broader record and makes reputation washing visible, although it does not eliminate it. End-user-level Sybil resistance remains out of scope (ADR 008).

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

The four registered categories are identity (`idn`), reputation (`rep`), compliance (`cmp`), and assurance (`asr`). Each signal has `cat`, `typ`, and type-specific fields; the schema and registry define the vocabulary.

**Identity floor.** A Trust Authority MUST NOT issue a TSAI credential unless it contains the operator's legal name (`idn/org`), jurisdiction (`idn/jur`), verification depth (`idn/kyc`: `basic`, `enhanced`, or `institutional`), and at least one verified controlled domain (`idn/dct`). The schema enforces presence and the signal metadata makes these signals non-disclosable. The floor is an issuer obligation, not a tier or verifier-configured profile.

**Reputation.** A registered TSAI reputation signal carries required `mtd`, `mtd#integrity`, `scr`, `cnt`, `wdw`, and `asof`. `mtd` identifies an immutable versioned methodology document, and its integrity value pins the exact bytes. The document defines the score's range, direction, semantics, calculation, evidence basis, and insufficient-history treatment. A Service Provider validates the document and calibrates policy by `(iss, typ, mtd)`; scores are not comparable across methodologies by default. Reputation is agent-scoped by default (`scp: agent`); an authority may additionally issue an operator aggregate (`scp: operator`). A Trust Authority asserts reputation only where it has a basis to observe it. A derived `vct` may define a different custom `rep` shape, and TSAI may add a comparable profile later when a shared evidence model exists.

The flat list is chosen over tiers because assurances are not cumulative, so an ordered scale implies an order that does not hold and is too coarse for the predicate a Service Provider evaluates. The category discriminator is chosen over a bare typed list because it lets a verifier classify a signal before it knows the specific type. The accepted costs are a governed category/type vocabulary and the loss of a single human-facing tier label.

---

## Consequences

- Supersedes ADR 004. The tiered model and its redundant markers are replaced by the flat signal list.
- A signal is an object with a `category`, a `type`, and type-specific fields. A Service Provider's admission policy is a predicate over these signals.
- The registered category/type vocabulary and field constraints live in the canonical schema and registry; extensions use derived credential types under ADR 015.
- Every credential identifies an accountable operator through the identity floor, without requiring Service-Provider policy. The floor does not define levels or ordering.
- Verification strength is no longer keyed to tiers; ADR 018 expresses it as a fixed baseline plus Service-Provider policy over the signals and action.
- Revocation stays atomic. A single credential carrying all signals is revoked as a whole, which fits the short-expiry-and-refresh model; per-signal revocation is not proposed.
- Registered reputation scores use an immutable, versioned, integrity-pinned methodology document plus mandatory interaction count, observation window, and timestamp. Agent-level reputation is primary, and an optional operator aggregate makes washing more visible but does not eliminate it. Custom derived reputation shapes remain possible; shared bands are deferred until a domain-specific evidence model can give them common semantics.
- Serialisation follows ADR 015, which selects SD-JWT VC, so the signals are carried as claims in the credential.

---

## References

- [ADR 003 — W3C Verifiable Credentials as Credential Format](./003-w3c-verifiable-credentials.md)
- [ADR 004 — Tiered Trust Model (T0-T3)](./004-tiered-trust-model.md)
- [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)
- [ADR 008 — User Privacy and Sybil Prevention](./008-user-privacy-and-sybil-prevention.md)
- ADR 014 — Holder Binding and Web Bot Auth Integration
- ADR 015 — Credential Serialisation Format
- ADR 018 — Verification Strength, Replay, and Lifetime without Tiers
- [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [draft-ietf-oauth-sd-jwt-vc](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-sd-jwt-vc)
