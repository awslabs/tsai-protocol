<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 018: Verification Strength, Replay, and Lifetime without Tiers

**Status:** Accepted  
**Date:** 2026-07-31  
**Deciders:** TSAI Working Group  
**Relationship to ADR 009:** amends [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)  
**Relationship to ADR 007:** amends [ADR 007 — Short-Lived Credentials](./007-short-lived-credentials.md)  
**Depends on:** ADR 014 (holder binding), ADR 015 (format), ADR 016 (signal structure), ADR 017 (party identity)


---

## Context

ADR 004 defined the tiers, and two other decisions keyed behaviour to them. ADR 009 keyed replay prevention to the tier: a timestamp within a fixed window for T0 and T1, and a challenge-response with a nonce for T2 and T3. ADR 007 keyed the credential lifetime to the tier: two to four hours for T0 and T1, one hour for T2, thirty minutes for T3. ADR 016 removes the tiers, so both need re-expressing.

The mechanisms to build on are already decided. Holder binding is a key-binding JWT per presentation (ADR 014), carrying `aud`, `iat`, an optional `nonce`, and `sd_hash`. A credential MAY carry a `status` claim keyed to the agent or operator identity (ADR 017, and the block decision recorded there). What remains is the policy over these mechanisms once there is no tier to key it to.

---

## Decision Criteria

1. **Security.** A captured credential or presentation must not be replayable to any material effect.
2. **Matches strength to risk.** The rigour of a check should follow the risk of the action, which a tier number captured only coarsely.
3. **Offline by default.** The common path must verify without contacting the Trust Authority at request time.
4. **Operational simplicity.** No per-request state or infrastructure beyond what the risk justifies.
5. **No tier.** The rule must not reintroduce a graded label on the credential.

---

## Options Considered

### Option 1: Keep a tier-keyed rule

Retain the ADR 009 and ADR 007 approach, a tier fixing the replay mechanism and the lifetime.

**Pros.** Familiar; a single label decides everything.

**Cons.** ADR 016 has removed the tiers, so there is nothing to key to, and the tier was coarse for the decision anyway (criterion 2).

### Option 2: A predicate over the signals and the action (recommended)

Express verification strength as the Service Provider's policy over the signals and the risk of the action. A fixed baseline always applies; the Service Provider escalates from it where the risk warrants.

**Pros.** Matches strength to risk at the granularity of the action (criterion 2), keeps the common path offline (criterion 3), and reintroduces no tier (criterion 5). It uses the mechanisms already decided.

**Cons.** The decision moves to the Service Provider, so there is no single portable label that says how strongly a credential was checked; interoperability rests on the baseline plus each Service Provider's stated policy.

### Option 3: A new fixed strength scale

Replace the tiers with a different fixed scale, decoupled from the signals.

**Pros.** A portable label survives.

**Cons.** It is the tier problem again under another name: a coarse scale that does not match the action, and a new vocabulary to standardise (criteria 2, 5).

---

## Decision

Adopt **Option 2**, with the following baseline and escalation.

**Lifetime.** A credential has a single lifetime: `exp` is 30 minutes after `iat`. A flow that outlives it obtains a fresh credential. This amends ADR 007, replacing the tiered expiry table. The lifetime is the re-issue cadence and is a separate clock from presentation freshness.

**Baseline, always applied.** Every presentation is verified per Section 3: the issuer signature, the key-binding signature against `cnf`, `aud` matching the Service Provider, `sd_hash`, and the lifetime. For freshness, the Service Provider bounds the age of the key-binding JWT: it SHOULD reject a key-binding JWT whose `iat` is more than 2 minutes old, with a clock-skew tolerance of 30 seconds. This is the offline baseline and needs nothing from the Trust Authority at request time. It amends ADR 009: the timestamp mechanism stands, and the tier-keying is removed.

**Escalation, by the Service Provider's policy over the signals and the action.** Where the risk of the action warrants, the Service Provider adds either or both of:

- a `nonce` it issues as a challenge, which the agent echoes in the key-binding JWT, closing the freshness window entirely;
- a fetch of the agent or operator status list, to honour a block within the lifetime.

Which action warrants which addition is the Service Provider's policy, read from the signals and the value at stake, not from a tier.

The decisive reason is that the tier was always a stand-in for a decision that is really a predicate over specific signals and the action, and removing the tier (ADR 016) lets that predicate be expressed directly. The cost accepted is that there is no single portable label for how strongly a presentation was checked; the baseline plus a stated Service-Provider policy carries that instead.

---

## Consequences

- Amends ADR 009: the timestamp-based freshness mechanism is retained and applied to the key-binding JWT; the tier-keyed escalation is replaced by the Service Provider's policy, with a nonce as the challenge where risk warrants.
- Amends ADR 007: the tiered expiry table is replaced by a single 30-minute lifetime with refresh.
- The baseline is normative and offline; the escalation is the Service Provider's policy and is non-normative, so two Service Providers may verify the same credential with different rigour.
- Section 3.4 of the verification document carries this rule directly, with this ADR cited for the rationale: the freshness bound, the nonce, and the status fetch on a risk basis.
- No tier is reintroduced.

---

## References

- [ADR 004 — Tiered Trust Model](./004-tiered-trust-model.md)
- [ADR 007 — Short-Lived Credentials](./007-short-lived-credentials.md)
- [ADR 009 — Timestamp-Based Replay Prevention](./009-timestamp-based-replay-prevention.md)
- ADR 014 (Holder Binding), ADR 016 (Trust Signal Structure), ADR 017 (Party Identity)
- [RFC 7519 — JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
