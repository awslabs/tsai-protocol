<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 004: Tiered Trust Model (T0-T3)

**Status:** Superseded  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group  
**Superseded by:** [Trust Signal Structure](./draft-xx3-trust-signal-structure.md) (this branch)  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

Agent interactions span a wide risk spectrum:

- **Low-risk:** Browsing, search, public APIs (millions of requests/day)
- **Medium-risk:** Content creation, moderate-value API calls
- **High-risk:** Transactions, payments, sensitive operations
- **Critical:** High-value transactions, regulated operations

A single trust level cannot serve all use cases efficiently. Low-risk scenarios need speed (<5ms); high-risk scenarios need assurance (real-time verification, economic stake).

---

## Tier Definitions

### T0: Basic Identity (MVP)

**Trust Signals:**
- Agent DID
- Operator identity
- Operator jurisdiction
- KYC level

**Verification:**
- Offline VP verification
- TA signature + agent signature
- Expiry check
- Revocation optional

**Use Cases:**
- Browsing, search, public APIs
- Low-risk interactions

**Performance:** <5ms verification

---

### T1: Identity + Reputation

**Trust Signals (T0 +):**
- Reputation score (0-100)
- Interaction count
- Success rate
- Time in operation
- Confidence level

**Verification:**
- Same as T0 (offline)
- Platform interprets reputation
- Revocation recommended but optional

**Use Cases:**
- Content creation
- Moderate-value API calls
- User interactions

**Performance:** <5ms verification

---

### T2: Identity + Reputation + Economic Stake

**Trust Signals (T1 +):**
- Posted collateral amount
- Insurance coverage
- Financial backing
- Payment reliability

**Verification:**
- VP + challenge-response
- Revocation check required
- Optional real-time TA query

**Use Cases:**
- Transactions, payments
- Sensitive operations

**Performance:** <500ms verification

---

### T3: Full Trust Signals + Real-Time Verification

**Trust Signals (T2 +):**
- Authorized operations (constraint profile)
- Value limits
- Rate limits
- Domain restrictions
- TEE attestations (optional)
- Audit reports

**Verification:**
- VP + challenge-response
- Real-time TA verification required
- Platform enforces constraints

**Use Cases:**
- High-value transactions
- Regulated operations
- Critical systems

**Performance:** <5s verification

---

## Alternatives Considered

### Option 1: Single Trust Level

**Description:** All agents have same credential type; platforms decide how to interpret.

**Pros:**
- Simplest protocol
- No tier complexity
- Easy to understand

**Cons:**
- No performance optimization (all credentials same size)
- No clear guidance for platforms
- Doesn't scale to diverse use cases
- Either too heavy for low-risk or too light for high-risk

---

### Option 2: Binary Model (Basic + Advanced)

**Description:** Two tiers only (basic identity, full trust signals).

**Pros:**
- Simpler than four tiers
- Clear distinction
- Easier to implement

**Cons:**
- Not granular enough for diverse use cases
- Reputation signals important for medium-risk scenarios
- Economic stake separate concern from constraints
- Misses optimization opportunities

---

### Option 3: Four-Tier Model (T0-T3) (Chosen)

**Description:** Four tiers with increasing trust signals and verification rigor.

**Pros:**
- Optimal performance/security balance
- Incremental adoption path
- Risk-calibrated trust
- Serves diverse use cases
- Clear guidance for platforms

**Cons:**
- More complex than single tier
- TAs may specialize in specific tiers
- Platforms must understand tier semantics

---

### Option 4: Continuous Trust Score

**Description:** Single credential with trust score (0-100); platforms set thresholds.

**Pros:**
- Maximum flexibility
- No discrete tiers
- Platforms decide thresholds

**Cons:**
- No performance optimization
- No clear verification requirements
- Ambiguous semantics (what does "75" mean?)
- Doesn't capture different signal types (reputation vs. stake vs. constraints)

---

## Decision

Implement a **four-tier trust model (T0-T3)** (Option 3) with increasing trust signals and verification rigor:

- **T0:** Basic identity (offline verification)
- **T1:** Identity + reputation (offline verification)
- **T2:** Identity + reputation + economic stake (challenge-response, revocation check)
- **T3:** Full trust signals + real-time verification (constraints, real-time TA query)

**Rationale:**

### Performance vs. Security Trade-off

**Low-risk scenarios (T0/T1):**
- Millions of requests per day
- Sub-5ms latency requirement
- Offline verification sufficient
- No TA runtime dependency

**High-risk scenarios (T2/T3):**
- Fewer requests (thousands per day)
- Higher latency acceptable (<500ms T2, <5s T3)
- Real-time verification justified
- TA dependency acceptable for assurance

**Tiered approach:**
- 95%+ of traffic uses T0/T1 (lightweight, offline)
- 5% uses T2/T3 (rigorous, online)
- Optimal balance of performance and security

### Incremental Adoption

**MVP (T0):**
- Identity only
- Simplest possible implementation
- Solves immediate problem (distinguish verified agents from bots)
- Low barrier to entry for TAs and platforms

**Growth (T1-T2):**
- Add reputation signals (T1)
- Add economic stake (T2)
- Platforms adopt incrementally based on needs

**Maturity (T3):**
- Full constraint profiles
- Real-time verification
- Regulated operations support

### Risk-Calibrated Trust

Different scenarios need different signals. Browsing (T0) needs only identity with speed. Content creation (T1) needs reputation with moderate risk. Payments (T2) need economic stake with accountability. Regulated operations (T3) need constraints with maximum assurance.

---

## Consequences

### Positive

- **Performance:** 95%+ of traffic uses lightweight offline verification
- **Adoption:** Incremental path from simple (T0) to complex (T3)
- **Flexibility:** Platforms choose appropriate tier for each use case
- **Clarity:** Clear semantics for each tier
- **Scalability:** Optimized for common cases, rigorous for high-stakes

### Negative

- **Complexity:** Four tiers to understand and implement
- **TA specialization:** Some TAs may only support lower tiers
- **Platform burden:** Must implement multiple verification paths

### Neutral

- **Ecosystem evolution:** Tiers enable phased rollout (T0 → T1 → T2 → T3)
- **Competition:** TAs can differentiate on tier support and methodology

---

## Implementation Notes

**MVP (Phase 1):**
- Implement T0 only
- Identity signals
- Offline verification
- Simplest possible start

**Phase 2:**
- Add T1 (reputation signals)
- Still offline verification
- Platforms can make risk-calibrated decisions

**Phase 3:**
- Add T2 (economic stake)
- Challenge-response verification
- Revocation checks
- Optional real-time TA queries

**Phase 4:**
- Add T3 (constraints)
- Real-time TA verification
- Constraint enforcement
- Regulated operations support

**Platform Integration:**
- Implement offline verification for T0/T1
- Add challenge-response for T2/T3
- Add real-time TA queries for T3
- Choose appropriate tier for each use case

**TA Implementation:**
- TAs may specialize in specific tiers
- T0/T1: Lower barrier to entry
- T2: Requires stake verification infrastructure
- T3: Requires real-time verification APIs

---

## References

- TSAI Design Considerations (concept/archive/01-design-considerations.md)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- Performance requirements analysis
