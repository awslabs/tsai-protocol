<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 019: Mandatory Identity Floor

**Status:** Accepted  
**Date:** 2026-08-01  
**Deciders:** TSAI Working Group  
**Relationship to ADR 016:** restores an invariant [ADR 016 — Trust Signal Structure](./016-trust-signal-structure.md) did not intend to remove

---

## Context

Before the flat signal list, the lowest tier already guaranteed an identity: a credential had to carry the operator's legal name, its jurisdiction, a verification depth, and a `did:web`, each with a stated verification method. ADR 016 replaced the tiers with a flat list in which `signals` is required but no individual signal is, and it deliberately deferred the vocabulary. The effect, unintended, was that a credential can now carry an empty signal list, validate, verify, and identify nobody. The vocabulary the architecture then defined has no type for the operator's legal name at all, while the domain model, the concept document, and the credential-format document all name the legal name as what identifies the operator.

TSAI exists so a Service Provider can know which accountable legal entity stands behind an agent. A protocol that neither requires that nor provides a field for it does not meet its own purpose. This ADR restores the guarantee. A floor is not a tier: it has no levels, and nothing is ordered against it.

---

## Decision Criteria

1. **Accountability by default.** The simplest conforming credential answers "which accountable entity is behind this agent".
2. **Minimal-integration default.** A Service Provider with no policy configured still gets the identity guarantee, without authoring anything.
3. **Not a tier.** The mechanism reintroduces no graded label.
4. **Correct actor and time.** The obligation binds the party that can meet it, at the moment it can be met.

---

## Options Considered

### Option 1: No floor (the state after ADR 016)

**Pros.** Nothing to build; maximal flexibility.

**Cons.** Fails criteria 1 and 2: a credential need identify no one, and the meaning of "a TSAI credential" is undefined.

### Option 2: The floor as a verifier-side base profile

Express the minimum as the base of the signal-profile scheme (ADR G.1 work), applied by the verifier at admission.

**Pros.** One construct for all admission policy.

**Cons.** Profiles are governance-body work and do not exist yet, so v1.0 would ship with no identity guarantee (criterion 2). A Service Provider on day one gets nothing until it configures a profile, which is the burden the incremental-adoption story says it removes.

### Option 3: The floor as an issuer obligation (decided)

A Trust Authority MUST NOT issue a credential that fails to identify its operator. Profiles then reference the floor rather than restate it.

**Pros.** Meets all four criteria. The obligation sits on the issuer at issuance, where it can be met; a profile is a predicate a verifier applies at admission, so the two constrain different actors at different times and do not duplicate. The base profile becomes "the identity floor, and nothing more", which gives the define-once property.

**Cons.** It changes what a TSAI credential means, so it is a decision rather than a schema tweak, and it is recorded here for that reason.

---

## Decision

Adopt **Option 3**. A Trust Authority MUST NOT issue a TSAI credential unless it carries the minimum identity set:

- the operator's legal name (a new identity type, `org`),
- the operator's jurisdiction (`jur`, an ISO 3166-1 alpha-2 code),
- the verification depth (`kyc`, one of `basic`, `enhanced`, `institutional`), and
- at least one verified controlled domain (`dct`).

These are all identity (`idn`) signals, verified by the Trust Authority, so they carry no `prv`. The credential schema enforces their presence, and the type metadata (ADR 022) marks them `mandatory`. The floor is not a tier and defines no ordering; a signal profile (the profile work) references it as its base.

---

## Consequences

- Every conforming credential identifies an accountable operator, and the simplest integration — "is this a verified operator I can name" — works with no Service-Provider policy.
- The identity vocabulary gains `org`, and the credential schema gains a minimum-presence constraint.
- The floor does not prevent reputation washing: an operator can register a new agent whose credential carries the operator's identity, compliance, and assurance but no agent reputation. That is the subject of ADR 021, and §5.11 records it.
- A profile scheme, when it lands, takes the floor as its base profile rather than restating the requirement.

---

## References

- [ADR 013 — VP-JWT Claim Structure](./013-vp-jwt-claim-structure.md) (the prior identity mandate lived in the tier model)
- [ADR 016 — Trust Signal Structure](./016-trust-signal-structure.md)
- [ADR 021 — Reputation Comparability, Support, and Attribution](./021-reputation.md)
- [ADR 022 — Holder-Directed Issuance and Type Metadata](./022-holder-directed-issuance-and-type-metadata.md)
