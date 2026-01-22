<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 007: Short-Lived Credentials with Revocation

**Status:** Accepted  
**Date:** 2026-01-22  
**Deciders:** TSAI Working Group

---

## Context

Credentials must balance security and performance:

**Security concerns:**
- Compromised agents must lose access quickly
- Stolen credentials must be invalidated
- Misbehaving agents must be revoked

**Performance concerns:**
- Revocation checks add latency
- Real-time revocation queries create TA dependency
- High-frequency verification must be fast (<5ms for T0/T1)

**Operational concerns:**
- Revocation infrastructure is complex
- Revocation lists grow over time
- Privacy implications (which credentials were checked?)

---

## Credential Expiry by Tier

| Tier | Expiry | Revocation Check | Rationale |
|------|--------|------------------|-----------|
| T0 | 2-4 hours | Optional | Low-risk, offline verification |
| T1 | 2-4 hours | Recommended | Moderate-risk, still offline |
| T2 | 1 hour | Required | High-risk, revocation adds protection |
| T3 | 30 minutes | Required (real-time) | Critical, maximum assurance |

---

## Revocation Mechanisms

### W3C BitstringStatusList (T2)

**Description:** Efficient, privacy-preserving revocation list.

**How it works:**
- TA maintains bitstring (one bit per credential)
- Bit = 0: valid, Bit = 1: revoked
- Platforms fetch bitstring, check credential's bit
- Bitstring cached (reduces TA load)

