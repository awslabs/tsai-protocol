<!--
Copyright Amazon.com Inc. or its affiliates.
SPDX-License-Identifier: Apache-2.0
-->

# ADR 009: Timestamp-Based Replay Prevention

**Status:** Accepted  
**Date:** 2026-01-27  
**Deciders:** TSAI Working Group  
**Amended by:** [ADR 012 — Service Provider Terminology](./012-service-provider-terminology.md)

---

## Context

T0/T1 credentials require replay attack prevention to ensure a stolen Verifiable Presentation (VP) cannot be reused. We need a mechanism that:
- Prevents replay attacks effectively
- Minimizes state management complexity
- Reduces network round-trips
- Works offline (no TA dependency for T0/T1)

---

## Decision

Use **timestamp-based replay prevention** for T0/T1 credentials:
- Agent includes current timestamp in VP
- Platform validates timestamp is within ±30 seconds of current time
- No per-request state or nonce management required
- Replay window limited to ~1 minute

---

## Options Considered

### Option 1: Challenge-Response with Rotating Nonces (Rejected)

**Description:** Platform publishes rotating challenge (e.g., hourly/daily nonce), agent includes in VP.

**Pros:**
- Strong replay prevention
- No clock synchronization dependency

**Cons:**
- Requires nonce rotation infrastructure
- State management complexity
- Daily rotation too long, hourly adds operational burden
- Agent must fetch nonce before creating VP (extra round-trip)

---

### Option 2: Per-Request Challenge-Response

**Description:** Platform generates unique challenge per request, agent responds with signed challenge.

**Pros:**
- Strongest replay prevention
- Standard pattern

**Cons:**
- Requires two round-trips (challenge request, response)
- Platform must manage per-request state
- Adds latency and failure points
- Overkill for T0/T1 use cases

---

### Option 3: Timestamp-Based

**Description:** Agent includes current timestamp in VP, platform validates freshness.

**Pros:**
- Single request (no extra round-trips)
- No state management required
- Simple to implement
- Replay window limited to ~1 minute (acceptable for T0/T1)
- Aligns with offline verification model

**Cons:**
- Requires clock synchronization (NTP)
- Replay possible within time window (~1 minute)
- Clock drift could cause issues

---

## Decision

Use **timestamp-based replay prevention** (Option 3) for T0/T1 credentials:
- Agent includes current timestamp in VP
- Platform validates timestamp is within ±30 seconds of current time
- No per-request state or nonce management required
- Replay window limited to ~1 minute

---

## Rationale

**Why timestamp-based wins:**

1. **Operational simplicity:** No nonce rotation, no state management, no extra infrastructure
2. **Performance:** Single request, no round-trips
3. **Acceptable security:** ~1 minute replay window is acceptable for T0/T1 use cases (browsing, search, low-risk APIs)
4. **Offline verification:** Works without TA runtime dependency
5. **Clock sync assumption:** Reasonable to assume NTP in 2026

**Replay window analysis:**
- ±30 second tolerance = ~1 minute replay window
- T0/T1 use cases (browsing, search) can tolerate this
- Platforms can optionally track VP signatures to prevent replay within window
- T2/T3 will use stronger mechanisms (challenge-response, real-time verification)

**Clock synchronization:**
- Modern systems use NTP by default
- ±30 seconds accommodates minor drift
- Platforms should monitor clock sync and alert on failures

---

## Consequences

**Positive:**
- Simple implementation for platforms and agents
- No state management or nonce infrastructure
- Single request flow (better UX, fewer failure points)
- Aligns with offline verification model for T0/T1
- Easy to test and debug

**Negative:**
- Requires NTP synchronization (operational dependency)
- ~1 minute replay window (acceptable for T0/T1, not for T2/T3)
- Clock drift could cause false rejections or extended replay windows
- Platforms must monitor clock synchronization

**Neutral:**
- T2/T3 will need stronger replay prevention (challenge-response or real-time verification)
- Platforms can optionally implement VP signature tracking for additional protection

---

## Implementation Notes

**For Agents:**
- Include current UTC timestamp in VP
- Ensure system clock is NTP-synchronized
- Handle timestamp validation errors gracefully

**For Platforms:**
- Validate VP timestamp is within ±30 seconds
- Monitor NTP synchronization status
- Optionally track VP signatures to prevent replay within time window
- Log timestamp validation failures for debugging

**For TAs:**
- Document clock synchronization requirements for operators
- Provide guidance on NTP configuration

---

## References

- TSAI Architecture Specification Section 3.3.3 (VP Verification)
- TSAI Architecture Specification Section 3.6.2 (Clock Synchronization)
- RFC 3161 (Time-Stamp Protocol) - for context on timestamp-based security