**Pros:**
- Efficient (compact representation)
- Privacy-preserving (doesn't reveal which credential was checked)
- Cacheable (reduces TA load)
- W3C standard

**Cons:**
- Requires bitstring management
- Cache invalidation complexity

**Use case:** T2 revocation checks

---

### TA Real-Time API (T3)

**Description:** Platform queries TA API for credential status.

**How it works:**
- Platform sends credential ID to TA API
- TA returns: valid/revoked + current stake/reputation + constraints
- Real-time verification (no caching)

**Pros:**
- Most current information
- Can validate constraints in real-time
- Can check current stake/reputation

**Cons:**
- TA dependency (must be highly available)
- Higher latency
- Privacy concerns (TA knows when credential is used)

**Use case:** T3 real-time verification

---

## Options Considered

### Option 1: Long-Lived Credentials + Real-Time Revocation

**Description:** Credentials valid for days/weeks; all verifications check revocation.

**Pros:**
- Less frequent credential refresh
- Lower TA load for issuance
- Simpler agent implementation

**Cons:**
- All verifications require revocation check (adds latency)
- TA dependency for all traffic (reduces availability)
- Revocation lists grow large over time
- Privacy concerns (revocation checks reveal usage patterns)
- Doesn't scale to millions of verifications/day

---

### Option 2: Short-Lived Credentials, No Revocation

**Description:** Credentials expire quickly; no revocation mechanism.

**Pros:**
- Simplest approach
- No revocation infrastructure
- No TA dependency
- Fastest verification

**Cons:**
- No emergency revocation (must wait for expiry)
- Compromised agent has access until expiry
- Not suitable for high-stakes scenarios (T2/T3)
- No way to revoke misbehaving agents immediately

---

### Option 3: Short-Lived Credentials + Tiered Revocation

**Description:**
- Short expiry (2-4 hours T0/T1, 1 hour T2, 30 min T3)
- Revocation optional for T0/T1
- Revocation required for T2/T3

**Pros:**
- Optimal performance/security balance
- 95%+ of traffic uses offline verification (no revocation)
- High-stakes scenarios get additional protection
- Emergency revocation available when needed
- Scales to millions of verifications/day

**Cons:**
- More complex than single approach
- Agents must refresh credentials frequently
- TAs must support both short expiry and revocation

---

### Option 4: Blockchain-Based Revocation

**Description:** Store revocation status on blockchain.

**Pros:**
- Decentralized (no TA dependency)
- Transparent (all revocations public)
- Tamper-evident

**Cons:**
- Latency (1-60 seconds per query)
- Cost (gas fees for updates)
- Privacy (all revocations public)
- Complexity (blockchain infrastructure)
- Doesn't align with centralized TA model

---

## Decision

Use **short-lived credentials with tiered revocation** (Option 3):

**T0/T1 (Low-stakes):**
- 2-4 hour expiry
- Revocation optional (short expiry provides sufficient protection)
- Offline verification (no TA dependency)

**T2 (Medium-stakes):**
- 1 hour expiry
- Revocation check required (W3C BitstringStatusList or TA API)
- Challenge-response verification

**T3 (High-stakes):**
- 30 minute expiry
- Real-time TA verification required (revocation + constraint validation)
- Challenge-response verification

**Rationale:**

### Short Expiry Reduces Revocation Dependency

Real-time revocation checks add latency and TA dependency. Short expiry limits damage window. T0/T1 (2-4 hours): Compromised agent loses access within 2-4 hours, acceptable for low-stakes scenarios (browsing, search), no revocation check needed (offline verification), no TA dependency (99.9% availability). T2 (1 hour): Compromised agent loses access within 1 hour, revocation check required for additional protection, acceptable latency (<500ms). T3 (30 minutes): Compromised agent loses access within 30 minutes, real-time TA verification catches issues immediately, acceptable latency (<5s).

### Revocation for High-Stakes Scenarios

T2/T3 require revocation checks for payments, transactions, sensitive operations where higher latency is acceptable and additional protection is justified. Revocation mechanisms: W3C BitstringStatusList (efficient, privacy-preserving) and TA real-time API (T3 only, full verification).

### Performance Optimization

95%+ of traffic uses T0/T1 with no revocation check (offline verification), <5ms latency, no TA dependency. 5% uses T2/T3 with revocation check required, higher latency acceptable, TA dependency justified for high-stakes.

### Credential Refresh

Agents refresh credentials before expiry via TA REST API for credential renewal. TAs can refuse renewal for misbehaving agents, enabling continuous re-evaluation of agent trustworthiness. Refresh frequency: T0/T1 every 2-4 hours, T2 every 1 hour, T3 every 30 minutes. Grace period: Agents should refresh 5-10 minutes before expiry to prevent credential expiry mid-transaction.

---

## Consequences

### Positive

- **Performance:** 95%+ of traffic uses offline verification (no revocation)
- **Security:** High-stakes scenarios get revocation protection
- **Scalability:** Scales to millions of verifications/day
- **Availability:** No TA dependency for common cases (T0/T1)
- **Flexibility:** Tiered approach balances performance and security

### Negative

- **Credential Refresh:** Agents must refresh frequently (every 2-4 hours)
- **TA Load:** Frequent credential issuance (mitigated by caching)
- **Complexity:** Multiple expiry times and revocation mechanisms

### Neutral

- **Grace Period:** Agents should refresh 5-10 minutes before expiry
- **Emergency Revocation:** Available for T2/T3 when needed
- **Continuous Evaluation:** TAs can refuse renewal for misbehaving agents

---

## Implementation Notes

### Trust Authorities

**Credential Issuance:**
- Set expiry based on tier (2-4h T0/T1, 1h T2, 30min T3)
- Include revocation status URL in credential (W3C BitstringStatusList)
- Implement credential refresh API

**Revocation:**
- Maintain BitstringStatusList (T2)
- Implement real-time verification API (T3)
- Update revocation status immediately when agent misbehaves

**Credential Refresh:**
- Agents request renewal before expiry
- TA re-evaluates agent (check for misbehavior)
- Issue new credential or refuse renewal

---

### Agents

**Credential Management:**
- Monitor credential expiry
- Refresh 5-10 minutes before expiry
- Handle refresh failures gracefully (retry, fallback)

**Refresh Strategy:**
- Proactive refresh (before expiry)
- Retry on failure (exponential backoff)
- Cache multiple credentials (from different TAs)

---

### Platforms

**Verification:**
- Check credential expiry (always)
- Check revocation status (T2/T3 only)
- Cache BitstringStatusList (reduce TA load)

**T0/T1 Verification:**
- Offline VP verification
- Check expiry
- No revocation check (optional)

**T2 Verification:**
- VP + challenge-response
- Check expiry
- Check BitstringStatusList (required)

**T3 Verification:**
- VP + challenge-response
- Check expiry
- Real-time TA query (required)

---

## References

- [W3C BitstringStatusList](https://www.w3.org/TR/vc-bitstring-status-list/)
- TSAI Design Considerations (concept/archive/01-design-considerations.md)
- TSAI High-Level Concept (concept/02-high-level-concept.md)
- Performance requirements analysis
